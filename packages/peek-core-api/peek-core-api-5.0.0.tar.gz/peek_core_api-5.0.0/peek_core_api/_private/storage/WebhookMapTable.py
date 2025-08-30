from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

from peek_core_api._private.PluginNames import apiTuplePrefix
from peek_core_api._private.storage.DeclarativeBase import DeclarativeBase


class WebhookMapTable(DeclarativeBase):
    __tablename__ = "WebhookMap"
    __tupleType__ = apiTuplePrefix + "WebhookMapTable"

    id = Column(Integer, primary_key=True)
    webhookId = Column(Integer, ForeignKey("Webhook.id"))
    pluginApiTupleKey = Column(
        String, ForeignKey("PublishedApi.pluginApiTupleKey")
    )
    postPath = Column(String, nullable=True)
