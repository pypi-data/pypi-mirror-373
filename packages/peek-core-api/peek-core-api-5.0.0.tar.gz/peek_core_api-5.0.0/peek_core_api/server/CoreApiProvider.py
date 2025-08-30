import logging

from twisted.internet.defer import inlineCallbacks
from vortex.TupleSelector import TupleSelector

from peek_core_api.server.JsonDataTupleProviderABC import (
    JsonDataTupleProviderABC,
)

logger = logging.Logger(__name__)


class CoreApiProvider:
    """API Provider

    This is used to associate tuple names with json data providers for
    peek-core-api to fetch data via the providers.
    """

    def __init__(self, pluginName: str, apiKey: str):
        self._apiKey = apiKey
        self._registeredTuples = {}
        self._pluginName = pluginName

    @property
    def registeredTuples(self) -> dict[str, JsonDataTupleProviderABC]:
        """list a dictionary of tuples with tuple providers

        :return: a dictionary of tuple names in string and instances of tuple
                providers
        """
        return self._registeredTuples.copy()

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
            raise ValueError(f"{tupleName} has existed in registeredTuples")

        self._registeredTuples[tupleName] = tupleProvider

    def registeredTupleNames(self):
        pluginApiTupleKeys = []

        for tupleName in self._registeredTuples.keys():
            pluginApiTupleKeys.append(self.makePluginApiTupleKey(tupleName))

        return pluginApiTupleKeys

    def makePluginApiTupleKey(self, tupleName):
        return f"{self._pluginName}:{self._apiKey}:{tupleName}"

    def getRegisteredTuple(self, tupleName) -> JsonDataTupleProviderABC:
        if self.hasRegisteredTuple(tupleName):
            return self._registeredTuples[tupleName]
