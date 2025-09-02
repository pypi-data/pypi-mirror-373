import { Observable, Subject } from "rxjs";
import { filter, first, takeUntil } from "rxjs/operators";
import { Injectable } from "@angular/core";
import {
    NgLifeCycleEvents,
    Payload,
    PayloadEnvelope,
    TupleOfflineStorageNameService,
    TupleOfflineStorageService,
    TupleSelector,
    TupleStorageBatchSaveArguments,
    TupleStorageFactoryService,
    VortexService,
    VortexStatusService,
} from "@synerty/vortexjs";

import {
    graphDbCacheStorageName,
    graphDbFilt,
    graphDbTuplePrefix,
} from "../PluginNames";
import { ItemKeyIndexEncodedChunkTuple } from "./ItemKeyIndexEncodedChunkTuple";
import { ItemKeyIndexUpdateDateTuple } from "./ItemKeyIndexUpdateDateTuple";
import { ItemKeyTuple } from "./ItemKeyTuple";
import { GraphDbModelSetTuple } from "../../GraphDbModelSetTuple";
import { GraphDbTupleService } from "../GraphDbTupleService";
import { GraphDbPackedItemKeyTuple } from "./GraphDbPackedItemKeyTuple";
import {
    DeviceOfflineCacheService,
    OfflineCacheLoaderStatusTuple,
} from "@peek/peek_core_device";

// ----------------------------------------------------------------------------

let clientItemKeyIndexWatchUpdateFromDeviceFilt = Object.assign(
    { key: "clientItemKeyIndexWatchUpdateFromDevice" },
    graphDbFilt,
);

const cacheAll = "cacheAll";

// ----------------------------------------------------------------------------
/** ItemKeyIndexChunkTupleSelector
 *
 * This is just a short cut for the tuple selector
 */

class ItemKeyIndexChunkTupleSelector extends TupleSelector {
    constructor(private chunkKey: string) {
        super(graphDbTuplePrefix + "ItemKeyIndexChunkTuple", { key: chunkKey });
    }

    override toOrderedJsonStr(): string {
        return this.chunkKey;
    }
}

// ----------------------------------------------------------------------------
/** UpdateDateTupleSelector
 *
 * This is just a short cut for the tuple selector
 */
class UpdateDateTupleSelector extends TupleSelector {
    constructor() {
        super(ItemKeyIndexUpdateDateTuple.tupleName, {});
    }
}

// ----------------------------------------------------------------------------
/** hash method
 */
let BUCKET_COUNT = 8192;

function keyChunk(modelSetKey: string, key: string): string {
    /** Object ID Chunk
     
     This method creates an int from 0 to MAX, representing the hash bucket for this
     object Id.
     
     This is simple, and provides a reasonable distribution
     
     @param modelSetKey: The key of the model set that the itemKeyIndexs are in
     @param key: The key of the itemKeyIndex to get the chunk key for
     
     @return: The bucket / chunkKey where you'll find the object with this ID
     
     */
    if (key == null || key.length == 0)
        throw new Error("key is None or zero length");

    let bucket = 0;

    for (let i = 0; i < key.length; i++) {
        bucket = (bucket << 5) - bucket + key.charCodeAt(i);
        bucket |= 0; // Convert to 32bit integer
    }

    bucket = bucket & (BUCKET_COUNT - 1);

    return `${modelSetKey}.${bucket}`;
}

// ----------------------------------------------------------------------------
/** ItemKeyIndex Cache
 *
 * This class has the following responsibilities:
 *
 * 1) Maintain a local storage of the index
 *
 * 2) Return DispKey graphdb based on the index.
 *
 */
@Injectable()
export class ItemKeyIndexLoaderService extends NgLifeCycleEvents {
    private UPDATE_CHUNK_FETCH_SIZE = 32;

    // Every 100 chunks from the server
    private SAVE_POINT_ITERATIONS = 100;

