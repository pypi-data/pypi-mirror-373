import { DiagramOverrideBase } from "@peek/peek_plugin_diagram/override/DiagramOverrideBase";

/**
 * Peek Canvas Model
 *
 * This class stores and manages the model of the NodeCoord and ConnCoord
 * objects that are within the viewable area.
 *
 */
export abstract class PeekCanvasModelOverrideA {
    protected constructor() {}

    // ------------------------------------------------------------------------
    // reset

    // ------------------------------------------------------------------------
    abstract setOverrides(overrides: DiagramOverrideBase[]): void;

    // ------------------------------------------------------------------------
    //
    // ------------------------------------------------------------------------

    // ------------------------------------------------------------------------
    compile(disps: any[]): void {}

    draw(ctx, zoom: number): void {}
}
