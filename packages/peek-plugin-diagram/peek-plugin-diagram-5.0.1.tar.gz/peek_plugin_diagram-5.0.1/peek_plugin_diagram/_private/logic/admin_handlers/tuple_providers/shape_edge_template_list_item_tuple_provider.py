import logging

from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

from peek_plugin_base.storage.DbConnection import DbSessionCreator
from peek_plugin_diagram._private.storage.Display import DispEdgeTemplate
from peek_plugin_diagram._private.tuples.admin.shape_edge_template_list_item_tuple import (
    ShapeEdgeTemplateListItemTuple,
)


logger = logging.getLogger(__name__)


class ShapeEdgeTemplateListItemTupleProvider(TuplesProviderABC):
    def __init__(self, dbSessionCreator: DbSessionCreator):
        self._dbSessionCreator = dbSessionCreator

    @deferToThreadWrapWithLogger(logger)
    def makeVortexMsg(self, filt: dict, tupleSelector: TupleSelector) -> bytes:
        coordSetId = tupleSelector.selector["coordSetId"]

        dbSession = self._dbSessionCreator()
        try:
            tuples = [
                ShapeEdgeTemplateListItemTuple(name=t.name)
                for t in dbSession.query(DispEdgeTemplate)
                .filter(DispEdgeTemplate.coordSetId == coordSetId)
                .order_by(DispEdgeTemplate.name)
            ]
        finally:
            dbSession.close()

        payloadEnvelope = Payload(filt, tuples=tuples).makePayloadEnvelope()
        vortexMsg = payloadEnvelope.toVortexMsg()
        return vortexMsg
