from typing import List
from typing import Union

from peek_plugin_diagram._private.storage.Lookups import DispColorTable
from peek_plugin_diagram._private.storage.Lookups import DispLineStyleTable
from peek_plugin_diagram.worker.canvas_shapes.ShapeBase import Point
from peek_plugin_diagram.worker.canvas_shapes.ShapeBase import ShapeBase


class ShapePoly(ShapeBase):
    @staticmethod
    def lineColor(disp) -> DispColorTable:
        return disp["lcl"]

    @staticmethod
    def lineStyle(disp) -> DispLineStyleTable:
        return disp["lsl"]

    @staticmethod
    def lineWidth(disp) -> float:
        return disp["w"]

    @staticmethod
    def geom(disp) -> List[float]:
        return disp["g"]

    @staticmethod
    def pointCount(disp) -> int:
        return int(len(ShapePoly.geom(disp)) / 2)

    @staticmethod
    def lastPoint(disp) -> Union[Point, None]:
        pointCount = len(ShapePoly.geom(disp))
        if pointCount == 0:
            return None

        return Point(x=disp["g"][pointCount - 1], y=disp["g"][pointCount - 2])
