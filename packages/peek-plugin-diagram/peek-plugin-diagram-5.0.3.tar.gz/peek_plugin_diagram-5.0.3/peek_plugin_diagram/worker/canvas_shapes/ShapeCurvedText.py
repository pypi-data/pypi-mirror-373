from typing import Union

from peek_plugin_diagram._private.storage.Lookups import DispColorTable
from peek_plugin_diagram._private.storage.Lookups import DispTextStyleTable
from peek_plugin_diagram.worker.canvas_shapes.ShapeBase import ShapeBase
from peek_plugin_diagram.worker.canvas_shapes.ShapeBase import Point
from peek_plugin_diagram.worker.canvas_shapes.ShapeText import ShapeText
from peek_plugin_diagram.worker.canvas_shapes.ShapeText import (
    TextHorizontalAlign,
)
from peek_plugin_diagram.worker.canvas_shapes.ShapeText import TextVerticalAlign


class ShapeCurvedText(ShapeBase):
    @staticmethod
    def textStyle(disp) -> DispTextStyleTable:
        return disp.get("fsl", DispTextStyleTable())

    @staticmethod
    def borderColor(disp) -> DispColorTable:
        return disp.get("bcl", DispColorTable())

    @staticmethod
    def color(disp) -> DispColorTable:
        return disp.get("cl", DispColorTable())

    @staticmethod
    def text(disp) -> str:
        return disp.get("te", "")

    @staticmethod
    def spacingBetweenTexts(disp) -> float:
        return disp.get("sbt")

    @staticmethod
    def geom(disp):
        return disp.get("g")