    // Saving the cache after each chunk is so expensive, we only do it every 20 or so
    private chunksSavedSinceLastIndexSave = 0;

    private index: ItemKeyIndexUpdateDateTuple | null = null;
    private askServerChunks: ItemKeyIndexUpdateDateTuple[] = [];

    private _hasLoaded = false;

    private _hasLoadedSubject = new Subject<void>();
    private storage: TupleOfflineStorageService;

    private _statusSubject = new Subject<OfflineCacheLoaderStatusTuple>();
    private _status = new OfflineCacheLoaderStatusTuple();

    private modelSetByIds: { [id: number]: GraphDbModelSetTuple } = {};
    private _hasModelSetLoaded = false;

    constructor(
        private vortexService: VortexService,
        private vortexStatusService: VortexStatusService,
        storageFactory: TupleStorageFactoryService,
        private tupleService: GraphDbTupleService,
        private deviceCacheControllerService: DeviceOfflineCacheService,
    ) {
        super();
        this._status.pluginName = "peek_plugin_graphdb";
        this._status.indexName = "Key Index";

        this.storage = new TupleOfflineStorageService(
            storageFactory,
            new TupleOfflineStorageNameService(
                graphDbCacheStorageName + ".item_key",
            ),
        );

        this.setupVortexSubscriptions();

        this.deviceCacheControllerService.offlineModeEnabled$
            .pipe(takeUntil(this.onDestroyEvent))
            .pipe(filter((v) => v))
            .pipe(first())
            .subscribe(() => {
                this.initialLoad();
            });

        this.deviceCacheControllerService.triggerCachingStartObservable
            .pipe(takeUntil(this.onDestroyEvent))
            .pipe(filter((v) => v))
            .subscribe(() => {
                this.askServerForUpdates();
                this._notifyStatus();
            });

        this.deviceCacheControllerService.triggerCachingResumeObservable
            .pipe(takeUntil(this.onDestroyEvent))

            .subscribe(() => {
                this._notifyStatus();
                this.askServerForNextUpdateChunk();
            });
    }

    isReady(): boolean {
        return this._hasLoaded;
    }

    isReadyObservable(): Observable<void> {
        return this._hasLoadedSubject;
    }

    statusObservable(): Observable<OfflineCacheLoaderStatusTuple> {
        return this._statusSubject;
    }

    status(): OfflineCacheLoaderStatusTuple {
        return this._status;
    }

    get offlineEnabled(): boolean {
        return this.index.initialLoadComplete;
    }

    /** Get Segment Keys
     *
     * Get the objects with matching keywords from the index..
     *
     */
    getSegmentKeys(
        modelSetKey: string,
        key: string,
        itemType: number = ItemKeyTuple.ITEM_TYPE_VERTEX,
    ): Promise<string[]> {
        return this.getItemKeys(modelSetKey, [key]).then(
            (tuples: ItemKeyTuple[]) => {
                let keys = [];
                for (let tuple of tuples) {
                    // if (tuple.itemType == itemType) {
                    for (let segmentKey of tuple.segmentKeys) {
                        keys.push(segmentKey);
                    }
                    // }
                }
                return keys;
            },
        );
    }

    private _notifyReady(): void {
        if (this._hasModelSetLoaded && this._hasLoaded)
            this._hasLoadedSubject.next();
    }

    private _notifyStatus(paused: boolean = false): void {
        this._status.lastCheckDate = new Date();
        this._status.paused = paused;
        this._status.initialFullLoadComplete = this.index.initialLoadComplete;

        this._status.loadingQueueCount = 0;
        for (let chunk of this.askServerChunks) {
            this._status.loadingQueueCount += Object.keys(
                chunk.updateDateByChunkKey,
            ).length;
        }

        this._statusSubject.next(this._status);
        this.deviceCacheControllerService.updateLoaderCachingStatus(
            this._status,
        );
    }

