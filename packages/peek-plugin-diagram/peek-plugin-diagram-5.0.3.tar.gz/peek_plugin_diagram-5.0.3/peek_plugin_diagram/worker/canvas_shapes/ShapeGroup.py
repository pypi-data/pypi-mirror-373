import json
from typing import List

from peek_plugin_diagram.worker.canvas_shapes.ShapeBase import ShapeBase


class ShapeGroup(ShapeBase):
    @staticmethod
    def items(disp) -> List[dict]:
        if disp["di"] is None:
            return []

        return json.loads(disp["di"])

    @staticmethod
    def groupName(disp) -> str:
        return disp["n"]
