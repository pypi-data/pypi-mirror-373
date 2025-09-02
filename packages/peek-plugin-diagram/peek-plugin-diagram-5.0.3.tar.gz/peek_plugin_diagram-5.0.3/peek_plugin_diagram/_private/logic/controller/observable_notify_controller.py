import logging

from vortex.TupleSelector import TupleSelector
from vortex.event_bus.TupleChangeEventABC import TupleChangeEventABC
from vortex.event_bus.TupleChangeEventBusObserverABC import (
    TupleChangeEventBusObserverABC,
)
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

from peek_plugin_diagram._private.logic.tuple_change_event_bus.canvas_config_change_event import (
    CanvasConfigChangeEvent,
)
from peek_plugin_diagram._private.logic.tuple_change_event_bus.diagram_lookup_change_event import (
    DiagramLookupChangeEvent,
)
from peek_plugin_diagram._private.logic.tuple_change_event_bus.diagram_tuple_change_event_bus import (
    plDiagramTupleChangeEventBus,
)
from peek_plugin_diagram._private.logic.tuple_change_event_bus.lookup_color_config_change_event import (
    LookupColorConfigChangeEvent,
)
from peek_plugin_diagram._private.logic.tuple_change_event_bus.lookup_layer_config_change_event import (
    LookupLayerConfigChangeEvent,
)
from peek_plugin_diagram._private.logic.tuple_change_event_bus.lookup_level_config_change_event import (
    LookupLevelConfigChangeEvent,
)
from peek_plugin_diagram._private.logic.tuple_change_event_bus.lookup_line_style_config_change_event import (
    LookupLineStyleConfigChangeEvent,
)
from peek_plugin_diagram._private.logic.tuple_change_event_bus.lookup_text_style_config_change_event import (
    LookupTextStyleConfigChangeEvent,
)
from peek_plugin_diagram._private.lookup_type_maps import (
    lookupTypeTableEnumToTable,
)
from peek_plugin_diagram._private.storage.Lookups import DispColorTable
from peek_plugin_diagram._private.storage.Lookups import DispLayerTable
from peek_plugin_diagram._private.storage.Lookups import DispLevelTable
from peek_plugin_diagram._private.storage.Lookups import DispLineStyleTable
from peek_plugin_diagram._private.storage.Lookups import DispTextStyleTable
from peek_plugin_diagram._private.storage.ModelSet import ModelCoordSetTable
from peek_plugin_diagram._private.tuples.admin.config_color_lookup_list_tuple import (
    ConfigColorLookupListTuple,
)
from peek_plugin_diagram._private.tuples.admin.config_layer_lookup_list_tuple import (
    ConfigLayerLookupListTuple,
)
from peek_plugin_diagram._private.tuples.admin.config_level_lookup_list_tuple import (
    ConfigLevelLookupListTuple,
)
from peek_plugin_diagram._private.tuples.admin.config_line_style_lookup_list_tuple import (
    ConfigLineStyleLookupListTuple,
)
from peek_plugin_diagram._private.tuples.admin.config_text_style_lookup_list_tuple import (
    ConfigTextStyleLookupListTuple,
)
from peek_plugin_diagram._private.tuples.admin.private_diagram_lookup_list_tuple import (
    PrivateDiagramLookupListTuple,
)

logger = logging.getLogger(__name__)


