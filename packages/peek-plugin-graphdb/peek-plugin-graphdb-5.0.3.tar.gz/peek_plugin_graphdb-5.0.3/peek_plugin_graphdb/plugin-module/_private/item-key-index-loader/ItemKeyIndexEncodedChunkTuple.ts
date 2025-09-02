import { addTupleType, Tuple } from "@synerty/vortexjs";
import { graphDbTuplePrefix } from "../PluginNames";

@addTupleType
export class ItemKeyIndexEncodedChunkTuple extends Tuple {
    public static readonly tupleName =
        graphDbTuplePrefix + "ItemKeyIndexEncodedChunkTuple";

    chunkKey: string;
    lastUpdate: string;
    encodedData: string;

    constructor() {
        super(ItemKeyIndexEncodedChunkTuple.tupleName);
    }
}
