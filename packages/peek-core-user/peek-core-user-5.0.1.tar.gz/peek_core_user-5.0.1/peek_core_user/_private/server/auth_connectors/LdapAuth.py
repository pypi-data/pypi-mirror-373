import logging
from collections import namedtuple
from typing import List

from twisted.cred.error import LoginFailed
from twisted.internet.defer import inlineCallbacks
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.VortexFactory import NoVortexException
from vortex.VortexFactory import VortexFactory

from peek_core_user._private.PluginNames import userPluginTuplePrefix
from peek_core_user._private.agent.RpcForLogic import RpcForLogic
from peek_core_user._private.ldap_auth.ldap_auth import checkLdapAuth
from peek_core_user._private.server.auth_connectors.AuthABC import AuthABC
from peek_core_user._private.storage.InternalUserTuple import InternalUserTuple
from peek_core_user._private.storage.LdapSetting import LdapSetting
from peek_core_user._private.storage.Setting import LDAP_AUTH_ENABLED
from peek_core_user._private.storage.Setting import LDAP_ENABLE_DOMAIN_SUPPORT
from peek_core_user._private.storage.Setting import LDAP_VERIFY_SSL
from peek_core_user._private.storage.Setting import globalSetting
from peek_platform.file_config.PeekFileConfigABC import PEEK_AGENT_SERVICE

__author__ = "synerty"

from peek_core_user._private.tuples.LdapLoggedInUserTuple import (
    LdapLoggedInUserTuple,
)
from peek_core_user.tuples.constants.UserAuthTargetEnum import (
    UserAuthTargetEnum,
)

logger = logging.getLogger(__name__)

import ldap


class LdapNotEnabledError(Exception):
    pass


_LdapAuthSettings = namedtuple(
    "_LdapAuthSettings", ["ldapSettings", "ldapVerifySsl", "ldapEnableDomain"]
)