class ObservableNotifyController(TupleChangeEventBusObserverABC):

    def __init__(
        self,
        adminTupleObservable: TupleDataObservableHandler,
        clientBackendTupleObservable: TupleDataObservableHandler,
    ):
        self._adminTupleObservable = adminTupleObservable
        self._clientBackendTupleObservable = clientBackendTupleObservable

        plDiagramTupleChangeEventBus.addObserver(self)

    def notifyFromBus(self, event: TupleChangeEventABC) -> None:
        if isinstance(event, CanvasConfigChangeEvent):
            self._notifyCanvasConfigTupleUpdate()
            return

        if isinstance(event, LookupColorConfigChangeEvent):
            self._notifyLookupColorConfigTupleUpdate(event)
            return

        if isinstance(event, LookupLayerConfigChangeEvent):
            self._notifyLookupLayerConfigTupleUpdate(event)
            return

        if isinstance(event, LookupLevelConfigChangeEvent):
            self._notifyLookupLevelConfigTupleUpdate(event)
            return

        if isinstance(event, LookupLineStyleConfigChangeEvent):
            self._notifyLookupLineStyleConfigTupleUpdate(event)
            return

        if isinstance(event, LookupTextStyleConfigChangeEvent):
            self._notifyLookupTextStyleConfigTupleUpdate(event)
            return

        if isinstance(event, DiagramLookupChangeEvent):
            self._notifyDiagamLookupListTupleUpdate(event)
            return

    def shutdown(self):
        self._adminTupleObservable = None

    def _notifyCanvasConfigTupleUpdate(self):
        self._clientBackendTupleObservable.notifyOfTupleUpdate(
            TupleSelector(ModelCoordSetTable.tupleName(), {})
        )

    def _notifyLookupColorConfigTupleUpdate(
        self, event: LookupColorConfigChangeEvent
    ):
        self._clientBackendTupleObservable.notifyOfTupleUpdate(
            TupleSelector(DispColorTable.tupleName(), {})
        )

        self._adminTupleObservable.notifyOfTupleUpdate(
            TupleSelector(
                PrivateDiagramLookupListTuple.tupleName(),
                {
                    "modelSetKey": event.modelSetKey,
                    "coordSetKey": None,
                    "lookupType": DispColorTable.LookupTypeE,
                },
            )
        )

        self._adminTupleObservable.notifyOfTupleUpdate(
            TupleSelector(
                ConfigColorLookupListTuple.tupleName(),
                {"modelSetId": event.modelSetId},
            )
        )

    def _notifyLookupLayerConfigTupleUpdate(
        self, event: LookupLayerConfigChangeEvent
    ):
        self._clientBackendTupleObservable.notifyOfTupleUpdate(
            TupleSelector(DispLayerTable.tupleName(), {})
        )

        self._adminTupleObservable.notifyOfTupleUpdate(
            TupleSelector(
                PrivateDiagramLookupListTuple.tupleName(),
                {
                    "modelSetKey": event.modelSetKey,
                    "coordSetKey": None,
                    "lookupType": DispLayerTable.LookupTypeE,
                },
            )
        )

        self._adminTupleObservable.notifyOfTupleUpdate(
            TupleSelector(
                ConfigLayerLookupListTuple.tupleName(),
                {"modelSetId": event.modelSetId},
            )
        )

    def _notifyLookupLevelConfigTupleUpdate(
        self, event: LookupLevelConfigChangeEvent
    ):
        self._clientBackendTupleObservable.notifyOfTupleUpdate(
            TupleSelector(DispLevelTable.tupleName(), {})
        )

        self._adminTupleObservable.notifyOfTupleUpdate(
            TupleSelector(
                PrivateDiagramLookupListTuple.tupleName(),
                {
                    "modelSetKey": event.modelSetKey,
                    "coordSetKey": event.coordSetKey,
                    "lookupType": DispLevelTable.LookupTypeE,
                },
            )
        )

        self._adminTupleObservable.notifyOfTupleUpdate(
            TupleSelector(
                ConfigLevelLookupListTuple.tupleName(),
                {"canvasId": event.coordSetId},
            )
        )

    def _notifyLookupLineStyleConfigTupleUpdate(
        self, event: LookupLineStyleConfigChangeEvent
    ):
        self._clientBackendTupleObservable.notifyOfTupleUpdate(
            TupleSelector(DispLineStyleTable.tupleName(), {})
        )

        self._adminTupleObservable.notifyOfTupleUpdate(
            TupleSelector(
                PrivateDiagramLookupListTuple.tupleName(),
                {
                    "modelSetKey": event.modelSetKey,
                    "coordSetKey": None,
                    "lookupType": DispLineStyleTable.LookupTypeE,
                },
            )
        )

        self._adminTupleObservable.notifyOfTupleUpdate(
            TupleSelector(
                ConfigLineStyleLookupListTuple.tupleName(),
                {"modelSetId": event.modelSetId},
            )
        )

    def _notifyLookupTextStyleConfigTupleUpdate(
        self, event: LookupTextStyleConfigChangeEvent
    ):
        self._clientBackendTupleObservable.notifyOfTupleUpdate(
            TupleSelector(DispTextStyleTable.tupleName(), {})
        )

        self._adminTupleObservable.notifyOfTupleUpdate(
            TupleSelector(
                PrivateDiagramLookupListTuple.tupleName(),
                {
                    "modelSetKey": event.modelSetKey,
                    "coordSetKey": None,
                    "lookupType": DispTextStyleTable.LookupTypeE,
                },
            )
        )

        self._adminTupleObservable.notifyOfTupleUpdate(
            TupleSelector(
                ConfigTextStyleLookupListTuple.tupleName(),
                {"modelSetId": event.modelSetId},
            )
        )

    def _notifyDiagamLookupListTupleUpdate(
        self, event: DiagramLookupChangeEvent
    ):
        self._clientBackendTupleObservable.notifyOfTupleUpdate(
            TupleSelector(
                lookupTypeTableEnumToTable[event.lookupType].tupleName(), {}
            )
        )

        self._adminTupleObservable.notifyOfTupleUpdate(
            TupleSelector(
                PrivateDiagramLookupListTuple.tupleName(),
                {
                    "modelSetKey": event.modelSetKey,
                    "coordSetKey": event.coordSetKey,
                    "lookupType": event.lookupType,
                },
            )
        )
