import logging
from datetime import datetime
from typing import List

from sqlalchemy import text
from vortex.TupleSelector import TupleSelector

from peek_core_api._private.logic.controller.HashController import (
    CoreApiPluginHasher,
)
from peek_core_api._private.storage.MessageQueueTable import MessageQueueTable
from peek_core_api._private.tuples.MessageBatchAvailableTuple import (
    MessageBatchAvailableTuple,
)
from peek_core_api._private.tuples.WebhookTuple import WebhookTuple


logger = logging.getLogger(__name__)


class MessageQueueController:
    def __init__(
        self,
        dbSessionCreator=None,
        publishedApiStore=None,
        tupleObservable=None,
        apiManagementController=None,
    ):
        self._dbSessionCreator = dbSessionCreator
        self._publishedApiStore = publishedApiStore
        self._apiManagementController = apiManagementController
        self._tupleObservable = tupleObservable

    def start(self):
        # setup tuple data observer to fetch http request from peek-plugin-other
        pass

    def shutdown(self):
        pass

    def enqueueMessage(
        self, pluginName: str, apiKey: str, tupleSelector: TupleSelector
    ):
        pluginApiTupleKey = f"{pluginName}:{apiKey}:{tupleSelector.name}"

        # check if pluginName is registered at Peek startup
        if not self._publishedApiStore.hasApi(pluginApiTupleKey):
            return

        # check if the plugin is linked to webhook(s)
        matchedWebhookTuples = self._apiManagementController.findMappedWebhooks(
            pluginApiTupleKey
        )

        # no web API subscriptions found, quit
        if not matchedWebhookTuples:
            return

        # get json data from the provider, gzip compressed in bytes
        # save message to db
        messageCount = self.fetchAndSaveMessage(
            pluginApiTupleKey, tupleSelector, matchedWebhookTuples
        )
        logger.info(
            f"{messageCount} new outbound API message(s) of "
            f"'{pluginApiTupleKey}' queued."
        )

        self.notifyAgentOfNewMessageBatch()

    def notifyAgentOfNewMessageBatch(self):
        # notify agent of new messages
        messageAvailableTupleSelector = TupleSelector(
            name=MessageBatchAvailableTuple.tupleName(),
            selector={},
        )
        self._tupleObservable.notifyOfTupleUpdate(messageAvailableTupleSelector)

    def fetchAndSaveMessage(
        self,
        pluginApiTupleKey: str,
        tupleSelector: TupleSelector,
        webHooksTuples: List[WebhookTuple],
    ) -> int:
        """
        :returns int: the number of messages saved
        """
        provider = self._publishedApiStore.getProvider(pluginApiTupleKey)
        if not provider:
            raise ValueError(f"{pluginApiTupleKey} is not registered.")

        data: bytes = provider.getJsonData(tupleSelector)
        now = datetime.now()

        rows = []
        for webHooksTuple in webHooksTuples:
            webHookId: tuple = CoreApiPluginHasher.decode(webHooksTuple.id)
            webHookId: int = webHookId[0]
            row = MessageQueueTable(
                webhookId=webHookId,
                queuedDate=now,
                deliveryStatus=MessageQueueTable.TYPE_DELIVERY_STATUS_NEW,
                messageBinary=data,
                pluginApiTupleKey=pluginApiTupleKey,
            )
            rows.append(row)

        session = self._dbSessionCreator()
        try:
            session.add_all(rows)
            session.commit()
            return len(rows)
        except Exception as e:
            session.rollback()
            logger.exception(e)
            return 0
        finally:
            session.close()

    def _getDataFromApiProvider(selfpluginName: str, tupleName: str):
        # lookup registered CoreApiProvider instance for this pluginname
        # call provider._getJsonDataFromCoreApiProvider() in the instance of provider to get data
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
