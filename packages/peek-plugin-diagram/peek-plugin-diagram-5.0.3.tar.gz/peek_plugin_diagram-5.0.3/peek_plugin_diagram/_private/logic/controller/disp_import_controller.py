import logging
from typing import List

from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.defer import inlineCallbacks
from vortex.Payload import Payload

from peek_plugin_base.storage.DbConnection import DbSessionCreator
from peek_plugin_base.storage.RunPyInPg import runPyInPg
from peek_plugin_diagram._private.storage.Display import DispBase
from peek_plugin_diagram.tuples.ImportGroupHashTuple import (
    ImportGroupHashTuple,
)
from peek_plugin_diagram._private.worker.tasks.ImportDispTask import (
    importDispsTask,
)
from peek_plugin_livedb.server.LiveDBWriteApiABC import LiveDBWriteApiABC

logger = logging.getLogger(__name__)


class SqlController:
    @classmethod
    @inlineCallbacks
    def getImportGroupHashes(
        cls,
        dbSessionCreator: DbSessionCreator,
        modelSetKey: str,
        coordSetKey: str,
        importGroupHashContains: str,
    ) -> List[str]:
        ret = yield runPyInPg(
            logger,
            dbSessionCreator,
            cls._getImportGroupHashes,
            None,
            modelSetKey=modelSetKey,
            coordSetKey=coordSetKey,
            importGroupHashContains=importGroupHashContains,
        )
        return ret

    @classmethod
    def _getImportGroupHashes(
        self,
        plpy,
        modelSetKey: str,
        coordSetKey: str,
        importGroupHashContains: str,
    ) -> List[ImportGroupHashTuple]:
        rows = plpy.execute(
            f"""
            SELECT DISTINCT
                db."importGroupHash"
            FROM
                pl_diagram."DispBase" AS db
                JOIN pl_diagram."ModelCoordSet" AS mcs ON mcs.id = db."coordSetId"
                JOIN pl_diagram."ModelSet" AS ms ON ms.id = mcs."modelSetId"
            WHERE
                ms.key = '{modelSetKey}'
                AND mcs.key = '{coordSetKey}'
                AND db."importGroupHash" LIKE '%{importGroupHashContains}%';
            """
        )

        ret = []
        for row in rows:
            tuple_ = ImportGroupHashTuple()
            tuple_.fromDict(row)
            ret.append(tuple_)
        return ret


class DispImportController:
    def __init__(
        self,
        dbSessionCreator: DbSessionCreator,
        liveDbWriteApi: LiveDBWriteApiABC,
    ):
        self._dbSessionCreator = dbSessionCreator
        self._liveDbWriteApi = liveDbWriteApi

    def shutdown(self):
        self._liveDbWriteApi = None

    @inlineCallbacks
    def importDisps(
        self,
        modelSetKey: str,
        coordSetKey: str,
        importGroupHash: str,
        dispsEncodedPayload: bytes,
    ):
        liveDbItemsToImport = yield importDispsTask.delay(
            modelSetKey, coordSetKey, importGroupHash, dispsEncodedPayload
        )

        if liveDbItemsToImport:
            yield self._liveDbWriteApi.importLiveDbItems(
                modelSetKey, liveDbItemsToImport
            )

            # Give and connector plugins time to load the new items
            yield self._sleep(2.0)

            yield self._liveDbWriteApi.pollLiveDbValueAcquisition(
                modelSetKey, [i.key for i in liveDbItemsToImport]
            )

    def _sleep(self, seconds):
        d = Deferred()
        reactor.callLater(seconds, d.callback, True)
        return d

    def getImportGroupHashes(
        self, modelSetKey: str, coordSetKey: str, importGroupHashContains: str
    ):
        return SqlController.getImportGroupHashes(
            self._dbSessionCreator,
            modelSetKey,
            coordSetKey,
            importGroupHashContains,
        )

    def removeDispsByImportGroupHash(
        self, modelSetKey: str, coordSetKey: str, importGroupHash: str
    ):
        emptyPayload = Payload(tuples=[]).toEncodedPayload()
        return importDispsTask.delay(
            modelSetKey, coordSetKey, importGroupHash, emptyPayload
        )