    /** Initial load
     *
     * Load the dates of the index buckets and ask the server if it has any updates.
     */
    private initialLoad(): void {
        this.storage
            .loadTuples(new UpdateDateTupleSelector())
            .then((tuplesAny: any[]) => {
                let tuples: ItemKeyIndexUpdateDateTuple[] = tuplesAny;
                if (tuples.length === 0) {
                    this.index = new ItemKeyIndexUpdateDateTuple();
                } else {
                    this.index = tuples[0];

                    if (this.index.initialLoadComplete) {
                        this._hasLoaded = true;
                        this._notifyReady();
                    }
                }

                this._notifyStatus();
            });
    }

    private setupVortexSubscriptions(): void {
        // Services don't have destructors, I'm not sure how to unsubscribe.
        this.vortexService
            .createEndpointObservable(
                this,
                clientItemKeyIndexWatchUpdateFromDeviceFilt,
            )
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((payloadEnvelope: PayloadEnvelope) => {
                this.processChunksFromServer(payloadEnvelope);
            });
    }

    private areWeTalkingToTheServer(): boolean {
        return (
            this.deviceCacheControllerService.offlineModeEnabled &&
            this.vortexStatusService.snapshot.isOnline
        );
    }

    /** Ask Server For Updates
     *
     * Tell the server the state of the chunks in our index and ask if there
     * are updates.
     *
     */
    private askServerForUpdates() {
        if (!this.areWeTalkingToTheServer()) return;

        // If we're still caching, then exit
        if (this.askServerChunks.length != 0) {
            this.askServerForNextUpdateChunk();
            return;
        }

        this.tupleService.observer
            .pollForTuples(new UpdateDateTupleSelector())
            .then((tuplesAny: any) => {
                let serverIndex: ItemKeyIndexUpdateDateTuple = tuplesAny[0];
                let keys = Object.keys(serverIndex.updateDateByChunkKey);
                let keysNeedingUpdate: string[] = [];

                this._status.totalLoadedCount = keys.length;

                // Tuples is an array of strings
                for (let chunkKey of keys) {
                    if (
                        !this.index.updateDateByChunkKey.hasOwnProperty(
                            chunkKey,
                        )
                    ) {
                        this.index.updateDateByChunkKey[chunkKey] = null;
                        keysNeedingUpdate.push(chunkKey);
                    } else if (
                        this.index.updateDateByChunkKey[chunkKey] !=
                        serverIndex.updateDateByChunkKey[chunkKey]
                    ) {
                        keysNeedingUpdate.push(chunkKey);
                    }
                }
                this.queueChunksToAskServer(keysNeedingUpdate);
            });
    }

    /** Queue Chunks To Ask Server
     *
     */
    private queueChunksToAskServer(keysNeedingUpdate: string[]) {
        if (!this.areWeTalkingToTheServer()) return;

        this.askServerChunks = [];

        let count = 0;
        let indexChunk = new ItemKeyIndexUpdateDateTuple();

        for (let key of keysNeedingUpdate) {
            indexChunk.updateDateByChunkKey[key] =
                this.index.updateDateByChunkKey[key] || "";
            count++;

            if (count == this.UPDATE_CHUNK_FETCH_SIZE) {
                this.askServerChunks.push(indexChunk);
                count = 0;
                indexChunk = new ItemKeyIndexUpdateDateTuple();
            }
        }

        if (count) this.askServerChunks.push(indexChunk);

        this.askServerForNextUpdateChunk();

        this._status.lastCheckDate = new Date();
    }

    private askServerForNextUpdateChunk() {
        if (!this.areWeTalkingToTheServer()) return;

        if (this.askServerChunks.length == 0) return;

        if (this.deviceCacheControllerService.isOfflineCachingPaused) {
            this.saveChunkCacheIndex(true) //
                .catch((e) => console.log(`ERROR saveChunkCacheIndex: ${e}`));
            this._notifyStatus(true);
            return;
        }

        let indexChunk: ItemKeyIndexUpdateDateTuple =
            this.askServerChunks.pop();
        let filt = Object.assign(
            {},
            clientItemKeyIndexWatchUpdateFromDeviceFilt,
        );
        filt[cacheAll] = true;
        let pl = new Payload(filt, [indexChunk]);
        this.vortexService.sendPayload(pl);

        this._status.lastCheckDate = new Date();
        this._notifyStatus();
    }

