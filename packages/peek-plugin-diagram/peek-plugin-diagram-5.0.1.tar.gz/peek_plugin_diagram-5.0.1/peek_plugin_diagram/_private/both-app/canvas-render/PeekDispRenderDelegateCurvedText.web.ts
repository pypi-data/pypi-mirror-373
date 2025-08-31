import { PeekCanvasConfig } from "../canvas/PeekCanvasConfig.web";
import {
    DrawModeE,
    PeekDispRenderDelegateABC,
} from "./PeekDispRenderDelegateABC.web";
import {
    DispCurvedText,
    DispCurvedTextT,
} from "../canvas-shapes/DispCurvedText";
import { pointToPixel } from "../DiagramUtil";
import { PeekCanvasBounds } from "../canvas/PeekCanvasBounds";
import { DispBaseT, PointI } from "../canvas-shapes/DispBase";
import { PeekCanvasModel } from "../canvas/PeekCanvasModel.web";
import { DispTextStyle } from "@peek/peek_plugin_diagram/_private/lookups";
import { DispPolygon } from "../canvas-shapes/DispPolygon";

interface SubPathIndexRange {
    isReversed: boolean;
    rightExclusiveBoundaryIndex: number;
}

interface ProcessedPath {
    subPaths: number[][];
    pathLength: number;
}

interface CurvedTextPathDrawingContext {
    distanceOfSegment: number;
    distanceConsumed: number;
    pathIndex: number;
    nextPoint?: {
        location: PointI;
        angle: number;
    };
}

export class PeekDispRenderDelegateCurvedText extends PeekDispRenderDelegateABC {
    private textMeasureCtx;

    constructor(config: PeekCanvasConfig, model: PeekCanvasModel) {
        super(config, model);

        // Create a canvas element for measuring text
        let canvas = document.createElement("canvas");
        this.textMeasureCtx = canvas.getContext("2d");
    }

    updateBounds(disp: DispBaseT): void {
        let geom = DispPolygon.geom(disp);
        disp.bounds = PeekCanvasBounds.fromGeom(geom);
    }

    /** Draw
     *
     * NOTE: The way the text is scaled and drawn must match _calcTextSize(..)
     * in python module DispCompilerTask.py
     */
    override draw(
        disp: DispCurvedTextT,
        ctx,
        zoom: number,
        pan: PointI,
        drawMode: DrawModeE,
    ) {
        if (drawMode === DrawModeE.ForEdit) {
            this.drawInvisible(disp, ctx, zoom);
        }
        this._draw(disp, ctx, zoom);
    }

    override drawSelected(
        disp,
        ctx,
        zoom: number,
        pan: PointI,
        drawMode: DrawModeE,
    ) {
        // NOTE: We should probably add the text height to the box
        let geom = DispCurvedText.geom(disp);

        let selectionConfig =
            this.config.getSelectionDrawDetailsForDrawMode(drawMode);

        // DRAW THE SELECTED BOX
        let bounds = PeekCanvasBounds.fromGeom(geom);

        // Move the selection line a bit away from the object
        let offset = (selectionConfig.width + selectionConfig.lineGap) / zoom;

        let twiceOffset = 2 * offset;
        let x = bounds.x - offset;
        let y = bounds.y - offset;
        let w = bounds.w + twiceOffset;
        let h = bounds.h + twiceOffset;

        ctx.dashedRect(x, y, w, h, selectionConfig.dashLen / zoom);
        ctx.strokeStyle = selectionConfig.color;
        ctx.lineWidth = selectionConfig.width / zoom;
        ctx.stroke();
    }

    override drawEditHandles(disp, ctx, zoom: number, pan: PointI) {
        ctx.fillStyle = this.config.editor.selectionHighlightColor;
        const handles = this.handles(disp, zoom);
        for (const handle of handles) {
            const b = handle.box;
            ctx.beginPath();
            ctx.arc(b.x + b.w / 2, b.y + b.h / 2, b.h / 2, 0, 2 * Math.PI);
            ctx.fill();
        }
    }

