import { GraphDbLinkedEdge } from "./GraphDbLinkedEdge";
import { GraphDbLinkedVertex } from "./GraphDbLinkedVertex";

/** Linked Segment
 
 This tuple is the publicly exposed Segment
 
 */
export class GraphDbLinkedSegment {
    //  The unique key of this segment
    key: string;

    //  The model set of this segment
    modelSetKey: string;

    //  The edges by key
    edgeByKey: { [key: string]: GraphDbLinkedEdge } = {};

    //  The vertexes by key
    vertexByKey: { [key: string]: GraphDbLinkedVertex } = {};

    unpackJson(
        packedJson: string,
        key: string,
        modelSetKey: string,
    ): GraphDbLinkedSegment {
        // Reconstruct the data
        let jsonDict: {} = JSON.parse(packedJson);

        this.key = key;
        this.modelSetKey = modelSetKey;

        let linksToSegmentKeysByVertexKey = {};
        for (let jsonLink of jsonDict["links"]) {
            let vertexKey = jsonLink["vk"];
            let segmentKey = jsonLink["sk"];

            let list = linksToSegmentKeysByVertexKey[vertexKey];
            if (list == null) {
                list = [];
                linksToSegmentKeysByVertexKey[vertexKey] = list;
            }

            list.push(segmentKey);
        }

        for (let jsonVertex of jsonDict["vertexes"]) {
            let newVertex = new GraphDbLinkedVertex();
            newVertex.key = jsonVertex["k"];
            newVertex.props = jsonVertex["p"];
            if (newVertex.key in linksToSegmentKeysByVertexKey)
                newVertex.linksToSegmentKeys =
                    linksToSegmentKeysByVertexKey[newVertex.key];
            this.vertexByKey[newVertex.key] = newVertex;
        }

        for (let jsonEdge of jsonDict["edges"]) {
            let newEdge = new GraphDbLinkedEdge();
            newEdge.key = jsonEdge["k"];
            newEdge.srcDirection = jsonEdge["sd"];
            newEdge.props = jsonEdge["p"];
            newEdge.srcVertex = this.vertexByKey[jsonEdge["sk"]];
            newEdge.dstVertex = this.vertexByKey[jsonEdge["dk"]];
            newEdge.srcVertex.edges.push(newEdge);
            newEdge.dstVertex.edges.push(newEdge);
            this.edgeByKey[newEdge.key] = newEdge;
        }

        return this;
    }
}
