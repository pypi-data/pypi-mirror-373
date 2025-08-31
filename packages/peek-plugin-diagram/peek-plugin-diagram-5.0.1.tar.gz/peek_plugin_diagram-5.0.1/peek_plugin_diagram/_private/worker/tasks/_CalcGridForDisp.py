import logging
import math
from typing import Dict
from typing import List

from peek_plugin_diagram._private.storage.Display import DispBase
from peek_plugin_diagram._private.storage.Display import DispPolygon
from peek_plugin_diagram._private.storage.Display import DispPolyline
from peek_plugin_diagram._private.storage.Lookups import DispTextStyleTable
from peek_plugin_diagram._private.storage.ModelSet import (
    ModelCoordSetGridSizeTable,
)
from peek_plugin_diagram._private.storage.ModelSet import ModelCoordSetTable

logger = logging.getLogger(__name__)


def makeGridKeysForDisp(
    coordSet: ModelCoordSetTable,
    disp,
    geomJson,
    textStyleById: Dict[int, DispTextStyleTable],
) -> List[str]:
    points = geomJson

    if not geomJson:
        logger.critical("geomJson is None or [] : %s ", disp)
        return []

    if len(points) % 2:
        logger.critical("geomJson is not an even number of points: %s ", disp)
        return []

    dispType = disp.type
    isTextShape = dispType == DispBase.TEXT
    isPolylineShape = dispType == DispBase.POLYLINE
    isCurveTextShape = dispType == DispBase.CURVED_TEXT
    isPolygonShape = dispType == DispBase.POLYGON
    isGroupShape = dispType == DispBase.GROUP
    isEllipseShape = dispType == DispBase.ELLIPSE
    isGroupPtrShape = dispType == DispBase.GROUP_PTR

    # If it's a text shape with no text, ignore it
    if isTextShape and not disp.text:
        return []

    # If it's a curved text shape with no text, ignore it
    if isCurveTextShape and not disp.text:
        return []

    if isPolygonShape and _isEmptyPolygon(disp, points):
        return []

    if isPolylineShape and _isEmptyPolyline(disp, points):
        return []

    gridKeys = []
    for gridSize in coordSet.gridSizes:
        # CHECK Declutter
        if isGroupShape and disp.level is None:
            # Skip the check if the DispGroup has no level. It will be in all levels.
            pass

        elif 0.0 > (
            min(gridSize.max, (disp.level.maxZoom - 0.00001))
            - max(gridSize.min, disp.level.minZoom + 0.00001)
        ):
            continue

        if isTextShape and _isTextTooSmall(disp, gridSize, textStyleById):
            continue

        # Check for NaN values in the points data
        if any(math.isnan(val) for val in points):
            logger.critical(
                "NaN values detected in geometry data."
                " Skipping grid calculation for disp=%s geomJson=%s",
                disp,
                geomJson,
            )
            return []

        # If this is just a point shape/geom, then add it and continue
        if isEllipseShape:

            # Check for NaN values in the points data
            if math.isnan(disp.xRadius) or math.isnan(disp.yRadius):
                logger.critical(
                    "NaN values detected in ellipse X/Y radius."
                    " Skipping grid calculation for disp=%s, geomJson=%s",
                    disp,
                    geomJson,
                )
                return []

            minx, miny, maxx, maxy = _calcEllipseBounds(
                disp, points[0], points[1]
            )

        elif len(points) == 2:  # 2 = [x, y]
            # This should be a text
            if not isTextShape and not isGroupShape and not isGroupPtrShape:
                logger.debug(
                    "TODO Determine size for disp type %s", disp.tupleType()
                )

            # Texts on the boundaries of grids could be a problem
            # They will seem them if the pan over just a little.
            gridKeys.append(
                gridSize.makeGridKey(
                    int(points[0] / gridSize.xGrid),
                    int(points[1] / gridSize.yGrid),
                )
            )
            continue

        else:
            # Else, All other shapes
            # Get the bounding box
            minx, miny, maxx, maxy = _calcBounds(points)

        # If the size is too small to see at the max zoom, then skip it
        size = math.hypot(maxx - minx, maxy - miny)
        largestSize = size * gridSize.max
        if largestSize < gridSize.smallestShapeSize:
            continue

        # Round the grid X min/max
        minGridX = int(minx / gridSize.xGrid)
        maxGridX = int(maxx / gridSize.xGrid) + 1

        # Round the grid Y min/max
        minGridY = int(miny / gridSize.yGrid)
        maxGridY = int(maxy / gridSize.yGrid) + 1

        if 50 < abs(minGridX - maxGridX):
            logger.warning(
                "Ignoring massive shape with disp.id=%s,"
                " it crosses too many horizontal grids at"
                " at gridSize.id=%s,"
                " grid count is %s",
                disp.id,
                gridSize.id,
                abs(minGridX - maxGridX),
            )
            continue

        if 50 < abs(minGridY - maxGridY):
            logger.warning(
                "Ignoring massive shape with disp.id=%s,"
                " it crosses too many vertical grids at"
                " at gridSize.id=%s,"
                " grid count is %s",
                disp.id,
                gridSize.id,
                abs(minGridY - maxGridY),
            )
            continue

        # Iterate through and create the grids.
        for gridX in range(minGridX, maxGridX):
            for gridY in range(minGridY, maxGridY):
                gridKeys.append(gridSize.makeGridKey(gridX, gridY))

    return gridKeys


