from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

from peek_core_api._private.logic.controller.ApiManagementController import (
    ApiManagementController,
)
from peek_core_api._private.logic.controller.MessageQueueController import (
    MessageQueueController,
)
from peek_core_api._private.logic.controller.ApiPublishingController import (
    ApiPublishingController,
)
from peek_plugin_base.storage.DbConnection import DbSessionCreator


class MainController:
    def __init__(
        self,
        dbSessionCreator: DbSessionCreator,
        tupleObservable: TupleDataObservableHandler,
    ):
        self._dbSessionCreator = dbSessionCreator
        self._tupleObservable = tupleObservable

        self._publishedApiStore = ApiPublishingController(
            dbSessionCreator=self._dbSessionCreator
        )

        self._publishedApiStore.load()

        self._apiManagementController = ApiManagementController(
            dbSessionCreator=self._dbSessionCreator,
            publishedApiStore=self._publishedApiStore,
        )

        self._messageQueueController = MessageQueueController(
            dbSessionCreator=self._dbSessionCreator,
            publishedApiStore=self._publishedApiStore,
            tupleObservable=self._tupleObservable,
            apiManagementController=self._apiManagementController,
        )

    @property
    def apiManagementController(self):
        return self._apiManagementController

    @property
    def messageQueueController(self):
        return self._messageQueueController

    @property
    def publishedApiStore(self):
        return self._publishedApiStore
