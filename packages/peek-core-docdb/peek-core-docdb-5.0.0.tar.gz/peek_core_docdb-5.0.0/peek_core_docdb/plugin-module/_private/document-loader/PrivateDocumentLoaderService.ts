import { Observable, Subject } from "rxjs";
import { filter, first, takeUntil } from "rxjs/operators";
import { Injectable } from "@angular/core";
import {
    Jsonable,
    NgLifeCycleEvents,
    Payload,
    PayloadEnvelope,
    TupleOfflineStorageNameService,
    TupleOfflineStorageService,
    TupleSelector,
    TupleStorageFactoryService,
    VortexService,
    VortexStatusService,
    TupleStorageBatchSaveArguments,
} from "@synerty/vortexjs";

import {
    docDbCacheStorageName,
    docDbFilt,
    docDbTuplePrefix,
} from "../PluginNames";
import { EncodedDocumentChunkTuple } from "./EncodedDocumentChunkTuple";
import { DocumentUpdateDateTuple } from "./DocumentUpdateDateTuple";
import { DocumentTuple } from "../../DocumentTuple";
import { DocDbTupleService } from "../DocDbTupleService";
import { DocDbDocumentTypeTuple } from "../../DocDbDocumentTypeTuple";
import { DocDbModelSetTuple } from "../../DocDbModelSetTuple";
import {
    DeviceOfflineCacheService,
    OfflineCacheLoaderStatusTuple,
} from "@peek/peek_core_device";

// ----------------------------------------------------------------------------

export interface DocumentResultI {
    [key: string]: DocumentTuple;
}

// ----------------------------------------------------------------------------

let clientDocumentWatchUpdateFromDeviceFilt = Object.assign(
    { key: "clientDocumentWatchUpdateFromDevice" },
    docDbFilt,
);

const cacheAll = "cacheAll";

// ----------------------------------------------------------------------------
/** DocumentChunkTupleSelector
 *
 * This is just a short cut for the tuple selector
 */

