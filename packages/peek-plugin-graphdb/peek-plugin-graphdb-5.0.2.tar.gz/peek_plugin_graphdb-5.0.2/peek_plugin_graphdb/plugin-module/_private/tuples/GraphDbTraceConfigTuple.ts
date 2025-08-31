import { addTupleType, Tuple } from "@synerty/vortexjs";
import { graphDbTuplePrefix } from "../PluginNames";
import { GraphDbTraceConfigRuleTuple } from "./GraphDbTraceConfigRuleTuple";

@addTupleType
export class GraphDbTraceConfigTuple extends Tuple {
    public static readonly tupleName =
        graphDbTuplePrefix + "GraphDbTraceConfigTuple";

    //  The modelSetId for this segment.
    modelSetKey: string;

    // The unique key of this trace config [Required]
    key: string;

    // The name for this trace config [Required]
    name: string;

    // The display title for this trace config [Required]
    title: string;

    // The name for this trace config
    rules: GraphDbTraceConfigRuleTuple[];

    // The comment for this trace config
    comment: string | null;

    // Is this rule enabled [Required]
    isEnabled: boolean;

    constructor() {
        super(GraphDbTraceConfigTuple.tupleName);
    }
}
