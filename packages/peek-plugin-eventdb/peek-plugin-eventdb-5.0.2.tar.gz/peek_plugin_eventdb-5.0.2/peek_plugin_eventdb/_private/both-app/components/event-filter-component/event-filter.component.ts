import { Component, Input, OnInit } from "@angular/core";
import {
    EventDBPropertyCriteriaTuple,
    EventDBPropertyShowFilterAsEnum,
    EventDBPropertyTuple,
} from "@peek/peek_plugin_eventdb/tuples";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import { EventDateTimeRangeI } from "@peek/peek_plugin_eventdb";
import { takeUntil } from "rxjs/operators";
import { EventDbController } from "../../controllers/event-db.controller";

@Component({
    selector: "plugin-eventdb-event-filter",
    templateUrl: "event-filter.component.html",
    styleUrls: ["./event-filter.component.scss"],
})
export class EventDBFilterComponent
    extends NgLifeCycleEvents
    implements OnInit
{
    @Input() controller: EventDbController;

    isVisible = false;
    isOkLoading = false;
    filterProps: EventDBPropertyTuple[] = [];
    dateTimeRange: EventDateTimeRangeI;
    liveEnabled: boolean = true;
    alarmsOnlyEnabled: boolean = false;
    FilterAsEnum = EventDBPropertyShowFilterAsEnum;

    private criteriaByPropKey: { [key: string]: EventDBPropertyCriteriaTuple } =
        {};

    constructor(private balloonMsg: BalloonMsgService) {
        super();
    }

    override ngOnInit() {
        this.controller
            .getState$()
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((state) => {
                this.filterProps = state.filterProps;
                this.dateTimeRange = state.dateTimeRange;
                this.liveEnabled = state.liveEnabled;
                this.alarmsOnlyEnabled = state.alarmsOnlyEnabled;
            });
    }

    criteria(prop: EventDBPropertyTuple): EventDBPropertyCriteriaTuple {
        if (this.criteriaByPropKey[prop.key] == null) {
            this.criteriaByPropKey[prop.key] =
                new EventDBPropertyCriteriaTuple();
            this.criteriaByPropKey[prop.key].property = prop;
        }
        return this.criteriaByPropKey[prop.key];
    }

    handleModalOpen(): void {
        this.isVisible = true;
    }

    handleFilterApply(): void {
        this.isOkLoading = true;

        const filter = {
            modelSetKey: this.controller.modelSetKey,
            alarmsOnly: this.alarmsOnlyEnabled,
            dateTimeRange: this.dateTimeRange,
            criteria: Object.values(this.criteriaByPropKey).filter(
                (criteria) =>
                    criteria.value != null && criteria.value.length > 0,
            ),
        };

        this.controller.updateFilter(filter);
        this.controller.updateLive(this.liveEnabled);
        this.controller.updateAlarmsOnly(this.alarmsOnlyEnabled);
        this.controller.updateRoute();

        setTimeout(() => {
            this.isVisible = false;
            this.isOkLoading = false;
        }, 500);
    }

    handleFilterReset(): void {
        this.criteriaByPropKey = {};
    }

    handleModalClose(): void {
        this.isVisible = false;
    }
}
