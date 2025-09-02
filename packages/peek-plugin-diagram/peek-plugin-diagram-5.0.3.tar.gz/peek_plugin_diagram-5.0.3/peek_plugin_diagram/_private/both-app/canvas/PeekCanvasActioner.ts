import { PrivateDiagramLookupService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramLookupService";
import { PrivateDiagramCoordSetService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramCoordSetService";
import { PrivateDiagramPositionService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramPositionService";
import {
    DispActionEnum,
    DispActionPositionOnDataT,
    DispBase,
    DispBaseT,
} from "../canvas-shapes/DispBase";
import { assert } from "../DiagramUtil";

/**
 * Peek Canvas Actioner
 *
 * This class is contains the logic for applying the actions from
 * the DispBase.action(disp)
 *
 */
export class PeekCanvasActioner {
    constructor(
        private modelSetKey: string,
        private coordSetCache: PrivateDiagramCoordSetService,
        private lookupService: PrivateDiagramLookupService,
        private positionService: PrivateDiagramPositionService,
    ) {}

    hasAction(disp: DispBaseT): boolean {
        return (
            DispBase.action(disp) != null &&
            DispBase.action(disp) != DispActionEnum.none
        );
    }

    applyAction(disp: DispBaseT): void {
        assert(this.hasAction(disp), "Disp has no action to perform.");

        const action = DispBase.action(disp);
        const data = DispBase.data(disp);

        switch (action) {
            case DispActionEnum.none:
                break;

            case DispActionEnum.positionOn: {
                const posData: DispActionPositionOnDataT | null =
                    data["actionPos"];
                if (posData == null) {
                    console.log(
                        "actionPos data is missing for position on action",
                    );
                    break;
                }

                const coordSet = this.coordSetCache.coordSetForKey(
                    this.modelSetKey,
                    posData.k,
                );

                if (coordSet == null) {
                    console.log(
                        `Can not find coordSet with key=|${posData.k}|`,
                    );
                }

                this.positionService.position(
                    coordSet.key,
                    posData.x,
                    posData.y,
                    posData.z,
                );
                break;
            }
        }
    }
}
