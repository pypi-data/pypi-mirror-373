export class GraphDbLinkedVertex {
    //  he key of the vertex that joins the two segments
    key: string;

    //  The properties of this vertex
    props: {};

    //  The edges of this vertex
    edges: any[] = [];

    //  The other segments that this vertex belongs to
    linksToSegmentKeys: string[];
}
