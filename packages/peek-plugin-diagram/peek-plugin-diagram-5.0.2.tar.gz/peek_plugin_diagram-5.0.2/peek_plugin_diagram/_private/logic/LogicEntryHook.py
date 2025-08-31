import logging

from twisted.internet.defer import inlineCallbacks
from vortex.DeferUtil import deferToThreadWrapWithLogger

from peek_plugin_base.server.PluginLogicEntryHookABC import (
    PluginLogicEntryHookABC,
)
from peek_plugin_base.server.PluginServerStorageEntryHookABC import (
    PluginServerStorageEntryHookABC,
)
from peek_plugin_base.server.PluginServerWorkerEntryHookABC import (
    PluginServerWorkerEntryHookABC,
)
from peek_plugin_diagram._private.logic.api.DiagramApi import DiagramApi
from peek_plugin_diagram._private.logic.client_handlers.rpc.BranchIndexChunkLoadRpc import (
    BranchIndexChunkLoadRpc,
)
from peek_plugin_diagram._private.logic.client_handlers.rpc.BranchIndexChunkUpdateHandler import (
    BranchIndexChunkUpdateHandler,
)
from peek_plugin_diagram._private.logic.client_handlers.rpc.ClientGridLoaderRpc import (
    ClientGridLoaderRpc,
)
from peek_plugin_diagram._private.logic.client_handlers.rpc.ClientGridUpdateHandler import (
    ClientGridUpdateHandler,
)
from peek_plugin_diagram._private.logic.client_handlers.rpc.ClientLocationIndexLoaderRpc import (
    ClientLocationIndexLoaderRpc,
)
from peek_plugin_diagram._private.logic.client_handlers.rpc.ClientLocationIndexUpdateHandler import (
    ClientLocationIndexUpdateHandler,
)
from peek_plugin_diagram._private.logic.controller.branch_index_compiler_queue_controller import (
    BranchIndexCompilerQueueController,
)
from peek_plugin_diagram._private.logic.controller.branch_live_edit_controller import (
    BranchLiveEditController,
)
from peek_plugin_diagram._private.logic.controller.branch_update_controller import (
    BranchUpdateController,
)
from peek_plugin_diagram._private.logic.controller.disp_compiler_queue_controller import (
    DispCompilerQueueController,
)
from peek_plugin_diagram._private.logic.controller.disp_import_controller import (
    DispImportController,
)
from peek_plugin_diagram._private.logic.controller.grid_key_compiler_queue_controller import (
    GridKeyCompilerQueueController,
)
from peek_plugin_diagram._private.logic.controller.live_db_watch_controller import (
    LiveDbWatchController,
)
from peek_plugin_diagram._private.logic.controller.location_compiler_queue_controller import (
    LocationCompilerQueueController,
)
from peek_plugin_diagram._private.logic.controller.lookup_import_controller import (
    LookupImportController,
)
from peek_plugin_diagram._private.storage import DeclarativeBase
from peek_plugin_diagram._private.storage.DeclarativeBase import (
    loadStorageTuples,
)
from peek_plugin_diagram._private.storage.Setting import BRANCH_COMPILER_ENABLED
from peek_plugin_diagram._private.storage.Setting import DISP_COMPILER_ENABLED
from peek_plugin_diagram._private.storage.Setting import GRID_COMPILER_ENABLED
from peek_plugin_diagram._private.storage.Setting import (
    LOCATION_COMPILER_ENABLED,
)
from peek_plugin_diagram._private.storage.Setting import globalProperties
from peek_plugin_diagram._private.storage.Setting import globalSetting
from peek_plugin_diagram._private.tuples import loadPrivateTuples
from peek_plugin_diagram.tuples import loadPublicTuples
from peek_plugin_livedb.server.LiveDBApiABC import LiveDBApiABC
from peek_plugin_diagram._private.logic.client_handlers.client_tuple_action_processor import (
    makeClientTupleActionProcessorHandler,
)
from peek_plugin_diagram._private.logic.client_handlers.client_tuple_data_observable import (
    makeClientTupleDataObservableHandler,
)
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

from .admin_handlers.SettingPropertyHandler import makeSettingPropertyHandler
from .admin_handlers.admin_tuple_action_processor import (
    makeAdminTupleActionProcessorHandler,
)
from .admin_handlers.admin_tuple_data_loader_delegate import (
    makeAdminTupleDataLoader,
)
from .admin_handlers.admin_tuple_data_observable import (
    makeAdminTupleDataObservableHandler,
)
from .controller.status_controller import StatusController
from .controller.admin_backend_controller import AdminBackendController
from .controller.observable_notify_controller import ObservableNotifyController

logger = logging.getLogger(__name__)


