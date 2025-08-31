import { GraphDbLinkedEdge } from "./GraphDbLinkedEdge";
import { GraphDbLinkedVertex } from "./GraphDbLinkedVertex";
import { GraphDbTraceResultTuple } from "./GraphDbTraceResultTuple";

/** Linked Segment
 
 This tuple is the publicly exposed Segment
 
 */
export class GraphDbLinkedModel {
    //  The model set of this segment
    modelSetKey: string;

    //  The edges by key
    edgeByKey: { [key: string]: GraphDbLinkedEdge } = {};

    //  The vertexes by key
    vertexByKey: { [key: string]: GraphDbLinkedVertex } = {};

    static createFromTraceResult(
        traceResult: GraphDbTraceResultTuple,
    ): GraphDbLinkedModel {
        let self = new GraphDbLinkedModel();
        self.modelSetKey = traceResult.modelSetKey;

        for (let resultVertex of traceResult.vertexes) {
            let newVertex = new GraphDbLinkedVertex();
            newVertex.key = resultVertex.key;
            newVertex.props = resultVertex.props;
            self.vertexByKey[newVertex.key] = newVertex;
        }

        for (let resultEdge of traceResult.edges) {
            let newEdge = new GraphDbLinkedEdge();
            newEdge.key = resultEdge.key;
            newEdge.props = resultEdge.props;
            newEdge.srcVertex = self.vertexByKey[resultEdge.srcVertexKey];
            newEdge.dstVertex = self.vertexByKey[resultEdge.dstVertexKey];
            newEdge.srcVertex.edges.push(newEdge);
            newEdge.dstVertex.edges.push(newEdge);
            self.edgeByKey[newEdge.key] = newEdge;
        }

        return self;
    }
}
