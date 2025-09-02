from vortex.TupleSelector import TupleSelector

from peek_core_api.server.CoreApiABC import CoreApiABC


class CoreApi(CoreApiABC):
    def __init__(
        self, apiManagementController=None, messageQueueController=None
    ):
        self._apiManagementController = apiManagementController
        self._messageQueueController = messageQueueController

    def publishApi(self, pluginName: str, apiKey: str, apiProvider):
        self._apiManagementController.publishApi(
            pluginName=pluginName, apiKey=apiKey, apiProvider=apiProvider
        )

    def notifyOfUpdate(
        self, pluginName: str, apiKey: str, tupleSelector: TupleSelector
    ):
        # check if pluginName is registered at Peek startup
        # check if the plugin is linked to webhook(s)
        # call jsonDataTupleProvider.getJsonData(tupleSelector)
        pass