    /** Process ItemKeyIndexes From Server
     *
     * Process the grids the server has sent us.
     */
    private async processChunksFromServer(
        payloadEnvelope: PayloadEnvelope,
    ): Promise<void> {
        if (payloadEnvelope.result != null && payloadEnvelope.result != true) {
            console.log(`ERROR: ${payloadEnvelope.result}`);
            return;
        }

        const tuplesToSave: ItemKeyIndexEncodedChunkTuple[] = <
            ItemKeyIndexEncodedChunkTuple[]
        >payloadEnvelope.data;

        try {
            await this.storeChunkTuples(tuplesToSave);
        } catch (e) {
            console.log(`ItemKeyIndexCache.storeChunkTuples: ${e}`);
        }

        if (this.askServerChunks.length == 0) {
            this.index.initialLoadComplete = true;
            await this.saveChunkCacheIndex(true);
            this._hasLoaded = true;
            this._hasLoadedSubject.next();
        } else if (payloadEnvelope.filt[cacheAll] == true) {
            this.askServerForNextUpdateChunk();
        }

        this._notifyStatus();
    }

    /** Store Index Bucket
     * Stores the index bucket in the local db.
     */
    private async storeChunkTuples(
        tuplesToSave: ItemKeyIndexEncodedChunkTuple[],
    ): Promise<void> {
        // noinspection BadExpressionStatementJS
        const Selector = ItemKeyIndexChunkTupleSelector;

        if (tuplesToSave.length == 0) return;

        const batchStore: TupleStorageBatchSaveArguments[] = [];
        for (const tuple of tuplesToSave) {
            batchStore.push({
                tupleSelector: new Selector(tuple.chunkKey),
                vortexMsg: tuple.encodedData,
            });
        }

        await this.storage.batchSaveTuplesEncoded(batchStore);

        for (const tuple of tuplesToSave) {
            this.index.updateDateByChunkKey[tuple.chunkKey] = tuple.lastUpdate;
        }
        await this.saveChunkCacheIndex(true);
    }

    /** Store Chunk Cache Index
     *
     * Updates our running tab of the update dates of the cached chunks
     *
     */
    private async saveChunkCacheIndex(force = false): Promise<void> {
        if (
            this.chunksSavedSinceLastIndexSave <= this.SAVE_POINT_ITERATIONS &&
            !force
        ) {
            return;
        }

        this.chunksSavedSinceLastIndexSave = 0;

        await this.storage.saveTuples(new UpdateDateTupleSelector(), [
            this.index,
        ]);
    }