class DocumentChunkTupleSelector extends TupleSelector {
    constructor(private chunkKey: string) {
        super(docDbTuplePrefix + "DocumentChunkTuple", { key: chunkKey });
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
        super(DocumentUpdateDateTuple.tupleName, {});
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
     
     @param modelSetKey: The key of the model set that the documents are in
     @param key: The key of the document to get the chunk key for
     
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
/** Document Cache
 *
 * This class has the following responsibilities:
 *
 * 1) Maintain a local storage of the index
 *
 * 2) Return DispKey docDbs based on the index.
 *
 */
@Injectable()
export class PrivateDocumentLoaderService extends NgLifeCycleEvents {
    private UPDATE_CHUNK_FETCH_SIZE = 5;

    // Every 100 chunks from the server
    private SAVE_POINT_ITERATIONS = 100;

    // Saving the cache after each chunk is so expensive, we only do it every 20 or so
    private chunksSavedSinceLastIndexSave = 0;

    private index: DocumentUpdateDateTuple | null;
    private askServerChunks: DocumentUpdateDateTuple[] = [];

    private _hasLoaded = false;
    private _hasLoadedSubject = new Subject<void>();

    private storage: TupleOfflineStorageService;

    private _statusSubject = new Subject<OfflineCacheLoaderStatusTuple>();
    private _status = new OfflineCacheLoaderStatusTuple();

    private objectTypesByIds: { [id: number]: DocDbDocumentTypeTuple } = {};
    private _hasDocTypeLoaded = false;

    private modelSetByIds: { [id: number]: DocDbModelSetTuple } = {};
    private _hasModelSetLoaded = false;

    constructor(
        private vortexService: VortexService,
        private vortexStatusService: VortexStatusService,
        storageFactory: TupleStorageFactoryService,
        private tupleService: DocDbTupleService,
        private deviceCacheControllerService: DeviceOfflineCacheService,
    ) {
        super();

        this._status.pluginName = "peek_core_docdb";
        this._status.indexName = "Document Index";

        let objTypeTs = new TupleSelector(DocDbDocumentTypeTuple.tupleName, {});
        this.tupleService.offlineObserver
            .subscribeToTupleSelector(objTypeTs)
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: DocDbDocumentTypeTuple[]) => {
                this.objectTypesByIds = {};
                for (let item of tuples) {
                    this.objectTypesByIds[item.id] = item;
                }
                this._hasDocTypeLoaded = true;
                this._notifyReady();
            });

        let modelSetTs = new TupleSelector(DocDbModelSetTuple.tupleName, {});
        this.tupleService.offlineObserver
            .subscribeToTupleSelector(modelSetTs)
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: DocDbModelSetTuple[]) => {
                this.modelSetByIds = {};
                for (let item of tuples) {
                    this.modelSetByIds[item.id] = item;
                }
                this._hasModelSetLoaded = true;
                this._notifyReady();
            });

        this.storage = new TupleOfflineStorageService(
            storageFactory,
            new TupleOfflineStorageNameService(docDbCacheStorageName),
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

    /** Get Documents
     *
     * Get the objects with matching keywords from the index..
     *
     */
    getDocuments(
        modelSetKey: string,
        keys: string[],
    ): Promise<DocumentResultI> {
        if (keys == null || keys.length == 0) {
            throw new Error("We've been passed a null/empty keys");
        }

        // If there is no offline support, or we're online
        if (this.vortexStatusService.snapshot.isOnline) {
            let ts = new TupleSelector(DocumentTuple.tupleName, {
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
                    this.tupleService.offlineObserver //
                        .pollForTuples(ts, false),
                )
                .then((docs: DocumentTuple[]) =>
                    this._populateAndIndexObjectTypes(docs),
                );
        }

        if (!this.offlineEnabled) {
            console.log(
                "WARNING The offline cache has not finished loading," +
                    " returning zero results",
            );
            return Promise.resolve({});
        }

        // If we do have offline support
        if (this.isReady()) {
            return this.getDocumentsWhenReady(modelSetKey, keys) //
                .then((docs) => this._populateAndIndexObjectTypes(docs));
        }

        return this.isReadyObservable()
            .pipe(first())
            .toPromise()
            .then(() => this.getDocumentsWhenReady(modelSetKey, keys))
            .then((docs) => this._populateAndIndexObjectTypes(docs));
    }

    private _notifyReady(): void {
        if (
            this._hasDocTypeLoaded &&
            this._hasModelSetLoaded &&
            this._hasLoaded
        )
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
                let tuples: DocumentUpdateDateTuple[] = tuplesAny;
                if (tuples.length === 0) {
                    this.index = new DocumentUpdateDateTuple();
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
                clientDocumentWatchUpdateFromDeviceFilt,
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
                let serverIndex: DocumentUpdateDateTuple = tuplesAny[0];
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
        this.chunksSavedSinceLastIndexSave = 0;

        let count = 0;
        let indexChunk = new DocumentUpdateDateTuple();

        for (let key of keysNeedingUpdate) {
            indexChunk.updateDateByChunkKey[key] =
                this.index.updateDateByChunkKey[key] || "";
            count++;

            if (count == this.UPDATE_CHUNK_FETCH_SIZE) {
                this.askServerChunks.push(indexChunk);
                count = 0;
                indexChunk = new DocumentUpdateDateTuple();
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

        let indexChunk: DocumentUpdateDateTuple = this.askServerChunks.pop();
        let filt = Object.assign({}, clientDocumentWatchUpdateFromDeviceFilt);
        filt[cacheAll] = true;
        let pl = new Payload(filt, [indexChunk]);
        this.vortexService.sendPayload(pl);

        this._status.lastCheckDate = new Date();
        this._notifyStatus();
    }

    /** Process Documentes From Server
     *
     * Process the grids the server has sent us.
     */
    private async processChunksFromServer(payloadEnvelope: PayloadEnvelope) {
        if (payloadEnvelope.result != null && payloadEnvelope.result != true) {
            console.log(`ERROR: ${payloadEnvelope.result}`);
            return;
        }

        const tuplesToSave: EncodedDocumentChunkTuple[] = <
            EncodedDocumentChunkTuple[]
        >payloadEnvelope.data;

        try {
            await this.storeChunkTuples(tuplesToSave);
        } catch (e) {
            console.log(`DocumentCache.storeDocumentPayload: ${e}`);
        }

        this.chunksSavedSinceLastIndexSave += tuplesToSave.length;

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
        tuplesToSave: EncodedDocumentChunkTuple[],
    ): Promise<void> {
        // noinspection BadExpressionStatementJS
        const Selector = DocumentChunkTupleSelector;

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
        await this.saveChunkCacheIndex();
    }

    /** Store Chunk Cache Index
     *
     * Updates our running tab of the update dates of the cached chunks
     *
     */
    private async saveChunkCacheIndex(force = false): Promise<void> {
        if (this.index == null) return;

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

    /** Get Documents When Ready
     *
     * Get the objects with matching keywords from the index..
     *
     */
    private getDocumentsWhenReady(
        modelSetKey: string,
        keys: string[],
    ): Promise<DocumentTuple[]> {
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
            promises.push(this.getDocumentsForKeys(keysForThisChunk, chunkKey));
        }

        return Promise.all(promises).then(
            (promiseResults: DocumentTuple[][]) => {
                let objects: DocumentTuple[] = [];
                for (let results of promiseResults) {
                    for (let result of results) {
                        objects.push(result);
                    }
                }
                return objects;
            },
        );
    }

    /** Get Documents for Object ID
     *
     * Get the objects with matching keywords from the index..
     *
     */
    private async getDocumentsForKeys(
        keys: string[],
        chunkKey: string,
    ): Promise<DocumentTuple[]> {
        // PY side = ClientDocumentTupleProvider.makeVortexMsg
        if (!this.index.updateDateByChunkKey.hasOwnProperty(chunkKey)) {
            console.log(`ObjectIDs: ${keys} doesn't appear in the index`);
            return [];
        }

        const vortexMsg: string = await this.storage.loadTuplesEncoded(
            new DocumentChunkTupleSelector(chunkKey),
        );

        if (vortexMsg == null) {
            return [];
        }

        const payload: Payload = await Payload.fromEncodedPayload(vortexMsg);
        const docsByKey: { [key: number]: string } = JSON.parse(
            <any>payload.tuples[0],
        );

        let foundDocuments: DocumentTuple[] = [];

        for (const key of keys) {
            // Find the keyword, we're just iterating
            if (!docsByKey.hasOwnProperty(key)) {
                console.log(
                    `WARNING: Document ${key} is missing from index,` +
                        ` chunkKey ${chunkKey}`,
                );
                continue;
            }

            // Reconstruct the data
            let objectProps: {} = JSON.parse(docsByKey[key]);
            objectProps = new Jsonable().fromJsonField(objectProps);

            // Get out the object type
            let thisDocumentTypeId = objectProps["_dtid"];
            delete objectProps["_dtid"];

            // Get out the object type
            let thisModelSetId = objectProps["_msid"];
            delete objectProps["_msid"];

            // Create the new object
            let newObject = new DocumentTuple();
            foundDocuments.push(newObject);

            newObject.key = key;
            newObject.modelSet = new DocDbModelSetTuple();
            newObject.modelSet.id = thisModelSetId;
            newObject.documentType = new DocDbDocumentTypeTuple();
            newObject.documentType.id = thisDocumentTypeId;
            newObject.document = objectProps;
        }

        return foundDocuments;
    }

    private _populateAndIndexObjectTypes(
        docs: DocumentTuple[],
    ): DocumentResultI {
        let objects: { [key: string]: DocumentTuple } = {};
        for (let doc of docs) {
            objects[doc.key] = doc;
            doc.documentType = this.objectTypesByIds[doc.documentType.id];
            doc.modelSet = this.modelSetByIds[doc.modelSet.id];
        }
        return objects;
    }
}
