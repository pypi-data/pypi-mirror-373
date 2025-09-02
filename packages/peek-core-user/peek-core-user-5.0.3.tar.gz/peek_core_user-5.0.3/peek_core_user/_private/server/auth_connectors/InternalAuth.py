import hashlib
import logging
from datetime import datetime

import pytz
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound
from twisted.cred.error import LoginFailed
from twisted.internet.defer import Deferred
from twisted.internet.defer import inlineCallbacks
from vortex.DeferUtil import deferToThreadWrapWithLogger

from peek_core_user._private.server.auth_connectors.AuthABC import AuthABC
from peek_core_user._private.server.auth_connectors.LdapAuth import LdapAuth
from peek_core_user._private.server.controller.PasswordUpdateController import (
    PasswordUpdateController,
)
from peek_core_user._private.storage.InternalGroupTuple import (
    InternalGroupTuple,
)
from peek_core_user._private.storage.InternalUserGroupTuple import (
    InternalUserGroupTuple,
)
from peek_core_user._private.storage.InternalUserTuple import InternalUserTuple
from peek_core_user._private.storage.Setting import ADMIN_LOGIN_GROUP
from peek_core_user._private.storage.Setting import FIELD_LOGIN_GROUP
from peek_core_user._private.storage.Setting import FIELD_OTP_LOGIN_GROUP
from peek_core_user._private.storage.Setting import (
    INTERNAL_AUTH_ENABLED_FOR_ADMIN,
)
from peek_core_user._private.storage.Setting import OFFICE_LOGIN_GROUP
from peek_core_user._private.storage.Setting import globalSetting
from peek_core_user.server.UserDbErrors import UserNotFoundException
from peek_core_user.server.UserDbErrors import UserPasswordNotSetException
from peek_core_user.tuples.constants.UserAuthTargetEnum import (
    UserAuthTargetEnum,
)

logger = logging.getLogger(__name__)