    /** Get Segment Keys
     *
     * Get the objects with matching keywords from the index..
     *
     */
    private getItemKeys(
        modelSetKey: string,
        keys: string[],
    ): Promise<ItemKeyTuple[]> {
        if (modelSetKey == null || modelSetKey.length == 0) {
            Promise.reject("We've been passed a null/empty modelSetKey");
        }

        if (keys == null || keys.length == 0) {
            Promise.reject("We've been passed a null/empty keys");
        }

        // If there is no offline support, or we're online
        // This is never used at present.
        if (this.vortexStatusService.snapshot.isOnline) {
            let ts = new TupleSelector(GraphDbPackedItemKeyTuple.tupleName, {
                modelSetKey: modelSetKey,
                keys: keys,
            });

            let isOnlinePromise: any = this.vortexStatusService.snapshot
                .isOnline
                ? Promise.resolve()
                : this.vortexStatusService.isOnline
                      .pipe(filter((online) => online))
                      .pipe(first())
                      .toPromise();

            return isOnlinePromise
                .then(() =>
                    this.tupleService.offlineObserver.pollForTuples(ts, false),
                )
                .then((packedKeyIndexes: GraphDbPackedItemKeyTuple[]) => {
                    let itemKeys = [];
                    for (let packed of packedKeyIndexes) {
                        // Create the new object
                        let newObject = new ItemKeyTuple();
                        newObject.unpackJson(
                            packed.packedJson,
                            packed.key,
                            modelSetKey,
                        );
                        itemKeys.push(newObject);
                    }
                    return itemKeys;
                });
        }

        if (!this.deviceCacheControllerService.offlineModeEnabled) {
            throw new Error(
                "Peek is not online," +
                    " and offline caching is not enabled" +
                    " or has not completed loading." +
                    " The ItemKeyIndex won't work.",
            );
        }

        // If we do have offline support
        if (this.isReady()) return this.getItemKeysWhenReady(modelSetKey, keys);

        return this.isReadyObservable()
            .pipe(first())
            .toPromise()
            .then(() => this.getItemKeysWhenReady(modelSetKey, keys));
    }

    /** Get ItemKeyIndexs When Ready
     *
     * Get the objects with matching keywords from the index..
     *
     */
    private getItemKeysWhenReady(
        modelSetKey: string,
        keys: string[],
    ): Promise<ItemKeyTuple[]> {
        let keysByChunkKey: { [key: string]: string[] } = {};
        let chunkKeys: string[] = [];

        for (let key of keys) {
            let chunkKey: string = keyChunk(modelSetKey, key);
            if (keysByChunkKey[chunkKey] == null) keysByChunkKey[chunkKey] = [];
            keysByChunkKey[chunkKey].push(key);
            chunkKeys.push(chunkKey);
        }

        let promises = [];
        for (let chunkKey of chunkKeys) {
            let keysForThisChunk = keysByChunkKey[chunkKey];
            promises.push(
                this.getItemKeysForKeys(
                    keysForThisChunk,
                    modelSetKey,
                    chunkKey,
                ),
            );
        }

        return Promise.all(promises).then(
            (promiseResults: ItemKeyTuple[][]) => {
                let objects: ItemKeyTuple[] = [];
                for (let results of promiseResults) {
                    for (let result of results) {
                        objects.push(result);
                    }
                }
                return objects;
            },
        );
    }

    /** Get ItemKeyIndexs for Object ID
     *
     * Get the objects with matching keywords from the index..
     *
     */
    private async getItemKeysForKeys(
        keys: string[],
        modelSetKey: string,
        chunkKey: string,
    ): Promise<ItemKeyTuple[]> {
        if (!this.index.updateDateByChunkKey.hasOwnProperty(chunkKey)) {
            console.log(`ObjectIDs: ${keys} doesn't appear in the index`);
            return Promise.resolve([]);
        }

        const vortexMsg: string = await this.storage.loadTuplesEncoded(
            new ItemKeyIndexChunkTupleSelector(chunkKey),
        );
        if (vortexMsg == null) {
            return [];
        }

        const payload: Payload = await Payload.fromEncodedPayload(vortexMsg);
        const chunkData: { [key: number]: string } = JSON.parse(
            <any>payload.tuples[0],
        );
        let foundItemKeyIndexs: ItemKeyTuple[] = [];

        for (let key of keys) {
            // Find the keyword, we're just iterating
            if (!chunkData.hasOwnProperty(key)) {
                console.log(
                    `WARNING: ItemKeyIndex ${key} is missing from index,` +
                        ` chunkKey ${chunkKey}`,
                );
                continue;
            }

            let packedJson = chunkData[key];
            foundItemKeyIndexs.push(
                new ItemKeyTuple().unpackJson(key, packedJson, modelSetKey),
            );
        }

        return foundItemKeyIndexs;
    }
}
