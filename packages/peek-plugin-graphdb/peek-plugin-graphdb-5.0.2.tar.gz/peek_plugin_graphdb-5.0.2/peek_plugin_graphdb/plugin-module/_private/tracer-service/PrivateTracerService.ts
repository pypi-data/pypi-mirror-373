import { filter, first, takeUntil } from "rxjs/operators";
import { Injectable } from "@angular/core";
import {
    NgLifeCycleEvents,
    TupleSelector,
    VortexService,
    VortexStatusService,
} from "@synerty/vortexjs";
import { PrivateSegmentLoaderService } from "../segment-loader/PrivateSegmentLoaderService";
import { GraphDbTupleService } from "../GraphDbTupleService";
import { GraphDbTraceConfigTuple } from "../tuples/GraphDbTraceConfigTuple";
import { ItemKeyIndexLoaderService } from "../item-key-index-loader";
import { GraphDbTraceResultTuple } from "../../GraphDbTraceResultTuple";
import { PrivateRunTrace } from "./PrivateRunTrace";
import { GraphDbDoesKeyExistTuple } from "../../GraphDbDoesKeyExistTuple";
import { DeviceOfflineCacheService } from "@peek/peek_core_device";

// ----------------------------------------------------------------------------

class _TraceAbortedWithMessageError extends Error {}

// ----------------------------------------------------------------------------
/** Tracer
 *
 * This class either asks the server for the trace result or traces locally
 *
 */
@Injectable()
export class PrivateTracerService extends NgLifeCycleEvents {
    constructor(
        private vortexService: VortexService,
        private vortexStatusService: VortexStatusService,
        private segmentLoader: PrivateSegmentLoaderService,
        private itemKeyLoader: ItemKeyIndexLoaderService,
        private tupleService: GraphDbTupleService,
        private deviceCacheControllerService: DeviceOfflineCacheService,
    ) {
        super();
    }

    doesKeyExist(
        modelSetKey: string,
        vertexOrEdgeKey: string,
    ): Promise<boolean> {
        if (modelSetKey == null || modelSetKey.length == 0) {
            return Promise.reject("We've been passed a null/empty modelSetKey");
        }

        if (vertexOrEdgeKey == null || vertexOrEdgeKey.length == 0) {
            return Promise.reject(
                "We've been passed a null/empty vertexOrEdgeKey",
            );
        }

        if (this.vortexStatusService.snapshot.isOnline) {
            return this.doesKeyExistServer(modelSetKey, vertexOrEdgeKey);
        }

        const offlineEnabled =
            this.itemKeyLoader.offlineEnabled &&
            this.segmentLoader.offlineEnabled;

        if (!offlineEnabled) {
            throw new Error(
                "Peek is not online," +
                    " and the offline cache has not completed loading." +
                    " The trace can't be run.",
            );
        }

        return this.doesKeyExistLocal(modelSetKey, vertexOrEdgeKey);
    }

    /** Get Segments
     *
     * Get the objects with matching keywords from the index..
     *
     */
    runTrace(
        modelSetKey: string,
        traceConfigKey: string,
        startVertexKey: string,
        maxVertexes: number | null = null,
    ): Promise<GraphDbTraceResultTuple> {
        if (modelSetKey == null || modelSetKey.length == 0) {
            return Promise.reject("We've been passed a null/empty modelSetKey");
        }

        if (traceConfigKey == null || traceConfigKey.length == 0) {
            return Promise.reject(
                "We've been passed a null/empty traceConfigKey",
            );
        }

        if (startVertexKey == null || startVertexKey.length == 0) {
            return Promise.reject(
                "We've been passed a null/empty startVertexKey",
            );
        }

        if (this.vortexStatusService.snapshot.isOnline) {
            return this.runServerTrace(
                modelSetKey,
                traceConfigKey,
                startVertexKey,
                maxVertexes,
            );
        }

        if (!this.deviceCacheControllerService.offlineModeEnabled) {
            throw new Error(
                "Peek is not online," +
                    " and offline caching is not enabled" +
                    " or has not completed loading." +
                    " The trace can't be run.",
            );
        }

        return this.runLocalTrace(
            modelSetKey,
            traceConfigKey,
            startVertexKey,
            maxVertexes,
        );
    }