    /**
     * Helper method to visualize the path of a curved text for debugging
     * This method can be called from draw() method to see the underlying path
     */
    private drawInvisible(disp: DispCurvedTextT, ctx, zoom: number) {
        let selectionConfig = this.config.renderer.invisible;

        const geom = disp.g;
        if (geom.length < 2) return;

        const oldAlpha = ctx.globalAlpha;
        const oldStrokeStyle = ctx.strokeStyle;
        const oldLineWidth = ctx.lineWidth;

        ctx.beginPath();
        ctx.moveTo(geom[0], geom[1]);

        let lastX = geom[0];
        let lastY = geom[1];

        for (let i = 2; i < geom.length; i += 2) {
            ctx.dashedLine(
                lastX,
                lastY,
                geom[i],
                geom[i + 1],
                selectionConfig.dashLen / zoom,
            );
            lastX = geom[i];
            lastY = geom[i + 1];
        }

        ctx.strokeStyle = selectionConfig.color;
        ctx.lineWidth = selectionConfig.width / zoom;
        ctx.stroke();

        // Restore context
        ctx.globalAlpha = oldAlpha;
        ctx.strokeStyle = oldStrokeStyle;
        ctx.lineWidth = oldLineWidth;
    }

    /** Draw
     *
     * NOTE: The way the text is scaled and drawn must match _calcTextSize(..)
     * in python module DispCompilerTask.py
     */
    private _draw(disp: DispCurvedTextT, ctx, zoom: number) {
        const textStyle = DispCurvedText.textStyle(disp);

        // Null colors are also not drawn
        const fillColor = DispCurvedText.color(disp)?.getColor(
            this.config.isLightMode,
        );
        const borderColor = DispCurvedText.borderColor(disp)?.getColor(
            this.config.isLightMode,
        );

        let fontSize = textStyle.fontSize * textStyle.scaleFactor;

        if (!textStyle.scalable) {
            fontSize /= zoom;
        }

        const font =
            (textStyle.fontStyle || "") +
            " " +
            fontSize +
            "px " +
            textStyle.fontName;

        // save state
        ctx.save();
        this.drawCurvedTexts(
            ctx,
            font,
            textStyle,
            zoom,
            disp,
            fillColor,
            borderColor,
        );

        // restore to original state
        ctx.restore();
    }

    private calculateDistance2D(
        x1: number,
        y1: number,
        x2: number,
        y2: number,
    ): number {
        const dx = x2 - x1;
        const dy = y2 - y1;
        return Math.sqrt(dx * dx + dy * dy);
    }

    private calculateRotationAngle(y, x) {
        return Math.atan2(y, x);
    }

    private reversePath(path: number[]) {
        const reversedPath = [];
        for (let i = path.length - 2; i >= 0; i -= 2) {
            reversedPath.push(path[i]);
            reversedPath.push(path[i + 1]);
        }
        return reversedPath;
    }

