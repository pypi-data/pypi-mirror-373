from datetime import datetime
from typing import List

from vortex.Tuple import Tuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

from peek_core_api._private.PluginNames import apiTuplePrefix


@addTupleType
class GzippedDataHttpResponseTuple(Tuple):
    __tupleType__ = apiTuplePrefix + "GzippedDataHttpResponseTuple"

    requestDate: datetime = TupleField()
    responseDate: datetime = TupleField()
    code: int = TupleField(defaultValue=0)
    version: tuple = TupleField()  # (b'HTTP', 1, 1)
    headers: dict[str, str] = TupleField()
    body: bytes = TupleField()
    exceptions: List[Exception] = TupleField(defaultValue=[])
