import { DispBasePartial, DispBaseT } from "../canvas-shapes/DispBasePartial";

/** Sort Disps
 *
 * This method sorts disps in the order needed for the model to compile them for the
 * renderer.
 *
 * This method was initially written for the BranchTuple.
 *
 * WARNING: Sorting disps is terrible for performance, this is only used while
 * the branch is being edited by the user.
 *
 * @param disps: A List of disps to sort
 * @returns: A list of sorted disps
 */
export function sortDisps(disps: DispBaseT[]): DispBaseT[] {
    return disps.sort((a, b) => {
        const aLevel = DispBasePartial.level(a);
        const bLevel = DispBasePartial.level(b);

        const aLevelOrderIsNull = aLevel.order == null;
        const bLevelOrderIsNull = bLevel.order == null;

        if (aLevelOrderIsNull && bLevelOrderIsNull) {
            return 0;
        }
        if (aLevelOrderIsNull) {
            return -1;
        }
        if (bLevelOrderIsNull) {
            return 1;
        }

        // Level first - by order, then by id
        if (aLevel.order !== bLevel.order) {
            return aLevel.order - bLevel.order;
        }
        if (aLevel.id !== bLevel.id) {
            return aLevel.id - bLevel.id;
        }

        const aLayer = DispBasePartial.layer(a);
        const bLayer = DispBasePartial.layer(b);

        // Then layer - by order, then by id
        if (aLayer.order !== bLayer.order) {
            return aLayer.order - bLayer.order;
        }
        if (aLayer.id !== bLayer.id) {
            return aLayer.id - bLayer.id;
        }

        // Then zOrder
        if (DispBasePartial.zOrder(a) !== DispBasePartial.zOrder(b)) {
            return DispBasePartial.zOrder(a) - DispBasePartial.zOrder(b);
        }

        // Finally type as tie-breaker
        return DispBasePartial.typeOf(a) - DispBasePartial.typeOf(b);
    });
}
