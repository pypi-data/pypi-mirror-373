import { assert } from "../DiagramUtil";
import { GridTuple } from "@peek/peek_plugin_diagram/_private/grid-loader/GridTuple";
import { PrivateDiagramLookupService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramLookupService";
import { DispBase, DispType } from "../canvas-shapes/DispBase";

/** Linked Grid
 *
 * This class represents a constructed grid of data, ready for use by a canvas model
 *
 */
export class LinkedGrid {
    gridKey = null;
    lastUpdate = null;
    loadedFromServerDate = new Date();
    disps = [];

    constructor(
        serverCompiledGridOrGridKey: string | GridTuple,
        lookupService: PrivateDiagramLookupService | null = null,
    ) {
        // initialise for empty grid keys
        if (typeof serverCompiledGridOrGridKey === "string") {
            this.gridKey = serverCompiledGridOrGridKey;
            return;
        }

        let serverCompiledGrid = <GridTuple>serverCompiledGridOrGridKey;
        assert(lookupService != null, "lookupStore can not be null");

        this.gridKey = serverCompiledGrid.gridKey;
        this.lastUpdate = serverCompiledGrid.lastUpdate;
        this.loadedFromServerDate = new Date();

        // Reconstruct the disps
        this.disps = [];
        let disps = [];

        if (
            serverCompiledGrid.dispJsonStr != null &&
            serverCompiledGrid.dispJsonStr.length != 0
        ) {
            try {
                disps = JSON.parse(serverCompiledGrid.dispJsonStr);
            } catch (e) {
                console.error(e.toString());
            }
        }

        // Resolve the lookups
        for (let j = 0; j < disps.length; j++) {
            let disp = disps[j];
            if (disp.id == null) {
                // This mitigates an old condition caused by the grid compiler
                // including dips that had not yet had json assigned.
                continue;
            }
            if (lookupService._linkDispLookups(disp) != null) {
                this.disps.push(disp);
            }
        }
    }

    hasData() {
        return !(this.lastUpdate == null && this.disps.length == 0);
    }

    relinkLookups(lookupService: PrivateDiagramLookupService): void {
        for (const disp of this.disps) lookupService._linkDispLookups(disp);
    }

    resetComputedProperties(): void {
        for (const disp of this.disps) {
            delete disp.bounds;
            delete disp.dispGroup;
            delete disp.disps;
        }
    }
}
