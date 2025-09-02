import logging

from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

from peek_core_api._private.PluginNames import apiFilt
from peek_core_api._private.PluginNames import apiObservableName
from peek_core_api._private.logic.tuple_providers.MessageBatchAvailableTupleProvider import (
    MessageBatchAvailableTupleProvider,
)
from peek_core_api._private.tuples.MessageBatchAvailableTuple import (
    MessageBatchAvailableTuple,
)
from peek_plugin_base.PeekVortexUtil import peekAgentName

logger = logging.getLogger(__name__)


def makeAgentTupleDataObservableHandler():
    observable = TupleDataObservableHandler(
        observableName=apiObservableName,
        additionalFilt=apiFilt,
        acceptOnlyFromVortex=peekAgentName,
    )

    observable.addTupleProvider(
        MessageBatchAvailableTuple.tupleName(),
        MessageBatchAvailableTupleProvider(),
    )

    return observable