    private preprocessPath(path: number[]): ProcessedPath {
        // check if the path is valid
        if (path.length % 2 != 0) {
            throw new Error(
                "path should be an 1-dimension array of coordinates of x and y.",
            );
        }

        const segmentLengths: number[] = [];
        let pathLength: number = 0;
        const angles: number[] = [];
        const reverseDirectionOfXAxisFlags: boolean[] = [];
        const subPathIndexRanges: SubPathIndexRange[] = [];

        const subPaths = [];

        // loop over each segment of the path
        for (let i = 2; i < path.length; i += 2) {
            const previousX = path[i - 2];
            const previousY = path[i - 1];
            const thisX = path[i];
            const thisY = path[i + 1];

            const segmentDistance = this.calculateDistance2D(
                previousX,
                previousY,
                thisX,
                thisY,
            );

            segmentLengths.push(segmentDistance);
            pathLength += segmentDistance;

            // add angle of two segments that forms
            const angle = this.calculateRotationAngle(
                thisY - previousY,
                thisX - previousX,
            );
            angles.push(angle);

            // check whether the text is straight up or up-side-down
            //  angles in quadrant II or III need normalising
            //  https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D/rotate#syntax
            //                     -90
            //                     │
            //                     │
            //                     │
            //                II   │     I
            //                     │
            //                     │
            // 180/-180 ───────────┼──────────── 0 x
            //                     │
            //                     │
            //                III  │     IV
            //                     │
            //                     │
            //                     │
            //                     │
            //                     90
            //                     y

            // normalisation ranges
            //  90   to  180 and -90    to  -180 in degree
            // 1/2Pi to  1Pi and -1/2Pi to  -1Pi in radian

            // normalisation shortcut: make angles in quadrant III and IV
            //  flipped horizontally into quadrant II and I
            const absoluteAngle = Math.abs(angle);
            reverseDirectionOfXAxisFlags.push(
                // check if it's in quadrant II
                absoluteAngle > Math.PI / 2 && absoluteAngle <= Math.PI,
            );
        }

        // check segments direction
        if (
            // segments go against with x-axis only
            reverseDirectionOfXAxisFlags.includes(true) &&
            !reverseDirectionOfXAxisFlags.includes(false)
        ) {
            // flipped/hanging texts can be fixed by
            // drawing the text sequentially along the reversed path
            const reversedPath = this.reversePath(path);
            subPaths.push(reversedPath);
        } else if (
            // segments go along and against x-axis
            reverseDirectionOfXAxisFlags.includes(false) &&
            reverseDirectionOfXAxisFlags.includes(true)
        ) {
            // handle mixed directions in path

            // find groups of continuous segments that go to the same direction
            //  this finds index range of coordinates in each group
            let lastSameDirectionAngleIndex: number = 0;
            for (let i = 0; i < reverseDirectionOfXAxisFlags.length; ++i) {
                const isReversed =
                    reverseDirectionOfXAxisFlags[lastSameDirectionAngleIndex];

                // give a range from the last angle to the last point of path
                if (i == reverseDirectionOfXAxisFlags.length - 1) {
                    subPathIndexRanges.push({
                        isReversed: isReversed,
                        rightExclusiveBoundaryIndex: path.length,
                    });
                    break;
                }

                if (
                    // this goes to a different direction from last angle
                    reverseDirectionOfXAxisFlags[i] !=
                    reverseDirectionOfXAxisFlags[lastSameDirectionAngleIndex]
                ) {
                    // find last point of the segment in this.path
                    const rightExclusiveBoundary =
                        2 * lastSameDirectionAngleIndex;
                    subPathIndexRanges.push({
                        isReversed: isReversed,
                        rightExclusiveBoundaryIndex: rightExclusiveBoundary,
                    });
                }
                // update last seen direction
                lastSameDirectionAngleIndex = i;
            }

            // generate subpaths based on index ranges
            for (let i = 0; i < subPathIndexRanges.length; ++i) {
                // make first subpath from the start of this.path
                const inclusiveStartPointXIndex =
                    i == 0
                        ? 0
                        : // make other subpaths starts inclusively
                          //  from previous right exclusive boundary
                          subPathIndexRanges[i - 1].rightExclusiveBoundaryIndex;
                const exclusiveEndPointXIndex =
                    subPathIndexRanges[i].rightExclusiveBoundaryIndex;

                // reverse the sub path if flagged as reversed
                const subPath = subPathIndexRanges[i].isReversed
                    ? this.reversePath(
                          // Array.slice treats the boundaries
                          //  as [leftIndex, rightIndex)
                          path.slice(
                              inclusiveStartPointXIndex,
                              exclusiveEndPointXIndex,
                          ),
                      )
                    : path.slice(
                          inclusiveStartPointXIndex,
                          exclusiveEndPointXIndex,
                      );
                subPaths.push(subPath);
            }
        } else if (
            reverseDirectionOfXAxisFlags.includes(false) &&
            !reverseDirectionOfXAxisFlags.includes(true)
        ) {
            // whole path is along with x-axis
            // draw along with the original path
            subPaths.push(path);
        }

        return { subPaths: subPaths, pathLength: pathLength };
    }

