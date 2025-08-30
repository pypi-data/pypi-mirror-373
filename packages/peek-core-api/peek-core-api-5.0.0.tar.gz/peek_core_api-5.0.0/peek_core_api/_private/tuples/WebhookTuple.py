from vortex.Tuple import Tuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

from peek_core_api._private.PluginNames import apiTuplePrefix


@addTupleType
class WebhookTuple(Tuple):
    __tupleType__ = apiTuplePrefix + "WebhookTuple"

    id = TupleField()
    name = TupleField()
    comment = TupleField()
    postUrl = TupleField()
    authToken = TupleField()
