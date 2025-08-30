import {
    DiagramOverrideBase,
    DiagramOverrideTypeE,
} from "./DiagramOverrideBase";
import { addTupleType } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "../_private/PluginNames";
import { ShapeColorTuple } from "@peek/peek_plugin_diagram/lookup_tuples";

/** Diagram Delta Color Override Tuple
 *
 * This delta applies an override colour to a set of display keys
 *
 */
@addTupleType
export class DiagramOverrideHighlight extends DiagramOverrideBase {
    public static readonly tupleName =
        diagramTuplePrefix + "DiagramOverrideHighlight";

    private dispKeys_: string[] = [];
    private color_: ShapeColorTuple | null = null;

    constructor(modelSetKey: string, coordSetKey: string) {
        super(
            modelSetKey,
            coordSetKey,
            DiagramOverrideTypeE.Highlight,
            DiagramOverrideHighlight.tupleName,
        );
    }

    // Disp Keys
    addDispKeys(dispKeys: string[]): void {
        this.dispKeys_.add(dispKeys);
    }

    get dispKeys(): string[] {
        return this.dispKeys_;
    }

    // Color
    get color(): ShapeColorTuple {
        return this.color_;
    }

    set color(value: ShapeColorTuple | null) {
        this.color_ = value;
    }
}
