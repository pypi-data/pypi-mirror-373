import { addTupleType, Tuple } from "@synerty/vortexjs";
import { graphDbTuplePrefix } from "./_private/PluginNames";

@addTupleType
export class GraphDbDoesKeyExistTuple extends Tuple {
    public static readonly tupleName =
        graphDbTuplePrefix + "GraphDbDoesKeyExistTuple";

    // Does the key exist in the model
    exists: boolean;

    constructor() {
        super(GraphDbDoesKeyExistTuple.tupleName);
    }
}
