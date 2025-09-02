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
from peek_plugin_diagram._private.logic.tuple_change_event_bus.lookup_text_style_config_change_event import (
    LookupTextStyleConfigChangeEvent,
)
from peek_plugin_diagram._private.storage.Lookups import DispTextStyleTable
from peek_plugin_diagram._private.tuples.admin.config_text_style_lookup_data_loader_tuple import (
    ConfigTextStyleLookupDataLoaderTuple,
)


logger = logging.getLogger(__name__)


class ConfigTextStyleLookupTupleDataLoaderDelegate(
    ConfigLookupTupleDataLoaderDelegateBase
):
    TableOrmClass = DispTextStyleTable

    @deferToThreadWrapWithLogger(logger)
    def createData(
        self, data: TupleDataLoaderTupleABC
    ) -> Union[Deferred, TupleSelector]:
        assert isinstance(data, ConfigTextStyleLookupDataLoaderTuple), (
            "ConfigTextStyleLookupTupleDataLoaderDelegate:"
            " data is not a ConfigTextStyleLookupDataLoaderTuple"
        )

        assert data.item.id is None, (
            "ConfigTextStyleLookupTupleDataLoaderDelegate:"
            " data.item.id is not None"
        )

        ormSession = self._ormSessionCreator()
        try:
            self._makeUniqueImportHash(data.item, ormSession)

            table = data.item

            ormSession.add(table)
            ormSession.commit()

            newItemId = table.id

            changeEvent = LookupTextStyleConfigChangeEvent(
                modelSetKey=table.modelSet.key,
                modelSetId=table.modelSetId,
                lookupId=table.id,
            )

        finally:
            ormSession.close()

        plDiagramTupleChangeEventBus.notify(changeEvent)

        return TupleSelector(
            ConfigTextStyleLookupDataLoaderTuple.tupleType(), {"id": newItemId}
        )

    @deferToThreadWrapWithLogger(logger)
    def loadData(
        self, tupleSelector: TupleSelector
    ) -> Union[Deferred, TupleDataLoaderTupleABC]:
        assert (
            "id" in tupleSelector.selector
        ), "ConfigTextStyleLookupTupleDataLoaderDelegate.loadData id is required"

        ormSession = self._ormSessionCreator()
        try:
            query = ormSession.query(DispTextStyleTable)
            query = query.filter(
                DispTextStyleTable.id == tupleSelector.selector["id"]
            )
            return ConfigTextStyleLookupDataLoaderTuple(item=query.one())

        except NoResultFound:
            return ConfigTextStyleLookupDataLoaderTuple()

        finally:
            ormSession.close()

    @deferToThreadWrapWithLogger(logger)
    def storeData(
        self,
        data: ConfigTextStyleLookupDataLoaderTuple,
        tupleSelector: TupleSelector,
    ) -> Optional[TupleSelector]:

        table = data.item
        ormSession = self._ormSessionCreator()
        try:
            row = (
                ormSession.query(DispTextStyleTable)
                .filter(DispTextStyleTable.id == table.id)
                .one_or_none()
            )
            if row:
                table = ormSession.merge(table)
            else:
                ormSession.add(table)

            ormSession.commit()

            changeEvent = LookupTextStyleConfigChangeEvent(
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
