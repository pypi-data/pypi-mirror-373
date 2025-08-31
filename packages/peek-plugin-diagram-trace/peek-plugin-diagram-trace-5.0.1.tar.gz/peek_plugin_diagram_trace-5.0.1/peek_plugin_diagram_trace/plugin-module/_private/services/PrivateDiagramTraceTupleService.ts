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
    diagramTraceActionProcessorName,
    diagramTraceFilt,
    diagramTraceObservableName,
    diagramTraceTupleOfflineServiceName,
} from "../PluginNames";

@Injectable()
export class PrivateDiagramTraceTupleService {
    public tupleOfflineAction: TupleActionPushOfflineService;
    public tupleDataOfflineObserver: TupleDataOfflineObserverService;

    constructor(
        tupleActionSingletonService: TupleActionPushOfflineSingletonService,
        vortexService: VortexService,
        vortexStatusService: VortexStatusService,
        storageFactory: TupleStorageFactoryService,
    ) {
        let tupleDataObservableName = new TupleDataObservableNameService(
            diagramTraceObservableName,
            diagramTraceFilt,
        );

        let storageName = new TupleOfflineStorageNameService(
            diagramTraceTupleOfflineServiceName,
        );

        let tupleActionName = new TupleActionPushNameService(
            diagramTraceActionProcessorName,
            diagramTraceFilt,
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
