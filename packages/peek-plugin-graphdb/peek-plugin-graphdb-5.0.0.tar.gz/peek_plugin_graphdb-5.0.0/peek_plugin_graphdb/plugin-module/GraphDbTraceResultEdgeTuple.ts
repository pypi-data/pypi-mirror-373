import { addTupleType, Tuple } from "@synerty/vortexjs";
import { graphDbTuplePrefix } from "./_private/PluginNames";
import { GraphDbLinkedEdge } from "./GraphDbLinkedEdge";

/** GraphDB Trace Result Edge Tuple
 *
 * This tuple contains the result of running a trace on the model
 *
 */
@addTupleType
export class GraphDbTraceResultEdgeTuple extends Tuple {
    public static readonly tupleName =
        graphDbTuplePrefix + "GraphDbTraceResultEdgeTuple";
    static readonly DIR_UNKNOWN = GraphDbLinkedEdge.DIR_UNKNOWN;
    static readonly DIR_SRC_IS_UPSTREAM = GraphDbLinkedEdge.DIR_SRC_IS_UPSTREAM;
    static readonly DIR_SRC_IS_DOWNSTREAM =
        GraphDbLinkedEdge.DIR_SRC_IS_DOWNSTREAM;
    static readonly DIR_SRC_IS_BOTH = GraphDbLinkedEdge.DIR_SRC_IS_BOTH;
    //  The key of this edge
    key: string;
    //  The key of the Trace Config
    srcVertexKey: string;
    //  The key of the vertex start point of this trace
    dstVertexKey: string;
    //  Is source upstream or downstream?
    srcDirection: number;
    //  The edges
    props: {};

    constructor() {
        super(GraphDbTraceResultEdgeTuple.tupleName);
    }
}
