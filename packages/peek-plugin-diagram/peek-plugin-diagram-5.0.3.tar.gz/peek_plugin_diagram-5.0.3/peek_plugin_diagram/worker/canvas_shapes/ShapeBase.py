import json
from collections import namedtuple
from typing import Union

from peek_plugin_diagram._private.storage.Lookups import DispLayerTable
from peek_plugin_diagram._private.storage.Lookups import DispLevelTable

Point = namedtuple("Point", ["x", "y"])


class ShapeType:
    ellipse = 0
    polygon = 1
    polyline = 2
    text = 3
    group = 4
    groupPointer = 5
    edgeTemplate = 6
    null_ = 7
    curvedText = 8


class ShapeActionEnum:
    none = 0  # Or null
    positionOn = 1


class ShapeBase:
    TYPE_DT = "DT"
    TYPE_DCT = "DCT"
    TYPE_DPG = "DPG"
    TYPE_DPL = "DPL"
    TYPE_DE = "DE"
    TYPE_DG = "DG"
    TYPE_DGP = "DGP"
    TYPE_DET = "DET"
    TYPE_DN = "DN"

    DEEP_COPY_FIELDS_TO_IGNORE = ["bounds", "disps", "dispGroup"]

    _typeMapInit = False
    _typeMap = {}

    @classmethod
    @property
    def typeMap(cls) -> dict:
        """
        Returns a dictionary mapping shape types to their corresponding
        ShapeType and name.

        This property uses lazy instantiation to initialize the type map only
        when it's first accessed.
        """
        if not cls._typeMapInit:
            cls._typeMapInit = True
            cls._typeMap[cls.TYPE_DT] = [ShapeType.text, "Text"]
            cls._typeMap[cls.TYPE_DCT] = [ShapeType.curvedText, "CurvedText"]
            cls._typeMap[cls.TYPE_DPG] = [ShapeType.polygon, "Polygon"]
            cls._typeMap[cls.TYPE_DPL] = [ShapeType.polyline, "Polyline"]
            cls._typeMap[cls.TYPE_DE] = [ShapeType.ellipse, "Ellipse"]
            cls._typeMap[cls.TYPE_DG] = [ShapeType.group, "Group"]
            cls._typeMap[cls.TYPE_DGP] = [
                ShapeType.groupPointer,
                "GroupPointer",
            ]
            cls._typeMap[cls.TYPE_DET] = [
                ShapeType.edgeTemplate,
                "EdgeTemplate",
            ]
            cls._typeMap[cls.TYPE_DN] = [ShapeType.null_, "Deleted Shape"]

        return cls._typeMap

    # Helper query methods
    @staticmethod
    def typeOf(disp) -> ShapeType:
        return (ShapeBase.typeMap)[disp["_tt"]][0]

    @staticmethod
    def hasColor(disp) -> bool:
        if disp["lcl"]:
            return True
        if disp["fcl"]:
            return True
        if disp["cl"]:
            return True
        return False

    @staticmethod
    def niceName(disp) -> str:
        return (ShapeBase.typeMap)[disp["_tt"]][1]

    # getters
    @staticmethod
    def type(disp) -> str:
        return disp.get("_tt")

    @staticmethod
    def id(disp) -> int:
        return disp.get("id")

    @staticmethod
    def zOrder(disp) -> int:
        if disp["z"]:
            return disp.get("z")
        return 0

    @staticmethod
    def hashId(disp) -> str:
        return disp.get("hid")

    @staticmethod
    def replacesHashId(disp) -> str:
        return disp.get("rid")

    @staticmethod
    def groupId(disp) -> Union[int, None]:
        return disp.get("gi")

    @staticmethod
    def branchId(disp) -> int:
        return disp.get("bi")

    @staticmethod
    def branchStage(disp) -> int:
        return disp.get("bs")

    @staticmethod
    def level(disp) -> DispLevelTable:
        return disp.get("lel", {})

    @staticmethod
    def layer(disp) -> DispLayerTable:
        return disp.get("lal", {})

    @staticmethod
    def isOverlay(disp) -> bool:
        return disp.get("o")

    @staticmethod
    def isSelectable(disp) -> bool:
        return disp.get("s")

    @staticmethod
    def key(disp) -> Union[str, None]:
        return disp.get("k")

    @staticmethod
    def action(disp) -> Union[ShapeActionEnum, None]:
        # ShapeActionEnum
        return disp.get("a")

    @staticmethod
    def data(disp) -> dict:
        if disp["d"] is None:
            return {}
        return json.loads(disp["d"])
