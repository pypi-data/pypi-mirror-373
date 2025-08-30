import { Subject } from "rxjs";
import { PeekCanvasBounds } from "./PeekCanvasBounds";
import { ModelCoordSet } from "@peek/peek_plugin_diagram/_private/tuples/ModelCoordSet";
import { EditorToolType } from "./PeekCanvasEditorToolType.web";
import { BranchTuple } from "@peek/peek_plugin_diagram/_private/branch";

export interface IPosition {
    x: number;
    y: number;
}

export interface ISelectionStyle {
    color: string;
    width: number;
    lineGap: number;
    dashLen: number;
    margin?: number;
}

export interface IInvisibleConfig {
    color: string;
    width: number;
    dashLen: number;
}

export interface IGridConfig {
    show: boolean;
    size: number;
    color: string;
    font: string;
    lineWidth: number;
    snapDashedLen: number;
}

export interface IControllerConfig {
    updateInterval: number;
    coordSetChange: Subject<ModelCoordSet>;
    coordSet: ModelCoordSet | null;
    modelSetKey: string;
}

export interface IRendererConfig {
    invalidate: Subject<void>;
    drawInterval: number;
    backgroundColor: string;
    isLightMode: boolean;
    useEdgeColors: boolean;
    selection: ISelectionStyle;
    suggestion: ISelectionStyle;
    editSelection: ISelectionStyle;
    invisible: IInvisibleConfig;
    grid: IGridConfig;
}

export interface IViewPortConfig {
    windowChange: Subject<PeekCanvasBounds>;
    window: PeekCanvasBounds;
    zoomChange: Subject<number>;
    panChange: Subject<IPosition>;
    pan: IPosition;
    zoom: number;
    minZoom: number;
    maxZoom: number;
}

export interface ICanvasConfig {
    windowChange: Subject<PeekCanvasBounds>;
    window: PeekCanvasBounds;
}

export interface IMouseConfig {
    currentDelegateName: EditorToolType;
    phUpDownZoomFactor: number;
    currentViewPortPosition: IPosition;
    currentCanvasPosition: IPosition;
    selecting: ISelectionStyle;
}

export interface IModelConfig {
    needsCompiling: Subject<void>;
    gridsWaitingForData: number;
    dispOnScreen: number;
    overlayEnabled: boolean;
}

export interface IEditorConfig {
    branchKeyChange: Subject<string | null>;
    branchKey: string | null;
    showAllLayers: boolean;
    showAllLevels: boolean;
    active: boolean;
    resizeHandleMargin: number;
    resizeHandleWidth: number;
    selectionHighlightColor: string;
    primaryEditActionCompleteColor: string;
    primaryEditActionDefaultColor: string;
    primaryEditActionHandleMargin: number;
    primaryEditActionHandleWidth: number;
    activeBranchTuple: BranchTuple | null;
    snapToGrid: boolean;
    snapSize: number;
}
