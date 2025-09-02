import { PointI } from "./DispBase";

export function rotatePointAboutCenter(
    center: PointI,
    point: PointI,
    rotationDegrees: number,
): PointI {
    const rotationRadians = (rotationDegrees * Math.PI) / 180;
    const cos = Math.cos(rotationRadians);
    const sin = Math.sin(rotationRadians);

    const x = point.x - center.x;
    const y = point.y - center.y;

    return {
        x: cos * x - sin * y + center.x,
        y: sin * x + cos * y + center.y,
    };
}

export function calculateRotationAfterPointMove(
    center: PointI,
    startPoint: PointI,
    movedPoint: PointI,
): number {
    const beforeX = startPoint.x - center.x;
    const beforeY = startPoint.y - center.y;
    const afterX = movedPoint.x - center.x;
    const afterY = movedPoint.y - center.y;

    const beforeRadians = Math.atan2(beforeY, beforeX); // In radians
    const afterRadians = Math.atan2(afterY, afterX); // In radians

    return (afterRadians - beforeRadians) * (180 / Math.PI);
}

export function movePointFurtherFromPoint(
    refPoint: PointI,
    point: PointI,
    distance: number,
): PointI {
    const adj = point.x - refPoint.x;
    const opp = point.y - refPoint.y;
    const hypot = Math.sqrt(Math.pow(adj, 2) + Math.pow(opp, 2));

    const multiplier = distance / hypot;

    return { x: point.x + adj * multiplier, y: point.y + opp * multiplier };
}
