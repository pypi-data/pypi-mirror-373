from typing import Dict
from typing import List
from typing import Union

from peek_plugin_diagram.worker.canvas_shapes.ShapeBase import Point
from peek_plugin_diagram.worker.canvas_shapes.ShapeBase import ShapeBase


class ShapeGroupPoint(ShapeBase):
    @staticmethod
    def targetGroupId(disp) -> int:
        return disp["tg"]

    @staticmethod
    def targetGroupCoordSetId(disp) -> Union[int, None]:
        if disp["tn"] is None or "|" not in disp["tn"]:
            return None

        number, _, _ = disp["tn"].partition("|")
        return int(number)

    @staticmethod
    def targetGroupName(disp) -> Union[str, None]:
        if disp["tn"] is None or "|" not in disp["tn"]:
            return None

        _, _, groupName = disp["tn"].partition("|")
        return groupName

    @staticmethod
    def verticalScale(disp) -> float:
        return disp["vs"]

    @staticmethod
    def horizontalScale(disp) -> float:
        return disp["hs"]

    @staticmethod
    def rotation(disp) -> float:
        if disp["r"] is None:
            return 0
        return disp["r"]

    @staticmethod
    def center(disp) -> Point:
        return Point(x=disp["g"][0], y=disp["g"][1])

    @staticmethod
    def geom(disp) -> List[float]:
        return disp["g"]

    @staticmethod
    def disps(disp) -> List[Dict]:
        return disp["disps"]
