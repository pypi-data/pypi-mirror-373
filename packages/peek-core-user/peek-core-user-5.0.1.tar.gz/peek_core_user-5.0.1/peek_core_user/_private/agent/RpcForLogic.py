import logging
from typing import List
from typing import Optional
from typing import Tuple

from vortex.rpc.RPC import vortexRPC

from peek_core_user._private.PluginNames import userPluginFilt
from peek_core_user._private.ldap_auth.ldap_auth import checkLdapAuth
from peek_core_user._private.storage.LdapSetting import LdapSetting
from peek_core_user._private.tuples.LdapLoggedInUserTuple import (
    LdapLoggedInUserTuple,
)
from peek_plugin_base.PeekVortexUtil import peekAgentName

logger = logging.getLogger(__name__)


class RpcForLogic:
    def __init__(self):
        pass

    def makeHandlers(self):
        """Make Handlers

        In this method we start all the RPC handlers
        start() returns an instance of itself so we can simply yield the result
        of the start method.

        """
        yield self.tryLdapLoginOnAgent.start(funcSelf=self)
        logger.debug("LogicService RPCs started")

    # -------------
    @vortexRPC(peekAgentName, additionalFilt=userPluginFilt)
    def tryLdapLoginOnAgent(
        self,
        username: str,
        password: str,
        ldapSetting: LdapSetting,
        userUuid: Optional[str],
    ) -> Tuple[List[str], LdapLoggedInUserTuple]:
        return checkLdapAuth(username, password, ldapSetting, userUuid)
