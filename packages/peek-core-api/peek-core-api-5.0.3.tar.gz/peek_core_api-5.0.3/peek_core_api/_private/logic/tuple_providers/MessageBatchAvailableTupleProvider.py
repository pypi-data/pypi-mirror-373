import logging

from twisted.internet.defer import Deferred
from twisted.internet.defer import inlineCallbacks
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

from peek_core_api._private.tuples.MessageBatchAvailableTuple import (
    MessageBatchAvailableTuple,
)

logger = logging.getLogger(__name__)


class MessageBatchAvailableTupleProvider(TuplesProviderABC):
    @inlineCallbacks
    def makeVortexMsg(
        self, filt: dict, tupleSelector: TupleSelector
    ) -> Deferred:
        tuple_ = MessageBatchAvailableTuple()

        payloadEnvelope = yield Payload(
            filt=filt, tuples=[tuple_]
        ).makePayloadEnvelopeDefer()
        vortexMsg = yield payloadEnvelope.toVortexMsgDefer()
        return vortexMsg
