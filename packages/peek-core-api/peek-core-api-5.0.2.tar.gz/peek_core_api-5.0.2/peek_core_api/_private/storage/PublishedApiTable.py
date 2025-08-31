from sqlalchemy import Column
from sqlalchemy import Computed
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String

from peek_core_api._private.PluginNames import apiTuplePrefix
from peek_core_api._private.storage.DeclarativeBase import DeclarativeBase


class PublishedApiTable(DeclarativeBase):
    __tablename__ = "PublishedApi"
    __tupleType__ = apiTuplePrefix + "PublishedApiTable"

    id = Column(Integer, primary_key=True)
    pluginName = Column(String, nullable=False)
    apiKey = Column(String, nullable=False)
    tupleName = Column(String, nullable=False)
    pluginApiTupleKey = Column(
        String,
        Computed(
            # e.g. peek_plugin_other:API1:peek_plugin_other.tuples.MyTuple1
            '"pluginName" || \':\' || "apiKey" || \':\' || "tupleName"',
            persisted=True,  # renders sql ``GENERATED ALWAYS AS ... STORED``
        ),
        unique=True,
    )
    lastPublishedDate = Column(DateTime(timezone=True), nullable=False)
