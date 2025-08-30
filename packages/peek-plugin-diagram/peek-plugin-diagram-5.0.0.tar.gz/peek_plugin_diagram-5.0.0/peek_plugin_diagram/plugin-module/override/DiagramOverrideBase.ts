/** Delta Base
 *
 * Static accessors, the code is structured to use these static accessor classes to
 * improve the performance of rendering.
 *
 * Rendering will require a smaller memory footprint, and no class instantiation to
 * access the json data, just like the diffs.
 *
 * This is the base class of all diagram deltas.
 *
 *
 */
import { Tuple } from "@synerty/vortexjs";

export enum DiagramOverrideTypeE {
    Color,
    Highlight,
}

export abstract class DiagramOverrideBase extends Tuple {
    private static overrideNum: number = 0;
    public readonly key: string;

    protected constructor(
        public readonly modelSetKey: string,
        public readonly coordSetKey: string,
        public readonly overrideType: DiagramOverrideTypeE,
        tupleType: string,
    ) {
        super(tupleType);
        this.key = `${new Date().getTime()}=${DiagramOverrideBase.overrideNum++}`;
    }
}
