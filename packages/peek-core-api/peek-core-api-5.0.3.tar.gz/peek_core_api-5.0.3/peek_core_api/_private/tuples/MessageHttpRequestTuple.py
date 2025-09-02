from vortex.Tuple import Tuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

from peek_core_api._private.PluginNames import apiTuplePrefix
from peek_core_api._private.logic.controller.HashController import (
    CoreApiPluginHasher,
)


@addTupleType
class MessageHttpRequestTuple(Tuple):
    __tupleType__ = apiTuplePrefix + "MessageHttpRequestTuple"

    # messageQueueTuple: MessageQueueTuple = TupleField()
    # webhookTuple: WebhookTuple = TupleField()
    # gzippedPayloadHttpResponseTuple: GzippedDataHttpResponseTuple = TupleField()
    # from MessageQueueTuple
    id = TupleField()
    webhookId = TupleField()
    queuedDate = TupleField()
    lastDeliveryAttemptDate = TupleField()
    lastDeliveryResponseCode = TupleField()
    attemptCount = TupleField()
    deliveredDate = TupleField()
    lastPostResponseSeconds = TupleField()
    deliveryStatus = TupleField()
    messageBinary = TupleField()
    postPath = TupleField()

    # from WebhookTuple
    postUrl = TupleField()
    authToken = TupleField()

    @staticmethod
    def fromDict(row: dict):
        row = row.copy()

        if type(row.get("id")) == int:
            row["id"] = CoreApiPluginHasher.encode(row["id"])

        return MessageHttpRequestTuple(
            id=row.get("id"),
            webhookId=row.get("webhookId"),
            queuedDate=row.get("queuedDate"),
            lastDeliveryAttemptDate=row.get("lastDeliveryAttemptDate"),
            lastDeliveryResponseCode=row.get("lastDeliveryResponseCode"),
            attemptCount=row.get("attemptCount"),
            deliveredDate=row.get("deliveredDate"),
            lastPostResponseSeconds=row.get("lastPostResponseSeconds"),
            deliveryStatus=row.get("deliveryStatus"),
            messageBinary=row.get("messageBinary"),
            postPath=row.get("postPath"),
            postUrl=row.get("postUrl"),
            authToken=row.get("authToken"),
        )