class InternalAuth(AuthABC):
    @inlineCallbacks
    def checkPassAsync(self, userName, password, forService):
        try:
            authenticatedUserPassword = yield self.getInternalUserAndPassword(
                userName
            )
        except NoResultFound:
            authenticatedUserPassword = None

        # if user not found
        if (
            not authenticatedUserPassword
            or not authenticatedUserPassword.InternalUserTuple
        ):
            logger.debug(f"User '{userName}' not found")
            raise UserNotFoundException(userName)

        # if user found but user is created by LDAP
        if (
            authenticatedUserPassword.InternalUserTuple.authenticationTarget
            == UserAuthTargetEnum.LDAP
        ):
            # delegate to LDAPAuth
            return (
                yield LdapAuth(self._dbSessionCreator).checkPassAsync(
                    userName, password, forService
                )
            )

        isPasswordOtp = yield self.checkIfUserAbleToLoginWithOtp(userName)

        if (
            not isPasswordOtp
            and not authenticatedUserPassword.InternalUserPassword
        ):
            logger.debug(f"Password is not set for user {userName}")
            raise UserPasswordNotSetException(userName)

        # Check if the user is actually logged into this device.
        if isPasswordOtp:
            return (
                yield self._authenticateViaInternalOtp(
                    authenticatedUserPassword, password
                )
            )

        return (
            yield self._authenticateViaInternalPassword(
                authenticatedUserPassword, password, forService
            )
        )

    @inlineCallbacks
    def _authenticateViaInternalOtp(self, authenticatedUser, password):
        internalUserTuple = authenticatedUser[0]
        now = datetime.now(pytz.utc)
        attempted = hashlib.sha256(password.encode()).hexdigest()
        if not (
            internalUserTuple.oneTimePasscode == attempted
            and now <= internalUserTuple.oneTimePasscodeExpiry
        ):
            msg = (
                f"Peek InternalAuth: "
                f"username or one-time password is incorrect or expired"
                f"for user "
                f"'{internalUserTuple.userTitle}'"
                f"({internalUserTuple.userName})"
            )
            logger.debug(msg)
            raise LoginFailed(msg)

        groups = yield self._getUserGroupsByUserId(
            self._dbSessionCreator, internalUserTuple.id
        )

        groupNames = [g.groupName for g in groups]

        hasAceessForService = yield self.checkIfUserInUserGroup(
            self._dbSessionCreator,
            internalUserTuple.userName,
            self.FOR_SERVICE_FIELD_OTP,
            groups,
        )

        if not hasAceessForService:
            msg = (
                f"Peek InternalAuth: "
                f"User '{internalUserTuple.userTitle}'"
                f"({internalUserTuple.userName}) "
                f"is not granted permission "
                f"to service {self.getForServiceName(self.FOR_SERVICE_FIELD_OTP)}. "
                f"Please check membership of related groups, "
                f"current joined groups of the user are {', '.join(groupNames)}"
            )
            logger.debug(msg)
            raise LoginFailed(msg)

        return groupNames, authenticatedUser.InternalUserTuple

    @inlineCallbacks
    def _authenticateViaInternalPassword(
        self, authenticatedUser, password, forService
    ):
        internalUserTuple = authenticatedUser[0]
        internalUserPassword = authenticatedUser[1]
        if internalUserPassword.password != PasswordUpdateController.hashPass(
            password
        ):
            msg = (
                f"Username or password is incorrect "
                f"for user "
                f"'{internalUserTuple.userTitle}'"
                f"({internalUserTuple.userName})"
            )
            logger.debug(msg)
            raise LoginFailed(msg)

        groups = yield self._getUserGroupsByUserId(
            self._dbSessionCreator, internalUserPassword.userId
        )

        hasAceessForService = yield self.checkIfUserInUserGroup(
            self._dbSessionCreator,
            internalUserTuple.userName,
            forService,
            groups,
        )

        groupNames = [g.groupName for g in groups]

        if not hasAceessForService:
            msg = (
                f"Peek InternalAuth: "
                f"User '{internalUserTuple.userTitle}'"
                f"({internalUserTuple.userName}) "
                f"is not granted permission "
                f"to service {self.getForServiceName(forService)}. "
                f"Please check membership of related groups, "
                f"current joined groups of the user are {', '.join(groupNames)}"
            )
            logger.debug(msg)
            raise LoginFailed(msg)

        return groupNames, authenticatedUser.InternalUserTuple

    @inlineCallbacks
    def checkIfUserAbleToLoginWithOtp(self, userName: str) -> bool:
        authSettings = yield self.getAuthSettings()

        if not authSettings.internalFieldEnabled:
            return False
        else:
            groups = yield self._getUserGroupsByUserName(
                self._dbSessionCreator, userName
            )

            return (
                yield self.checkIfUserInUserGroup(
                    dbSessionCreator=self._dbSessionCreator,
                    userName=userName,
                    forService=AuthABC.FOR_SERVICE_FIELD_OTP,
                    groups=groups,
                )
            )

    @deferToThreadWrapWithLogger(logger)
    def _getUserGroupsByUserId(self, dbSessionCreator, userId):
        ormSession = dbSessionCreator()
        try:
            return (
                ormSession.query(InternalGroupTuple)
                .join(InternalUserGroupTuple)
                .filter(InternalUserGroupTuple.userId == userId)
                .all()
            )
        finally:
            ormSession.close()

    @deferToThreadWrapWithLogger(logger)
    def _getUserGroupsByUserName(
        self, dbSessionCreator, userName
    ) -> Deferred[list[InternalGroupTuple]]:
        ormSession = dbSessionCreator()
        try:
            groups = (
                ormSession.query(InternalGroupTuple)
                .join(
                    InternalUserGroupTuple,
                    onclause=InternalUserGroupTuple.groupId
                    == InternalGroupTuple.id,
                )
                .join(
                    InternalUserTuple,
                    onclause=InternalUserGroupTuple.userId
                    == InternalUserTuple.id,
                )
                .filter(
                    func.lower(InternalUserTuple.userName) == userName.lower()
                )
                .all()
            )
            return groups
        finally:
            ormSession.close()

    @classmethod
    @deferToThreadWrapWithLogger(logger)
    def checkIfUserInUserGroup(
        cls,
        dbSessionCreator,
        userName: str,
        forService,
        groups: list[InternalGroupTuple],
    ) -> bool:
        ormSession = dbSessionCreator()
        try:
            groupNames = [g.groupName for g in groups]
            if forService == cls.FOR_SERVICE_ADMIN:
                adminGroup = globalSetting(ormSession, ADMIN_LOGIN_GROUP)
                if adminGroup not in set(groupNames):
                    logger.debug(
                        "Peek InternalAuth: checkIfUserInUserGroup,"
                        " [%s]"
                        " Admin Service, Group %s, not in Groups %s",
                        userName,
                        adminGroup,
                        groupNames,
                    )
                    return False

            elif forService == cls.FOR_SERVICE_OFFICE:
                officeGroup = globalSetting(ormSession, OFFICE_LOGIN_GROUP)
                if officeGroup not in set(groupNames):
                    logger.debug(
                        "Peek InternalAuth: checkIfUserInUserGroup,"
                        " [%s]"
                        " Office Service, Group %s, not in Groups %s",
                        userName,
                        officeGroup,
                        groupNames,
                    )
                    return False

            elif (
                forService == cls.FOR_SERVICE_FIELD
                or forService == cls.FOR_SERVICE_FIELD_OTP
            ):
                fieldGroup = globalSetting(ormSession, FIELD_LOGIN_GROUP)
                if fieldGroup not in set(groupNames):
                    logger.debug(
                        "Peek InternalAuth: checkIfUserInUserGroup,"
                        " [%s]"
                        " Field Service, Group %s, not in Groups %s",
                        userName,
                        fieldGroup,
                        groupNames,
                    )
                    return False

                if forService == cls.FOR_SERVICE_FIELD_OTP:
                    fieldGroup = globalSetting(
                        ormSession, FIELD_OTP_LOGIN_GROUP
                    )
                    if fieldGroup not in set(groupNames):
                        logger.debug(
                            "Peek InternalAuth: checkIfUserInUserGroup,"
                            " [%s]"
                            " Field Service OTP, Group %s, not in Groups %s",
                            userName,
                            fieldGroup,
                            groupNames,
                        )
                        return False

            else:
                msg = (
                    f"Peek InternalAuth: Unhandled forService type "
                    f"{forService}({cls.getForServiceName(forService)})"
                )
                logger.debug(msg)
                raise Exception(msg)
            return True
        finally:
            ormSession.close()

    @deferToThreadWrapWithLogger(logger)
    def isInternalAuthEnabled(self):
        ormSession = self._dbSessionCreator()
        try:
            return globalSetting(ormSession, INTERNAL_AUTH_ENABLED_FOR_ADMIN)
            # No commit needed, we only query

        finally:
            ormSession.close()
