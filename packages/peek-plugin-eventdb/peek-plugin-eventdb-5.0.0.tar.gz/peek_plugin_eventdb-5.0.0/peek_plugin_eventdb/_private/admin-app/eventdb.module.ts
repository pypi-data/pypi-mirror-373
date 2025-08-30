import { CommonModule } from "@angular/common";
import { HttpClientModule } from "@angular/common/http";
import { FormsModule } from "@angular/forms";
import { NgModule } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";
import { NzTabsModule } from "ng-zorro-antd/tabs";
import { NzButtonModule } from "ng-zorro-antd/button";
import { NzIconModule } from "ng-zorro-antd/icon";
import { NzSwitchModule } from "ng-zorro-antd/switch";
import { NzSelectModule } from "ng-zorro-antd/select";
import { NzInputNumberModule } from "ng-zorro-antd/input-number";
import { NzTableModule } from "ng-zorro-antd/table";
import { NzBadgeModule } from "ng-zorro-antd/badge";
import { NzCardModule } from "ng-zorro-antd/card";
import { NzLayoutModule } from "ng-zorro-antd/layout";
import { NzInputModule } from "ng-zorro-antd/input";
import { NzTagModule } from "ng-zorro-antd/tag";
import { NzDividerModule } from "ng-zorro-antd/divider";
import { EditSettingComponent } from "./components/edit-setting-table/edit.component";
import { EventdbPageComponent } from "./components/eventdb-page/eventdb-page.component";
import { StatusComponent } from "./components/status/status.component";
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
    eventdbActionProcessorName,
    eventdbFilt,
    eventdbObservableName,
    eventdbTupleOfflineServiceName,
} from "./PluginNames";
import { EditPropertyComponent } from "./components/edit-property-table/edit.component";
import { NzDescriptionsModule } from "ng-zorro-antd/descriptions";
import { NzEmptyModule } from "ng-zorro-antd/empty";

export function tupleActionPushNameServiceFactory() {
    return new TupleActionPushNameService(
        eventdbActionProcessorName,
        eventdbFilt,
    );
}

export function tupleDataObservableNameServiceFactory() {
    return new TupleDataObservableNameService(
        eventdbObservableName,
        eventdbFilt,
    );
}

export function tupleOfflineStorageNameServiceFactory() {
    return new TupleOfflineStorageNameService(eventdbTupleOfflineServiceName);
}

export const pluginRoutes: Routes = [
    {
        path: "",
        component: EventdbPageComponent,
    },
];

@NgModule({
    imports: [
        CommonModule,
        HttpClientModule,
        RouterModule.forChild(pluginRoutes),
        FormsModule,
        NzTabsModule,
        NzSwitchModule,
        NzButtonModule,
        NzIconModule,
        NzSelectModule,
        NzInputNumberModule,
        NzTableModule,
        NzBadgeModule,
        NzCardModule,
        NzLayoutModule,
        NzInputModule,
        NzTagModule,
        NzDividerModule,
        NzDescriptionsModule,
        NzEmptyModule,
    ],
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
    declarations: [
        EventdbPageComponent,
        StatusComponent,
        EditSettingComponent,
        EditPropertyComponent,
    ],
})
export class EventDBModule {}
