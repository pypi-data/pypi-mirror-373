import logging

from vortex.TupleSelector import TupleSelector

from peek_core_api._private.tuples.MessageBatchAvailableTuple import (
    MessageBatchAvailableTuple,
)
from peek_core_api.server.CoreApiABC import CoreApiABC
from peek_core_api.server.CoreApiProvider import CoreApiProvider

logger = logging.getLogger(__name__)


class CoreApi(CoreApiABC):
    def __init__(
        self,
        mainController=None,
    ):
        self._mainController = mainController

        self._apiManagementController = (
            self._mainController.apiManagementController
        )
        self._messageQueueController = (
            self._mainController.messageQueueController
        )

    def publishApi(self, apiProvider: CoreApiProvider):
        self._apiManagementController.publishApi(apiProvider=apiProvider)

    # @inlineCallbacks
    def notifyOfUpdate(
        self, pluginName: str, apiKey: str, tupleSelector: TupleSelector
    ):
        self._messageQueueController.enqueueMessage(
            pluginName, apiKey, tupleSelector
        )
