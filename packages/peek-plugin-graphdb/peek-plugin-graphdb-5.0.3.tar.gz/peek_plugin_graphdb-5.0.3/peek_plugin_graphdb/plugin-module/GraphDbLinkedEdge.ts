import { GraphDbLinkedVertex } from "./GraphDbLinkedVertex";

export class GraphDbLinkedEdge {
    static readonly DIR_UNKNOWN = 0;
    static readonly DIR_SRC_IS_UPSTREAM = 1;
    static readonly DIR_SRC_IS_DOWNSTREAM = 2;
    static readonly DIR_SRC_IS_BOTH = 3;
    //  The key of this edge
    key: string;
    //  The src vertex
    srcVertex: GraphDbLinkedVertex;
    //  The dst vertex
    dstVertex: GraphDbLinkedVertex;
    //  Is source upstream or downstream?
    srcDirection: number;
    //  The properties of this edge
    props: {};

    getOtherVertex(vertexKey: string): GraphDbLinkedVertex {
        if (this.srcVertex.key == vertexKey) return this.dstVertex;
        return this.srcVertex;
    }
}
