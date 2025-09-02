import { CommonModule } from "@angular/common";
import { NgModule } from "@angular/core";
import { RouterModule, Route, Routes } from "@angular/router";
import { FormsModule } from "@angular/forms";
import { NzIconModule } from "ng-zorro-antd/icon";
import { HttpClientModule } from "@angular/common/http";
import { GisDiagramComponent } from "./gisDiagram.component";
import {
    TupleActionPushNameService,
    TupleActionPushOfflineService,
    TupleActionPushService,
    TupleDataObservableNameService,
    TupleDataObserverService,
    TupleDataOfflineObserverService,
    TupleOfflineStorageNameService,
    TupleOfflineStorageService,
} from "@synerty/vortexjs";
import {
    gisDiagramFilt,
    gisDiagramObservableName,
    gisDiagramTupleOfflineServiceName,
} from "@peek/peek_plugin_gis_diagram/_private/PluginNames";
import { ShowDiagramComponent } from "./show-diagram/show-diagram.component";
import { gisDiagramActionProcessorName } from "@peek/peek_plugin_gis_diagram/_private";
import { PeekPluginDiagramModule } from "@peek/peek_plugin_diagram";

export function tupleActionPushNameServiceFactory() {
    return new TupleActionPushNameService(
        gisDiagramActionProcessorName,
        gisDiagramFilt,
    );
}

export function tupleDataObservableNameServiceFactory() {
    return new TupleDataObservableNameService(
        gisDiagramObservableName,
        gisDiagramFilt,
    );
}

export function tupleOfflineStorageNameServiceFactory() {
    return new TupleOfflineStorageNameService(
        gisDiagramTupleOfflineServiceName,
    );
}

// Define the child routes for this plugin.
export const pluginRoutes: Routes = [
    {
        path: "",
        pathMatch: "full",
        component: GisDiagramComponent,
    },
];

// Define the root module for this plugin.
// This module is loaded by the lazy loader, what ever this defines is what is started.
// When it first loads, it will look up the routes and then select the component to load.
@NgModule({
    imports: [
        CommonModule,
        HttpClientModule,
        RouterModule.forChild(pluginRoutes),
        FormsModule,
        NzIconModule,
        PeekPluginDiagramModule,
    ],
    exports: [],
    providers: [
        TupleActionPushOfflineService,
        TupleActionPushService,
        {
            provide: TupleActionPushNameService,
            useFactory: tupleActionPushNameServiceFactory,
        },
        TupleOfflineStorageService,
        {
            provide: TupleOfflineStorageNameService,
            useFactory: tupleOfflineStorageNameServiceFactory,
        },
        TupleDataObserverService,
        TupleDataOfflineObserverService,
        {
            provide: TupleDataObservableNameService,
            useFactory: tupleDataObservableNameServiceFactory,
        },
    ],
    declarations: [GisDiagramComponent, ShowDiagramComponent],
})
export class GisDiagramModule {}
