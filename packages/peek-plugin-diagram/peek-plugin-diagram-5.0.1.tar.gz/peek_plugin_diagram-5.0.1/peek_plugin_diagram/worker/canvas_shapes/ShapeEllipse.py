from peek_plugin_diagram._private.storage.Lookups import DispColorTable
from peek_plugin_diagram._private.storage.Lookups import DispLineStyleTable
from peek_plugin_diagram.worker.canvas_shapes.ShapeBase import Point
from peek_plugin_diagram.worker.canvas_shapes.ShapeBase import ShapeBase
from typing import Optional


class ShapeEllipse(ShapeBase):
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
    def lineWidth(disp) -> Optional[float]:
        return float(disp.get("w")) if disp.get("w") else None

    @staticmethod
    def centerPointX(disp) -> float:
        return disp.get("g")[0]

    @staticmethod
    def centerPointY(disp) -> float:
        return disp.get("g")[1]

    @staticmethod
    def center(disp) -> Point:
        return Point(
            x=ShapeEllipse.centerPointX(disp), y=ShapeEllipse.centerPointY(disp)
        )

    @staticmethod
    def xRadius(disp) -> float:
        return disp.get("xr")

    @staticmethod
    def yRadius(disp) -> float:
        return disp.get("yr")

    @staticmethod
    def rotation(disp) -> float:
        return disp.get("r")

    @staticmethod
    def startAngle(disp) -> float:
        """

        :param disp: a dict
        :return: startAngle in degrees
        """
        return disp.get("sa")

    @staticmethod
    def endAngle(disp) -> float:
        """

        :param disp: a dict
        :return:  endAngle in degrees
        """
        return disp.get("ea")
