import logging

from peek_core_api._private.logic.TupleDataObservable import (
    makeTupleDataObservableHandler,
)
from peek_core_api._private.logic.agent_handlers.RpcForAgent import RpcForAgent
from peek_core_api._private.logic.api.CoreApi import CoreApi
from peek_core_api._private.logic.controller.MainController import (
    MainController,
)
from peek_core_api._private.storage.DeclarativeBase import DeclarativeBase
from peek_core_api._private.storage.DeclarativeBase import loadStorageTuples
from peek_core_api._private.tuples import loadPrivateTuples
from peek_plugin_base.server.PluginLogicEntryHookABC import (
    PluginLogicEntryHookABC,
)
from peek_plugin_base.server.PluginServerStorageEntryHookABC import (
    PluginServerStorageEntryHookABC,
)

logger = logging.getLogger(__name__)


class LogicEntryHook(PluginLogicEntryHookABC, PluginServerStorageEntryHookABC):
    def __init__(self, *args, **kwargs):
        """ " Constructor"""
        # Call the base classes constructor
        PluginLogicEntryHookABC.__init__(self, *args, **kwargs)

        #: Loaded Objects, This is a list of all objects created when we start
        self._loadedObjects = []

        self._api = None

    @property
    def dbMetadata(self):
        return DeclarativeBase.metadata

    def load(self) -> None:
        """Load

        This will be called when the plugin is loaded, just after the db is migrated.
        Place any custom initialiastion steps here.

        """
        loadStorageTuples()
        loadPrivateTuples()
        # loadPublicTuples()
        logger.debug("Loaded")

    def start(self):
        """Start

        This will be called when the plugin is loaded, just after the db is migrated.
        Place any custom initialiastion steps here.

        """
        tupleObservable = makeTupleDataObservableHandler()
        self._loadedObjects.append(tupleObservable)

        mainController = MainController(
            dbSessionCreator=self.dbSessionCreator,
            tupleObservable=tupleObservable,
        )

        self._loadedObjects.append(mainController)

        self._loadedObjects.extend(
            RpcForAgent(
                dbSessionCreator=self.dbSessionCreator,
                mainController=mainController,
            ).makeHandlers()
        )

        # Initialise the API object that will be shared with other plugins
        self._api = CoreApi(
            mainController=mainController,
        )
        self._loadedObjects.append(self._api)

        logger.debug("Started")

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
