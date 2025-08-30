import { addTupleType, Tuple } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "../PluginNames";
import { ModelCoordSetGridSize } from "./ModelCoordSetGridSize";
import { PeekCanvasBounds } from "../PeekCanvasBounds";

/* Make Disp Group Grid Key
 
 Make the special disp group grid key name.
 This is used to store all of the DispGroups that are not specifically stored in a
 grid, with the DispGroupPtr that uses it.
 
 */
export function makeDispGroupGridKey(coordSetId: number): string {
    return `${coordSetId}|dispgroup`;
}

interface _XY {
    x: number;
    y: number;
}

@addTupleType
export class ModelCoordSet extends Tuple {
    public static readonly tupleName = diagramTuplePrefix + "ModelCoordSet";

    id: number;
    key: string;
    name: string;
    initialPanX: number;
    initialPanY: number;
    initialZoom: number;
    initialDarkMode: boolean;

    // The pre-configured zoom level for this coord set to use when positioning.
    positionOnZoom: number;

    backgroundDarkColor: string;
    backgroundLightColor: string;

    enabled: boolean;
    lightModeEnabled: boolean;

    comment: string;

    modelSetId: number;

    minZoom: number;
    maxZoom: number;

    gridSizes: ModelCoordSetGridSize[];

    // Misc data holder
    data: { [key: string]: any } | null;

    // Show this Coord Set as a group of DispGroups to choose from in the Editor
    dispGroupTemplatesEnabled: boolean;

    // Show this Coord Set as a group of Line Templates to choose from in the Editor
    edgeTemplatesEnabled: boolean;

    // Show "Select Branches" button
    branchesEnabled: boolean;

    // Edit fields
    editEnabled: boolean;

    // Default Layer for new shapes
    editDefaultLayerId: number;

    // Default Level for new shapes
    editDefaultLevelId: number;

    // Default Color for new shapes
    editDefaultColorId: number;

    // Default Line for new shapes
    editDefaultLineStyleId: number;

    // Default Text for new shapes
    editDefaultTextStyleId: number;

    // Default Vertex/Node/Equipment Coord Set
    editDefaultVertexCoordSetId: number;
    editDefaultVertexGroupName: string;

    // Default Edge/Conductor Coord Set
    editDefaultEdgeCoordSetId: number;
    editDefaultEdgeGroupName: string;

    userGroupsAllowed: string;
    userGroupsDenied: string;

    // The order of the coordset, the first is the landing one
    order: number;

    constructor() {
        super(ModelCoordSet.tupleName);
    }

    /** Grid size for Zoom
     *
     * This method calculates which Z grid to use based on a zoom level
     */
    gridSizeForZoom(zoom: number): ModelCoordSetGridSize {
        if (zoom == null) throw new Error("Zoom can't be null");

        // Figure out the Z grid
        for (let gridSize of this.gridSizes) {
            if (gridSize.min <= zoom && zoom < gridSize.max) {
                return gridSize;
            }
        }
        throw new Error(`Unable to determine grid size for zoom ${zoom}`);
    }

    centerGridKeyForArea(area: PeekCanvasBounds, zoom: number): string {
        const gridSize = this.gridSizeForZoom(zoom);
        const centerGridXY = this.areaCenterGrid(area, gridSize);

        return this.getGrid(gridSize, centerGridXY.x, centerGridXY.y);
    }

    /** Grid Keys For Area
     *
     * This method returns the grids required for a certain area of a certain zoom level.
     *
     */
    gridKeysForArea(area: PeekCanvasBounds, zoom: number): string[] {
        const gridSize = this.gridSizeForZoom(zoom);

        const center = this.areaCenterGrid(area, gridSize);

        // Round the X min/max
        const minGridX = this.trunc(area.x / gridSize.xGrid);
        const maxGridX = this.trunc((area.x + area.w) / gridSize.xGrid) + 1;

        // Round the Y min/max
        const minGridY = this.trunc(area.y / gridSize.yGrid);
        const maxGridY = this.trunc((area.y + area.h) / gridSize.yGrid) + 1;

        // Iterate through and create the grids.
        const gridKeysWithDistance = [];
        for (let x = minGridX; x < maxGridX; x++) {
            for (let y = minGridY; y < maxGridY; y++) {
                gridKeysWithDistance.push({
                    distance: Math.hypot(center.x - x, center.y - y),
                    grid: this.getGrid(gridSize, x, y),
                });
            }
        }

        gridKeysWithDistance.sort((a, b) => a.distance - b.distance);

        return gridKeysWithDistance.map((item) => item.grid);
    }

    private trunc(num: any) {
        return parseInt(num);
    }

    private areaCenterGrid(
        area: PeekCanvasBounds,
        gridSize: ModelCoordSetGridSize,
    ): _XY {
        return {
            x: this.trunc(
                (area.x + area.w / 2 - gridSize.xGrid / 2) / gridSize.xGrid,
            ),
            y: this.trunc(
                (area.y + area.h / 2 - gridSize.yGrid / 2) / gridSize.yGrid,
            ),
        };
    }

    private getGrid(gridSize: ModelCoordSetGridSize, x: number, y: number) {
        return this.id.toString() + "|" + gridSize.key + "." + x + "x" + y;
    }
}
