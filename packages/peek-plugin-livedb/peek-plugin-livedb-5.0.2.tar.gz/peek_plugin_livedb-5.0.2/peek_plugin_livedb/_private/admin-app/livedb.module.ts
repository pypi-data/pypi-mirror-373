import { CommonModule } from "@angular/common";
import { FormsModule } from "@angular/forms";
import { NgModule } from "@angular/core";
import { RouterModule, Route, Routes } from "@angular/router";
import {
    TupleActionPushNameService,
    TupleActionPushService,
    TupleDataObservableNameService,
    TupleDataObserverService,
    TupleDataOfflineObserverService,
    TupleOfflineStorageNameService,
    TupleOfflineStorageService,
} from "@synerty/vortexjs";

import {
    livedbActionProcessorName,
    livedbFilt,
    livedbObservableName,
    livedbTupleOfflineServiceName,
} from "@peek/peek_plugin_livedb/_private";

// Import Ant Design modules
import { NzTabsModule } from "ng-zorro-antd/tabs";
import { NzTableModule } from "ng-zorro-antd/table";
import { NzButtonModule } from "ng-zorro-antd/button";
import { NzInputModule } from "ng-zorro-antd/input";
import { NzSwitchModule } from "ng-zorro-antd/switch";
import { NzInputNumberModule } from "ng-zorro-antd/input-number";
import { NzDividerModule } from "ng-zorro-antd/divider";
import { NzTagModule } from "ng-zorro-antd/tag";
import { NzIconModule } from "ng-zorro-antd/icon";
import { StatusComponent } from "./components/status/status.component";
import { EditSettingComponent } from "./components/edit-setting-table/edit.component";
import { LivedbPageComponent } from "./components/livedb-page/livedb-page.component";
import { NzCardModule } from "ng-zorro-antd/card";
import { NzDescriptionsModule } from "ng-zorro-antd/descriptions";
import { NzEmptyModule } from "ng-zorro-antd/empty";

export function tupleActionPushNameServiceFactory() {
    return new TupleActionPushNameService(
        livedbActionProcessorName,
        livedbFilt,
    );
}

export function tupleDataObservableNameServiceFactory() {
    return new TupleDataObservableNameService(livedbObservableName, livedbFilt);
}

export function tupleOfflineStorageNameServiceFactory() {
    return new TupleOfflineStorageNameService(livedbTupleOfflineServiceName);
}

export const pluginRoutes: Routes = [
    {
        path: "",
        component: LivedbPageComponent,
    },
];

@NgModule({
    imports: [
        CommonModule,
        RouterModule.forChild(pluginRoutes),
        FormsModule,
        // Add Ant Design modules
        NzTabsModule,
        NzTableModule,
        NzButtonModule,
        NzInputModule,
        NzSwitchModule,
        NzInputNumberModule,
        NzDividerModule,
        NzTagModule,
        NzIconModule,
        NzCardModule,
        NzDescriptionsModule,
        NzEmptyModule,
    ],
    exports: [],
    providers: [
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
    declarations: [LivedbPageComponent, StatusComponent, EditSettingComponent],
})
export class LiveDBModule {}
