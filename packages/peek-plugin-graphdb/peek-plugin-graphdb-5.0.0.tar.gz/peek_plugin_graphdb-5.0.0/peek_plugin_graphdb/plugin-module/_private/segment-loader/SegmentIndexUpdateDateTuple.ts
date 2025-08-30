import { addTupleType, Tuple } from "@synerty/vortexjs";
import { graphDbTuplePrefix } from "../PluginNames";

@addTupleType
export class SegmentIndexUpdateDateTuple extends Tuple {
    public static readonly tupleName =
        graphDbTuplePrefix + "SegmentIndexUpdateDateTuple";
    initialLoadComplete: boolean = false;
    updateDateByChunkKey: {} = {};
    // Improve performance of the JSON serialisation
    protected override _rawJonableFields = [
        "initialLoadComplete",
        "updateDateByChunkKey",
    ];

    constructor() {
        super(SegmentIndexUpdateDateTuple.tupleName);
    }
}
