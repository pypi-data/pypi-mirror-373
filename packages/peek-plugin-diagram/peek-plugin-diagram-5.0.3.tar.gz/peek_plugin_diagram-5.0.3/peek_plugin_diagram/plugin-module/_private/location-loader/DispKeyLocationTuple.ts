import { addTupleType, Tuple } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "@peek/peek_plugin_diagram/_private";

@addTupleType
export class DispKeyLocationTuple extends Tuple {
    public static readonly tupleName =
        diagramTuplePrefix + "DispKeyLocationTuple";

    coordSetKey: string;
    coordSetId: number;

    dispId: number;

    x: number;
    y: number;

    constructor() {
        super(DispKeyLocationTuple.tupleName);
    }

    static fromLocationJson(data: any[]): DispKeyLocationTuple {
        let self = new DispKeyLocationTuple();
        self.coordSetId = data[0];
        self.dispId = data[1];
        self.x = data[2];
        self.y = data[3];
        return self;
    }
}
