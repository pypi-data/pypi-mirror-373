import { AfterViewInit, Component, ViewChild } from "@angular/core";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { HeaderService } from "@synerty/peek-plugin-base-js";
import { ActivatedRoute, Router } from "@angular/router";
import { EventDBEventListComponent } from "../event-list-component/event-list.component";
import { EventDbController } from "../../controllers/event-db.controller";
import { PrivateEventDBService } from "@peek/peek_plugin_eventdb/_private/PrivateEventDBService";

@Component({
    selector: "plugin-eventdb-event-page",
    templateUrl: "event-page.component.html",
    styleUrls: ["../event-toolbar-component/event-toolbar.component.scss"],
})
export class EventDBPageComponent
    extends NgLifeCycleEvents
    implements AfterViewInit
{
    @ViewChild("eventList", { static: true })
    eventList: EventDBEventListComponent;

    modelSetKey = "pofDiagram";
    public eventDbController: EventDbController;

    constructor(
        private headerService: HeaderService,
        route: ActivatedRoute,
        router: Router,
        eventService: PrivateEventDBService,
    ) {
        super();
        headerService.setTitle("Alarm and Events");
        this.eventDbController = new EventDbController(
            this.modelSetKey,
            route,
            router,
            eventService,
        );
    }

    override ngAfterViewInit() {
        this.eventDbController.initialize(this.modelSetKey);
    }

    override ngOnDestroy() {
        super.ngOnDestroy();
        this.eventDbController.destroy();
    }
}