    private locateNextCharacter(
        distanceFromStart: number,
        path: number[],
        curvedTextPathDrawingContext: CurvedTextPathDrawingContext,
    ): CurvedTextPathDrawingContext {
        {
            // get states from context
            let _distanceOfSegment =
                curvedTextPathDrawingContext.distanceOfSegment;
            let _distanceConsumed =
                curvedTextPathDrawingContext.distanceConsumed;
            let _pathIndex = curvedTextPathDrawingContext.pathIndex;

            //  if next drawing position fits on this segment of path
            if (
                !_distanceOfSegment ||
                _distanceConsumed + _distanceOfSegment < distanceFromStart
            ) {
                // search the segment that fits the position to draw next
                for (; _pathIndex < path.length; ) {
                    _distanceOfSegment = this.calculateDistance2D(
                        path[_pathIndex - 2],
                        path[_pathIndex - 1],
                        path[_pathIndex],
                        path[_pathIndex + 1],
                    );
                    if (
                        _distanceConsumed + _distanceOfSegment >
                        distanceFromStart
                    )
                        // segment found and stop searching on the path
                        break;
                    // go to the next segment on path
                    _pathIndex += 2;
                    // updated used distance
                    _distanceConsumed += _distanceOfSegment;
                    // stop searching if all segmentLengths are used
                    if (_pathIndex >= path.length) break;
                }
            }

            // new segment for drawing has found from above

            const distanceFromLastKeyPoint =
                distanceFromStart - _distanceConsumed;
            // use last key point on path if searching overshoots the path
            if (_pathIndex >= path.length) {
                _pathIndex = path.length - 2;
            }

            let x, y;
            // new drawing is on keypoint
            if (!distanceFromLastKeyPoint) {
                // get {x,y} of the previous point on path
                x = path[_pathIndex - 2];
                y = path[_pathIndex - 1];
            } else {
                // get {x,y} between key points with a ratio of new distance
                x =
                    path[_pathIndex - 2] +
                    ((path[_pathIndex] - path[_pathIndex - 2]) *
                        distanceFromLastKeyPoint) /
                        _distanceOfSegment;
                y =
                    path[_pathIndex - 1] +
                    ((path[_pathIndex + 1] - path[_pathIndex - 1]) *
                        distanceFromLastKeyPoint) /
                        _distanceOfSegment;
            }

            const deltaY = path[_pathIndex + 1] - path[_pathIndex - 1];
            const deltaX = path[_pathIndex] - path[_pathIndex - 2];
            const rotationAngle = this.calculateRotationAngle(deltaY, deltaX);

            return {
                distanceOfSegment: _distanceOfSegment,
                distanceConsumed: _distanceConsumed,
                pathIndex: _pathIndex,
                nextPoint: { location: { x: x, y: y }, angle: rotationAngle },
            };
        }
    }

