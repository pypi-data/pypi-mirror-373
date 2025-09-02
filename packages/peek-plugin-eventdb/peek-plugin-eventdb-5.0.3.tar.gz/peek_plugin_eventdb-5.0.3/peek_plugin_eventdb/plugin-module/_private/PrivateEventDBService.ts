import { BehaviorSubject, Observable } from "rxjs";
import { map, takeUntil } from "rxjs/operators";
import { Injectable } from "@angular/core";
import { NgLifeCycleEvents, TupleSelector } from "@synerty/vortexjs";
import {
    EventDBPropertyShowFilterAsEnum,
    EventDBPropertyTuple,
} from "../tuples/EventDBPropertyTuple";
import { EventDBPropertyCriteriaTuple } from "../tuples/EventDBPropertyCriteriaTuple";
import { EventDBEventTuple } from "../tuples/EventDBEventTuple";
import { EventDateTimeRangeI, EventDBService } from "../EventDBService";
import { EventDBTupleService } from "./EventDBTupleService";

@Injectable()
export class PrivateEventDBService
    extends NgLifeCycleEvents
    implements EventDBService
{
    private _propertiesByModelSetKey: {
        [modelSetKey: string]: EventDBPropertyTuple[];
    } = {};
    private _subjectByModelSetKey: {
        [modelSetKey: string]: BehaviorSubject<EventDBPropertyTuple[]>;
    } = {};
    private _isReady: boolean = false;

    constructor(private tupleService: EventDBTupleService) {
        super();
        this.initialLoad();
    }

    shutdown(): void {}

    isReady(): boolean {
        return this._isReady;
    }

    propertyTuples(
        modelSetKey: string,
    ): Observable<EventDBPropertyTuple[]> | null {
        if (this._subjectByModelSetKey[modelSetKey] == null) {
            const props = this._propertiesByModelSetKey[modelSetKey];
            this._subjectByModelSetKey[modelSetKey] = new BehaviorSubject<
                EventDBPropertyTuple[]
            >(props || []);
        }

        const subject = this._subjectByModelSetKey[modelSetKey];
        return subject ? subject : null;
    }

    eventTuples(
        modelSetKey: string,
        dateTimeRange: EventDateTimeRangeI | null = null,
        criteria: EventDBPropertyCriteriaTuple[] = [],
        alarmsOnly: boolean,
    ): Observable<EventDBEventTuple[]> {
        if (modelSetKey == null || modelSetKey.length === 0) {
            throw new Error(
                "eventTuples: modelSetKey argument is null" +
                    " or an empty string",
            );
        }

        const ts = this.eventTupleSelector(
            modelSetKey,
            dateTimeRange,
            criteria,
            alarmsOnly,
        );

        const observable: Observable<EventDBEventTuple[]> = <
            Observable<EventDBEventTuple[]>
        >this.tupleService.offlineObserver
            .subscribeToTupleSelector(ts)
            .pipe(takeUntil(this.onDestroyEvent));

        return observable.pipe(
            map((events: EventDBEventTuple[]) => {
                // Convert the json string to actual json objects
                // Don't do it if it's already done as
                // VortexJS caches the data in memory for a short period.
                if (events != null && events.length != 0) {
                    if (typeof events[0].value === "string") {
                        for (let event of events) {
                            event.value = JSON.parse(event.value);
                        }
                    }
                }
                return events;
            }),
        );
    }

    eventTupleSelector(
        modelSetKey: string,
        dateTimeRange: EventDateTimeRangeI | null = null,
        criteria: EventDBPropertyCriteriaTuple[] = [],
        alarmsOnly: boolean,
    ): TupleSelector {
        const P = EventDBPropertyShowFilterAsEnum;

        const singleCriterias = {};
        const multiCriterias = {};

        for (let cri of criteria) {
            if (cri.property.showFilterAs == P.SHOW_FILTER_AS_FREE_TEXT) {
                singleCriterias[cri.property.key] = cri.value;
            } else if (
                cri.property.showFilterAs == P.SHOW_FILTER_SELECT_MANY ||
                cri.property.showFilterAs == P.SHOW_FILTER_SELECT_ONE
            ) {
                // Make sure
                multiCriterias[cri.property.key] = cri.value;
            } else {
                throw new Error("Unknown Property Type");
            }
        }

        return new TupleSelector(EventDBEventTuple.tupleName, {
            modelSetKey: modelSetKey,
            alarmsOnly: alarmsOnly,
            newestDateTime:
                dateTimeRange != null ? dateTimeRange.newestDateTime : null,
            oldestDateTime:
                dateTimeRange != null ? dateTimeRange.oldestDateTime : null,
            singleCriterias: singleCriterias,
            multiCriterias: multiCriterias,
        });
    }

    private initialLoad(): void {
        const ts = new TupleSelector(EventDBPropertyTuple.tupleName, {});

        this.tupleService.offlineObserver
            .subscribeToTupleSelector(ts)
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: EventDBPropertyTuple[]) => {
                this._propertiesByModelSetKey = {};
                const dict = this._propertiesByModelSetKey;

                for (let item of tuples) {
                    // Coord Set by Coord Set Key, by Model Set Key
                    const data =
                        dict[item.modelSetKey] == null
                            ? (dict[item.modelSetKey] = [])
                            : dict[item.modelSetKey];

                    data.push(item);
                }

                this._isReady = tuples.length != 0;
                for (let key of Object.keys(dict)) {
                    const subject = this._subjectByModelSetKey[key];
                    if (subject != null) subject.next(dict[key]);
                }
            });
    }
}
