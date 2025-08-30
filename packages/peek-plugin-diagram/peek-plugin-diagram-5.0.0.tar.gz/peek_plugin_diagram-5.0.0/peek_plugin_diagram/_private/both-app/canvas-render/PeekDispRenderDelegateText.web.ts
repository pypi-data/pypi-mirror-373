import { PeekCanvasConfig } from "../canvas/PeekCanvasConfig.web";
import {
    DrawModeE,
    PeekDispRenderDelegateABC,
} from "./PeekDispRenderDelegateABC.web";
import {
    DispText,
    DispTextT,
    TextHorizontalAlign,
    TextVerticalAlign,
} from "../canvas-shapes/DispText";
import { pointToPixel } from "../DiagramUtil";
import { PeekCanvasBounds } from "../canvas/PeekCanvasBounds";
import { DispBaseT, PointI } from "../canvas-shapes/DispBase";
import { PeekCanvasModel } from "../canvas/PeekCanvasModel.web";
import { DispTextStyle } from "@peek/peek_plugin_diagram/_private/lookups";

export class PeekDispRenderDelegateText extends PeekDispRenderDelegateABC {
    private textMeasureCtx;

    constructor(config: PeekCanvasConfig, model: PeekCanvasModel) {
        super(config, model);

        // Create a canvas element for measuring text
        let canvas = document.createElement("canvas");
        this.textMeasureCtx = canvas.getContext("2d");
    }

    updateBounds(disp: DispBaseT, zoom: number): void {
        this.drawAndCalcBounds(
            <DispTextT>disp,
            this.textMeasureCtx,
            zoom,
            true
        );
    }

    /** Draw
     *
     * NOTE: The way the text is scaled and drawn must match _calcTextSize(..)
     * in python module DispCompilerTask.py
     */
    draw(disp: DispTextT, ctx, zoom: number, pan: PointI, drawMode: DrawModeE) {
        this.drawAndCalcBounds(disp, ctx, zoom, false);
    }

