import logging
from datetime import datetime
from typing import List

from twisted.internet import reactor
from twisted.internet.defer import DeferredSemaphore
from twisted.internet.defer import inlineCallbacks
from vortex.rpc.RPC import vortexRPC

from peek_core_api._private.PluginNames import apiFilt
from peek_core_api._private.logic.controller.HashController import (
    CoreApiPluginHasher,
)
from peek_core_api._private.logic.controller.SqlController import (
    SqlController,
)
from peek_core_api._private.storage.MessageQueueTable import MessageQueueTable
from peek_core_api._private.tuples.MessageHttpRequestTuple import (
    MessageHttpRequestTuple,
)
from peek_core_api._private.tuples.MessageHttpResponseTuple import (
    MessageHttpResponseTuple,
)
from peek_plugin_base.PeekVortexUtil import peekAgentName
from peek_plugin_base.PeekVortexUtil import peekServerName

logger = logging.getLogger(__name__)


class RpcForAgent:
    DeliverableStatus = {
        MessageQueueTable.TYPE_DELIVERY_STATUS_NEW,
        MessageQueueTable.TYPE_DELIVERY_STATUS_FAILED_RETRYING,
    }

    def __init__(self, dbSessionCreator, mainController):
        self._dbSessionCreator = dbSessionCreator
        self._messageController = mainController.messageQueueController
        self._semaphore = DeferredSemaphore(1)

    def makeHandlers(self):
        """Make Handlers

        In this method we start all the RPC handlers
        start() returns an instance of itself so we can simply yield the result
        of the start method.

        """

        yield self.getMessageBatch.start(funcSelf=self)
        yield self.reportMessageDeliveryOutcome.start(funcSelf=self)
        yield self.agentOnline.start(funcSelf=self)
        logger.debug("RPCs started")

    @vortexRPC(
        peekServerName,
        acceptOnlyFromVortex=peekAgentName,
        additionalFilt=apiFilt,
        timeoutSeconds=10,
        inlineCallbacks=True,
    )
    def getMessageBatch(self) -> List[MessageHttpRequestTuple]:
        # get the up to 10 messages in the FIFO queue
        batch = yield self._semaphore.run(self._getMessageBatch)
        return batch

    @inlineCallbacks
    def _getMessageBatch(self):
        messageHttpRequestTuple = yield SqlController.getMessageBatch(
            self._dbSessionCreator
        )
        return messageHttpRequestTuple

    @vortexRPC(
        peekServerName,
        acceptOnlyFromVortex=peekAgentName,
        additionalFilt=apiFilt,
        timeoutSeconds=10,
    )
    def reportMessageDeliveryOutcome(self, message: MessageHttpResponseTuple):
        id_ = CoreApiPluginHasher.decode(message.id)
        session = self._dbSessionCreator()

        # update row if exists
        query = session.query(MessageQueueTable).filter(
            MessageQueueTable.id == id_
        )
        row: MessageQueueTable = query.one_or_none()

        if not row:
            raise ValueError(
                f"MessageQueue id: {id_} is not found in 'MessageQueueTable'."
            )

        try:
            row.attemptCount += 1
            row.lastDeliveryResponseCode = message.code

            if message.code != 0:
                # got a response, record time-related info
                row.lastDeliveryAttemptDate = message.requestDate
                row.lastPostResponseSeconds = message.responseSeconds

            if message.code // 100 == 2:
                # TODO: get setting 'timeout' from Peek admin
                if message.responseSeconds > 60.0:
                    # reset to 'NEW' if the response is out of timeout limit
                    reactor.callLater(
                        5.0,
                        self._rollbackToStatusNewAndNotifyAgent,
                        row.webhookId,
                        row.queuedDate,
                    )
                else:
                    # delivery success
                    row.deliveryStatus = (
                        MessageQueueTable.TYPE_DELIVERY_STATUS_SUCCESS
                    )
                    row.deliveredDate = message.responseDate

            if message.code // 100 != 2:
                # delivery failed, set to status 'NEW' to be deliveried later
                reactor.callLater(
                    5.0,
                    self._rollbackToStatusNewAndNotifyAgent,
                    row.webhookId,
                    row.queuedDate,
                )

            session.commit()
        except Exception as e:
            session.rollback()
            raise e

    @inlineCallbacks
    def _rollbackToStatusNewAndNotifyAgent(
        self, webhookId: int, queuedDate: datetime
    ):
        yield SqlController.resetStatusToNewAfterFirstFailedRetrying(
            self._dbSessionCreator, webhookId, queuedDate
        )
        self._messageController.notifyAgentOfNewMessageBatch()

    @vortexRPC(
        peekServerName,
        acceptOnlyFromVortex=peekAgentName,
        additionalFilt=apiFilt,
        timeoutSeconds=10,
        inlineCallbacks=True,
    )
    def agentOnline(self):
        ret = yield SqlController.resetStatusInProgressToNewOnAgentOnline(
            self._dbSessionCreator
        )
        return ret
