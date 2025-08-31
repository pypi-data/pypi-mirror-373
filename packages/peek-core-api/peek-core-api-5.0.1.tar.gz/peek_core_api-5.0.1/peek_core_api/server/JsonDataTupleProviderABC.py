from abc import ABCMeta
from abc import abstractmethod
from typing import Union

from twisted.internet.defer import Deferred
from vortex.TupleSelector import TupleSelector


class JsonDataTupleProviderABC(metaclass=ABCMeta):
    @abstractmethod
    def getJsonData(
        self, tupleSelector: TupleSelector
    ) -> Union[bytes, Deferred]:
        """Provide Json data of a tuple for CoreApiProvider

        :param tupleSelector: The tuple selector us used to determine which
        tuples to send back
        """
