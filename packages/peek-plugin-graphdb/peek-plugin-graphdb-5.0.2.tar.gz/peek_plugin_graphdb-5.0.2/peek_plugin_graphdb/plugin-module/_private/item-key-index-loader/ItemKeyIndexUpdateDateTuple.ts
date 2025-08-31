import { addTupleType, Tuple } from "@synerty/vortexjs";
import { graphDbTuplePrefix } from "../PluginNames";

@addTupleType
export class ItemKeyIndexUpdateDateTuple extends Tuple {
    public static readonly tupleName =
        graphDbTuplePrefix + "ItemKeyIndexUpdateDateTuple";
    initialLoadComplete: boolean = false;
    updateDateByChunkKey: {} = {};
    // Improve performance of the JSON serialisation
    protected override _rawJonableFields = [
        "initialLoadComplete",
        "updateDateByChunkKey",
    ];

    constructor() {
        super(ItemKeyIndexUpdateDateTuple.tupleName);
    }
}
