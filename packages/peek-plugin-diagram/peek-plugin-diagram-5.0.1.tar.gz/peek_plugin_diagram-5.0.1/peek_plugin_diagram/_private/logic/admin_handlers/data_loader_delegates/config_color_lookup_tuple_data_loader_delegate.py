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
from peek_plugin_diagram._private.logic.tuple_change_event_bus.lookup_color_config_change_event import (
    LookupColorConfigChangeEvent,
)
from peek_plugin_diagram._private.storage.Lookups import DispColorTable
from peek_plugin_diagram._private.tuples.admin.config_color_lookup_data_loader_tuple import (
    ConfigColorLookupDataLoaderTuple,
)


logger = logging.getLogger(__name__)


class ConfigColorLookupTupleDataLoaderDelegate(
    ConfigLookupTupleDataLoaderDelegateBase
):
    TableOrmClass = DispColorTable

    @deferToThreadWrapWithLogger(logger)
    def createData(
        self, data: TupleDataLoaderTupleABC
    ) -> Union[Deferred, TupleSelector]:
        assert isinstance(data, ConfigColorLookupDataLoaderTuple), (
            "ConfigColorLookupTupleDataLoaderDelegate:"
            " data is not a ConfigColorLookupDataLoaderTuple"
        )

        assert data.item.id is None, (
            "ConfigColorLookupTupleDataLoaderDelegate:"
            " data.item.id is not None"
        )

        ormSession = self._ormSessionCreator()
        try:
            self._makeUniqueImportHash(data.item, ormSession)

            table = data.item

            ormSession.add(table)
            ormSession.commit()

            newItemId = table.id

            changeEvent = LookupColorConfigChangeEvent(
                modelSetKey=table.modelSet.key,
                modelSetId=table.modelSetId,
                lookupId=table.id,
            )

        finally:
            ormSession.close()

        plDiagramTupleChangeEventBus.notify(changeEvent)

        return TupleSelector(
            ConfigColorLookupDataLoaderTuple.tupleType(), {"id": newItemId}
        )

    @deferToThreadWrapWithLogger(logger)
    def loadData(
        self, tupleSelector: TupleSelector
    ) -> Union[Deferred, TupleDataLoaderTupleABC]:
        assert (
            "id" in tupleSelector.selector
        ), "ConfigColorLookupTupleDataLoaderDelegate.loadData id is required"

        ormSession = self._ormSessionCreator()
        try:
            query = ormSession.query(DispColorTable)
            query = query.filter(
                DispColorTable.id == tupleSelector.selector["id"]
            )
            return ConfigColorLookupDataLoaderTuple(item=query.one())

        except NoResultFound:
            return ConfigColorLookupDataLoaderTuple()

        finally:
            ormSession.close()

    @deferToThreadWrapWithLogger(logger)
    def storeData(
        self,
        data: ConfigColorLookupDataLoaderTuple,
        tupleSelector: TupleSelector,
    ) -> Optional[TupleSelector]:

        table = data.item
        ormSession = self._ormSessionCreator()
        try:
            row = (
                ormSession.query(DispColorTable)
                .filter(DispColorTable.id == table.id)
                .one_or_none()
            )
            if row:
                table = ormSession.merge(table)
            else:
                ormSession.add(table)

            ormSession.commit()

            changeEvent = LookupColorConfigChangeEvent(
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

        return TupleSelector(
            ConfigColorLookupDataLoaderTuple.tupleType(), {"id": table.id}
        )
