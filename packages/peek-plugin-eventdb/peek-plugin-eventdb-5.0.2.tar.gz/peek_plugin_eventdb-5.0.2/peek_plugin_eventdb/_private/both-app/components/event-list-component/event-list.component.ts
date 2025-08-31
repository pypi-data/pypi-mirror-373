import { Component, Input, OnInit } from "@angular/core";
import {
    EventDBEventTuple,
    EventDBPropertyTuple,
} from "@peek/peek_plugin_eventdb/tuples";
import { DocDbPopupService, DocDbPopupTypeE } from "@peek/peek_core_docdb";
import { eventdbPluginName } from "@peek/peek_plugin_eventdb/_private/PluginNames";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { takeUntil } from "rxjs/operators";
import { EventDbController } from "../../controllers/event-db.controller";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";

@Component({
    selector: "plugin-eventdb-event-list",
    templateUrl: "event-list.component.html",
    styleUrls: ["../event-toolbar-component/event-toolbar.component.scss"],
})
export class EventDBEventListComponent
    extends NgLifeCycleEvents
    implements OnInit
{
    @Input() controller: EventDbController;

    events: EventDBEventTuple[] = [];
    props: EventDBPropertyTuple[] = [];
    displayProps: EventDBPropertyTuple[] = [];
    isDataLoading = true;
    colorsEnabled: boolean = false;

    constructor(
        private balloonMsg: BalloonMsgService,
        private objectPopupService: DocDbPopupService,
    ) {
        super();
    }

    override ngOnInit() {
        this.controller
            .getState$()
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((state) => {
                this.events = state.events;
                this.props = state.allProps;
                this.displayProps = state.displayProps;
                this.isDataLoading = state.isDataLoading;
                this.colorsEnabled = state.colorsEnabled;
            });
    }

    displayValue(event: EventDBEventTuple, prop: EventDBPropertyTuple): string {
        const eventVal = event.value[prop.key];
        return prop.values != null && prop.values.length != 0
            ? prop.rawValToUserVal(eventVal)
            : eventVal;
    }

    colorValue(event: EventDBEventTuple): string {
        if (!this.colorsEnabled) return null;

        // Stash this value here to improve performance
        if (event.color != null) return event.color;

        let color = "";
        for (let prop of this.props) {
            const eventVal = event.value[prop.key];
            const thisColor = prop.rawValToColor(eventVal);
            if (thisColor != null) {
                color = thisColor;
                break;
            }
        }

        event["color"] = color;
        return color;
    }

    handleInfoClick($event: MouseEvent, event: EventDBEventTuple): void {
        const docdbPopupKey = this.getDocDBPopupKey(event);
        if (docdbPopupKey == null) {
            this.balloonMsg.showInfo("No info availible for this event");
            return;
        }

        this.objectPopupService.hidePopup(DocDbPopupTypeE.tooltipPopup);
        this.objectPopupService.showPopup(
            true,
            DocDbPopupTypeE.summaryPopup,
            eventdbPluginName,
            $event,
            this.controller.modelSetKey,
            docdbPopupKey,
        );
        console.log(
            "Triggered DocDB Popup, it will only appear if there is" +
                " a document for key: " +
                docdbPopupKey,
        );
    }

    private getDocDBPopupKey(event: EventDBEventTuple): string | null {
        for (let prop of this.props) {
            if (prop.useForPopup && event.value[prop.key] != null) {
                return event.value[prop.key];
            }
        }
        return null;
    }
}
