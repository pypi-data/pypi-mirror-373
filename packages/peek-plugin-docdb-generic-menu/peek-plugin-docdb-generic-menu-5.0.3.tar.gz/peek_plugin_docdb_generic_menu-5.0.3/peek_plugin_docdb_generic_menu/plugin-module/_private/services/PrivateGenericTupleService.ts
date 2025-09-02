import { Injectable } from "@angular/core";
import {
    TupleActionPushNameService,
    TupleActionPushOfflineService,
    TupleActionPushOfflineSingletonService,
    TupleDataObservableNameService,
    TupleDataOfflineObserverService,
    TupleOfflineStorageNameService,
    TupleOfflineStorageService,
    TupleStorageFactoryService,
    VortexService,
    VortexStatusService,
} from "@synerty/vortexjs";

import {
    docDbGenericMenuActionProcessorName,
    docDbGenericMenuFilt,
    docDbGenericMenuObservableName,
    docDbGenericMenuTupleOfflineServiceName,
} from "../PluginNames";

@Injectable()
export class PrivateGenericTupleService {
    public tupleOfflineAction: TupleActionPushOfflineService;
    public tupleDataOfflineObserver: TupleDataOfflineObserverService;

    constructor(
        tupleActionSingletonService: TupleActionPushOfflineSingletonService,
        vortexService: VortexService,
        vortexStatusService: VortexStatusService,
        storageFactory: TupleStorageFactoryService,
    ) {
        let tupleDataObservableName = new TupleDataObservableNameService(
            docDbGenericMenuObservableName,
            docDbGenericMenuFilt,
        );

        let storageName = new TupleOfflineStorageNameService(
            docDbGenericMenuTupleOfflineServiceName,
        );

        let tupleActionName = new TupleActionPushNameService(
            docDbGenericMenuActionProcessorName,
            docDbGenericMenuFilt,
        );

        let tupleOfflineStorageService = new TupleOfflineStorageService(
            storageFactory,
            storageName,
        );

        this.tupleDataOfflineObserver = new TupleDataOfflineObserverService(
            vortexService,
            vortexStatusService,
            tupleDataObservableName,
            tupleOfflineStorageService,
        );

        this.tupleOfflineAction = new TupleActionPushOfflineService(
            tupleActionName,
            vortexService,
            vortexStatusService,
            tupleActionSingletonService,
        );
    }
}
