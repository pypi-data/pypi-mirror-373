import {
    ChangeDetectionStrategy,
    Component,
    Input,
    OnInit,
} from "@angular/core";
import { takeUntil } from "rxjs/operators";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { EventDbController } from "../../controllers/event-db.controller";
import { FilterI } from "../../controllers/event-db.types";
import { BehaviorSubject } from "rxjs";

@Component({
    selector: "plugin-eventdb-event-toolbar",
    templateUrl: "event-toolbar.component.html",
    styleUrls: ["./event-toolbar.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EventDBToolbarComponent
    extends NgLifeCycleEvents
    implements OnInit
{
    @Input() controller: EventDbController;

    protected readonly colorsEnabled$ = new BehaviorSubject<boolean>(false);
    protected readonly alarmsOnlyEnabled$ = new BehaviorSubject<boolean>(false);
    protected readonly liveEnabled$ = new BehaviorSubject<boolean>(true);

    private currentFilter: FilterI | null = null;

    constructor() {
        super();
    }

    get colorsEnabled(): boolean {
        return this.colorsEnabled$.getValue();
    }

    set colorsEnabled(value: boolean) {
        this.colorsEnabled$.next(value);
    }

    get alarmsOnlyEnabled(): boolean {
        return this.alarmsOnlyEnabled$.getValue();
    }

    set alarmsOnlyEnabled(value: boolean) {
        this.alarmsOnlyEnabled$.next(value);
    }

    get liveEnabled(): boolean {
        return this.liveEnabled$.getValue();
    }

    set liveEnabled(value: boolean) {
        this.liveEnabled$.next(value);
    }

    override ngOnInit() {
        this.controller
            .getState$()
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((state) => {
                this.colorsEnabled = state.colorsEnabled;
                this.alarmsOnlyEnabled = state.alarmsOnlyEnabled;
                this.liveEnabled = state.liveEnabled;
                // Update current filter
                this.currentFilter = {
                    modelSetKey: state.modelSetKey,
                    alarmsOnly: state.alarmsOnlyEnabled,
                    dateTimeRange: state.dateTimeRange,
                    criteria: state.selectedCriterias,
                };
            });
    }

    handleDownload(): string {
        return this.controller.getDownloadUrl();
    }

    handleColorsToggle(enabled: boolean): void {
        this.controller.updateColors(enabled);
        this.controller.updateRoute();
    }

    handleAlarmsOnlyToggle(enabled: boolean): void {
        this.controller.updateAlarmsOnly(enabled);
        this.controller.updateRoute();
    }

    handleLiveToggle(enabled: boolean): void {
        this.controller.updateLive(enabled);
        this.controller.updateRoute();
    }
}