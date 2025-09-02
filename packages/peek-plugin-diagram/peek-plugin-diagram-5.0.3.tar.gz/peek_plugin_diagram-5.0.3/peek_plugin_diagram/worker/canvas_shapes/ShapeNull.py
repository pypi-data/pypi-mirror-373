from typing import List

from peek_plugin_diagram.worker.canvas_shapes.ShapeBase import Point
from peek_plugin_diagram.worker.canvas_shapes.ShapeBase import ShapeBase


class ShapeNull(ShapeBase):
    @staticmethod
    def geom(disp) -> List[float]:
        return disp["g"]

    @staticmethod
    def centerPointX(disp) -> float:
        return disp["g"][0]

    @staticmethod
    def centerPointY(disp) -> float:
        return disp["g"][1]

    @staticmethod
    def center(disp) -> Point:
        return Point(
            x=ShapeNull.centerPointX(disp), y=ShapeNull.centerPointY(disp)
        )
