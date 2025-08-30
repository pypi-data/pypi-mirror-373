import { addTupleType, Tuple } from "@synerty/vortexjs";
import { graphDbTuplePrefix } from "../PluginNames";

@addTupleType
export class ServerStatusTuple extends Tuple {
    public static readonly tupleName = graphDbTuplePrefix + "ServerStatusTuple";

    segmentCompilerQueueStatus: boolean;
    segmentCompilerQueueSize: number;
    segmentCompilerQueueProcessedTotal: number;
    segmentCompilerQueueLastError: string;

    itemKeyIndexCompilerQueueStatus: boolean;
    itemKeyIndexCompilerQueueSize: number;
    itemKeyIndexCompilerQueueProcessedTotal: number;
    itemKeyIndexCompilerQueueLastError: string;

    constructor() {
        super(ServerStatusTuple.tupleName);
    }
}
