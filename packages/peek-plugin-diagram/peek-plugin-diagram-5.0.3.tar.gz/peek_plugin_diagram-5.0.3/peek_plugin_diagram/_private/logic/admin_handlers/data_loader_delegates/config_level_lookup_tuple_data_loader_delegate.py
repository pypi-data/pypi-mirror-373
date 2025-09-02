import logging
from typing import Optional
from typing import Union

from sqlalchemy.exc import NoResultFound
from twisted.internet.defer import Deferred
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.TupleSelector import TupleSelector
from vortex.data_loader.TupleDataLoaderTupleABC import TupleDataLoaderTupleABC

from peek_plugin_diagram._private.logic.admin_handlers.data_loader_delegates.config_lookup_tuple_data_loader_delegate_base import (
    ConfigLookupTupleDataLoaderDelegateBase,
)
from peek_plugin_diagram._private.logic.tuple_change_event_bus.diagram_tuple_change_event_bus import (
    plDiagramTupleChangeEventBus,
)
from peek_plugin_diagram._private.logic.tuple_change_event_bus.lookup_level_config_change_event import (
    LookupLevelConfigChangeEvent,
)
from peek_plugin_diagram._private.storage.Lookups import DispLevelTable
from peek_plugin_diagram._private.tuples.admin.config_level_lookup_data_loader_tuple import (
    ConfigLevelLookupDataLoaderTuple,
)


logger = logging.getLogger(__name__)


class ConfigLevelLookupTupleDataLoaderDelegate(
    ConfigLookupTupleDataLoaderDelegateBase
):
    TableOrmClass = DispLevelTable

    @deferToThreadWrapWithLogger(logger)
    def createData(
        self, data: TupleDataLoaderTupleABC
    ) -> Union[Deferred, TupleSelector]:
        assert isinstance(data, ConfigLevelLookupDataLoaderTuple), (
            "ConfigLevelLookupTupleDataLoaderDelegate:"
            " data is not a ConfigLevelLookupDataLoaderTuple"
        )

        assert data.item.id is None, (
            "ConfigLevelLookupTupleDataLoaderDelegate:"
            " data.item.id is not None"
        )

        ormSession = self._ormSessionCreator()
        try:
            self._makeUniqueImportHash(data.item, ormSession)

            table = data.item

            ormSession.add(table)
            ormSession.commit()

            newItemId = table.id

            changeEvent = LookupLevelConfigChangeEvent(
                modelSetKey=table.coordSet.modelSet.key,
                coordSetKey=table.coordSet.key,
                coordSetId=table.coordSetId,
                lookupId=table.id,
            )

        finally:
            ormSession.close()

        plDiagramTupleChangeEventBus.notify(changeEvent)

        return TupleSelector(
            ConfigLevelLookupDataLoaderTuple.tupleType(), {"id": newItemId}
        )

    @deferToThreadWrapWithLogger(logger)
    def loadData(
        self, tupleSelector: TupleSelector
    ) -> Union[Deferred, TupleDataLoaderTupleABC]:
        assert (
            "id" in tupleSelector.selector
        ), "ConfigLevelLookupTupleDataLoaderDelegate.loadData id is required"

        ormSession = self._ormSessionCreator()
        try:
            query = ormSession.query(DispLevelTable)
            query = query.filter(
                DispLevelTable.id == tupleSelector.selector["id"]
            )
            return ConfigLevelLookupDataLoaderTuple(item=query.one())

        except NoResultFound:
            return ConfigLevelLookupDataLoaderTuple()

        finally:
            ormSession.close()

    @deferToThreadWrapWithLogger(logger)
    def storeData(
        self,
        data: ConfigLevelLookupDataLoaderTuple,
        tupleSelector: TupleSelector,
    ) -> Optional[TupleSelector]:

        table = data.item
        ormSession = self._ormSessionCreator()
        try:
            row = (
                ormSession.query(DispLevelTable)
                .filter(DispLevelTable.id == table.id)
                .one_or_none()
            )
            if row:
                table = ormSession.merge(table)
            else:
                ormSession.add(table)

            ormSession.commit()

            changeEvent = LookupLevelConfigChangeEvent(
                modelSetKey=table.coordSet.modelSet.key,
                coordSetKey=table.coordSet.key,
                coordSetId=table.coordSetId,
                lookupId=table.id,
            )

        except Exception as e:
            ormSession.rollback()
            raise e

        finally:
            ormSession.close()

        plDiagramTupleChangeEventBus.notify(changeEvent)

        return None
