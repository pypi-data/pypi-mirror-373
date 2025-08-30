import time
from enum import Enum

from vortex.Tuple import Tuple
from vortex.Tuple import TupleField


class DiagramOverrideBase(Tuple):
    TYPE_COLOR = 0
    TYPE_HIGHLIGHT = 1

    _overrideNum = 0

    key = TupleField()
    modelSetKey: int | None = TupleField()
    coordSetKey: int | None = TupleField()
    overrideType: int = TupleField()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.key = f"{int(time.time())}={DiagramOverrideBase._overrideNum}"
        DiagramOverrideBase._overrideNum += 1
