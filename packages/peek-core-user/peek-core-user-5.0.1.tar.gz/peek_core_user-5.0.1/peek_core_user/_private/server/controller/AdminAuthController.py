import logging
from typing import List

from twisted.cred.error import LoginFailed
from twisted.internet.defer import inlineCallbacks

from peek_core_user._private.server.auth_connectors.InternalAuth import (
    InternalAuth,
)
from peek_core_user._private.server.auth_connectors.LdapAuth import LdapAuth
from peek_plugin_base.storage.DbConnection import DbSessionCreator

logger = logging.getLogger(__name__)


class AdminAuthController:
    def __init__(self, dbSessionCreator: DbSessionCreator):
        self._dbSessionCreator: DbSessionCreator = dbSessionCreator

    def shutdown(self):
        pass

    @inlineCallbacks
    def check(self, userName, password) -> List[str]:
        if not password:
            raise LoginFailed("Password is empty")

        lastException = None

        # TRY INTERNAL IF ITS ENABLED
        try:
            internalAuth = InternalAuth(self._dbSessionCreator)
            if (yield internalAuth.isInternalAuthEnabled()):
                groupNames, _ = yield internalAuth.checkPassAsync(
                    userName, password, InternalAuth.FOR_SERVICE_ADMIN
                )
                return groupNames

        except Exception as e:
            lastException = e

        # TRY LDAP IF ITS ENABLED
        try:
            ldapAuth = LdapAuth(self._dbSessionCreator)
            if (yield ldapAuth.isLdapAuthEnabled()):
                # TODO Make the client tell us if it's for office or field
                internalUser = yield ldapAuth.getInternalUser(
                    userName, raiseNotLoggedInException=False
                )
                userUuid = internalUser.userUuid if internalUser else None

                groups, ldapLoggedInUser = yield ldapAuth.checkPassAsync(
                    userName, password, LdapAuth.FOR_SERVICE_ADMIN, userUuid
                )

                return groups, ldapLoggedInUser

        except Exception as e:
            lastException = e

        if lastException:
            raise lastException

        raise Exception(
            "No authentication handlers are enabled, enable one in settings"
        )