def _pointToPixel(point: float) -> float:
    return point * 96 / 72


def _isTextTooSmall(
    disp,
    gridSize: ModelCoordSetGridSizeTable,
    textStyleById: Dict[int, DispTextStyleTable],
) -> bool:
    """Is Text Too Small

    This method calculates the size that the text will appear on the diagram at max zoom
    for the provided gird.

    We'll only work this out based on the height

    NOTE: This must match how it's rendered PeekDispRenderDelegateText.ts
    """

    fontStyle = textStyleById[disp.textStyleId]

    if disp.textHeight:
        lineHeight = disp.textHeight
    else:
        fontSize = fontStyle.fontSize * fontStyle.scaleFactor
        lineHeight = _pointToPixel(fontSize)

    if fontStyle.scalable:
        largestSize = lineHeight * gridSize.max
    else:
        largestSize = lineHeight

    return largestSize < gridSize.smallestTextSize


def _calcEllipseBounds(disp, x, y):
    """Calculate the bounds of an ellipse"""
    # NOTE: To do this accurately we should look at the start and end angles.
    # in the interest simplicity we're not going to.
    # We'll potentially include SMALLEST_SHAPE_SIZE / 2 as well, no big deal.

    minx = x - disp.xRadius
    maxx = x + disp.xRadius

    miny = y - disp.yRadius
    maxy = y + disp.yRadius

    return minx, miny, maxx, maxy


def _calcBounds(points: List[float]):
    minx = None
    maxx = None
    miny = None
    maxy = None

    for index, val in enumerate(points):
        isY = bool(index % 2)

        if isY:
            if miny is None or val < miny:
                miny = val

            if maxy is None or maxy < val:
                maxy = val

        else:
            if minx is None or val < minx:
                minx = val

            if maxx is None or maxx < val:
                maxx = val

    return minx, miny, maxx, maxy


def _isEmptyPolyline(disp: DispPolyline, points):
    # Shapes with keys are used for locations, or Override apis
    if disp.key:
        return False

    # Shapes with actions can bring up menus, and are often invisible
    if disp.action:
        return False

    # It must have a line (width and style).
    if not disp.lineWidth or disp.lineStyleId is None:
        return True

    # At this point, it must have a colour
    if (
        disp.lineColorId is None
        and disp.borderColorId is None
        and disp.edgeColorId is None
    ):
        return True

    # All other cases assume it's not useless
    return False


def _isEmptyPolygon(disp: DispPolygon, points):
    # Shapes with keys are used for locations, or Override apis
    if disp.key:
        return False

    # Shapes with actions can bring up menus, and are often invisible
    if disp.action:
        return False

    # It's filled
    if disp.fillColorId is not None:
        return False

    # It must have a line (width and style).
    if not disp.lineWidth or disp.lineStyleId is None:
        return True

    # It must have a colour
    if disp.lineColorId is None:
        return True

    # All other cases assume it's not useless
    return False
