import logging
from abc import ABCMeta
from abc import abstractmethod

from vortex.TupleSelector import TupleSelector

from peek_core_api.server.CoreApiProvider import CoreApiProvider

logger = logging.Logger(__name__)


class CoreApiABC(metaclass=ABCMeta):
    """Core API

    This is the public API for the part of the plugin that runs on the server service.

    """

    @abstractmethod
    def publishApi(self, apiProvider: CoreApiProvider):
        """publish API

        peek-plugin-other will call peek-core-api.publishApi
        (apiProvoder:CoreApiProvider) to ensure peek-core-api knows that
        peek-plugin-other has an outgoing API.

        :param apiProvider: an instanceof CoreApiProvider where tuples are
        tuples are registered with tupleProviders.
        """

    @abstractmethod
    def notifyOfUpdate(
        self, pluginName: str, apiKey: str, tupleSelector: TupleSelector
    ):
        """notify of an data update of a Tuple Type

        :param pluginName: str
        :param apiKey: str, apiKey is the name of the API, this just a logical
        name for the API, to allow one plugin to present multiple APIs
        :param tupleSelector: TupleSelector,
        """
