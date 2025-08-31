import { PrivateDiagramLookupService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramLookupService";
import {
    DiagramOverrideBase,
    DiagramOverrideTypeE,
} from "@peek/peek_plugin_diagram/override/DiagramOverrideBase";
import { DispBase, DispBaseT } from "../canvas-shapes/DispBase";
import { DispFactory } from "../canvas-shapes/DispFactory";
import { DiagramOverrideHighlight } from "@peek/peek_plugin_diagram/override/DiagramOverrideHighlight";
import { PeekCanvasModelOverrideA } from "./PeekCanvasModelOverrideA";
import { PeekCanvasConfig } from "../canvas/PeekCanvasConfig.web";
import { PeekCanvasBounds } from "@peek/peek_plugin_diagram/_private/PeekCanvasBounds";
import { DrawModeE } from "../canvas-render/PeekDispRenderDrawModeE.web";

interface DispOverrideI {
    disp: DispBaseT;
    override: DiagramOverrideHighlight;
}
/**
 * Peek Canvas Model
 *
 * This class stores and manages the model of the NodeCoord and ConnCoord
 * objects that are within the viewable area.
 *
 */
export class PeekCanvasModelOverrideHighlight extends PeekCanvasModelOverrideA {
    private overridesByDispKey: { [key: string]: DiagramOverrideHighlight[] } =
        {};

    private compiledDisps: DispOverrideI[] = [];

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
            if (overrideBase.overrideType !== DiagramOverrideTypeE.Highlight)
                continue;

            const override: DiagramOverrideHighlight = <any>overrideBase;
            for (const key of override.dispKeys) {
                this.getArrayForKey(key).push(override);
            }
        }
    }

    // ------------------------------------------------------------------------
    override compile(disps: any[]): void {
        this.compiledDisps = [];
        for (const disp of disps) {
            const dispKey = DispBase.key(disp);
            if (dispKey == null) continue;

            const array = this.getArrayForKey(dispKey, false);
            if (array == null) continue;

            for (const override of array) {
                this.compiledDisps.push({
                    disp: disp,
                    override: override,
                });
            }
        }
    }

    // ------------------------------------------------------------------------

    override draw(ctx, zoom: number): void {
        for (const pair of this.compiledDisps) {
            this.applyOverride(pair.disp, pair.override, ctx, zoom);
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

    private applyOverride(
        disp: DispBaseT,
        override: DiagramOverrideHighlight,
        ctx,
        zoom: number,
    ) {
        const Wrapper = DispFactory.wrapper(disp);
        // If this wrapper has no geom method, then ignore it.
        if (Wrapper.geom == null) return;

        // DRAW THE SELECTED BOX
        const geom = Wrapper.geom(disp);
        const bounds = PeekCanvasBounds.fromGeom(geom);

        const selectionConfig = this.config.getSelectionDrawDetailsForDrawMode(
            DrawModeE.ForView,
        );

        // Move the selection line a bit away from the object
        // Double it from the default selection
        const offset =
            (2 * (selectionConfig.width + selectionConfig.lineGap)) / zoom;

        const twiceOffset = 2 * offset;
        const x = bounds.x - offset;
        const y = bounds.y - offset;
        const w = bounds.w + twiceOffset;
        const h = bounds.h + twiceOffset;

        ctx.dashedRect(x, y, w, h, selectionConfig.dashLen / zoom);
        ctx.strokeStyle = override.color.getColor(this.config.isLightMode);
        ctx.lineWidth = selectionConfig.width / zoom;
        ctx.stroke();
    }
}
