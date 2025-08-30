import logging
from collections import defaultdict
from typing import Dict
from typing import List

from vortex.Tuple import Tuple

from peek_plugin_diagram._private.storage.Lookups import _Hasher
from peek_plugin_diagram.tuples.lookup_tuples.ShapeLayerTuple import (
    ShapeLayerTuple,
)
from peek_plugin_diagram.tuples.lookup_tuples.ShapeLevelTuple import (
    ShapeLevelTuple,
)
from peek_plugin_diagram.worker.WorkerDiagramLookupApi import (
    WorkerDiagramLookupApi,
)

logger = logging.getLogger(__name__)


_hasher = _Hasher()


class ShapeLookupLinker:
    def __init__(self):
        self._isLoaded = False

        self._levelsById = {}
        self._layersById = {}
        self._colorById = {}
        self._textStyleById = {}
        self._lineStyleById = {}

        self._linkedLevelIds = set()
        self._linkedLayerIds = set()

        self._shapeIndexSetByLevelId = defaultdict(set)
        self._shapeIndexSetByLayerId = defaultdict(set)

        self.loadLookups()

    def loadLookups(self):
        if not self._isLoaded:
            self._loadAllLookups()
            self._isLoaded = True

    def levelsOrderedByOrder(
        self, coordSetKey: str, linkedOnly: bool = False
    ) -> List[ShapeLevelTuple]:
        levels = []
        for level in self._levelsById.values():
            if linkedOnly and level.id not in self._linkedLevelIds:
                continue
            if level.data.get("coordSetKey") == coordSetKey:
                levels.append(level)

        levels.sort(key=lambda l: l.order)

        return levels

    @property
    def shapeIndexSetByLevelId(self):
        return self._shapeIndexSetByLevelId

    def layersOrderedByOrder(
        self, modelSetKey: str, linkedOnly: bool = False
    ) -> List[ShapeLayerTuple]:
        layers = []
        for layer in self._layersById.values():
            if linkedOnly and layer.id not in self._linkedLayerIds:
                continue
            if layer.data.get("modelSetKey") == modelSetKey:
                layers.append(layer)

        layers.sort(key=lambda l: l.order)

        return layers

    @property
    def shapeIndexSetByLayerId(self):
        return self._shapeIndexSetByLayerId

    def _loadAllLookups(self):
        levels = WorkerDiagramLookupApi.getLevels()
        self._levelsById = self._makeLookupMap(levels)

        colors = WorkerDiagramLookupApi.getColors()
        self._colorById = self._makeLookupMap(colors)

        lineStyles = WorkerDiagramLookupApi.getLineStyles()
        self._lineStyleById = self._makeLookupMap(lineStyles)

        textStyles = WorkerDiagramLookupApi.getTextStyles()
        self._textStyleById = self._makeLookupMap(textStyles)

        layers = WorkerDiagramLookupApi.getLayers()
        self._layersById = self._makeLookupMap(layers)

    def _makeLookupMap(
        self,
        lookups: List[Tuple],
    ) -> Dict[str, Tuple]:
        mapped = {}

        for lookup in lookups:
            key = str(getattr(lookup, "key"))
            id_ = str(_hasher.decode(key)[0])
            mapped[id_] = lookup

        return mapped

    def linkShapesToLookups(self, shapes: List[Dict]) -> List[Dict]:
        self._linkedLevelIds = set()
        self._linkedLayerIds = set()

        self._shapeIndexSetByLevelId = defaultdict(set)
        self._shapeIndexSetByLayerId = defaultdict(set)

        for shapeIndex, shape in enumerate(shapes, 0):
            try:
                linkedLevelKey, linkedLayerKey = self._linkShapeLookups(shape)

                if linkedLevelKey:
                    self._linkedLevelIds.add(linkedLevelKey)
                    self._shapeIndexSetByLevelId[linkedLevelKey].add(shapeIndex)
                if linkedLayerKey:
                    self._linkedLayerIds.add(linkedLayerKey)
                    self._shapeIndexSetByLayerId[linkedLayerKey].add(shapeIndex)
            except KeyError as e:
                logger.error(shape)
                logger.exception(e)

        return shapes

    def _linkShapeLookups(self, shape: Dict):
        linkedLevelId = None
        linkedLayerId = None

        if le := shape.get("le"):
            linkedLevelId = le
            le = str(le)
            shape["lel"] = self._levelsById.get(le)

        if la := shape.get("la"):
            linkedLayerId = la
            la = str(la)
            shape["lal"] = self._layersById.get(la)

        if fs := shape.get("fs"):
            fs = str(fs)
            shape["fsl"] = self._textStyleById.get(fs)

        if c := shape.get("c"):
            c = str(c)
            shape["cl"] = self._colorById.get(c)

        if bc := shape.get("bc"):
            bc = str(bc)
            shape["bcl"] = self._colorById.get(bc)

        if lc := shape.get("lc"):
            lc = str(lc)
            shape["lcl"] = self._colorById.get(lc)

        if ec := shape.get("ec"):
            ec = str(ec)
            shape["ecl"] = self._colorById.get(ec)

        if fc := shape.get("fc"):
            fc = str(fc)
            shape["fcl"] = self._colorById.get(fc)

        if ls := shape.get("ls"):
            ls = str(ls)
            shape["lsl"] = self._lineStyleById.get(ls)

        return linkedLevelId, linkedLayerId