    private drawCurvedTexts(
        ctx,
        font: string,
        textStyle: DispTextStyle,
        zoom: number,
        disp: DispCurvedTextT,
        fillColor: string | null,
        borderColor: string | null,
    ): void {
        // set up text styling
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.font = font;

        // draw

        // cache all text measurement to workaround for performance
        //  https://bugzilla.mozilla.org/show_bug.cgi?id=527386#c19
        const chars = DispCurvedText.text(disp).replace("\n", " ");
        if (!chars) {
            return;
        }

        const textWidth = ctx.measureText(chars).width;

        // Measure Text is EXTREMELY SLOW
        // We will sacrifice fonts that have variable letter widths for
        // performance.
        const charWidth = ctx.measureText(chars[0]).width;

        // this works like space-around in flexbox
        const spacingInBetween =
            DispCurvedText.spacingBetweenTexts(disp) === undefined
                ? DispCurvedText.spacingBetweenTexts(disp) / zoom // from disp
                : DispCurvedText.textStyle(disp).spacingBetweenTexts / zoom; // from text style
        const horizontalMargin = spacingInBetween / 4;
        const marginTotalWidth = horizontalMargin * 2;

        // draw text(s) on each sub-path where all turns of the subpath are towards
        //  the same direction of x axis i.e. west or east
        const processedPath = this.preprocessPath(disp.g);

        for (const subPath of processedPath.subPaths) {
            // const textPositioner = new TextPositioner(chars, subPath);
            const processedSubPath = this.preprocessPath(subPath);
            let curvedTextPathDrawingContext: CurvedTextPathDrawingContext = {
                distanceOfSegment: 0,
                distanceConsumed: 0,
                pathIndex: 2,
            };

            let spareDistance: number;
            let repeatCount: number;
            let marginAddable: boolean;

            // check if text needs repeating with proper margins and spacings
            // when path is too short to fit text
            if (processedSubPath.pathLength < textWidth) {
                //  skip the whole length - draw nothing
                repeatCount = 0;
                spareDistance = processedSubPath.pathLength;
                marginAddable = false;
            }
            // when path can fit at least one drawing of text
            // path can repeat text drawings
            //  i.e. >= 2 drawings of text with spacing inbetween
            else if (
                processedSubPath.pathLength >=
                2 * textWidth + 2 * marginTotalWidth + spacingInBetween
            ) {
                repeatCount = Math.floor(
                    (processedSubPath.pathLength + spacingInBetween) /
                        (marginTotalWidth + textWidth + spacingInBetween),
                );
                spareDistance =
                    processedSubPath.pathLength -
                    repeatCount * (marginTotalWidth + textWidth) -
                    (repeatCount - 1) * spacingInBetween;
                marginAddable = true;
            } else {
                // when path can fit one drawing of text only
                //  with or without margins
                // draw the text in the middle
                repeatCount = 1;
                spareDistance = processedSubPath.pathLength - textWidth;
                marginAddable = false;
            }

            // start drawing at the location where the text(s) are centered
            let distanceFromStartPoint = spareDistance / 2;

            // repeat text until it occupies the whole length of the path
            for (let i = 0; i < repeatCount; ++i) {
                // add distance used for left margin
                if (marginAddable) distanceFromStartPoint += horizontalMargin;

                // draw each character of the text
                for (let charIndex = 0; charIndex < chars.length; ++charIndex) {
                    const char = chars[charIndex];
                    curvedTextPathDrawingContext = this.locateNextCharacter(
                        distanceFromStartPoint + charWidth / 2,
                        subPath,
                        curvedTextPathDrawingContext,
                    );
                    ctx.save();

                    ctx.translate(
                        curvedTextPathDrawingContext.nextPoint.location.x,
                        curvedTextPathDrawingContext.nextPoint.location.y,
                    );
                    ctx.rotate(curvedTextPathDrawingContext.nextPoint.angle);

                    if (fillColor) {
                        ctx.fillStyle = fillColor;
                        ctx.fillText(char, 0, 0);
                    }

                    if (textStyle.borderWidth && borderColor !== null) {
                        // apply border width if set
                        ctx.lineWidth = textStyle.borderWidth;
                        ctx.strokeStyle = borderColor;
                        ctx.strokeText(char, 0, 0);
                    }
                    ctx.restore();
                    // add distance used for the character
                    distanceFromStartPoint += charWidth;
                }
                // add distance used for right margin
                if (marginAddable) distanceFromStartPoint += horizontalMargin;
                // add spacing between text repeats
                if (i < repeatCount) distanceFromStartPoint += spacingInBetween;
            }
        }
    }
}
