import logging

from peek_core_user._private.agent.RpcForLogic import RpcForLogic
from peek_core_user._private.storage.DeclarativeBase import loadStorageTuples
from peek_core_user._private.tuples import loadPrivateTuples
from peek_core_user.tuples import loadPublicTuples
from peek_plugin_base.agent.PluginAgentEntryHookABC import (
    PluginAgentEntryHookABC,
)

logger = logging.getLogger(__name__)


class AgentEntryHook(PluginAgentEntryHookABC):
    _loadedObjects = []

    def load(self) -> None:
        loadStorageTuples()
        loadPrivateTuples()
        loadPublicTuples()

        logger.debug("Loaded")

    def start(self):
        self._loadedObjects.extend(RpcForLogic().makeHandlers())
        logger.debug("Started")

    def stop(self):
        logger.debug("Stopped")

    def unload(self):
        logger.debug("Unloaded")
