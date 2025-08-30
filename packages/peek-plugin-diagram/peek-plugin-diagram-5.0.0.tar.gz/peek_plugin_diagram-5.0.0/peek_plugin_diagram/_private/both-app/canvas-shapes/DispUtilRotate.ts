import { DispHandleI, DispHandleTypeE, PointI } from "./DispBase";
import {
    calculateRotationAfterPointMove,
    movePointFurtherFromPoint,
    rotatePointAboutCenter,
} from "./DispUtil";

export function makeRotateHandlePoints(
    disp,
    margin: number,
    center: PointI,
    rotation: number,
): DispHandleI[] {
    const bounds = disp.bounds;
    if (bounds == null) {
        console.log("No bounds, exiting");
        return [];
    }

    if (disp.tempRotation == null) disp.tempRotation = rotation;

    const cp = center;
    const maxRadius = Math.max.apply(Math, [
        Math.hypot(bounds.x + bounds.w - cp.x, cp.y - bounds.y),
        Math.hypot(cp.x - bounds.x, bounds.y + bounds.h - cp.y),
        Math.hypot(bounds.x + bounds.w - cp.x, cp.y - bounds.y),
        Math.hypot(cp.x - bounds.x, bounds.y + bounds.h - cp.y),
        margin,
    ]);

    return [
        {
            disp: disp,
            center: { x: cp.x, y: cp.y + maxRadius },
            handleType: DispHandleTypeE.freeRotate,
        },
        {
            disp: disp,
            center: { x: cp.x, y: cp.y - maxRadius },
            handleType: DispHandleTypeE.snapRotate,
        },
    ].map((handle: DispHandleI) => {
        if (disp.tempRotation != 0)
            handle.center = rotatePointAboutCenter(
                cp,
                handle.center,
                disp.tempRotation,
            );

        handle.center = movePointFurtherFromPoint(cp, handle.center, margin);
        return handle;
    });
}

/** Calculate Rotation from Handle Delta
 *
 * Calculate the rotation and work out the new delta.
 *
 * @param handle
 * @param dx
 * @param dy
 */
export function calculateRotationFromHandleDelta(
    handle: DispHandleI,
    dx: number,
    dy: number,
    currentRotation: number,
    tempRotation: number,
    center: PointI,
): { newRotation: number; deltaRotation: number; tempRotation: number } {
    if (
        handle.handleType != DispHandleTypeE.freeRotate &&
        handle.handleType != DispHandleTypeE.snapRotate
    ) {
        console.log(
            "ERROR: DispGroup only has rotate handles, " +
                `${handle.handleIndex} passed`,
        );
        return null;
    }

    // Set the center if required
    if (handle.lastDeltaPoint == null) {
        const startPoint: PointI = handle.center;
        handle.lastDeltaPoint = {
            x: startPoint.x,
            y: startPoint.y,
        };
    }

    const nextPoint = {
        x: handle.lastDeltaPoint.x + dx,
        y: handle.lastDeltaPoint.y + dy,
    };

    let rotationDegreesDelta = calculateRotationAfterPointMove(
        center,
        handle.lastDeltaPoint,
        nextPoint,
    );

    handle.lastDeltaPoint = nextPoint;

    // Calculate the center rotation
    let newRotation = (tempRotation + rotationDegreesDelta) % 360;
    tempRotation = newRotation;

    // Snap the new rotation for the symbol
    if (handle.handleType == DispHandleTypeE.snapRotate) {
        // Work out the snapped rotation
        newRotation += newRotation < 0 ? -20 : 20; // Add an offset to help snapping
        newRotation = newRotation - (newRotation % 45);
    }

    // Work out how far we need to rotate the disps
    rotationDegreesDelta = newRotation - currentRotation;

    return {
        newRotation: newRotation,
        deltaRotation: rotationDegreesDelta,
        tempRotation: tempRotation,
    };
}
