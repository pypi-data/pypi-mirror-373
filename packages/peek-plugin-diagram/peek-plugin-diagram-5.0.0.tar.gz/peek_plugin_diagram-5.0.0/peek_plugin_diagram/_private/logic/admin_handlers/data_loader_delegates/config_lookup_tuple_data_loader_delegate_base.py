import logging
from abc import ABCMeta

from sqlalchemy import and_
from twisted.internet.defer import Deferred
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.TupleSelector import TupleSelector
from vortex.data_loader.TupleDataLoaderDelegate import (
    TupleDataLoaderDelegateABC,
)


logger = logging.getLogger(__name__)


class ConfigLookupTupleDataLoaderDelegateBase(
    TupleDataLoaderDelegateABC, metaclass=ABCMeta
):
    TableOrmClass = None

    def __init__(self, ormSessionCreator):
        self._ormSessionCreator = ormSessionCreator

    def _makeUniqueImportHash(self, item, ormSession):
        if not item.importHash:
            return

        if hasattr(item, "coordSetId"):
            predicate = item.coordSetId == item.coordSetId
        else:
            predicate = item.modelSetId == item.modelSetId

        copyNum = 2
        originalImportHash = item.importHash
        while (
            ormSession.query(self.TableOrmClass)
            .filter(
                and_(
                    predicate,
                    self.TableOrmClass.importHash == item.importHash,
                    self.TableOrmClass.id != item.id,
                )
            )
            .count()
        ):
            item.importHash = f"{originalImportHash}-{copyNum}"
            copyNum = copyNum + 1

    @deferToThreadWrapWithLogger(logger)
    def deleteData(self, tupleSelector: TupleSelector) -> Deferred:
        raise NotImplementedError("We don't delete settings")
