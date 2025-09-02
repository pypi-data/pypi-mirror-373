import { addTupleType, Tuple } from "@synerty/vortexjs";
import { graphDbTuplePrefix } from "../PluginNames";

@addTupleType
export class GraphDbPackedItemKeyTuple extends Tuple {
    public static readonly tupleName =
        graphDbTuplePrefix + "GraphDbPackedItemKeyTuple";

    //  The unique key of this segment
    key: string;

    //  The raw packed data of the segment (Not in vortex.Tuple format)
    packedJson: string;

    constructor() {
        super(GraphDbPackedItemKeyTuple.tupleName);
        this._rawJonableFields = ["key", "packedJson"];
    }
}
