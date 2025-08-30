from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import LargeBinary
from sqlalchemy import String
from sqlalchemy import and_
from sqlalchemy import text
from sqlalchemy import select
from sqlalchemy import asc
from sqlalchemy.sql import Select
from sqlalchemy.sql import func

from peek_core_api._private.PluginNames import apiTuplePrefix
from peek_core_api._private.logic.controller.HashController import (
    CoreApiPluginHasher,
)
from peek_core_api._private.storage.DeclarativeBase import DeclarativeBase
from peek_core_api._private.tuples.MessageQueueTuple import MessageQueueTuple


class MessageQueueTable(DeclarativeBase):
    __tablename__ = "MessageQueue"
    __tupleType__ = apiTuplePrefix + "MessageQueueTable"

    TYPE_DELIVERY_STATUS_UNKNOWN = -1  # reserved for agent
    TYPE_DELIVERY_STATUS_NEW = 0
    TYPE_DELIVERY_STATUS_IN_PROGRESS = 1
    TYPE_DELIVERY_STATUS_SUCCESS = 2
    TYPE_DELIVERY_STATUS_FAILED_RETRYING = 3
    TYPE_DELIVERY_STATUS_FAILED_PERMANENTLY = 4

    id = Column(Integer, primary_key=True)
    webhookId = Column(Integer, ForeignKey("Webhook.id"), nullable=False)
    queuedDate = Column(DateTime(timezone=True), nullable=False)
    lastDeliveryAttemptDate = Column(DateTime(timezone=True), nullable=True)
    lastDeliveryResponseCode = Column(Integer, nullable=True)
    attemptCount = Column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    deliveredDate = Column(DateTime(timezone=True), nullable=True)
    lastPostResponseSeconds = Column(Float, nullable=True)
    deliveryStatus = Column(Integer, nullable=False)
    messageBinary = Column(
        LargeBinary, nullable=False, comment="in binary, gzip compressed"
    )
    postPath = Column(String, nullable=True)
    pluginApiTupleKey = Column(
        String, ForeignKey("PublishedApi.pluginApiTupleKey"), nullable=False
    )

    def toTuple(self):
        return MessageQueueTuple(
            id=CoreApiPluginHasher.encode(self.id),
            webhookId=CoreApiPluginHasher.encode(self.webhookId),
            queuedDate=self.queuedDate,
            lastDeliveryAttemptDate=self.lastDeliveryAttemptDate,
            lastDeliveryResponseCode=self.lastDeliveryResponseCode,
            attemptCount=self.attemptCount,
            deliveredDate=self.deliveredDate,
            lastPostResponseSeconds=self.lastPostResponseSeconds,
            deliveryStatus=self.deliveryStatus,
            messageBinary=self.messageBinary,
            postPath=self.postPath,
        )

    @classmethod
    def _makePlPyBaseQuery(cls) -> Select:
        messageQueueTable = cls.__table__
        # list all deliverable messages ordered by queued date and webhookId
        # with index number for each webhook sub-queue
        # more in PEEP9
        queuedMessages = select(
            func.rank()
            .over(
                partition_by=messageQueueTable.webhookId,
                order_by=messageQueueTable.queuedDate,
            )
            .alias(name="rnk"),
            messageQueueTable.id,
            messageQueueTable.webhookId,
            messageQueueTable.queuedDate,
            messageQueueTable.messageBinary,
        ).where(
            messageQueueTable.deliveryStatus.in_(
                (
                    cls.TYPE_DELIVERY_STATUS_NEW,
                    cls.TYPE_DELIVERY_STATUS_FAILED_RETRYING,
                )
            ).order_by(
                and_(
                    asc(messageQueueTable.queuedDate),
                    asc(messageQueueTable.webhookId),
                )
            )
        )

        queuedMessages = queuedMessages.cte("windowed")

    @classmethod
    def makePlPyQuery(cls) -> Select:
        messageQueueTable = cls.__table__
        # get a batch of deliverable message
        w = cls._makePlPyBaseQuery()
        w.select(
            messageQueueTable.id,
            messageQueueTable.webhookId,
            messageQueueTable.queuedDate,
            messageQueueTable.messageBinary,
        ).where(w.rnk <= 5)
