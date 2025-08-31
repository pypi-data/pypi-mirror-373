from vortex.handler.TupleDataObservableProxyHandler import (
    TupleDataObservableProxyHandler,
)

from peek_plugin_diagram._private.client.controller.BranchIndexCacheController import (
    BranchIndexCacheController,
)
from peek_plugin_diagram._private.client.controller.CoordSetCacheController import (
    CoordSetCacheController,
)
from peek_plugin_diagram._private.client.controller.GridCacheController import (
    GridCacheController,
)
from peek_plugin_diagram._private.client.controller.LocationIndexCacheController import (
    LocationIndexCacheController,
)
from peek_plugin_diagram._private.client.controller.LookupCacheController import (
    LookupCacheController,
)
from peek_plugin_diagram._private.client.controller.ModelSetCacheController import (
    ModelSetCacheController,
)
from peek_plugin_diagram._private.client.tuple_providers.BranchIndexUpdateDateTupleProvider import (
    BranchIndexUpdateDateTupleProvider,
)
from peek_plugin_diagram._private.client.tuple_providers.BranchTupleProvider import (
    BranchTupleProvider,
)
from peek_plugin_diagram._private.client.tuple_providers.ClientCoordSetTupleProvider import (
    ClientCoordSetTupleProvider,
)
from peek_plugin_diagram._private.client.tuple_providers.ClientDispKeyLocationTupleProvider import (
    ClientDispKeyLocationTupleProvider,
)
from peek_plugin_diagram._private.client.tuple_providers.ClientGroupDispsTupleProvider import (
    ClientGroupDispsTupleProvider,
)
from peek_plugin_diagram._private.client.tuple_providers.ClientLocationIndexUpdateDateTupleProvider import (
    ClientLocationIndexUpdateDateTupleProvider,
)
from peek_plugin_diagram._private.client.tuple_providers.ClientLookupTupleProvider import (
    ClientLookupTupleProvider,
)
from peek_plugin_diagram._private.client.tuple_providers.ClientModelSetTupleProvider import (
    ClientModelSetTupleProvider,
)
from peek_plugin_diagram._private.client.tuple_providers.GridCacheIndexTupleProvider import (
    GridCacheIndexTupleProvider,
)
from peek_plugin_diagram._private.storage.Lookups import DispColorTable
from peek_plugin_diagram._private.storage.Lookups import DispLayerTable
from peek_plugin_diagram._private.storage.Lookups import DispLevelTable
from peek_plugin_diagram._private.storage.Lookups import DispLineStyleTable
from peek_plugin_diagram._private.storage.Lookups import DispTextStyleTable
from peek_plugin_diagram._private.storage.ModelSet import ModelCoordSetTable
from peek_plugin_diagram._private.storage.ModelSet import ModelSetTable
from peek_plugin_diagram._private.tuples.GroupDispsTuple import GroupDispsTuple
from peek_plugin_diagram._private.tuples.branch.BranchIndexUpdateDateTuple import (
    BranchIndexUpdateDateTuple,
)
from peek_plugin_diagram._private.tuples.branch.BranchTuple import BranchTuple
from peek_plugin_diagram._private.tuples.grid.GridUpdateDateTuple import (
    GridUpdateDateTuple,
)
from peek_plugin_diagram._private.tuples.location_index.DispKeyLocationTuple import (
    DispKeyLocationTuple,
)
from peek_plugin_diagram._private.tuples.location_index.LocationIndexUpdateDateTuple import (
    LocationIndexUpdateDateTuple,
)


def makeClientTupleDataObservableHandler(
    tupleObservable: TupleDataObservableProxyHandler,
    modelSetCacheController: ModelSetCacheController,
    coordSetCacheController: CoordSetCacheController,
    gridCacheController: GridCacheController,
    lookupCacheController: LookupCacheController,
    locationCacheController: LocationIndexCacheController,
    branchCacheController: BranchIndexCacheController,
):
    """ " Make CLIENT Tuple Data Observable Handler

    This method creates the observable object, registers the tuple providers and then
    returns it.

    :param branchCacheController:
    :param modelSetCacheController:
    :param locationCacheController:
    :param tupleObservable: The tuple observable proxy
    :param coordSetCacheController: The clients coord set cache controller
    :param gridCacheController: The cache controller for the grid
    :param lookupCacheController: The clients lookup cache controller
    :return: An instance of :code:`TupleDataObservableHandler`

    """
    # Register TupleProviders here
    lookupTupleProvider = ClientLookupTupleProvider(lookupCacheController)

    # Add the lookup providers
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

    # Add the CoordSet providers

    tupleObservable.addTupleProvider(
        ModelSetTable.tupleName(),
        ClientModelSetTupleProvider(modelSetCacheController),
    )

    tupleObservable.addTupleProvider(
        ModelCoordSetTable.tupleName(),
        ClientCoordSetTupleProvider(coordSetCacheController),
    )

    tupleObservable.addTupleProvider(
        GridUpdateDateTuple.tupleName(),
        GridCacheIndexTupleProvider(gridCacheController),
    )

    tupleObservable.addTupleProvider(
        DispKeyLocationTuple.tupleName(),
        ClientDispKeyLocationTupleProvider(
            locationCacheController, coordSetCacheController
        ),
    )

    tupleObservable.addTupleProvider(
        LocationIndexUpdateDateTuple.tupleName(),
        ClientLocationIndexUpdateDateTupleProvider(locationCacheController),
    )

    tupleObservable.addTupleProvider(
        BranchTuple.tupleName(), BranchTupleProvider(branchCacheController)
    )

    tupleObservable.addTupleProvider(
        BranchIndexUpdateDateTuple.tupleName(),
        BranchIndexUpdateDateTupleProvider(branchCacheController),
    )

    tupleObservable.addTupleProvider(
        GroupDispsTuple.tupleName(),
        ClientGroupDispsTupleProvider(gridCacheController),
    )

    return tupleObservable
