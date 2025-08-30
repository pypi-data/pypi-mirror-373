from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObserverClient import TupleDataObserverClient

from peek_core_api._private.PluginNames import apiFilt
from peek_core_api._private.PluginNames import apiObservableName
from peek_core_api._private.tuples.MessageBatchAvailableTuple import (
    MessageBatchAvailableTuple,
)
from peek_plugin_base.PeekVortexUtil import peekServerName


def makeTupleDataObserverClient(controller):
    logicObserver = TupleDataObserverClient(
        peekServerName,
        apiObservableName,
        additionalFilt=apiFilt,
    )

    logicObserver.subscribeToTupleSelector(
        TupleSelector(MessageBatchAvailableTuple.tupleName())
    ).subscribe(lambda _: controller.onNewMessageBatch())

    return logicObserver