class LogicEntryHook(
    PluginLogicEntryHookABC,
    PluginServerStorageEntryHookABC,
    PluginServerWorkerEntryHookABC,
):

    def __init__(self, *args, **kwargs):
        """ " Constructor"""
        # Call the base classes constructor
        PluginLogicEntryHookABC.__init__(self, *args, **kwargs)

        #: Loaded Objects, This is a list of all objects created when we start
        self._loadedObjects = []

        self._api = None

    @property
    def workerTaskImports(self):
        from peek_plugin_diagram._private.worker.tasks import (
            GridCompilerTask,
            ImportDispTask,
            DispCompilerTask,
            LocationIndexCompilerTask,
        )
        from peek_plugin_diagram._private.worker.tasks.branch import (
            BranchIndexCompilerTask,
            BranchIndexImporterTask,
            BranchIndexUpdaterTask,
        )
        return [
            BranchIndexUpdaterTask.__name__,
            BranchIndexCompilerTask.__name__,
            BranchIndexImporterTask.__name__,
            DispCompilerTask.__name__,
            GridCompilerTask.__name__,
            ImportDispTask.__name__,
            LocationIndexCompilerTask.__name__,
        ]


    def load(self) -> None:
        """Load

        This will be called when the plugin is loaded, just after the db is migrated.
        Place any custom initialiastion steps here.

        """
        loadStorageTuples()
        loadPrivateTuples()
        loadPublicTuples()
        logger.debug("Loaded")

    @property
    def dbMetadata(self):
        return DeclarativeBase.metadata

    @inlineCallbacks
    def start(self):
        """Start

        This will be called when the plugin is loaded, just after the db is migrated.
        Place any custom initialisation steps here.

        """

        # ----------------
        # Get a reference to the LiveDB API
        liveDbApi = self.platform.getOtherPluginApi("peek_plugin_livedb")
        assert isinstance(
            liveDbApi, LiveDBApiABC
        ), "peek_plugin_diagram LiveDBApi not loaded"

        # ----------------
        # create the client grid updater
        clientGridUpdateHandler = ClientGridUpdateHandler(self.dbSessionCreator)
        self._loadedObjects.append(clientGridUpdateHandler)

        # ----------------
        # create the client disp key index updater
        clientDispIndexUpdateHandler = ClientLocationIndexUpdateHandler(
            self.dbSessionCreator
        )
        self._loadedObjects.append(clientDispIndexUpdateHandler)

        # ----------------
        # Create the client branch index handler
        clientBranchIndexChunkUpdateHandler = BranchIndexChunkUpdateHandler(
            self.dbSessionCreator
        )
        self._loadedObjects.append(clientBranchIndexChunkUpdateHandler)

        # ----------------
        # create the Status Controller
        statusController = StatusController()
        self._loadedObjects.append(statusController)

        # ----------------
        # Create the GRID KEY queue
        gridKeyCompilerQueueController = GridKeyCompilerQueueController(
            self.dbSessionCreator, statusController, clientGridUpdateHandler
        )
        self._loadedObjects.append(gridKeyCompilerQueueController)

        def locationsCanBeQueuedFunc() -> bool:
            return (
                not gridKeyCompilerQueueController.isBusy()
                and not dispCompilerQueueController.isBusy()
            )

        # ----------------
        # Create the LOCATION INDEX queue
        locationIndexCompilerQueueController = LocationCompilerQueueController(
            self.dbSessionCreator,
            statusController,
            clientDispIndexUpdateHandler,
            readyLambdaFunc=locationsCanBeQueuedFunc,
        )
        self._loadedObjects.append(locationIndexCompilerQueueController)

        # ----------------
        # Create the DISP queue
        dispCompilerQueueController = DispCompilerQueueController(
            self.dbSessionCreator, statusController
        )
        self._loadedObjects.append(dispCompilerQueueController)

        # ----------------
        # Branch Live Edit Controller

        branchLiveEditController = BranchLiveEditController()
        self._loadedObjects.append(branchLiveEditController)

        # ----------------
        # Branch Index Compiler Controller
        branchIndexCompilerQueueController = BranchIndexCompilerQueueController(
            dbSessionCreator=self.dbSessionCreator,
            statusController=statusController,
            clientUpdateHandler=clientBranchIndexChunkUpdateHandler,
        )
        self._loadedObjects.append(branchIndexCompilerQueueController)

        # ----------------
        # Create the Tuple Observer
        clientBackendTupleObservable = makeClientTupleDataObservableHandler(
            self.dbSessionCreator, branchLiveEditController
        )
        self._loadedObjects.append(clientBackendTupleObservable)

        # ----------------
        # Tell the status controller about the Tuple Observable
        branchLiveEditController.setTupleObservable(
            clientBackendTupleObservable
        )

        # ----------------
        # Create the display object Import Controller
        dispImportController = DispImportController(
            dbSessionCreator=self.dbSessionCreator,
            liveDbWriteApi=liveDbApi.writeApi,
        )
        self._loadedObjects.append(dispImportController)

        # ----------------
        # Create the import lookup controller
        lookupImportController = LookupImportController(
            dbSessionCreator=self.dbSessionCreator
        )
        self._loadedObjects.append(lookupImportController)

        # ----------------
        # Create the update branch controller
        branchUpdateController = BranchUpdateController(
            liveDbWriteApi=liveDbApi.writeApi,
            tupleObservable=clientBackendTupleObservable,
            liveEditController=branchLiveEditController,
            dbSessionCreator=self.dbSessionCreator,
        )
        self._loadedObjects.append(branchUpdateController)

        # ----------------
        # Create the Watch Grid Controller
        liveDbWatchController = LiveDbWatchController(
            liveDbWriteApi=liveDbApi.writeApi,
            liveDbReadApi=liveDbApi.readApi,
            dbSessionCreator=self.dbSessionCreator,
        )
        self._loadedObjects.append(liveDbWatchController)

        # ----------------
        # Create the GRID API for the client
        self._loadedObjects.extend(
            ClientGridLoaderRpc(
                liveDbWatchController=liveDbWatchController,
                dbSessionCreator=self.dbSessionCreator,
            ).makeHandlers()
        )

        # ----------------
        # Create the Branch Index for the client
        self._loadedObjects.extend(
            BranchIndexChunkLoadRpc(
                dbSessionCreator=self.dbSessionCreator
            ).makeHandlers()
        )

        # ----------------
        # Create the LOCATION API for the client
        self._loadedObjects.extend(
            ClientLocationIndexLoaderRpc(
                dbSessionCreator=self.dbSessionCreator
            ).makeHandlers()
        )

        # ----------------
        # Initialise the API object that will be shared with other plugins
        self._api = DiagramApi(
            statusController,
            dispImportController,
            lookupImportController,
            branchUpdateController,
            self.dbSessionCreator,
        )
        self._loadedObjects.append(self._api)

        # ----------------
        # Create the Action Processor
        clientTupleActionProcessor = makeClientTupleActionProcessorHandler(
            branchUpdateController, branchLiveEditController
        )
        self._loadedObjects.append(clientTupleActionProcessor)

        # ----------------
        # Start the admin backend
        yield self._startAdminBackend(
            statusController=statusController,
            dispCompilerQueueController=dispCompilerQueueController,
            gridKeyCompilerQueueController=gridKeyCompilerQueueController,
            clientBackendTupleObservable=clientBackendTupleObservable,
        )

        # ----------------
        # Start the queue controller

        settings = yield self._loadSettings()

        if settings[DISP_COMPILER_ENABLED]:
            dispCompilerQueueController.start()

        if settings[GRID_COMPILER_ENABLED]:
            gridKeyCompilerQueueController.start()

        if settings[BRANCH_COMPILER_ENABLED]:
            branchIndexCompilerQueueController.start()

        if settings[LOCATION_COMPILER_ENABLED]:
            locationIndexCompilerQueueController.start()

        logger.debug("Started")

    @inlineCallbacks
    def _startAdminBackend(
        self,
        statusController: StatusController,
        dispCompilerQueueController: DispCompilerQueueController,
        gridKeyCompilerQueueController: GridKeyCompilerQueueController,
        clientBackendTupleObservable: TupleDataObservableHandler,
    ):
        yield None

        self._loadedObjects.append(
            makeSettingPropertyHandler(self.dbSessionCreator)
        )

        # AdminBackendController
        adminBackendController = AdminBackendController(
            dispCompilerQueueController, gridKeyCompilerQueueController
        )

        # makeAdminTupleDataObservableHandler
        adminTupleObservable = makeAdminTupleDataObservableHandler(
            self.dbSessionCreator, statusController
        )
        self._loadedObjects.append(adminTupleObservable)

        # makeAdminTupleActionProcessorHandler
        adminTupleActionProcessor = makeAdminTupleActionProcessorHandler(
            adminBackendController
        )
        self._loadedObjects.append(adminTupleActionProcessor)

        # makeAdminTupleDataLoader
        adminTupleDataLoader = makeAdminTupleDataLoader(
            adminTupleObservable,
            adminTupleActionProcessor,
            self.dbSessionCreator,
        )
        self._loadedObjects.append(adminTupleDataLoader)
        adminTupleDataLoader.start()

        # ObservableNotifyController
        observableNotifyController = ObservableNotifyController(
            adminTupleObservable=adminTupleObservable,
            clientBackendTupleObservable=clientBackendTupleObservable,
        )
        self._loadedObjects.append(observableNotifyController)

        statusController.setTupleObservable(adminTupleObservable)

    def stop(self):
        """Stop

        This method is called by the platform to tell the peek app to shutdown and stop
        everything it's doing
        """
        # Shutdown and dereference all objects we constructed when we started
        while self._loadedObjects:
            self._loadedObjects.pop().shutdown()

        self._api = None

        logger.debug("Stopped")

    def unload(self):
        """Unload

        This method is called after stop is called, to unload any last resources
        before the PLUGIN is unlinked from the platform

        """
        logger.debug("Unloaded")

    @property
    def publishedServerApi(self) -> object:
        """Published Server API

        :return  class that implements the API that can be used by other Plugins on this
        platform service.
        """
        return self._api

    @deferToThreadWrapWithLogger(logger)
    def _loadSettings(self):
        dbSession = self.dbSessionCreator()
        try:
            return {
                globalProperties[p.key]: p.value
                for p in globalSetting(dbSession).propertyObjects
            }

        finally:
            dbSession.close()

    ###### Implement PluginServerWorkerEntryHookABC
