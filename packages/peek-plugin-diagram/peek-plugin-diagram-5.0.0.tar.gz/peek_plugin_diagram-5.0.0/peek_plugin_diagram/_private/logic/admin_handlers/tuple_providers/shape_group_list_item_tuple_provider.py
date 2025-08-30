import logging

from sqlalchemy import and_
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

from peek_plugin_base.storage.DbConnection import DbSessionCreator
from peek_plugin_diagram._private.storage.Display import DispGroup
from peek_plugin_diagram._private.tuples.admin.shape_group_list_item_tuple import (
    ShapeGroupListItemTuple,
)


logger = logging.getLogger(__name__)


class ShapeGroupListItemTupleProvider(TuplesProviderABC):
    def __init__(self, dbSessionCreator: DbSessionCreator):
        self._dbSessionCreator = dbSessionCreator

    @deferToThreadWrapWithLogger(logger)
    def makeVortexMsg(self, filt: dict, tupleSelector: TupleSelector) -> bytes:
        coordSetId = tupleSelector.selector["coordSetId"]

        dbSession = self._dbSessionCreator()
        try:
            tuples = [
                ShapeGroupListItemTuple(name=t.name)
                for t in dbSession.query(DispGroup)
                .filter(
                    and_(
                        DispGroup.coordSetId == coordSetId,
                        DispGroup.compileAsTemplate == True,
                    )
                )
                .order_by(DispGroup.name)
            ]
        finally:
            dbSession.close()

        payloadEnvelope = Payload(filt, tuples=tuples).makePayloadEnvelope()
        vortexMsg = payloadEnvelope.toVortexMsg()
        return vortexMsg
