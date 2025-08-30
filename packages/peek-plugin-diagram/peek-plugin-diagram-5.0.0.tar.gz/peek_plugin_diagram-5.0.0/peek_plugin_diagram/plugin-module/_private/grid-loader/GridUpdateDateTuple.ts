import { addTupleType, Tuple } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "../PluginNames";

// ----------------------------------------------------------------------------
/** Grid Cache Index
 *
 * The index is probably a terrible name.
 *
 * This tuple stores the updateDate for all grids cached in the database.
 *
 */
@addTupleType
export class GridUpdateDateTuple extends Tuple {
    public static readonly tupleName =
        diagramTuplePrefix + "GridUpdateDateTuple";
    initialLoadComplete: boolean = false;
    // initialLoadComplete: boolean = false;
    updateDateByChunkKey: { [gridKey: string]: string } = {};
    // Improve performance of the JSON serialisation
    protected override _rawJonableFields = [
        "initialLoadComplete",
        "updateDateByChunkKey",
    ];

    constructor() {
        super(GridUpdateDateTuple.tupleName);
    }
}
