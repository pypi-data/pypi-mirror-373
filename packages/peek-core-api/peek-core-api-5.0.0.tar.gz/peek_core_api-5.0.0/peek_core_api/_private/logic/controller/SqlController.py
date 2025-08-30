import logging
from datetime import datetime
from typing import List

from twisted.internet.defer import inlineCallbacks

from peek_core_api._private.tuples.MessageHttpRequestTuple import (
    MessageHttpRequestTuple,
)
from peek_plugin_base.storage.DbConnection import DbSessionCreator
from peek_plugin_base.storage.RunPyInPg import runPyInPg

logger = logging.getLogger(__name__)


class SqlController:
    @classmethod
    @inlineCallbacks
    def resetStatusInProgressToNewOnAgentOnline(
        cls, dbSessionCreator: DbSessionCreator
    ):
        # Set any messages IN_PROGRESS to NEW when Agent notifies Logic of
        # “Agent Online” via RPC
        yield runPyInPg(
            logger,
            dbSessionCreator,
            cls._resetStatusInProgressToNewOnAgentOnline,
            None,
        )

    @classmethod
    def _resetStatusInProgressToNewOnAgentOnline(cls, plpy):
        plpy.execute(
            """update CORE_API."MessageQueue"
        set "deliveryStatus" = 0
        where "deliveryStatus" = 1;"""
        )

    def resetStatusToNewAfterTimeout(self, timeoutSeconds: float):
        # Set any messages FAILED_RETRYING to NEW after a timeout is expired
        # by a looping call on Logic

        """update CORE_API."MessageQueue"
        set "deliveryStatus" = 0
        where "deliveryStatus" = 3 and "lastPostResponseSeconds" >= timeout;
        """
        pass

    @classmethod
    @inlineCallbacks
    def resetStatusToNewAfterFirstFailedRetrying(
        cls, dbSessionCreator, webhookId: int, queuedDate: datetime
    ):
        # In a sub-queue with messages of FAILED_RETRYING, set any messages
        # to NEW after the first FAILED_RETRYING when Logic receives the
        # outcome of a message in such case
        yield runPyInPg(
            logger,
            dbSessionCreator,
            cls._resetStatusToNewAfterFirstFailedRetrying,
            None,
            webhookId=webhookId,
            queuedDate=queuedDate,
        )

    @classmethod
    def _resetStatusToNewAfterFirstFailedRetrying(
        cls, plpy, webhookId: int, queuedDate: datetime
    ):
        # datetime is in format ISO8601 with timezone
        plpy.execute(
            f"""
            UPDATE core_api."MessageQueue"
            SET "deliveryStatus" = 0
            WHERE "webhookId" = {webhookId}
                AND "queuedDate" >= '{queuedDate.astimezone().isoformat()}';
            """
        )

    @classmethod
    @inlineCallbacks
    def getMessageBatch(
        cls, dbSessionCreator: DbSessionCreator
    ) -> List[MessageHttpRequestTuple]:
        tuples = yield runPyInPg(
            logger, dbSessionCreator, cls._getMessageBatch, None
        )
        return tuples

    @classmethod
    def _getMessageBatch(cls, plpy) -> List[MessageHttpRequestTuple]:
        tuples = []

        # get a batch
        rows = plpy.execute(
            """
            WITH NonSuccessMessagesInSubQueues as (
            SELECT RANK() OVER (
                    PARTITION BY "webhookId"
                    ORDER BY "queuedDate"
                ) AS RNK,
                "webhookId",
                "deliveryStatus"
            FROM CORE_API."MessageQueue"
            WHERE "deliveryStatus" != 2
            ORDER BY "queuedDate",
                "webhookId"
        ),
        DeliervableWebhooks as (
            SELECT "webhookId"
            FROM NonSuccessMessagesInSubQueues
            WHERE "rnk" = 1
                and "deliveryStatus" = 0
        ),
        Deliverables AS (
            SELECT RANK() OVER (
                    PARTITION BY t."webhookId"
                    ORDER BY t."queuedDate"
                ) AS RNK,
                t.*
            FROM CORE_API."MessageQueue" as t
                join DeliervableWebhooks on t."webhookId" = DeliervableWebhooks."webhookId"
            WHERE "deliveryStatus" != 2
            ORDER BY t."queuedDate",
                t."webhookId"
        )
        SELECT Deliverables.id as "id",
            "webhookId",
            "queuedDate",
            "lastDeliveryAttemptDate",
            "lastDeliveryResponseCode",
            "attemptCount",
            "deliveredDate",
            "lastPostResponseSeconds",
            "deliveryStatus",
            "messageBinary",
            "postPath",
            "pluginApiTupleKey",
            webhook."postUrl" as "postUrl",
            webhook."authToken" as "authToken"
        FROM Deliverables join core_api."Webhook" as webhook
            on Deliverables."webhookId" = Webhook."id"
        WHERE "rnk" <= 5
        order by "webhookId",
            "queuedDate"
            """
        )

        for row in rows:
            tuples.append(MessageHttpRequestTuple.fromDict(row))

        rowIds = [str(row.get("id")) for row in rows]
        if not rowIds:
            rowIds = ["0"]  # fallback message queue table id
        rowIds = ",".join(rowIds)
        # update status to IN_PROGRESS
        plpy.execute(
            f"""
        UPDATE CORE_API."MessageQueue"
        SET "deliveryStatus" = 1
        WHERE "id" in ({rowIds});
        """
        )
        return tuples
