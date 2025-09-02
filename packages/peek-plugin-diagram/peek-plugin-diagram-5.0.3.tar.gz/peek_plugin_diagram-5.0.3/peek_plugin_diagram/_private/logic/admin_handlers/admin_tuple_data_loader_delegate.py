import logging

from vortex.data_loader.TupleDataLoader import TupleDataLoader

from peek_plugin_diagram._private.logic.admin_handlers.data_loader_delegates.config_canvas_tuple_data_loader_delegate import (
    ConfigConfigDataLoaderTupleDelegate,
)
from peek_plugin_diagram._private.logic.admin_handlers.data_loader_delegates.config_color_lookup_tuple_data_loader_delegate import (
    ConfigColorLookupTupleDataLoaderDelegate,
)
from peek_plugin_diagram._private.logic.admin_handlers.data_loader_delegates.config_layer_lookup_tuple_data_loader_delegate import (
    ConfigLayerLookupTupleDataLoaderDelegate,
)
from peek_plugin_diagram._private.logic.admin_handlers.data_loader_delegates.config_level_lookup_tuple_data_loader_delegate import (
    ConfigLevelLookupTupleDataLoaderDelegate,
)
from peek_plugin_diagram._private.logic.admin_handlers.data_loader_delegates.config_line_style_lookup_tuple_data_loader_delegate import (
    ConfigLineStyleLookupTupleDataLoaderDelegate,
)
from peek_plugin_diagram._private.logic.admin_handlers.data_loader_delegates.config_text_style_lookup_tuple_data_loader_delegate import (
    ConfigTextStyleLookupTupleDataLoaderDelegate,
)
from peek_plugin_diagram._private.tuples.admin.config_canvas_data_loader_tuple import (
    ConfigCanvasDataLoaderTuple,
)
from peek_plugin_diagram._private.tuples.admin.config_color_lookup_data_loader_tuple import (
    ConfigColorLookupDataLoaderTuple,
)
from peek_plugin_diagram._private.tuples.admin.config_layer_lookup_data_loader_tuple import (
    ConfigLayerLookupDataLoaderTuple,
)
from peek_plugin_diagram._private.tuples.admin.config_level_lookup_data_loader_tuple import (
    ConfigLevelLookupDataLoaderTuple,
)
from peek_plugin_diagram._private.tuples.admin.config_line_style_lookup_data_loader_tuple import (
    ConfigLineStyleLookupDataLoaderTuple,
)
from peek_plugin_diagram._private.tuples.admin.config_text_style_lookup_data_loader_tuple import (
    ConfigTextStyleLookupDataLoaderTuple,
)


logger = logging.getLogger(__name__)


def makeAdminTupleDataLoader(
    adminTupleObservable, adminActionProcessor, ormSessionCreator
):
    dataLoader = TupleDataLoader(adminTupleObservable, adminActionProcessor)

    dataLoader.setDelegate(
        ConfigCanvasDataLoaderTuple.tupleName(),
        ConfigConfigDataLoaderTupleDelegate(ormSessionCreator),
    )

    dataLoader.setDelegate(
        ConfigColorLookupDataLoaderTuple.tupleName(),
        ConfigColorLookupTupleDataLoaderDelegate(ormSessionCreator),
    )

    dataLoader.setDelegate(
        ConfigLevelLookupDataLoaderTuple.tupleName(),
        ConfigLevelLookupTupleDataLoaderDelegate(ormSessionCreator),
    )

    dataLoader.setDelegate(
        ConfigLayerLookupDataLoaderTuple.tupleName(),
        ConfigLayerLookupTupleDataLoaderDelegate(ormSessionCreator),
    )

    dataLoader.setDelegate(
        ConfigTextStyleLookupDataLoaderTuple.tupleName(),
        ConfigTextStyleLookupTupleDataLoaderDelegate(ormSessionCreator),
    )

    dataLoader.setDelegate(
        ConfigLineStyleLookupDataLoaderTuple.tupleName(),
        ConfigLineStyleLookupTupleDataLoaderDelegate(ormSessionCreator),
    )

    return dataLoader
