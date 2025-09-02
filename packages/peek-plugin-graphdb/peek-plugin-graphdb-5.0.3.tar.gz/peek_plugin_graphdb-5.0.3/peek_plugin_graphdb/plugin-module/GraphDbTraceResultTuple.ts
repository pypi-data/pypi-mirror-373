import { addTupleType, Tuple } from "@synerty/vortexjs";
import { graphDbTuplePrefix } from "./_private/PluginNames";
import { GraphDbTraceResultVertexTuple } from "./GraphDbTraceResultVertexTuple";
import { GraphDbTraceResultEdgeTuple } from "./GraphDbTraceResultEdgeTuple";

@addTupleType
export class GraphDbTraceResultTuple extends Tuple {
    public static readonly tupleName =
        graphDbTuplePrefix + "GraphDbTraceResultTuple";

    //  The key of the model set that the resuslt was created with.
    modelSetKey: string;

    //  The key of the Trace Config
    traceConfigKey: string;

    //  The key of the vertex start point of this trace
    startVertexKey: string;

    //  The edges
    edges: GraphDbTraceResultEdgeTuple[] = [];

    //  The vertexes
    vertexes: GraphDbTraceResultVertexTuple[] = [];

    //  Trace Aborted Message
    traceAbortedMessage: string | null;

    constructor() {
        super(GraphDbTraceResultTuple.tupleName);
    }
}
