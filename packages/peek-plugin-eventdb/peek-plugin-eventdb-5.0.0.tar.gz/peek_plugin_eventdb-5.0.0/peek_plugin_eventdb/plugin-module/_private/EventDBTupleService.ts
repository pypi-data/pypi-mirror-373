import { Injectable } from "@angular/core";
import {
    TupleActionPushNameService,
    TupleActionPushOfflineService,
    TupleActionPushOfflineSingletonService,
    TupleActionPushService,
    TupleDataObservableNameService,
    TupleDataObserverService,
    TupleDataOfflineObserverService,
    TupleOfflineStorageNameService,
    TupleOfflineStorageService,
    TupleStorageFactoryService,
    VortexService,
    VortexStatusService,
} from "@synerty/vortexjs";

import {
    eventdbActionProcessorName,
    eventdbFilt,
    eventdbObservableName,
    eventdbTupleOfflineServiceName,
} from "./PluginNames";

export function tupleDataObservableNameServiceFactory() {
    return new TupleDataObservableNameService(
        eventdbObservableName,
        eventdbFilt,
    );
}

export function tupleOfflineStorageNameServiceFactory() {
    return new TupleOfflineStorageNameService(eventdbTupleOfflineServiceName);
}

export function tupleActionPushNameServiceFactory() {
    return new TupleActionPushNameService(
        eventdbActionProcessorName,
        eventdbFilt,
    );
}

@Injectable()
export class EventDBTupleService {
    public offlineStorage: TupleOfflineStorageService;
    public offlineObserver: TupleDataOfflineObserverService;
    public observer: TupleDataObserverService;

    public action: TupleActionPushService;
    public offlineAction: TupleActionPushOfflineService;

    constructor(
        storageFactory: TupleStorageFactoryService,
        vortexService: VortexService,
        vortexStatusService: VortexStatusService,
        actionSingleton: TupleActionPushOfflineSingletonService,
    ) {
        // Create the offline storage
        this.offlineStorage = new TupleOfflineStorageService(
            storageFactory,
            tupleOfflineStorageNameServiceFactory(),
        );

        // Online Actions
        this.action = new TupleActionPushService(
            tupleActionPushNameServiceFactory(),
            vortexService,
            vortexStatusService,
        );

        // Offline Actions
        this.offlineAction = new TupleActionPushOfflineService(
            tupleActionPushNameServiceFactory(),
            vortexService,
            vortexStatusService,
            actionSingleton,
        );

        // Offline Tuple Data Observer
        let observerName = tupleDataObservableNameServiceFactory();
        this.offlineObserver = new TupleDataOfflineObserverService(
            vortexService,
            vortexStatusService,
            observerName,
            this.offlineStorage,
        );

        // Online Tuple Data Observer
        this.observer = new TupleDataObserverService(
            this.offlineObserver,
            observerName,
        );
    }
}
