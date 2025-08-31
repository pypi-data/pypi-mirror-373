from peek_core_api.server.CoreApiProviderABC import CoreApiProviderABC


class ApiManagementController:
    def __init__(self):
        pass

    def shutdown(self):
        pass

    def publishApi(
        self, pluginName: str, apiKey: str, apiProvider: CoreApiProviderABC
    ):
        """loop over tuples in apiProvider and for each, upsert it in the table
        core_api.PublishedApi with columns of
        * plugin name
        * apiKey
        * tuple name

        add rows to PublishedApiTable if not exist
        """

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
