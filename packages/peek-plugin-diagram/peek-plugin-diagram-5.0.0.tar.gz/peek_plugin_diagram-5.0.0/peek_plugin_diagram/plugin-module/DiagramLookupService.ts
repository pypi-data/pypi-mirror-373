import { Observable } from "rxjs";
import {
    ShapeColorTuple,
    ShapeLayerTuple,
    ShapeLevelTuple,
} from "@peek/peek_plugin_diagram/lookup_tuples";
import { Injectable } from "@angular/core";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { PrivateDiagramLookupService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramLookupService";
import { PrivateDiagramCoordSetService } from "@peek/peek_plugin_diagram/_private/services";

/** Lookup Cache
 *
 * This class provides handy access to the lookup objects
 *
 * Typically there will be only a few hundred of these.
 *
 */
@Injectable()
export class DiagramLookupService extends NgLifeCycleEvents {
    constructor(
        private privateService: PrivateDiagramLookupService,
        private coordSetService: PrivateDiagramCoordSetService,
    ) {
        super();
    }

    isReady(): boolean {
        return this.privateService.isReady();
    }

    isReadyObservable(): Observable<boolean> {
        return this.privateService.isReadyObservable();
    }

    // ============================================================================
    // Accessors

    levels(modelSetKey: string, coordSetKey: string): ShapeLevelTuple[] {
        const coordSet = this.coordSetService.coordSetForKey(
            modelSetKey,
            coordSetKey,
        );
        return this.privateService
            .levelsOrderedByOrder(coordSet.id)
            .map((t) => t.toTuple());
    }

    layers(modelSetKey: string): ShapeLayerTuple[] {
        return this.privateService
            .layersOrderedByOrder(modelSetKey)
            .map((t) => t.toTuple());
    }

    /** Color for Name
     *
     * Returns a DispColor if there is one where .color == name
     * @param modelSetKey
     * @param name
     */
    colorForName(modelSetKey: string, name: string): ShapeColorTuple | null {
        return this.privateService.colorForName(modelSetKey, name)?.toTuple();
    }

    colorsOrderedByName(modelSetKey: string): ShapeColorTuple[] {
        return this.privateService
            .colorsOrderedByName(modelSetKey)
            .map((t) => t.toTuple());
    }
}
