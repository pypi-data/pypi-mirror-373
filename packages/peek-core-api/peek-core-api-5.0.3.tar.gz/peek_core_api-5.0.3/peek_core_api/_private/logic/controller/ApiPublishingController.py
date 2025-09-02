import logging
from datetime import datetime
from typing import Union

from psycopg import errors
from pytz import utc
from sqlalchemy.exc import IntegrityError

from peek_core_api._private.storage.PublishedApiTable import PublishedApiTable
from peek_core_api.server.CoreApiProvider import CoreApiProvider
from peek_core_api.server.JsonDataTupleProviderABC import (
    JsonDataTupleProviderABC,
)


logger = logging.getLogger(__name__)

UniqueViolation = errors.lookup("23505")


class ApiPublishingController:
    def __init__(self, dbSessionCreator=None):
        self._dbSessionCreator = dbSessionCreator
        self._committedApi = {}
        self._toBeAddedApi = {}
        self._toBeDeletedApi = {}
        self._storeLoadDate: datetime = datetime.now(tz=utc)

    # non-transactional operations
    def getProvider(
        self, pluginApiTupleKey: str
    ) -> Union[JsonDataTupleProviderABC, None]:
        return self._committedApi.get(pluginApiTupleKey, None)

    # transactional operations
    def load(self):
        """initialise store

        This delete all existing published apis in the dastabase and start a
        fresh new instance for api associating api providers
        """
        # clear all instances
        self._committedApi = {}
        self._toBeAddedApi = {}

        # load apis to committed api
        session = self._dbSessionCreator()
        query = session.query(PublishedApiTable)
        for row in query.all():
            self._committedApi[row.pluginApiTupleKey] = None

    def addApi(self, pluginApiTupleKey: str, apiProvider: CoreApiProvider):
        if pluginApiTupleKey in self._toBeAddedApi:
            # it's in self._toBeAddedApi, do nothing
            return

        self._toBeAddedApi[pluginApiTupleKey] = apiProvider

    def removeApi(self, pluginApiTupleKey: str):
        if pluginApiTupleKey in self._toBeDeletedApi:
            # it's in self._toBeAddedApi, do nothing
            return

        if pluginApiTupleKey in self._committedApi:
            toBedeletedApiProvider = self._committedApi.pop(pluginApiTupleKey)
            self._toBeDeletedApi[pluginApiTupleKey] = toBedeletedApiProvider

    def save(self):
        """save adds to database"""
        if self.isReady:
            return

        if self._toBeAddedApi:
            self._addToDb()
            self._toBeAddedApi = {}

    def hasApi(self, pluginApiTupleKey: str):
        if pluginApiTupleKey in self._committedApi:
            return True
        return False

    @property
    def isReady(self):
        if self.hasAdditions:
            return False
        return True

    @property
    def hasAdditions(self):
        if self._toBeAddedApi:
            return True
        return False

    def _addToDb(self):
        if not self.hasAdditions:
            return

        for (
            pluginApiTupleKey,
            stagedProvider,
        ) in self._toBeAddedApi.items():
            pluginName, apiKey, tupleName = pluginApiTupleKey.split(":")
            thePlugin = PublishedApiTable(
                pluginName=pluginName,
                apiKey=apiKey,
                tupleName=tupleName,
                lastPublishedDate=self._storeLoadDate,
            )
            self._committedApi[pluginApiTupleKey] = stagedProvider

            try:
                session = self._dbSessionCreator()
                session.add(thePlugin)
                session.commit()
            except IntegrityError as e:
                # if the pluginApiTupleKey exists, update lastPublishedDate
                session.rollback()
                existingRow = (
                    session.query(PublishedApiTable)
                    .filter(
                        PublishedApiTable.pluginApiTupleKey == pluginApiTupleKey
                    )
                    .one()
                )
                existingRow.lastPublishedDate = self._storeLoadDate
                session.commit()
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()
