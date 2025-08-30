import logging
import os

from jsoncfg.value_mappers import require_string
from peek_core_user._private.server.controller.AdminAuthController import (
    AdminAuthController,
)
from sqlalchemy import MetaData, text

from peek_core_device.server.DeviceApiABC import DeviceApiABC
from peek_core_user._private.server.controller.metrics_controller import (
    MetricsController,
)
from peek_plugin_base.server.PluginLogicEntryHookABC import (
    PluginLogicEntryHookABC,
)
from peek_plugin_base.server.PluginServerStorageEntryHookABC import (
    PluginServerStorageEntryHookABC,
)
from peek_plugin_base.server.PluginServerWorkerEntryHookABC import (
    PluginServerWorkerEntryHookABC,
)
from peek_core_user._private.server.AdminTupleDataObservable import (
    makeAdminTupleDataObservableHandler,
)
from peek_core_user._private.server.ClientTupleActionProcessor import (
    makeTupleActionProcessorHandler,
)
from peek_core_user._private.server.ClientTupleDataObservable import (
    makeTupleDataObservableHandler,
)
from peek_core_user._private.server.admin_backend import (
    makeAdminBackendHandlers,
)
from peek_core_user._private.server.api.UserApi import UserApi
from peek_core_user._private.server.controller.ImportController import (
    ImportController,
)
from peek_core_user._private.server.controller.LoginLogoutController import (
    LoginLogoutController,
)
from peek_core_user._private.server.controller.MainController import (
    MainController,
)
from peek_core_user._private.tuples.LoggedInUserStatusTuple import (
    LoggedInUserStatusTuple,
)
from peek_core_user.server.UserApiABC import UserApiABC
from peek_plugin_base.storage.DbConnection import DbConnection

logger = logging.getLogger(__name__)


class PluginLogicEntryHook(
    PluginLogicEntryHookABC,
    PluginServerStorageEntryHookABC,
    PluginServerWorkerEntryHookABC,
):

    def __init__(self, *args, **kwargs):
        PluginLogicEntryHookABC.__init__(self, *args, **kwargs)
        self._userApi = None

        self._handlers = []

    @property
    def workerTaskImports(self):
        from peek_core_user._private.worker.tasks import (
            UserImportInternalGroupTask,
            UserImportInternalUserTask,
        )

        return [
            UserImportInternalGroupTask.__name__,
            UserImportInternalUserTask.__name__,
        ]

    def _migrateStorageSchema(self, metadata: MetaData) -> None:
        """Migrate Storage Schema

        Rename the schema

        """

        relDir = self._packageCfg.config.storage.alembicDir(require_string)
        alembicDir = os.path.join(self.rootDir, relDir)
        if not os.path.isdir(alembicDir):
            raise NotADirectoryError(alembicDir)

        dbConn = DbConnection(
            dbConnectString=self.platform.dbConnectString,
            metadata=metadata,
            alembicDir=alembicDir,
            enableCreateAll=False,
        )

        # Rename the plugin schema to core.
        renameToCoreSql = text(
            """
            DO $$
            BEGIN
                IF EXISTS(
                    SELECT schema_name
                      FROM information_schema.schemata
                      WHERE schema_name = 'pl_user'
                  )
                THEN
                  EXECUTE ' DROP SCHEMA IF EXISTS core_user CASCADE ';
                  EXECUTE ' ALTER SCHEMA pl_user RENAME TO core_user ';
                END IF;
            END
            $$;
        """
        )

        dbSession = dbConn.ormSessionCreator()
        try:
            dbSession.execute(renameToCoreSql)
            dbSession.commit()

        finally:
            dbSession.close()
            dbConn.dbEngine.dispose()

        PluginServerStorageEntryHookABC._migrateStorageSchema(self, metadata)

    def load(self) -> None:
        from peek_core_user._private.tuples import loadPrivateTuples

        loadPrivateTuples()

        from peek_core_user._private.storage.DeclarativeBase import (
            loadStorageTuples,
        )

        loadStorageTuples()

        from peek_core_user.tuples import loadPublicTuples

        loadPublicTuples()

        # ----------------
        # Setup our API
        self._userApi = UserApi()

        logger.debug("loaded")

    def start(self):
        """Start

        This will be called when the plugin is loaded, just after the db is migrated.
        Place any custom initialiastion steps here.

        """
        metricsController = MetricsController(
            writeDir=self.platform.metricsWriteDirectory,
            ormSessionCreator=self.dbSessionCreator,
        )
        metricsController.start()
        self._handlers.append(metricsController)

        # ----------------
        # Setup the APIs
        deviceApi: DeviceApiABC = self.platform.getOtherPluginApi(
            "peek_core_device"
        )
        emailApi = self.platform.getOtherPluginApi("peek_core_email")

        # ----------------
        # Import Controller
        importController = ImportController()
        self._handlers.append(importController)

        # ----------------
        # Login / Logout Controller
        loginLogoutController = LoginLogoutController(
            deviceApi, emailApi, self.dbSessionCreator
        )
        self._handlers.append(loginLogoutController)

        # ----------------
        # Login / Logout Controller
        adminAuthController = AdminAuthController(self.dbSessionCreator)
        self._handlers.append(adminAuthController)

        # ----------------
        # Setup our API
        self._userApi.setStartValues(
            self.dbSessionCreator,
            deviceApi,
            importController,
            loginLogoutController,
            adminAuthController,
        )

        # ----------------
        # Main Controller
        mainController = MainController(self.dbSessionCreator, self._userApi)
        self._handlers.append(mainController)

        # ----------------
        # Client Tuple Observable
        clientTupleObservable = makeTupleDataObservableHandler(
            self.dbSessionCreator, self._userApi
        )
        self._handlers.append(clientTupleObservable)

        # ----------------
        # Admin Tuple Observable
        adminTupleObservable = makeAdminTupleDataObservableHandler(
            self.dbSessionCreator, deviceApi, self._userApi
        )
        self._handlers.append(adminTupleObservable)

        # ----------------
        # Setup controllers.
        loginLogoutController.setup(
            clientTupleObservable,
            adminTupleObservable,
            self._userApi.fieldHookApi,
            self._userApi.infoApi,
        )
        importController.setTupleObserver(clientTupleObservable)

        # Make the admin observable send an update when device online / offline
        # state changes occur
        deviceApi.deviceOnlineStatus().subscribe(
            lambda _: adminTupleObservable.notifyOfTupleUpdateForTuple(
                LoggedInUserStatusTuple.tupleType()
            )
        )

        # ----------------
        # Setup the Action Processor
        self._handlers.append(makeTupleActionProcessorHandler(mainController))

        # ----------------
        # Setup admin backend
        self._handlers.extend(
            makeAdminBackendHandlers(
                clientTupleObservable, self.dbSessionCreator
            )
        )

        logger.debug("started")

    def stop(self):
        for handler in self._handlers:
            handler.shutdown()

        if self._userApi:
            self._userApi.shutdown()

        logger.debug("stopped")

    def unload(self):
        logger.debug("unloaded")

    @property
    def publishedServerApi(self) -> UserApiABC:
        return self._userApi

    @property
    def dbMetadata(self):
        from peek_core_user._private.storage import DeclarativeBase

        return DeclarativeBase.metadata

    ###### Implement PluginServerWorkerEntryHookABC
