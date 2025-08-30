import logging
from typing import Optional
from typing import Union

from sqlalchemy import and_
from sqlalchemy.exc import NoResultFound
from twisted.internet.defer import Deferred
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.TupleSelector import TupleSelector
from vortex.data_loader.TupleDataLoaderDelegate import (
    TupleDataLoaderDelegateABC,
)
from vortex.data_loader.TupleDataLoaderTupleABC import TupleDataLoaderTupleABC

from peek_plugin_diagram._private.logic.tuple_change_event_bus.canvas_config_change_event import (
    CanvasConfigChangeEvent,
)
from peek_plugin_diagram._private.logic.tuple_change_event_bus.diagram_tuple_change_event_bus import (
    plDiagramTupleChangeEventBus,
)
from peek_plugin_diagram._private.storage.ModelSet import (
    ModelCoordSetGridSizeTable,
)
from peek_plugin_diagram._private.storage.ModelSet import ModelCoordSetTable
from peek_plugin_diagram._private.tuples.admin.config_canvas_data_loader_tuple import (
    ConfigCanvasDataLoaderTuple,
)


logger = logging.getLogger(__name__)


class ConfigConfigDataLoaderTupleDelegate(TupleDataLoaderDelegateABC):
    def __init__(self, ormSessionCreator):
        self._ormSessionCreator = ormSessionCreator

    @deferToThreadWrapWithLogger(logger)
    def createData(
        self, data: TupleDataLoaderTupleABC
    ) -> Union[Deferred, TupleSelector]:
        raise NotImplementedError()

    @deferToThreadWrapWithLogger(logger)
    def loadData(
        self, tupleSelector: TupleSelector
    ) -> Union[Deferred, TupleDataLoaderTupleABC]:
        assert (
            "id" in tupleSelector.selector
        ), "ConfigConfigDataLoaderTupleDelegate.loadData id is required"

        ormSession = self._ormSessionCreator()
        try:
            query = ormSession.query(ModelCoordSetTable)
            query = query.filter(
                ModelCoordSetTable.id == tupleSelector.selector["id"]
            )
            table = query.one()
            return ConfigCanvasDataLoaderTuple(
                item=table,
                modelSetKey=table.modelSet.key,
                coordSetKey=table.key,
            )

        except NoResultFound:
            return ConfigCanvasDataLoaderTuple()

        finally:
            ormSession.close()

    @deferToThreadWrapWithLogger(logger)
    def storeData(
        self, data: ConfigCanvasDataLoaderTuple, tupleSelector: TupleSelector
    ) -> Optional[TupleSelector]:

        table = data.item
        ormSession = self._ormSessionCreator()
        try:
            # Get list of polyLevel IDs to keep
            gridSizeIds = [level.id for level in data.item.gridSizes]

            # Delete poly levels not in the list
            ormSession.query(ModelCoordSetGridSizeTable).filter(
                and_(
                    ModelCoordSetGridSizeTable.coordSetId == table.id,
                    ~ModelCoordSetGridSizeTable.id.in_(gridSizeIds),
                )
            ).delete(synchronize_session=False)

            row = (
                ormSession.query(ModelCoordSetTable)
                .filter(ModelCoordSetTable.id == table.id)
                .one_or_none()
            )
            if row:
                table = ormSession.merge(table)
            else:
                ormSession.add(table)

            ormSession.commit()
            changeEvent = CanvasConfigChangeEvent(table.id)

        except Exception as e:
            ormSession.rollback()
            raise e

        finally:
            ormSession.close()

        plDiagramTupleChangeEventBus.notify(changeEvent)

        return None

    @deferToThreadWrapWithLogger(logger)
    def deleteData(self, tupleSelector: TupleSelector) -> Deferred:
        raise NotImplementedError("We don't delete settings")
