import logging
from typing import List

from peek_core_api._private.storage.WebhookMapTable import WebhookMapTable
from peek_core_api._private.storage.WebhookTable import WebhookTable
from peek_core_api._private.tuples.WebhookTuple import WebhookTuple
from peek_core_api.server.CoreApiProvider import CoreApiProvider


logger = logging.getLogger(__name__)


class ApiManagementController:
    def __init__(self, dbSessionCreator=None, publishedApiStore=None):
        self._dbSessionCreator = dbSessionCreator
        self._publishedApiStore = publishedApiStore

    def start(self):
        pass

    def shutdown(self):
        pass

    def publishApi(self, apiProvider: CoreApiProvider):
        """loop over tuples in apiProvider and for each, upsert it in the table
        core_api.PublishedApi with columns of
        * plugin name
        * apiKey
        * tuple name

        add rows to PublishedApiTable if not exist
        """
        for tupleName, tupleProvider in apiProvider.registeredTuples.items():
            pluginApiTupleKey = apiProvider.makePluginApiTupleKey(tupleName)
            self._publishedApiStore.addApi(pluginApiTupleKey, tupleProvider)
        self._publishedApiStore.save()

    def addWebhook(self, name: str, comment: str, postUrl: str):
        """Add a new webhook
        :param name: str, a user-friendly name
        :param comment: str
        :param postUrl: str, the url to post all the updates to

        add rows in WebhookTable
        """

    def removeWebhook(self, name: str):
        """remove a webhook
        :param name: str, a user-friendly name

        delete rows in WebhookTable
        """

    def mapWebhook(self, webhookName: str, pluginApiTupleKey: str):
        """map a webhook to a pluginApiTupleKey

        :param webhookName: str, the name of an existing webhook
        :param pluginApiTupleKey: str, the unique identifier of a string
        that represents the pluginName, the apiKey and the tuple.

        add rows in WebhookMapTable
        """

    def unmapWebhook(self, webhookName: str, pluginApiTupleKey: str):
        """remove mapping to a webhook to a pluginApiTupleKey

        :param webhookName: str, the name of an existing webhook
        :param pluginApiTupleKey: str, the unique identifier of a string
        that represents the pluginName, the apiKey and the tuple.

        delete rows in WebhookMapTable
        """

    def findMappedWebhooks(self, pluginApiTupleKey: str) -> List[WebhookTuple]:
        session = self._dbSessionCreator()

        query = (
            session.query(WebhookMapTable, WebhookTable)
            .join(WebhookTable)
            .filter(WebhookMapTable.pluginApiTupleKey == pluginApiTupleKey)
        )

        matchedWebhookTuples = []

        for webhookMapTableRow, webhookTableRow in query.all():
            webHookTuple = webhookTableRow.toTuple()
            matchedWebhookTuples.append(webHookTuple)

        return matchedWebhookTuples
