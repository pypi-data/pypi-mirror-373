from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

from peek_plugin_base.PeekVortexUtil import peekAdminName
from peek_plugin_base.storage.DbConnection import DbSessionCreator
from peek_plugin_diagram._private.PluginNames import diagramFilt
from peek_plugin_diagram._private.PluginNames import diagramObservableName
from peek_plugin_diagram._private.logic.admin_handlers.tuple_providers.config_canvas_list_tuple_provider import (
    ConfigCanvasListTupleProvider,
)
from peek_plugin_diagram._private.logic.admin_handlers.tuple_providers.config_color_lookup_list_tuple_provider import (
    ConfigColorLookupListTupleProvider,
)
from peek_plugin_diagram._private.logic.admin_handlers.tuple_providers.config_layer_lookup_list_tuple_provider import (
    ConfigLayerLookupListTupleProvider,
)
from peek_plugin_diagram._private.logic.admin_handlers.tuple_providers.config_level_lookup_list_tuple_provider import (
    ConfigLevelLookupListTupleProvider,
)
from peek_plugin_diagram._private.logic.admin_handlers.tuple_providers.config_line_style_lookup_list_tuple_provider import (
    ConfigLineStyleLookupListTupleProvider,
)
from peek_plugin_diagram._private.logic.admin_handlers.tuple_providers.config_model_set_list_tuple_provider import (
    ConfigModelSetListTupleProvider,
)
from peek_plugin_diagram._private.logic.admin_handlers.tuple_providers.config_text_style_lookup_list_tuple_provider import (
    ConfigTextStyleLookupListTupleProvider,
)
from peek_plugin_diagram._private.logic.admin_handlers.tuple_providers.private_diagram_lookup_list_tuple_provider import (
    PrivateDiagramLookupListTupleProvider,
)
from peek_plugin_diagram._private.logic.admin_handlers.tuple_providers.diagram_processing_status_tuple_provider import (
    DiagramProcessingStatusTupleProvider,
)
from peek_plugin_diagram._private.logic.admin_handlers.tuple_providers.shape_edge_template_list_item_tuple_provider import (
    ShapeEdgeTemplateListItemTupleProvider,
)
from peek_plugin_diagram._private.logic.admin_handlers.tuple_providers.shape_group_list_item_tuple_provider import (
    ShapeGroupListItemTupleProvider,
)
from peek_plugin_diagram._private.logic.controller.status_controller import (
    StatusController,
)
from peek_plugin_diagram._private.tuples.admin.diagram_importer_status_tuple import (
    DiagramProcessingStatusTuple,
)
from peek_plugin_diagram._private.tuples.admin.config_canvas_list_tuple import (
    ConfigCanvasListTuple,
)
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
from peek_plugin_diagram._private.tuples.admin.config_model_list_tuple import (
    ConfigModelSetListTuple,
)
from peek_plugin_diagram._private.tuples.admin.config_text_style_lookup_list_tuple import (
    ConfigTextStyleLookupListTuple,
)
from peek_plugin_diagram._private.tuples.admin.private_diagram_lookup_list_tuple import (
    PrivateDiagramLookupListTuple,
)
from peek_plugin_diagram._private.tuples.admin.shape_edge_template_list_item_tuple import (
    ShapeEdgeTemplateListItemTuple,
)
from peek_plugin_diagram._private.tuples.admin.shape_group_list_item_tuple import (
    ShapeGroupListItemTuple,
)


def makeAdminTupleDataObservableHandler(
    dbSessionCreator: DbSessionCreator, statusController: StatusController
) -> TupleDataObservableHandler:
    """ " Make Tuple Data Observable Handler

    This method creates the observable object, registers the tuple providers and then
    returns it.

    :param dbSessionCreator: A function that returns a SQLAlchemy session when called
    :param statusController: The Status Controller
    :param lookupImportController: The Loookup import controller the API uses

    :return: An instance of :code:`TupleDataObservableHandler`

    """
    tupleObservable = TupleDataObservableHandler(
        observableName=diagramObservableName,
        additionalFilt=diagramFilt,
        acceptOnlyFromVortex=peekAdminName,
    )

    # Register TupleProviders here
    tupleObservable.addTupleProvider(
        DiagramProcessingStatusTuple.tupleName(),
        DiagramProcessingStatusTupleProvider(statusController),
    )

    tupleObservable.addTupleProvider(
        ConfigModelSetListTuple.tupleName(),
        ConfigModelSetListTupleProvider(dbSessionCreator),
    )

    tupleObservable.addTupleProvider(
        ConfigCanvasListTuple.tupleName(),
        ConfigCanvasListTupleProvider(dbSessionCreator),
    )

    tupleObservable.addTupleProvider(
        ConfigColorLookupListTuple.tupleName(),
        ConfigColorLookupListTupleProvider(dbSessionCreator),
    )

    tupleObservable.addTupleProvider(
        ConfigLevelLookupListTuple.tupleName(),
        ConfigLevelLookupListTupleProvider(dbSessionCreator),
    )

    tupleObservable.addTupleProvider(
        ConfigLayerLookupListTuple.tupleName(),
        ConfigLayerLookupListTupleProvider(dbSessionCreator),
    )

    tupleObservable.addTupleProvider(
        ConfigTextStyleLookupListTuple.tupleName(),
        ConfigTextStyleLookupListTupleProvider(dbSessionCreator),
    )

    tupleObservable.addTupleProvider(
        ConfigLineStyleLookupListTuple.tupleName(),
        ConfigLineStyleLookupListTupleProvider(dbSessionCreator),
    )

    tupleObservable.addTupleProvider(
        PrivateDiagramLookupListTuple.tupleName(),
        PrivateDiagramLookupListTupleProvider(dbSessionCreator),
    )

    tupleObservable.addTupleProvider(
        ShapeGroupListItemTuple.tupleName(),
        ShapeGroupListItemTupleProvider(dbSessionCreator),
    )

    tupleObservable.addTupleProvider(
        ShapeEdgeTemplateListItemTuple.tupleName(),
        ShapeEdgeTemplateListItemTupleProvider(dbSessionCreator),
    )

    return tupleObservable
