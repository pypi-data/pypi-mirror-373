import { PrivateDiagramLookupService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramLookupService";
import {
    DiagramOverrideBase,
    DiagramOverrideTypeE,
} from "@peek/peek_plugin_diagram/override/DiagramOverrideBase";
import { DiagramOverrideColor } from "@peek/peek_plugin_diagram/override/DiagramOverrideColor";
import { DispBase } from "../canvas-shapes/DispBase";
import { DispFactory } from "../canvas-shapes/DispFactory";
import { PeekCanvasModelOverrideA } from "./PeekCanvasModelOverrideA";
import { PeekCanvasConfig } from "../canvas/PeekCanvasConfig.web";

/**
 * Peek Canvas Model
 *
 * This class stores and manages the model of the NodeCoord and ConnCoord
 * objects that are within the viewable area.
 *
 */
export class PeekCanvasModelOverrideColor extends PeekCanvasModelOverrideA {
    private overridesByDispKey: { [key: string]: DiagramOverrideColor[] } = {};

    constructor(
        private config: PeekCanvasConfig,
        private lookupCache: PrivateDiagramLookupService,
    ) {
        super();
    }

    // ------------------------------------------------------------------------
    setOverrides(overrides: DiagramOverrideBase[]): void {
        this.overridesByDispKey = {};
        for (const overrideBase of overrides) {
            if (overrideBase.overrideType !== DiagramOverrideTypeE.Color)
                continue;

            const colorOverride: DiagramOverrideColor = <any>overrideBase;
            for (const key of colorOverride.dispKeys) {
                this.getArrayForKey(key).push(colorOverride);
            }
        }
    }

    // ------------------------------------------------------------------------
    override compile(disps: any[]): void {
        for (const disp of disps) {
            const dispKey = DispBase.key(disp);
            if (dispKey == null) continue;

            const array = this.getArrayForKey(dispKey, false);
            if (array == null) continue;

            for (const override of array)
                this.applyColorOverride(disp, override);
        }
    }

    private getArrayForKey(key: string, create: boolean = true): any[] {
        let array = this.overridesByDispKey[key];
        if (array == null && create) {
            array = [];
            this.overridesByDispKey[key] = array;
        }
        return array;
    }

    private applyColorOverride(disp, colorOverride: DiagramOverrideColor) {
        const Wrapper = DispFactory.wrapper(disp);
        if (colorOverride.lineColor != null && Wrapper.setLineColor != null)
            Wrapper.setLineColor(disp, colorOverride.lineColor);

        if (colorOverride.fillColor != null && Wrapper.setFillColor != null)
            Wrapper.setFillColor(disp, colorOverride.fillColor);

        if (colorOverride.color != null && Wrapper.setColor != null)
            Wrapper.setColor(disp, colorOverride.color);
    }
}