    drawSelected(disp, ctx, zoom: number, pan: PointI, drawMode: DrawModeE) {
        let bounds = disp.bounds;
        if (bounds == null) return;

        // DRAW THE SELECTED BOX
        let selectionConfig =
            this.config.getSelectionDrawDetailsForDrawMode(drawMode);

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

    drawEditHandles(disp, ctx, zoom: number, pan: PointI) {
        /*
         // DRAW THE EDIT HANDLES
         ctx.fillStyle = CanvasRenderer.SELECTION_COLOR;
         let handles = this.handles();
         for (let i = 0; i < handles.length; ++i) {
         let handle = handles[i];
         ctx.fillRect(handle.x, handle.y, handle.w, handle.h);
         }
         */
    }

    /** Draw
     *
     * NOTE: The way the text is scaled and drawn must match _calcTextSize(..)
     * in python module DispCompilerTask.py
     */
    private drawAndCalcBounds(
        disp: DispTextT,
        ctx,
        zoom: number,
        updateBounds: boolean
    ) {
        // Give meaning to our short names
        const rotationRadian = (DispText.rotation(disp) / 180.0) * Math.PI;

        const fontStyle = DispText.textStyle(disp);

        const horizontalStretchFactor = DispText.horizontalStretch(disp);
        const textHeight = DispText.height(disp);

        let fontSize = fontStyle.fontSize * fontStyle.scaleFactor;

        if (textHeight != null) fontSize = textHeight;

        // Do our line splits
        const renderedLines = this.splitAndWrapLines(fontStyle, disp);

        const lineHeight = pointToPixel(fontSize);
        const allLinesHeight = (lineHeight * renderedLines.length)/zoom;

        // Null colors are also not drawn
        const fillColor = DispText.color(disp)?.getColor(
            this.config.isLightMode
        );
        const borderColor = DispText.borderColor(disp)?.getColor(
            this.config.isLightMode
        );

        // TODO, Draw a box around the text, based on line style

        const font =
            (fontStyle.fontStyle || "") +
            " " +
            fontSize +
            "px " +
            fontStyle.fontName;

        const centerX = DispText.centerPointX(disp);
        let centerY = DispText.centerPointY(disp);

        let textAlign = null;
        const horizontalAlignEnum = DispText.horizontalAlign(disp);
        if (horizontalAlignEnum == TextHorizontalAlign.left)
            textAlign = "start";
        else if (horizontalAlignEnum == TextHorizontalAlign.center)
            textAlign = "center";
        else if (horizontalAlignEnum == TextHorizontalAlign.right)
            textAlign = "end";

        const textBaseline = "top";
        const verticalAlignEnum = DispText.verticalAlign(disp);
        if (verticalAlignEnum == TextVerticalAlign.top) {
            // Do nothing, the text will render top to bottom
        } else if (verticalAlignEnum == TextVerticalAlign.center) {
            centerY -= allLinesHeight / 2;
        } else if (verticalAlignEnum == TextVerticalAlign.bottom) {
            centerY -= allLinesHeight ;
        }

        // save state
        ctx.save();
        ctx.translate(centerX, centerY);
        ctx.rotate(rotationRadian); // Degrees to radians

        ctx.textAlign = textAlign;
        ctx.textBaseline = textBaseline;
        ctx.font = font;

        if (!fontStyle.scalable) {
            let unscale = 1.0 / zoom;
            ctx.scale(unscale, unscale);
        }

        if (horizontalStretchFactor != 1) {
            ctx.scale(horizontalStretchFactor, 1);
        }

        // Bounds can get serliased in branches, so check to see if it's actually the
        // class or just the restored object that it serialises to.
        if (updateBounds) {
            disp.bounds = new PeekCanvasBounds();
            disp.bounds.w = 0;
        }

        for (let lineIndex = 0; lineIndex < renderedLines.length; ++lineIndex) {
            let line = renderedLines[lineIndex];
            let yOffset = lineHeight * lineIndex;

            // Measure the width
            if (updateBounds) {
                let thisWidth = ctx.measureText(line).width / zoom;
                if (disp.bounds.w < thisWidth) disp.bounds.w = thisWidth;
            }

            if (fillColor) {
                ctx.fillStyle = fillColor;
                ctx.fillText(line, 0, yOffset);
            }

            if (fontStyle.borderWidth && borderColor !== null) {
                // apply border width if set
                ctx.lineWidth = fontStyle.borderWidth;
                ctx.strokeStyle = borderColor;
                ctx.strokeText(line, 0, yOffset);
            }
        }

        let singleLineHeight = lineHeight / zoom;
        if (updateBounds) {
            disp.bounds.h = singleLineHeight * renderedLines.length;
        }

        // restore to original state
        ctx.restore();

        if (updateBounds) {
            if (horizontalAlignEnum == TextHorizontalAlign.left)
                disp.bounds.x = centerX;
            else if (horizontalAlignEnum == TextHorizontalAlign.center)
                disp.bounds.x = centerX - disp.bounds.w / 2;
            else if (horizontalAlignEnum == TextHorizontalAlign.right)
                disp.bounds.x = centerX - disp.bounds.w;

            if (verticalAlignEnum == TextVerticalAlign.top)
                disp.bounds.y = centerY;
            else if (verticalAlignEnum == TextVerticalAlign.center)
                disp.bounds.y = centerY - singleLineHeight / 2;
            else if (verticalAlignEnum == TextVerticalAlign.bottom)
                disp.bounds.y = centerY - singleLineHeight;
        }
    }

    private splitAndWrapLines(fontStyle: DispTextStyle, disp: DispTextT) {
        let renderedLines = [];
        if ((fontStyle.wrapTextAtChars || 0) <= 0) {
            renderedLines = DispText.text(disp).split("\n");
        } else {
            const wrappedLines = this.wrapText(
                DispText.text(disp),
                fontStyle.wrapTextAtChars,
                fontStyle.wrapTextAtCharSplitBetweenWords
            );
            for (const wrappedLine of wrappedLines) {
                for (const renderedLine of wrappedLine.split("\n")) {
                    renderedLines.push(renderedLine);
                }
            }
        }
        return renderedLines;
    }

    private wrapText(
        text: string,
        width: number,
        splitBetweenWords: boolean
    ): string[] {
        const substrings: string[] = [];

        if (!splitBetweenWords) {
            for (let i = 0; i < text.length; i += width) {
                const substring = text.slice(i, i + width);
                substrings.push(substring);
            }
        } else {
            const words = text.split(" ");

            let substring = "";
            while (words.length > 0) {
                const word = words.shift();

                if (word.length >= width) {
                    if (substring.length > 0) {
                        substrings.push(substring);
                        substring = "";
                    }
                    substrings.push(word);
                    continue;
                }

                if (substring.length + word.length <= width) {
                    substring += word;
                    continue;
                }

                if (substring.length + word.length > width) {
                    substrings.push(substring);
                    substring = "";
                    substring += word;
                }
            }

            if (substring.length > 0) {
                substrings.push(substring);
            }
        }
        return substrings;
    }
}