class LdapAuth(AuthABC):
    @inlineCallbacks
    def checkPassAsync(self, userName, password, forService, userUuid=None):
        """Login User

        :param forService:
        :param userName: The username of the user.
        :param password: The users secret password.
        :param userUuid: The decoded objectSid of the user from LDAP
        :rtype
        """

        assert forService in (
            AuthABC.FOR_SERVICE_FIELD,
            AuthABC.FOR_SERVICE_OFFICE,
            AuthABC.FOR_SERVICE_ADMIN,
        ), "Unhandled authentication for service type"

        authSettings: _LdapAuthSettings = yield self._getSettings()

        if not authSettings.ldapEnableDomain and "@" in userName:
            raise Exception(
                "Please login with a username, not an email address"
            )

        if not authSettings.ldapVerifySsl:
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

        if not authSettings.ldapSettings:
            raise Exception("LDAPAuth: No LDAP servers configured.")

        firstException = None

        for ldapSetting in authSettings.ldapSettings:
            if forService == self.FOR_SERVICE_ADMIN:
                if not ldapSetting.adminEnabled:
                    continue

            elif forService == self.FOR_SERVICE_OFFICE:
                if not ldapSetting.desktopEnabled:
                    continue

            elif forService == self.FOR_SERVICE_FIELD:
                if not ldapSetting.mobileEnabled:
                    continue

            else:
                raise Exception(
                    "LDAPAuth: Unhandled forService type %s" % forService
                )

            if (
                "@" in userName
                and userName.split("@")[1] != ldapSetting.ldapDomain
            ):
                continue

            try:
                logger.info("Trying LDAP login for %s", ldapSetting.ldapDomain)

                # None, zero length string and just spaces.
                if (
                    not ldapSetting.agentHost
                    or not ldapSetting.agentHost.strip()
                ):
                    logger.debug("Trying LDAP on Logic Service")
                    (groups, ldapLoggedInUser) = checkLdapAuth(
                        userName, password, ldapSetting, userUuid
                    )

                else:
                    logger.debug(
                        "Trying LDAP on Agent %s", ldapSetting.agentHost
                    )
                    (groups, ldapLoggedInUser) = (
                        yield self._forwardLdapAuthToAgent(
                            userName, password, ldapSetting, userUuid
                        )
                    )

                internalUser = yield self._getOrCreateInternalUserAsync(
                    ldapLoggedInUser
                )
                return groups, internalUser

            except LoginFailed as e:
                if not firstException:
                    firstException = e

        logger.error("Login failed for %s, %s", userName, str(firstException))

        if firstException:
            raise firstException

        raise LoginFailed("LDAPAuth: No LDAP providers found for this service")

    @inlineCallbacks
    def _forwardLdapAuthToAgent(
        self, userName, password, ldapSetting, userUuid
    ):
        agentHost = ldapSetting.agentHost
        try:
            vortexUuid = VortexFactory.getRemoteVortexInfoByIp(
                agentHost, PEEK_AGENT_SERVICE
            )

        except KeyError:
            logger.error(f"Could not find Peek Agent with hostname {agentHost}")
            raise LoginFailed(
                "Failed to login, ask an administrator to check " "the logs"
            )

        except NoVortexException as e:
            logger.error(str(e))
            raise LoginFailed(
                "Failed to login, ask an administrator to check " "the logs"
            )

        try:
            return (
                yield RpcForLogic.tryLdapLoginOnAgent.callForVortexUuid(
                    vortexUuid, userName, password, ldapSetting, userUuid
                )
            )
        except Exception as e:
            logger.debug("Login failed on agent, here is the error: %s", e)
            raise LoginFailed(
                str(e)
                .splitlines()[-1]
                .replace("twisted.cred.error.LoginFailed: LDAPAuth: ", "")
            )

    @deferToThreadWrapWithLogger(logger)
    def _getOrCreateInternalUserAsync(
        self, ldapLoggedInUser: LdapLoggedInUserTuple
    ) -> List[LdapSetting]:
        session = self._dbSessionCreator()
        try:
            internalUser = self._getOrCreateInternalUserBlocking(
                session, ldapLoggedInUser
            )
            session.expunge_all()
            session.commit()

            return internalUser

        finally:
            session.close()

    # noinspection PyMethodMayBeStatic
    def _getOrCreateInternalUserBlocking(
        self, dbSession, ldapLoggedInUser: LdapLoggedInUserTuple
    ) -> InternalUserTuple:
        internalUser = (
            dbSession.query(InternalUserTuple)
            .filter(InternalUserTuple.userUuid == ldapLoggedInUser.userUuid)
            .first()
        )

        # do no create, return the existing user
        if internalUser:
            logger.info("Found existing internal user %s", internalUser.userKey)
            if "@" not in internalUser.userKey:
                internalUser.userKey = (
                    internalUser.userName
                    if "@" in internalUser.userName
                    else (
                        "%s@%s"
                        % (internalUser.userName, ldapLoggedInUser.ldapDomain)
                    )
                )
                dbSession.merge(internalUser)
                dbSession.commit()

            return internalUser

        userKey = "%s@%s" % (
            ldapLoggedInUser.username,
            ldapLoggedInUser.ldapDomain,
        )
        logger.info("Creating new internal user: %s", userKey)
        newInternalUser = InternalUserTuple(
            userName=ldapLoggedInUser.username.lower(),
            userKey=(
                ldapLoggedInUser.username
                if "@" in ldapLoggedInUser.username
                else userKey
            ).lower(),
            userTitle="%s (%s)"
            % (ldapLoggedInUser.userTitle, ldapLoggedInUser.ldapName),
            userUuid=ldapLoggedInUser.userUuid,
            email=(
                ldapLoggedInUser.email.lower()
                if ldapLoggedInUser.email
                else None
            ),
            authenticationTarget=UserAuthTargetEnum.LDAP,
            importSource="LDAP",
            # importHash e.g. 'peek_core_user.LDAPAuth:<md5 hash>'
            importHash=f"{userPluginTuplePrefix}LDAPAuth:{ldapLoggedInUser.userUuid}",
        )

        try:
            dbSession.add(newInternalUser)
        except Exception as e:
            logger.info(e)
            raise LoginFailed(
                "Failed to create Internal User. Use the full name <username>@<ldap-domain> to login"
            )
        dbSession.commit()
        return newInternalUser

    @deferToThreadWrapWithLogger(logger)
    def _getSettings(self) -> _LdapAuthSettings:
        session = self._dbSessionCreator()
        try:
            # Check if the user is actually logged into this device.
            ldapSettings = session.query(LdapSetting).all()
            ldapVerifySsl = globalSetting(session, LDAP_VERIFY_SSL)
            ldapEnableDomain = globalSetting(
                session, LDAP_ENABLE_DOMAIN_SUPPORT
            )

            session.expunge_all()

            return _LdapAuthSettings(
                ldapSettings=ldapSettings,
                ldapVerifySsl=ldapVerifySsl,
                ldapEnableDomain=ldapEnableDomain,
            )

            # No commit needed, we only query

        finally:
            session.close()

    @deferToThreadWrapWithLogger(logger)
    def isLdapAuthEnabled(self) -> _LdapAuthSettings:
        session = self._dbSessionCreator()
        try:
            return globalSetting(session, LDAP_AUTH_ENABLED)
            # No commit needed, we only query

        finally:
            session.close()
