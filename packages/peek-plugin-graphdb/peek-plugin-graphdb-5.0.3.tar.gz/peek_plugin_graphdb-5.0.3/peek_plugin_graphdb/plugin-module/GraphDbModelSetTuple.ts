import { addTupleType, Tuple } from "@synerty/vortexjs";
import { graphDbTuplePrefix } from "./_private/PluginNames";

@addTupleType
export class GraphDbModelSetTuple extends Tuple {
    public static readonly tupleName =
        graphDbTuplePrefix + "GraphDbModelSetTuple";

    //  A private variable
    id: number;

    //  The unique key of this segment
    key: string;

    //  The unique name of this segment
    name: string;

    comment: string;
    propsJson: {};

    constructor() {
        super(GraphDbModelSetTuple.tupleName);
    }
}
