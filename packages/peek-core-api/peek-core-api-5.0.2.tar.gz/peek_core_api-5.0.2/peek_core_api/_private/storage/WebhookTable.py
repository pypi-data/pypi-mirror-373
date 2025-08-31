from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from peek_core_api._private.PluginNames import apiTuplePrefix
from peek_core_api._private.logic.controller.HashController import (
    CoreApiPluginHasher,
)
from peek_core_api._private.storage.DeclarativeBase import DeclarativeBase
from peek_core_api._private.tuples.WebhookTuple import WebhookTuple


class WebhookTable(DeclarativeBase):
    __tablename__ = "Webhook"
    __tupleType__ = apiTuplePrefix + "WebhookTable"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    comment = Column(String, nullable=True)
    postUrl = Column(String, nullable=False)
    authToken = Column(String, nullable=True, comment="authorisation token")

    def toTuple(self):
        return WebhookTuple(
            id=CoreApiPluginHasher.encode(self.id),
            name=self.name,
            comment=self.comment,
            postUrl=self.postUrl,
            authToken=self.authToken,
        )
