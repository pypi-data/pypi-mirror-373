from datetime import datetime

from vortex.Tuple import Tuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

from peek_core_api._private.PluginNames import apiTuplePrefix
from peek_core_api._private.storage.MessageQueueTable import MessageQueueTable
from peek_core_api._private.tuples.GzippedDataHttpResponseTuple import (
    GzippedDataHttpResponseTuple,
)


@addTupleType
class MessageHttpResponseTuple(Tuple):
    __tupleType__ = apiTuplePrefix + "MessageHttpResponseTuple"

    # from GzippedDataHttpResponseTuple
    requestDate: datetime = TupleField()
    responseDate: datetime = TupleField()
    responseSeconds: float = TupleField()
    code: int = TupleField()
    version: tuple = TupleField()  # (b'HTTP', 1, 1)
    headers: dict[str, str] = TupleField()
    body: bytes = TupleField()

    # from MessageQueueTuple
    id: str = TupleField()
    deliveryStatus: int = TupleField()

    # messageQueueTuple: MessageQueueTuple = TupleField()
    # gzippedPayloadHttpResponseTuple: GzippedDataHttpResponseTuple = TupleField()
    # from MessageQueueTuple

    @staticmethod
    def fromTuple(
        gzippedDataHttpResponseTuple: GzippedDataHttpResponseTuple, id: int
    ):
        responseSeconds = None

        if (
            gzippedDataHttpResponseTuple.responseDate
            and gzippedDataHttpResponseTuple.requestDate
        ):
            responseSeconds = (
                gzippedDataHttpResponseTuple.responseDate
                - gzippedDataHttpResponseTuple.requestDate
            ).total_seconds()

        return MessageHttpResponseTuple(
            id=id,
            requestDate=gzippedDataHttpResponseTuple.requestDate,
            responseDate=gzippedDataHttpResponseTuple.responseDate,
            responseSeconds=responseSeconds,
            code=gzippedDataHttpResponseTuple.code,
            version=gzippedDataHttpResponseTuple.version,
            headers=gzippedDataHttpResponseTuple.headers,
            body=gzippedDataHttpResponseTuple.body,
            deliveryStatus=MessageQueueTable.TYPE_DELIVERY_STATUS_UNKNOWN,
        )
