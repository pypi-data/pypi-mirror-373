import logging

from peek_plugin_base.worker.plugin_worker_entry_hook_abc import (
    PluginWorkerEntryHookABC,
)
from peek_core_user._private.storage.DeclarativeBase import loadStorageTuples
from peek_core_user._private.tuples import loadPrivateTuples
from peek_core_user.tuples import loadPublicTuples

logger = logging.getLogger(__name__)


class WorkerEntryHook(PluginWorkerEntryHookABC):
    def load(self):
        loadStorageTuples()
        loadPrivateTuples()
        loadPublicTuples()

        logger.debug("loaded")

    def start(self):
        logger.debug("started")

    def stop(self):
        logger.debug("stopped")

    def unload(self):
        logger.debug("unloaded")