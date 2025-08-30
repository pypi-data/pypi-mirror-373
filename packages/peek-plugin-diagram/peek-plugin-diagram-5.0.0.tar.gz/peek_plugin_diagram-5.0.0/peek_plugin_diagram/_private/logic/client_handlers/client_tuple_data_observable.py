from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

from peek_plugin_base.PeekVortexUtil import peekBackendNames
from peek_plugin_diagram._private.PluginNames import diagramFilt
from peek_plugin_diagram._private.PluginNames import diagramObservableName
from peek_plugin_diagram._private.logic.controller.branch_live_edit_controller import (
    BranchLiveEditController,
)
from peek_plugin_diagram._private.logic.client_handlers.tuple_providers.BranchKeyToIdMapProvider import (
    BranchKeyToIdMapTupleProvider,
)
from peek_plugin_diagram._private.logic.client_handlers.tuple_providers.BranchLiveEditTupleProvider import (
    BranchLiveEditTupleProvider,
)
from peek_plugin_diagram._private.logic.client_handlers.tuple_providers.ServerCoordSetTupleProvider import (
    ServerCoordSetTupleProvider,
)
from peek_plugin_diagram._private.logic.client_handlers.tuple_providers.ServerLookupTupleProvider import (
    ServerLookupTupleProvider,
)
from peek_plugin_diagram._private.logic.client_handlers.tuple_providers.ServerModelSetTupleProvider import (
    ServerModelSetTupleProvider,
)
from peek_plugin_diagram._private.storage.Lookups import DispColorTable
from peek_plugin_diagram._private.storage.Lookups import DispLayerTable
from peek_plugin_diagram._private.storage.Lookups import DispLevelTable
from peek_plugin_diagram._private.storage.Lookups import DispLineStyleTable
from peek_plugin_diagram._private.storage.Lookups import DispTextStyleTable
from peek_plugin_diagram._private.storage.ModelSet import ModelCoordSetTable
from peek_plugin_diagram._private.storage.ModelSet import ModelSetTable
from peek_plugin_diagram._private.tuples.branch.BranchKeyToIdMapTuple import (
    BranchKeyToIdMapTuple,
)
from peek_plugin_diagram._private.tuples.branch.BranchLiveEditTuple import (
    BranchLiveEditTuple,
)


def makeClientTupleDataObservableHandler(
    ormSessionCreator, branchLiveEditController: BranchLiveEditController
):
    """ " Make Tuple Data Observable Handler

    This method creates the observable object, registers the tuple providers and then
    returns it.

    :param branchLiveEditController:
    :param ormSessionCreator: A callable that returns an SQLAlchemy session
    :param statusController: The status controller
    :return: An instance of :code:`TupleDataObservableHandler`

    """
    tupleObservable = TupleDataObservableHandler(
        observableName=diagramObservableName,
        additionalFilt=diagramFilt,
        acceptOnlyFromVortex=peekBackendNames,
    )

    # Register TupleProviders here
    tupleObservable.addTupleProvider(
        ModelSetTable.tupleName(),
        ServerModelSetTupleProvider(ormSessionCreator),
    )

    # Register TupleProviders here
    tupleObservable.addTupleProvider(
        ModelCoordSetTable.tupleName(),
        ServerCoordSetTupleProvider(ormSessionCreator),
    )

    # Register TupleProviders here
    tupleObservable.addTupleProvider(
        BranchKeyToIdMapTuple.tupleName(),
        BranchKeyToIdMapTupleProvider(ormSessionCreator),
    )

    # Register TupleProviders here
    lookupTupleProvider = ServerLookupTupleProvider(ormSessionCreator)
    tupleObservable.addTupleProvider(
        DispLevelTable.tupleName(), lookupTupleProvider
    )
    tupleObservable.addTupleProvider(
        DispLayerTable.tupleName(), lookupTupleProvider
    )
    tupleObservable.addTupleProvider(
        DispColorTable.tupleName(), lookupTupleProvider
    )
    tupleObservable.addTupleProvider(
        DispLineStyleTable.tupleName(), lookupTupleProvider
    )
    tupleObservable.addTupleProvider(
        DispTextStyleTable.tupleName(), lookupTupleProvider
    )

    tupleObservable.addTupleProvider(
        BranchLiveEditTuple.tupleName(),
        BranchLiveEditTupleProvider(branchLiveEditController),
    )

    return tupleObservable
