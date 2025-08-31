import { filter, first, takeUntil } from "rxjs/operators";
import { Injectable } from "@angular/core";
import {
    NgLifeCycleEvents,
    TupleSelector,
    VortexStatusService,
} from "@synerty/vortexjs";
import { GraphDbTupleService } from "./GraphDbTupleService";
import { GraphDbModelSetTuple } from "../GraphDbModelSetTuple";
import { GraphDbTraceConfigTuple } from "./tuples/GraphDbTraceConfigTuple";

/** Diagram Lookups offline cacher
 *
 * This Service is never unloaded, it makes sure that the lookups that the diagram
 * needs are always stored in the local DB.
 *
 * For NS, This is where the embedded web version reads it from.
 *
 */
@Injectable()
export class GraphDbOfflineTupleCacherService extends NgLifeCycleEvents {
    constructor(
        private tupleService: GraphDbTupleService,
        vortexStatusService: VortexStatusService,
    ) {
        super();

        // Delete data older than 7 days
        let date7DaysAgo = new Date(Date.now() - 7 * 24 * 3600 * 1000);

        let promise = null;
        if (vortexStatusService.snapshot.isOnline) {
            promise = this.tupleService.offlineStorage
                .deleteOldTuples(date7DaysAgo)
                .catch((err) =>
                    console.log(`ERROR: Failed to delete old tuples`),
                );
        } else {
            vortexStatusService.isOnline
                .pipe(takeUntil(this.onDestroyEvent))
                .pipe(filter((val) => val === true))
                .pipe(first())
                .subscribe(() => {
                    this.tupleService.offlineStorage
                        .deleteOldTuples(date7DaysAgo)
                        .catch((err) =>
                            console.log(`ERROR: Failed to delete old tuples`),
                        );
                });
            promise = Promise.resolve();
        }

        promise.then(() => {
            this.loadModelSet();
            this.loadTraceConfigs();
        });
    }

    /**
     * Cache Model Set
     *
     * This method caches the model set list for offline use.
     *
     */
    private loadModelSet() {
        let ts = new TupleSelector(GraphDbModelSetTuple.tupleName, {});

        this.tupleService.offlineObserver
            .subscribeToTupleSelector(ts)
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe(() => this.tupleService.offlineObserver.flushCache(ts));
    }

    /**
     * Cache Trace Configs
     *
     * This method caches the Trace Configs
     *
     */
    private loadTraceConfigs() {
        let ts = new TupleSelector(GraphDbTraceConfigTuple.tupleName, {});

        this.tupleService.offlineObserver
            .subscribeToTupleSelector(ts)
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe(() => this.tupleService.offlineObserver.flushCache(ts));
    }
}
