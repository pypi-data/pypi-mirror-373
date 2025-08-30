import logging
from typing import Optional
from typing import Union

from sqlalchemy.exc import NoResultFound
from twisted.internet.defer import Deferred
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.TupleSelector import TupleSelector
from vortex.data_loader.TupleDataLoaderDelegate import (
    TupleDataLoaderDelegateABC,
)
from vortex.data_loader.TupleDataLoaderTupleABC import TupleDataLoaderTupleABC

from peek_plugin_diagram._private.logic.admin_handlers.data_loader_delegates.config_lookup_tuple_data_loader_delegate_base import (
    ConfigLookupTupleDataLoaderDelegateBase,
)
from peek_plugin_diagram._private.logic.tuple_change_event_bus.diagram_tuple_change_event_bus import (
    plDiagramTupleChangeEventBus,
)
from peek_plugin_diagram._private.logic.tuple_change_event_bus.lookup_line_style_config_change_event import (
    LookupLineStyleConfigChangeEvent,
)
from peek_plugin_diagram._private.storage.Lookups import DispLineStyleTable
from peek_plugin_diagram._private.tuples.admin.config_line_style_lookup_data_loader_tuple import (
    ConfigLineStyleLookupDataLoaderTuple,
)


logger = logging.getLogger(__name__)


class ConfigLineStyleLookupTupleDataLoaderDelegate(
    ConfigLookupTupleDataLoaderDelegateBase
):
    TableOrmClass = DispLineStyleTable

    @deferToThreadWrapWithLogger(logger)
    def createData(
        self, data: TupleDataLoaderTupleABC
    ) -> Union[Deferred, TupleSelector]:
        assert isinstance(data, ConfigLineStyleLookupDataLoaderTuple), (
            "ConfigLineStyleLookupTupleDataLoaderDelegate:"
            " data is not a ConfigLineStyleLookupDataLoaderTuple"
        )

        assert data.item.id is None, (
            "ConfigLineStyleLookupTupleDataLoaderDelegate:"
            " data.item.id is not None"
        )

        ormSession = self._ormSessionCreator()
        try:
            self._makeUniqueImportHash(data.item, ormSession)

            table = data.item

            ormSession.add(table)
            ormSession.commit()

            newItemId = table.id

            changeEvent = LookupLineStyleConfigChangeEvent(
                modelSetKey=table.modelSet.key,
                modelSetId=table.modelSetId,
                lookupId=table.id,
            )

        finally:
            ormSession.close()

        plDiagramTupleChangeEventBus.notify(changeEvent)

        return TupleSelector(
            ConfigLineStyleLookupDataLoaderTuple.tupleType(), {"id": newItemId}
        )

    @deferToThreadWrapWithLogger(logger)
    def loadData(
        self, tupleSelector: TupleSelector
    ) -> Union[Deferred, TupleDataLoaderTupleABC]:
        assert (
            "id" in tupleSelector.selector
        ), "ConfigLineStyleLookupTupleDataLoaderDelegate.loadData id is required"

        ormSession = self._ormSessionCreator()
        try:
            query = ormSession.query(DispLineStyleTable)
            query = query.filter(
                DispLineStyleTable.id == tupleSelector.selector["id"]
            )
            return ConfigLineStyleLookupDataLoaderTuple(item=query.one())

        except NoResultFound:
            return ConfigLineStyleLookupDataLoaderTuple()

        finally:
            ormSession.close()

    @deferToThreadWrapWithLogger(logger)
    def storeData(
        self,
        data: ConfigLineStyleLookupDataLoaderTuple,
        tupleSelector: TupleSelector,
    ) -> Optional[TupleSelector]:

        table = data.item
        ormSession = self._ormSessionCreator()
        try:
            row = (
                ormSession.query(DispLineStyleTable)
                .filter(DispLineStyleTable.id == table.id)
                .one_or_none()
            )
            if row:
                table = ormSession.merge(table)
            else:
                ormSession.add(table)

            ormSession.commit()

            changeEvent = LookupLineStyleConfigChangeEvent(
                modelSetKey=table.modelSet.key,
                modelSetId=table.modelSetId,
                lookupId=table.id,
            )

        except Exception as e:
            ormSession.rollback()
            raise e

        finally:
            ormSession.close()

        plDiagramTupleChangeEventBus.notify(changeEvent)

        return None
