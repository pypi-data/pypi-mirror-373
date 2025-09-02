import {
    DispBaseT,
    DispHandleI,
    DispType,
    PointI,
    PointsT,
} from "./DispBasePartial";
import {
    PeekCanvasShapePropsContext,
    ShapeProp,
    ShapePropType,
} from "../canvas/PeekCanvasShapePropsContext";
import { ModelCoordSet } from "@peek/peek_plugin_diagram/_private/tuples";
import { DispGroup, DispGroupT } from "./DispGroup";
import { PrivateDiagramLookupService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramLookupService";
import { BranchTuple } from "@peek/peek_plugin_diagram/_private/branch/BranchTuple";
import {
    calculateRotationFromHandleDelta,
    makeRotateHandlePoints,
} from "./DispUtilRotate";
import { DispText } from "./DispText";
import { getWrapper } from "./DispFactoryTypeMap";
import { DispBase } from "./DispBase";
import { DispGroupPointerPartial } from "./DispGroupPointerPartial";

export interface DispGroupPointerT extends DispBaseT {
    // verticalScale
    vs: number;

    // horizontalScale
    hs: number;

    // targetGroupId
    tg: number;

    // targetGroupName
    tn: string;

    // Rotation
    r: number;

    // Temporary rotation, used for edit support
    tempRotation: number | null;

    // Disps that belong to this disp group
    // Set by the model compiler
    // COMPUTED PROPERTY, it's computed somewhere
    disps: DispBaseT[];
}

export class DispGroupPointer extends DispBase {
    static override resetMoveData(disp): void {
        disp.tempRotation = null;
        DispBase.resetMoveData(disp);
    }

    static targetGroupId(disp: DispGroupPointerT): number {
        return DispGroupPointerPartial.targetGroupId(disp);
    }

    static setTargetGroupId(disp: DispGroupPointerT, val: number): void {
        DispGroupPointerPartial.setTargetGroupId(disp, val);
    }

    static setTargetGroupName(
        disp: DispGroupPointerT,
        coordSetId: number,
        name: string,
    ): void {
        DispGroupPointerPartial.setTargetGroupName(disp, coordSetId, name);
    }

    static targetGroupCoordSetId(disp: DispGroupPointerT): number | null {
        if (disp.tn == null || disp.tn.indexOf("|") === -1) return null;
        return parseInt(disp.tn.split("|")[0]);
    }

    static targetGroupName(disp: DispGroupPointerT): string | null {
        if (disp.tn == null || disp.tn.indexOf("|") === -1) return null;
        return disp.tn.split("|")[1];
    }

    static verticalScale(disp: DispGroupPointerT): number {
        return disp.vs;
    }

    static horizontalScale(disp: DispGroupPointerT): number {
        return disp.hs;
    }

    static rotation(disp: DispGroupPointerT): number {
        if (disp.r == null) return 0;
        return disp.r;
    }

    static setRotation(disp: DispGroupPointerT, val: number): void {
        disp.r = val;
    }

    static setCenterPoint(disp: DispGroupPointerT, x: number, y: number): void {
        disp.g = [x, y];
    }

    static override geom(disp): PointsT {
        return disp.g;
    }

    static disps(disp): DispBaseT[] | null {
        return disp.disps;
    }

    // ---------------
    // Delta move helpers

    static override deltaMoveHandle(
        handle: DispHandleI,
        dx: number,
        dy: number,
    ): void {
        const disp = <DispGroupPointerT>handle.disp;
        const center = DispGroupPointer.center(disp);

        const data = calculateRotationFromHandleDelta(
            handle,
            dx,
            dy,
            DispGroupPointer.rotation(disp),
            disp.tempRotation,
            center,
        );

        if (data == null) return;

        // We've rotate the disps, now store the current rotation
        DispGroupPointer.setRotation(disp, data.newRotation);
        disp.tempRotation = data.tempRotation;

        for (const childDisp of disp.disps) {
            const Wrapper = getWrapper(DispBase.type(childDisp));
            Wrapper.rotateAboutAxis(childDisp, center, data.deltaRotation);
        }
        DispBase.setBoundsNull(disp);
    }

    static override rotateAboutAxis(
        disp,
        center: PointI,
        rotationDegrees: number,
    ) {
        console.log("NOT IMPLEMENTED: Rotating child DispGroupPtrs");
    }

    // ---------------
    // Create Method

    static override create(coordSet: ModelCoordSet): DispGroupPointerT {
        let newDisp = {
            ...DispBase.create(coordSet, DispBase.TYPE_DGP),
            // From Text
            tg: null, // TextVerticalAlign.targetGroupId
            vs: 1.0, // TextHorizontalAlign.verticalScale
            hs: 1.0, // TextHorizontalAlign.horizontalScale
        };

        DispGroupPointer.setSelectable(newDisp, true);
        DispGroupPointer.setCenterPoint(newDisp, 0, 0);

        return newDisp;
    }

    static override makeShapeContext(
        context: PeekCanvasShapePropsContext,
    ): void {
        DispBase.makeShapeContext(context);

        const disp = <DispGroupPointerT>context.disp;

        if (disp.disps != null) {
            for (const childDisp of disp.disps) {
                if (DispBase.typeOf(childDisp) == DispType.text) {
                    context.addProp(
                        new ShapeProp(
                            ShapePropType.MultilineString,
                            DispText.text,
                            DispText.setText,
                            "Text",
                            { alternateDisp: childDisp },
                        ),
                    );
                }
            }
        }
    }

    // ---------------
    // Represent the disp as a user friendly string

    static override makeShapeStr(disp: DispGroupPointerT): string {
        let center = DispGroupPointer.center(disp);
        let str = DispBase.makeShapeStr(disp);
        if (DispGroupPointer.targetGroupName(disp))
            str += `\nName : ${DispGroupPointer.targetGroupName(disp)}`;
        str += `\nAt : ${parseInt(<any>center.x)}x${parseInt(<any>center.y)}`;
        return str;
    }

    /** Set Disp Group
     *
     * Change the template that this disp groupd points to.
     *
     * This is achived by deleting the current disp items in this group,
     * and adding the new templates in.
     *
     * @param dispGroupPtr
     * @param groupDisp
     * @param lookupService
     * @param branchTuple
     */
    static setDispGroup(
        dispGroupPtr: DispGroupPointerT,
        groupDisp: DispGroupT,
        groupDispCoordSetId: number,
        lookupService: PrivateDiagramLookupService,
        branchTuple: BranchTuple,
    ): void {
        let center = DispGroupPointer.center(dispGroupPtr);

        let oldDisps = branchTuple.disps.filter(
            (d) => DispBase.groupId(d) == DispBase.id(dispGroupPtr),
        );

        branchTuple.removeDisps(oldDisps);
        let coordSetId = branchTuple.coordSetId;
        let thisCoordSetLevelsByOrder = {};
        for (let level of lookupService.levelsOrderedByOrder(coordSetId)) {
            thisCoordSetLevelsByOrder[level.order] = level;
        }

        function findLevel(oldLevel): any {
            return thisCoordSetLevelsByOrder[oldLevel.order];
        }

        let newDisps = [];
        for (let disp of DispGroup.items(groupDisp)) {
            // INTERIM FIX - DON'T COPY TEXT ITEMS
            // This will need to be sorted more elegantly when we want to use Peek to
            // to create patches.
            if (DispBase.typeOf(disp) == DispType.text) continue;

            disp = DispBase.cloneDisp(disp);
            DispBase.setSelectable(disp, false);
            DispBase.setKey(disp, null);
            DispBase.setId(disp, null);
            DispBase.setReplacesHashId(disp, null);
            DispBase.setHashId(disp, null);

            lookupService._linkDispLookups(disp);

            // Convert this to this coord sets levels
            DispBase.setLevel(disp, findLevel(DispBase.level(disp)));

            DispBase.deltaMove(disp, center.x, center.y);
            DispBase.setGroupId(disp, DispBase.id(dispGroupPtr));
            newDisps.push(disp);
        }

        DispGroupPointer.setTargetGroupName(
            dispGroupPtr,
            groupDispCoordSetId,
            DispGroup.groupName(groupDisp),
        );
        branchTuple.addNewDisps(newDisps);
    }

    static override primaryActionHandlePoint(
        disp,
        margin: number,
    ): DispHandleI | null {
        return null;
    }

    static override handlePoints(disp, margin: number): DispHandleI[] {
        return makeRotateHandlePoints(
            disp,
            margin,
            DispGroupPointer.center(disp),
            DispGroupPointer.rotation(disp),
        );
    }
}
