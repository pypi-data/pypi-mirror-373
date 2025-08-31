import { CommonModule } from "@angular/common";
import { HttpClientModule } from "@angular/common/http";
import { FormsModule } from "@angular/forms";
import { NgModule } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";
import { NzDropDownModule } from "ng-zorro-antd/dropdown";
import { NzTableModule } from "ng-zorro-antd/table";
import { NzToolTipModule } from "ng-zorro-antd/tooltip";
import { NzButtonModule } from "ng-zorro-antd/button";
import { NzCardModule } from "ng-zorro-antd/card";
import { NzMenuModule } from "ng-zorro-antd/menu";
import { NzModalModule } from "ng-zorro-antd/modal";
import { NzSelectModule } from "ng-zorro-antd/select";
import { NzInputModule } from "ng-zorro-antd/input";
import { NzIconModule } from "ng-zorro-antd/icon";
import { EventDBEventListComponent } from "./components/event-list-component/event-list.component";
import { EventDBFilterComponent } from "./components/event-filter-component/event-filter.component";
import { EventDBColumnComponent } from "./components/event-column-component/event-column.component";
import { EventDBPageComponent } from "./components/event-page-component/event-page.component";
import { EventDBToolbarComponent } from "./components/event-toolbar-component/event-toolbar.component";
import { NzDatePickerModule } from "ng-zorro-antd/date-picker";
import { NzGridModule } from "ng-zorro-antd/grid";
import { NzSwitchModule } from "ng-zorro-antd/switch";
import { NzCheckboxModule } from "ng-zorro-antd/checkbox";
import { NzAlertModule } from "ng-zorro-antd/alert";

// Define the child routes for this plugin
export const pluginRoutes: Routes = [
    {
        path: "",
        pathMatch: "full",
        component: EventDBPageComponent,
    },
];

@NgModule({
    imports: [
        CommonModule,
        HttpClientModule,
        FormsModule,
        RouterModule.forChild(pluginRoutes),
        NzIconModule,
        NzDropDownModule,
        NzTableModule,
        NzToolTipModule,
        NzButtonModule,
        NzCardModule,
        NzMenuModule,
        NzModalModule,
        NzSelectModule,
        NzInputModule,
        NzDatePickerModule,
        NzGridModule,
        NzSwitchModule,
        NzCheckboxModule,
        NzAlertModule,
    ],
    exports: [EventDBEventListComponent, EventDBFilterComponent],
    providers: [],
    declarations: [
        EventDBPageComponent,
        EventDBEventListComponent,
        EventDBFilterComponent,
        EventDBColumnComponent,
        EventDBToolbarComponent,
    ],
})
export class EventDBModule {}
