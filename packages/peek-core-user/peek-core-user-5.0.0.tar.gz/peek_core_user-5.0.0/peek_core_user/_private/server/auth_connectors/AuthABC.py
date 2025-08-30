import logging
from abc import ABCMeta
from abc import abstractmethod
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Tuple

from sqlalchemy import Row
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.orm.exc import NoResultFound
from twisted.internet.defer import Deferred
from vortex.DeferUtil import deferToThreadWrapWithLogger

from peek_core_user._private.storage.Setting import (
    INTERNAL_AUTH_ENABLED_FOR_ADMIN,
)
from peek_core_user._private.storage.Setting import (
    INTERNAL_AUTH_ENABLED_FOR_FIELD,
)
from peek_core_user._private.storage.Setting import (
    INTERNAL_AUTH_ENABLED_FOR_OFFICE,
)
from peek_core_user._private.storage.Setting import LDAP_AUTH_ENABLED
from peek_core_user._private.storage.Setting import globalSetting
from peek_core_user._private.storage.InternalUserPassword import (
    InternalUserPassword,
)
from peek_core_user._private.storage.InternalUserTuple import InternalUserTuple
from peek_plugin_base.storage.DbConnection import DbSessionCreator

logger = logging.getLogger(__name__)


class AuthSettings(NamedTuple):
    internalFieldEnabled: bool
    internalOfficeEnabled: bool
    internalAdminEnabled: bool
    ldapAuthEnabled: bool


class AuthABC(metaclass=ABCMeta):
    FOR_SERVICE_ADMIN = 1
    FOR_SERVICE_OFFICE = 2
    FOR_SERVICE_FIELD = 3
    FOR_SERVICE_FIELD_OTP = 4

    def __init__(self, dbSessionCreator: DbSessionCreator):
        self._dbSessionCreator = dbSessionCreator

    @abstractmethod
    def checkPassAsync(
        self, userName: str, password: str, forService: int
    ) -> Tuple[List[str], InternalUserTuple]:
        raise NotImplementedError()

    @deferToThreadWrapWithLogger(logger)
    def getInternalUser(
        self, userName, raiseNotLoggedInException=True
    ) -> Optional[InternalUserTuple]:
        ormSession = self._dbSessionCreator()
        try:
            authenticatedUsers = (
                ormSession.query(InternalUserTuple)
                .filter(func.lower(InternalUserTuple.userName) == userName.lower())
                .all()
            )
            ormSession.expunge_all()

            if len(authenticatedUsers) == 0:
                if raiseNotLoggedInException:
                    raise NoResultFound()
                else:
                    return None

            if len(authenticatedUsers) != 1:
                if raiseNotLoggedInException:
                    raise Exception("Too many users found")
                else:
                    return None

            return authenticatedUsers[0]

            # No commit needed, we only query
        finally:
            ormSession.close()

    @deferToThreadWrapWithLogger(logger)
    def getInternalUserAndPassword(
        self, userName
    ) -> Deferred[Row[InternalUserTuple, InternalUserPassword]]:
        ormSession = self._dbSessionCreator()
        try:
            statement = (
                select(InternalUserTuple, InternalUserPassword)
                .join(
                    InternalUserPassword, isouter=True
                )  # effectively `LEFT JOIN`
                .filter(
                    func.lower(InternalUserTuple.userName) == userName.lower()
                )
            )
            authenticatedUserPasswords = ormSession.execute(
                statement
            ).fetchall()
            ormSession.expunge_all()

            if len(authenticatedUserPasswords) == 0:
                raise NoResultFound()

            if len(authenticatedUserPasswords) != 1:
                raise Exception("Too many users found")

            return authenticatedUserPasswords[0]

            # No commit needed, we only query
        finally:
            ormSession.close()

    @deferToThreadWrapWithLogger(logger)
    def getAuthSettings(self) -> AuthSettings:
        """
        Returns Deferred[UserLogoutResponseTuple]
        """

        ormSession = self._dbSessionCreator()
        try:
            settings = globalSetting(ormSession)
            return AuthSettings(
                internalFieldEnabled=settings[INTERNAL_AUTH_ENABLED_FOR_FIELD],
                internalOfficeEnabled=settings[
                    INTERNAL_AUTH_ENABLED_FOR_OFFICE
                ],
                internalAdminEnabled=settings[INTERNAL_AUTH_ENABLED_FOR_ADMIN],
                ldapAuthEnabled=settings[LDAP_AUTH_ENABLED],
            )

        finally:
            ormSession.close()

    @deferToThreadWrapWithLogger(logger)
    def getInternalUserAndOtp(self, userName) -> Deferred[InternalUserTuple]:
        ormSession = self._dbSessionCreator()
        try:
            authenticatedUserOtps = (
                ormSession.query(InternalUserTuple)
                .filter(
                    func.lower(InternalUserTuple.userName) == userName.lower()
                )
                .all()
            )
            ormSession.expunge_all()

            if len(authenticatedUserOtps) == 0:
                raise NoResultFound()

            if len(authenticatedUserOtps) != 1:
                raise Exception("Too many users found")

            return authenticatedUserOtps[0]

            # No commit needed, we only query
        finally:
            ormSession.close()

    @classmethod
    def getForServiceName(cls, forService: int):
        if forService == cls.FOR_SERVICE_ADMIN:
            return "admin"
        elif forService == cls.FOR_SERVICE_OFFICE:
            return "office"
        elif forService == cls.FOR_SERVICE_FIELD:
            return "field"
        elif forService == cls.FOR_SERVICE_FIELD_OTP:
            return "field otp"
        return "unknown"
