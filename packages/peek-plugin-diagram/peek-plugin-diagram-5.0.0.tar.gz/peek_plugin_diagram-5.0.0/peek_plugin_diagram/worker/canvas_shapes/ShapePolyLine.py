from typing import Union

from peek_plugin_diagram._private.storage.Lookups import DispColorTable
from peek_plugin_diagram.worker.canvas_shapes.ShapeBase import Point
from peek_plugin_diagram.worker.canvas_shapes.ShapeBase import ShapeBase


class DispPolylineEndTypeEnum:
    None_ = 0
    Arrow = 1
    Dot = 2


class ShapePolyLine(ShapeBase):
    @staticmethod
    def targetGroupId(disp) -> int:
        return disp.get("ti")

    @staticmethod
    def targetEdgeTemplateCoordSetId(disp) -> Union[int, None]:
        if disp.get("tn") is None or "|" not in disp.get("tn"):
            return None

        id_, _, _ = disp.partition("|")
        return id_

    @staticmethod
    def targetEdgeTemplateName(disp) -> Union[str, None]:
        if disp.get("tn") is None or "|" not in disp.get("tn"):
            return None

        _, _, name = disp.partition("|")
        return name

    @staticmethod
    def edgeColor(disp) -> DispColorTable:
        return disp.get("ecl")
        
    @staticmethod
    def borderWidth(disp) -> Union[int, None]:
        return disp.get("bw")
    
    @staticmethod
    def borderColor(disp) -> DispColorTable:
        return disp.get("bcl")

    @staticmethod
    def startKey(disp) -> Union[str, None]:
        return disp.get("sk")

    @staticmethod
    def startEndType(disp) -> int:
        return disp.get("st") if disp.get("st") else 0

    @staticmethod
    def endEndType(disp) -> int:
        return disp.get("et") if disp.get("et") else 0

    @staticmethod
    def center(disp) -> Point:
        # TODO
        raise NotImplementedError

    @staticmethod
    def firstPoint(disp) -> Point:
        return Point(x=disp.get("g")[0], y=disp.get("g")[1])

    @staticmethod
    def lastPoint(disp) -> Point:
        length = len(disp.get("g"))
        return Point(x=disp.get("g")[length - 2], y=disp.get("g")[length - 1])

    @staticmethod
    def contains(disp, point: Point, margin: float):
        # TODO
        raise NotImplementedError
