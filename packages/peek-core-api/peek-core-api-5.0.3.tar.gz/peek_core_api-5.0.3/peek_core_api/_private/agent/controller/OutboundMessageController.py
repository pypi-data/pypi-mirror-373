import logging
from itertools import groupby
from typing import List
from typing import Type

from twisted.internet.defer import Deferred
from twisted.internet.defer import DeferredList
from twisted.internet.defer import inlineCallbacks
from twisted.internet.error import TimeoutError as TwistedTimeoutError
from vortex.DeferUtil import vortexLogFailure
from vortex.restful.GzippedDataHttpClient import GzippedDataHttpClient
from vortex.restful.RestfulResource import HTTP_REQUEST

from peek_core_api._private.logic.agent_handlers.RpcForAgent import RpcForAgent
from peek_core_api._private.tuples.GzippedDataHttpResponseTuple import (
    GzippedDataHttpResponseTuple,
)
from peek_core_api._private.tuples.MessageHttpRequestTuple import (
    MessageHttpRequestTuple,
)
from peek_core_api._private.tuples.MessageHttpResponseTuple import (
    MessageHttpResponseTuple,
)

logger = logging.getLogger(__name__)


class QueueProcessingBreakException(Exception):
    pass


class OutboundMessageController:
    def __init__(self):
        self._currentMessageBatch = []

    @inlineCallbacks
    def start(self):
        yield RpcForAgent.agentOnline()
        yield self._beginSendMessageCycle()

    def shutdown(self):
        pass

    @property
    def idle(self) -> bool:
        return not self._currentMessageBatch

    def onNewMessageBatch(self):
        logger.info("new message batch available on Peek Logic.")
        if self.idle:
            self._beginSendMessageCycle()

    def _beginSendMessageCycle(self):
        d = self._sendMessageCycle()
        d.addErrback(vortexLogFailure, logger, consumeError=True)

    @inlineCallbacks
    def _sendMessageCycle(self) -> Deferred:
        """Drain the message queue

        This deques messages from Logic
        """
        self._currentMessageBatch = yield RpcForAgent.getMessageBatch()
        while self._currentMessageBatch:
            yield self._processBatch(self._currentMessageBatch)
            self._currentMessageBatch = yield RpcForAgent.getMessageBatch()

    @inlineCallbacks
    def _processBatch(self, messageBatch: List[MessageHttpRequestTuple]):
        """Process Batch

        This method will processa batch of messages from the logic service.

        We can have multiple messages for multiple webhooks. We need to sort
        this into each of their webhook queus and then call _processSubQueue to
        process the messages for each webhook.

        We won't handle any errors here, we will just wait until
        _processSubQueue has completed.
        """
        queue = []
        for webhookId, subQueueGenerator in groupby(
            messageBatch, key=lambda m: m.webhookId
        ):
            subQueue: List = sorted(
                subQueueGenerator, key=lambda m: m.queuedDate
            )
            queue.append(subQueue)

        yield DeferredList(
            [self._processSubQueue(subQueue) for subQueue in queue]
        )

    @inlineCallbacks
    def _processSubQueue(self, messages: List[MessageHttpRequestTuple]):
        """Process Queue

        This method sequentially processes messages that are destined for the
        same webhook.

        An error from the _sendHttpRequest will interupt processing of
        the queue and return.
        """
        drainedQueue = messages[:]
        while drainedQueue:
            try:
                yield self._sendHttpRequest(drainedQueue[0])
                drainedQueue.pop(0)

            except QueueProcessingBreakException as e:
                message = drainedQueue[0]
                logger.info(
                    f"Message to '{message.postUrl}' failed to send. "
                    f"There are {len(drainedQueue)} messages pending to this "
                    f"webhook. We'll retry later."
                )
                break

            except Exception as e:
                message = drainedQueue[0]
                logger.exception(e)
                logger.error(
                    f"There is an error when processing message "
                    f"'{message.postUrl}'. "
                    f"There are {len(drainedQueue)} messages pending to this "
                    f"webhook. We'll retry later."
                )
                break

    @inlineCallbacks
    def _sendHttpRequest(
        self, messageHttpRequestTuple: MessageHttpRequestTuple
    ):
        """Send HTTP Request

        This method is responsibile for delivering a single message
        and then telling the sercer of the success/failure of that message
        delivery
        """
        logger.info("HTTP SEND")
        logger.info(
            f"{messageHttpRequestTuple.id} "
            f"{messageHttpRequestTuple.postUrl} "
            f"post length"
            f" {len(messageHttpRequestTuple.messageBinary)}"
        )

        url = messageHttpRequestTuple.postUrl
        payload = messageHttpRequestTuple.messageBinary
        headers = {}
        if messageHttpRequestTuple.authToken:
            headers["Authorization"] = [messageHttpRequestTuple.authToken]
        responseTuple = GzippedDataHttpResponseTuple()
        client = GzippedDataHttpClient(
            url=url,
            payload=payload,
            headers=headers,
            method=HTTP_REQUEST.POST,
            meta=responseTuple,
            isPayloadGzipped=True,
            compressed=True,
            timeout=10.0,
        )
        gzippedPayloadHttpResponseTuple = yield client.run()

        outcomeTuple = MessageHttpResponseTuple.fromTuple(
            id=messageHttpRequestTuple.id,
            gzippedDataHttpResponseTuple=gzippedPayloadHttpResponseTuple,
        )

        # report http request outcome to Logic via RPC
        yield RpcForAgent.reportMessageDeliveryOutcome(outcomeTuple)

        self._assertHttpStatusCode2xx(responseTuple)

        self._assertHttpTimeout(gzippedPayloadHttpResponseTuple)

    def _assertHttpTimeout(self, responseTuple: GzippedDataHttpResponseTuple):
        ofTimeout = map(
            self._checkHttpTimeoutException,
            responseTuple.exceptions,
        )
        if any(ofTimeout):
            raise QueueProcessingBreakException

    def _assertHttpStatusCode2xx(
        self, responseTuple: GzippedDataHttpResponseTuple
    ):
        if responseTuple.code // 100 != 2:
            raise QueueProcessingBreakException

    def _checkHttpTimeoutException(self, e: Type[Exception]):
        return isinstance(e, TwistedTimeoutError)