    private loadTraceConfig(
        modelSetKey: string,
        traceConfigKey: string,
    ): Promise<GraphDbTraceConfigTuple | null> {
        let ts = new TupleSelector(GraphDbTraceConfigTuple.tupleName, {});
        let promise = this.tupleService.offlineObserver
            .promiseFromTupleSelector(ts)
            .then((tuples: GraphDbTraceConfigTuple[]) => {
                if (!tuples.length) return null;

                for (let tuple of tuples) {
                    if (
                        tuple.modelSetKey == modelSetKey &&
                        tuple.key == traceConfigKey
                    ) {
                        return tuple;
                    }
                }
                return null;
            });
        return promise;
    }

    private async doesKeyExistServer(
        modelSetKey: string,
        vertexOrEdgeKey: string,
    ): Promise<boolean> {
        const ts = new TupleSelector(GraphDbDoesKeyExistTuple.tupleName, {
            modelSetKey: modelSetKey,
            vertexOrEdgeKey: vertexOrEdgeKey,
        });

        if (!this.vortexStatusService.snapshot.isOnline) {
            await this.vortexStatusService.isOnline
                .pipe(filter((online) => online))
                .pipe(first())
                .toPromise();
        }

        const tuples: GraphDbDoesKeyExistTuple[] = <any>(
            await this.tupleService.offlineObserver.pollForTuples(ts, false)
        );
        return tuples.length != 0 && tuples[0].exists;
    }

    private async doesKeyExistLocal(
        modelSetKey: string,
        vertexOrEdgeKey: string,
    ): Promise<boolean> {
        const keys = await this.itemKeyLoader.getSegmentKeys(
            modelSetKey,
            vertexOrEdgeKey,
        );
        return keys.length != 0;
    }

    private runServerTrace(
        modelSetKey: string,
        traceConfigKey: string,
        startVertexKey: string,
        maxVertexes: number,
    ): Promise<GraphDbTraceResultTuple> {
        let ts = new TupleSelector(GraphDbTraceResultTuple.tupleName, {
            modelSetKey: modelSetKey,
            traceConfigKey: traceConfigKey,
            startVertexKey: startVertexKey,
            maxVertexes: maxVertexes,
        });

        let isOnlinePromise: any = this.vortexStatusService.snapshot.isOnline
            ? Promise.resolve()
            : this.vortexStatusService.isOnline
                  .pipe(filter((online) => online))
                  .pipe(first())
                  .toPromise();

        return isOnlinePromise
            .then(() =>
                this.tupleService.offlineObserver.pollForTuples(ts, false),
            )
            .then((tuples) => tuples[0]);
    }

    private runLocalTrace(
        modelSetKey: string,
        traceConfigKey: string,
        startVertexKey: string,
        maxVertexes: number,
    ): Promise<GraphDbTraceResultTuple> {
        let result = new GraphDbTraceResultTuple();
        result.modelSetKey = modelSetKey;
        result.traceConfigKey = traceConfigKey;
        result.startVertexKey = startVertexKey;

        let traceConfigParam = null;

        let promise: any = this.loadTraceConfig(modelSetKey, traceConfigKey)
            // Prepare the trace config
            .then((traceConfig: GraphDbTraceConfigTuple) => {
                // Assign the trace config for the RunTrace class
                traceConfigParam = traceConfig;

                // Preprocess some trace rules
                for (let rule of traceConfig.rules) {
                    rule.prepare();
                }
            })
            .then(() => {
                return this.itemKeyLoader.getSegmentKeys(
                    modelSetKey,
                    startVertexKey,
                );
            })
            .then((startSegmentKeys: string[]) => {
                const runTrace = new PrivateRunTrace(
                    result,
                    traceConfigParam,
                    this.segmentLoader,
                    startVertexKey,
                    startSegmentKeys,
                    maxVertexes,
                );

                return runTrace.run();
            })
            .then(() => result);
        return promise;
    }
}
