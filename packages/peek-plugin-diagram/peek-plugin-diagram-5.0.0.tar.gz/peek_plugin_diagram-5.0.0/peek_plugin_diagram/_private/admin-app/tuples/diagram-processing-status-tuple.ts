import { addTupleType, Tuple } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "@peek/peek_plugin_diagram/_private/PluginNames";

@addTupleType
export class DiagramProcessingStatusTuple extends Tuple {
    public static readonly tupleName =
        diagramTuplePrefix + "DiagramProcessingStatusTuple";

    displayCompilerQueueStatus: boolean;
    displayCompilerQueueSize: number;
    displayCompilerProcessedTotal: number;
    displayCompilerLastError: string;

    gridCompilerQueueStatus: boolean;
    gridCompilerQueueSize: number;
    gridCompilerProcessedTotal: number;
    gridCompilerLastError: string;

    locationIndexCompilerQueueStatus: boolean;
    locationIndexCompilerQueueSize: number;
    locationIndexCompilerProcessedTotal: number;
    locationIndexCompilerLastError: string;

    branchIndexCompilerQueueStatus: boolean;
    branchIndexCompilerQueueSize: number;
    branchIndexCompilerProcessedTotal: number;
    branchIndexCompilerLastError: string;

    constructor() {
        super(DiagramProcessingStatusTuple.tupleName);
    }
}
