import { addTupleType, Tuple } from "@synerty/vortexjs";
import { graphDbTuplePrefix } from "../PluginNames";

@addTupleType
export class EncodedSegmentChunkTuple extends Tuple {
    public static readonly tupleName =
        graphDbTuplePrefix + "EncodedSegmentChunkTuple";

    chunkKey: string;
    lastUpdate: string;
    encodedData: string;

    constructor() {
        super(EncodedSegmentChunkTuple.tupleName);
    }
}
