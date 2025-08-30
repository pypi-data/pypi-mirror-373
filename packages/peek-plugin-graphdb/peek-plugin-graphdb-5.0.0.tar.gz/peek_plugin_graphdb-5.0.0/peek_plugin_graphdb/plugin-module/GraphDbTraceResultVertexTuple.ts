import { addTupleType, Tuple } from "@synerty/vortexjs";
import { graphDbTuplePrefix } from "./_private/PluginNames";

@addTupleType
export class GraphDbTraceResultVertexTuple extends Tuple {
    public static readonly tupleName =
        graphDbTuplePrefix + "GraphDbTraceResultVertexTuple";

    //  The key of this vertex
    key: string;

    //  The properties of this vertex
    props: {};

    constructor() {
        super(GraphDbTraceResultVertexTuple.tupleName);
    }
}
