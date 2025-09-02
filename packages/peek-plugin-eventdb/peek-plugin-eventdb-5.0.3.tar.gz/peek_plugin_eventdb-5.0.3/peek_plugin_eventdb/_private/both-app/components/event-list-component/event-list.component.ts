import {
    ChangeDetectionStrategy,
    Component,
    Input,
    OnInit,
} from "@angular/core";
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
import { BehaviorSubject } from "rxjs";

@Component({
    selector: "plugin-eventdb-event-list",
    templateUrl: "event-list.component.html",
    styleUrls: ["../event-toolbar-component/event-toolbar.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EventDBEventListComponent
    extends NgLifeCycleEvents
    implements OnInit
{
    @Input() controller: EventDbController;

    protected readonly events$ = new BehaviorSubject<EventDBEventTuple[]>([]);
    protected readonly props$ = new BehaviorSubject<EventDBPropertyTuple[]>([]);
    protected readonly displayProps$ = new BehaviorSubject<
        EventDBPropertyTuple[]
    >([]);
    protected readonly isDataLoading$ = new BehaviorSubject<boolean>(true);
    protected readonly colorsEnabled$ = new BehaviorSubject<boolean>(false);

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
                this.events$.next(state.events);
                this.props$.next(state.allProps);
                this.displayProps$.next(state.displayProps);
                this.isDataLoading$.next(state.isDataLoading);
                this.colorsEnabled$.next(state.colorsEnabled);
            });
    }

    private get events(): EventDBEventTuple[] {
        return this.events$.getValue();
    }

    private set events(value: EventDBEventTuple[]) {
        this.events$.next(value);
    }

    private get props(): EventDBPropertyTuple[] {
        return this.props$.getValue();
    }

    private set props(value: EventDBPropertyTuple[]) {
        this.props$.next(value);
    }

    private get displayProps(): EventDBPropertyTuple[] {
        return this.displayProps$.getValue();
    }

    private set displayProps(value: EventDBPropertyTuple[]) {
        this.displayProps$.next(value);
    }

    private get isDataLoading(): boolean {
        return this.isDataLoading$.getValue();
    }

    private set isDataLoading(value: boolean) {
        this.isDataLoading$.next(value);
    }

    private get colorsEnabled(): boolean {
        return this.colorsEnabled$.getValue();
    }

    private set colorsEnabled(value: boolean) {
        this.colorsEnabled$.next(value);
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
