from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

from peek_core_api._private.PluginNames import apiFilt
from peek_core_api._private.PluginNames import apiObservableName
from peek_core_api._private.logic.tuple_providers.MessageBatchAvailableTupleProvider import (
    MessageBatchAvailableTupleProvider,
)
from peek_core_api._private.tuples.MessageBatchAvailableTuple import (
    MessageBatchAvailableTuple,
)


def makeTupleDataObservableHandler() -> TupleDataObservableHandler:
    """Make Tuple Data Observable Handler

    This handler emits tuple data on CoreApi.notifyOfUpdate() from
    peek-plugin-other

    :return: An instance of :code:`TupleDataObservableHandler`

    """
    tupleObservable = TupleDataObservableHandler(
        observableName=apiObservableName, additionalFilt=apiFilt
    )

    # Register TupleProviders here
    tupleObservable.addTupleProvider(
        MessageBatchAvailableTuple.tupleName(),
        MessageBatchAvailableTupleProvider(),
    )

    return tupleObservable
