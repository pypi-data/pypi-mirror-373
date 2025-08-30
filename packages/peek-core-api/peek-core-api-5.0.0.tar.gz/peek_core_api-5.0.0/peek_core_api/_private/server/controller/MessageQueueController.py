from vortex.TupleSelector import TupleSelector


class MessageQueueController:
    def __init__(self, rpcForServer=None):
        self._rpcForServer = rpcForServer

    def start(self):
        # setup tuple data observer to fetch http request from peek-plugin-other
        pass

    def shutdown(self):
        pass

    def enqueueMessage(
        self, pluginName: str, apiKey: str, tupleSelector: TupleSelector
    ):
        """Add an entry to the message queue

        :param pluginName: str
        :param apiKey: str
        :param tupleSelector: TupleSelector

        add rows to MessageQueueTable
        """

        # get webhookId, pluginApiTupleKey

        # if not exists
        # return

        # enqueue message to db
        # update deliveryStatus = new, queuedDate

        # get HTTP request payload from peek-plugin-other via registered
        # CoreApiProvider
        # self._getJsonData(pluginName, tupleName)

        # send http request on Agent via RPC

        # wait for agent responding with a request to get message of jsonStr
        # self.processHttpResult
        pass

    def _getDataFromApiProvider(selfpluginName: str, tupleName: str):
        # lookup registered CoreApiProvider instance for this pluginname
        # call provider.getJsonData() in the instance of provider to get data
        # deserialise vortex message
        pass

    def processHttpResult(self, coreApiAgentHttpResultTuple):
        # class CoreApiAgentHttpResultTuple
        # url
        # request
        # request date
        # response code
        # response body

        # get message queue Id with deobfuscation (hashid.decode)
        # deliveryStatus = delivery in progress

        # update lastDeliveryAttemptDate

        # get jsonStr from db
        # send HTTP request payload via RPC to Agent
        # wait and gather result of the http request on Agent

        # update delivery state

        # if http.200
        # self.succeedMessage
        # deliveryStatus = delivered successfully
        # update other status in table

        # else:
        # get retry count
        # if retry < limit:

        # self.retryMessage
        # deliveryStatus = delivery failed, retrying
        # callLater self.onNewMessageRequestFromAgent

        # else:
        # self.failMessage
        # delivery failed permanently
        pass
