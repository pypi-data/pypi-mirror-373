import { Injectable } from "@angular/core";
import { NgLifeCycleEvents, TupleSelector } from "@synerty/vortexjs";
import { PrivateTracerService } from "./_private/tracer-service";
import { GraphDbTraceResultTuple } from "./GraphDbTraceResultTuple";
import { GraphDbLinkedModel } from "./GraphDbLinkedModel";
import { GraphDbTupleService } from "./_private";
import { GraphDbTraceConfigTuple } from "./_private/tuples/GraphDbTraceConfigTuple";
import { map } from "rxjs/operators";
import { Observable } from "rxjs";

export interface TraceConfigListItemI {
    name: string;
    title: string;
    key: string;
}

// ----------------------------------------------------------------------------
/** LocationIndex Cache
 *
 * This class has the following responsibilities:
 *
 * 1) Maintain a local storage-old of the index
 *
 * 2) Return DispKey locations based on the index.
 *
 */
@Injectable()
export class GraphDbService extends NgLifeCycleEvents {
    constructor(
        private tupleService: GraphDbTupleService,
        private tracerService: PrivateTracerService,
    ) {
        super();
    }

    /** Does Key Exist
     *
     * Does the key exist in the GraphDB Model
     *
     */
    doesKeyExist(
        modelSetKey: string,
        vertexOrEdgeKey: string,
    ): Promise<boolean> {
        return this.tracerService.doesKeyExist(modelSetKey, vertexOrEdgeKey);
    }

    /** Get Trace Result
     *
     * Trace the graph with a pre-defined trace rule, and return a flat model
     *
     */
    getTraceResult(
        modelSetKey: string,
        traceConfigKey: string,
        startVertexKey: string,
        maxVertexes: number | null = null,
    ): Promise<GraphDbTraceResultTuple> {
        return this.tracerService.runTrace(
            modelSetKey,
            traceConfigKey,
            startVertexKey,
            maxVertexes,
        );
    }

    /** Get Trace Model
     *
     * Trace the graph with a pre-defined trace rule, and return a linked model
     *
     */
    getTraceModel(
        modelSetKey: string,
        traceConfigKey: string,
        startVertexKey: string,
        maxVertexes: number | null = null,
    ): Promise<GraphDbLinkedModel> {
        return this.tracerService
            .runTrace(modelSetKey, traceConfigKey, startVertexKey, maxVertexes)
            .then((result: GraphDbTraceResultTuple) => {
                return GraphDbLinkedModel.createFromTraceResult(result);
            });
    }

    /** Trace Config List Items Observable
     *
     * Trace the graph with a pre-defined trace rule, and return a linked model
     *
     */
    traceConfigListItemsObservable(
        modelSetKey: string,
    ): Observable<TraceConfigListItemI[]> {
        const ts = new TupleSelector(GraphDbTraceConfigTuple.tupleName, {
            modelSetKey: modelSetKey,
        });

        return this.tupleService.offlineObserver
            .subscribeToTupleSelector(ts)
            .pipe(
                map((tuples: GraphDbTraceConfigTuple[]) => {
                    const out = [];
                    tuples.sort((a, b) =>
                        a.title == b.title ? 0 : a.title < b.title ? -1 : 1,
                    );
                    for (let tuple of tuples) {
                        if (!tuple.isEnabled) continue;
                        out.push({
                            name: tuple.name,
                            title: tuple.title,
                            key: tuple.key,
                        });
                    }
                    return out;
                }),
            );
    }
}
