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
export class DiagramOverrideColor extends DiagramOverrideBase {
    public static readonly tupleName =
        diagramTuplePrefix + "DiagramOverrideColor";

    private dispKeys_: string[] = [];
    private lineColor_: ShapeColorTuple | null = null;
    private fillColor_: ShapeColorTuple | null = null;
    private color_: ShapeColorTuple | null = null;

    constructor(modelSetKey: string, coordSetKey: string) {
        super(
            modelSetKey,
            coordSetKey,
            DiagramOverrideTypeE.Color,
            DiagramOverrideColor.tupleName,
        );
    }

    get dispKeys(): string[] {
        return this.dispKeys_;
    }

    get lineColor(): ShapeColorTuple {
        return this.lineColor_;
    }

    get fillColor(): ShapeColorTuple {
        return this.fillColor_;
    }

    get color(): ShapeColorTuple {
        return this.color_;
    }

    addDispKeys(dispKeys: string[]): void {
        this.dispKeys_.add(dispKeys);
    }

    // Line Color
    setLineColor(value: ShapeColorTuple | null): void {
        this.lineColor_ = value;
    }

    // Fill Color
    setFillColor(value: ShapeColorTuple | null): void {
        this.fillColor_ = value;
    }

    // Color
    setColor(value: ShapeColorTuple | null): void {
        this.color_ = value;
    }
}
