from typing import Union

from peek_plugin_diagram.tuples.lookup_tuples.ShapeColorTuple import (
    ShapeColorTuple,
)
from peek_plugin_diagram.tuples.lookup_tuples.ShapeTextStyleTuple import (
    ShapeTextStyleTuple,
)
from peek_plugin_diagram.worker.canvas_shapes.ShapeBase import ShapeBase
from peek_plugin_diagram.worker.canvas_shapes.ShapeBase import Point


class TextVerticalAlign:
    top = -1
    center = 0
    bottom = 1


class TextHorizontalAlign:
    left = -1
    center = 0
    right = 1


class ShapeText(ShapeBase):
    @staticmethod
    def textStyle(disp) -> "ShapeTextStyleTuple":
        return disp.get("fsl", ShapeTextStyleTuple())

    @staticmethod
    def borderColor(disp) -> "ShapeColorTuple":
        return disp.get("bcl", ShapeColorTuple())

    @staticmethod
    def color(disp) -> "ShapeColorTuple":
        return disp.get("cl", ShapeColorTuple())

    @staticmethod
    def verticalAlign(disp) -> int:
        val = disp.get("va")

        if val == TextVerticalAlign.top:
            return TextVerticalAlign.top

        if val == TextVerticalAlign.bottom:
            return TextVerticalAlign.bottom

        return TextVerticalAlign.center

    @staticmethod
    def horizontalAlign(disp) -> int:
        val = disp.get("ha")

        if val == TextHorizontalAlign.left:
            return TextHorizontalAlign.left

        if val == TextHorizontalAlign.right:
            return TextHorizontalAlign.right

        return TextHorizontalAlign.center

    @staticmethod
    def rotation(disp) -> int:
        return disp.get("r")

    @staticmethod
    def text(disp) -> str:
        return disp.get("te", "")

    @staticmethod
    def height(disp) -> Union[int, None]:
        return disp.get("th", None)

    @staticmethod
    def horizontalStretch(disp) -> float:
        return disp.get("hs")

    @staticmethod
    def centerPointX(disp) -> float:
        return disp["g"][0]

    @staticmethod
    def centerPointY(disp) -> float:
        return disp["g"][1]

    @staticmethod
    def center(disp) -> Point:
        return Point(
            x=ShapeText.centerPointX(disp), y=ShapeText.centerPointY(disp)
        )
