from typing import Optional

from peek_plugin_diagram._private.storage.Lookups import DispColorTable
from peek_plugin_diagram._private.storage.Lookups import DispLineStyleTable
from peek_plugin_diagram.worker.canvas_shapes.ShapeBase import Point
from peek_plugin_diagram.worker.canvas_shapes.ShapeBase import ShapeBase


class PolygonFillDirectionEnum:
    fillBottomToTop = 0
    fillBottomToTop = 1
    fillRightToLeft = 2
    fillLeftToRight = 3


class ShapePolygon(ShapeBase):
    FILL_TOP_TO_BOTTOM = 0
    FILL_BOTTOM_TO_TOP = 1
    FILL_RIGHT_TO_LEFT = 2
    FILL_LEFT_TO_RIGHT = 3

    @staticmethod
    def fillColor(disp) -> DispColorTable:
        return disp.get("fcl")

    @staticmethod
    def lineColor(disp) -> DispColorTable:
        return disp.get("lcl")

    @staticmethod
    def lineStyle(disp) -> DispLineStyleTable:
        return disp.get("lsl")

    @staticmethod
    def lineWidth(disp) -> DispLineStyleTable:
        return disp.get("w")

    @staticmethod
    def cornerRadius(disp) -> float:
        return disp.get("cr")

    @staticmethod
    def fillDirection(disp) -> int:
        fillDirection = disp.get("fd")
        if fillDirection in (
            ShapePolygon.FILL_BOTTOM_TO_TOP,
            ShapePolygon.FILL_RIGHT_TO_LEFT,
            ShapePolygon.FILL_LEFT_TO_RIGHT,
        ):
            return fillDirection

        # Else, default to Top to Bottom
        return ShapePolygon.FILL_TOP_TO_BOTTOM

    @staticmethod
    def fillPercent(disp) -> Optional[float]:
        fillPercentage = float(disp.get("fp")) if disp.get("fp") else None

        if fillPercentage is None:
            return None

        return max(0.0, min(100.0, fillPercentage))

    @staticmethod
    def isRectangle(disp) -> bool:
        return bool(disp.get("r"))

    @staticmethod
    def center(disp) -> Point:
        # TODO
        raise NotImplementedError

    @staticmethod
    def contains(disp, point: Point, margin: float) -> bool:
        raise NotImplementedError

    @staticmethod
    def geom(disp):
        return disp.get("g")
