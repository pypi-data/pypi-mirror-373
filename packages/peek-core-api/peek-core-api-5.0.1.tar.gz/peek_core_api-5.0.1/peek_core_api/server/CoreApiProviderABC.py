import logging
from abc import ABCMeta

from twisted.internet.defer import inlineCallbacks
from vortex.TupleSelector import TupleSelector

from peek_core_api.server.JsonDataTupleProviderABC import (
    JsonDataTupleProviderABC,
)

logger = logging.Logger(__name__)


class CoreApiProviderABC(metaclass=ABCMeta):
    """API Provider

    This is used to associate tuple names with json data providers for
    peek-core-api to fetch data via the providers.
    """

    def __init__(self, pluginName: str):
        self._registeredTuples = {}

    @property
    def registeredTupleNames(self) -> dict[str, JsonDataTupleProviderABC]:
        """list a dictionary of tuples with tuple providers

        :return: a dictionary of tuple names in string and instances of tuple
                providers
        """
        return self._registeredTuples

    def hasRegisteredTuple(self, tupleName: str) -> bool:
        if tupleName in self._registeredTuples.keys():
            return True
        return False

    def registerTuple(
        self, tupleName: str, tupleProvider: JsonDataTupleProviderABC
    ):
        """add a tuple with a tuple provider to CoreApiProvider

        :param: tupleName: str
        :param: tupleProvider: JsonDataTupleProviderABC
        """
        if self.hasRegisteredTuple(tupleName):
            e = ValueError(f"{tupleName} has existed in registeredTuples")
            logger.exception(e)
            raise e

        self._registeredTuples[tupleName] = tupleProvider

    def deRegisterTuple(self, tupleName: str):
        """remove a tuple with a tuple provider to CoreApiProvider

        :param: tupleName: str
        """
        if self.hasRegisteredTuple(tupleName):
            self._registeredTuples.pop(tupleName)

    @inlineCallbacks
    def getJsonData(self, tupleSelector: TupleSelector):
        if not self.hasRegisteredTuple(tupleSelector.name):
            e = ValueError(f"{tupleSelector.name} is not a registered tuple")
            logger.exception(e)
            raise

        tupleProvider: JsonDataTupleProviderABC = self._registeredTuples[
            tupleSelector.name
        ]

        # fetch data via tupleProvider by peek-plugin-other
        jsonData = yield tupleProvider.getJsonData(tupleSelector)
        return jsonData
