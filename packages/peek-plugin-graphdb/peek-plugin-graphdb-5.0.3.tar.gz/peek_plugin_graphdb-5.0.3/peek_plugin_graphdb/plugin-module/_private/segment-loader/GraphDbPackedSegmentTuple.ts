import { addTupleType, Tuple } from "@synerty/vortexjs";
import { graphDbTuplePrefix } from "../PluginNames";

@addTupleType
export class GraphDbPackedSegmentTuple extends Tuple {
    public static readonly tupleName =
        graphDbTuplePrefix + "GraphDbPackedSegmentTuple";

    //  The unique key of this segment
    key: string;

    //  The raw packed data of the segment (Not in vortex.Tuple format)
    packedJson: string;

    constructor() {
        super(GraphDbPackedSegmentTuple.tupleName);
        this._rawJonableFields = ["key", "packedJson"];
    }
}
