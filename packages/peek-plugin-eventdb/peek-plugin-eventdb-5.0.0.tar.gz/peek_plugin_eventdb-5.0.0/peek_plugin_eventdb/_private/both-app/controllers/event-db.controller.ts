import { BehaviorSubject, Observable, Subject } from "rxjs";
import { EventState, FilterI, RouteFilterI } from "./event-db.types";
import {
    EventDBEventTuple,
    EventDBPropertyCriteriaTuple,
    EventDBPropertyTuple,
} from "@peek/peek_plugin_eventdb/tuples";
import { PrivateEventDBService } from "@peek/peek_plugin_eventdb/_private/PrivateEventDBService";

import { SerialiseUtil } from "@synerty/vortexjs";
import { takeUntil } from "rxjs/operators";
import { ActivatedRoute, Params, Router } from "@angular/router";

export class EventDbController {
    private destroy$ = new Subject<void>();
    private routeUpdateTimer: any | null = null;
    private state: EventState = {
        modelSetKey: "",
        events: [],
        isDataLoading: true,
        colorsEnabled: false,
        displayProps: [],
        allProps: [],
        filterProps: [],
        liveEnabled: true,
        alarmsOnlyEnabled: false,
        dateTimeRange: null,
        selectedCriterias: [],
    };

    private state$ = new BehaviorSubject<EventState>(this.state);
    private liveUpdateTimer: any;
    private criteriaByPropKey: { [key: string]: EventDBPropertyCriteriaTuple } =
        {};
    private propByKey: { [key: string]: EventDBPropertyTuple } = {};

    private unsubLastEventsSubject = new Subject<void>();

    constructor(
        public modelSetKey: string,
        private route: ActivatedRoute,
        private router: Router,
        private eventService: PrivateEventDBService,
    ) {
        this.initializeLiveUpdate();
        this.initializeFromRoute();
    }

    getState$(): Observable<EventState> {
        return this.state$;
    }

    initialize(modelSetKey: string): void {
        this.state.modelSetKey = modelSetKey;
        this.state.dateTimeRange = {
            oldestDateTime: this.defaultOldestDateTime(),
            newestDateTime: null,
        };

        this.loadProperties();
    }

    applyDefaultColumns(): void {
        if (this.state.allProps.length === 0) return;

        const defaultProps = this.state.allProps.filter(
            (prop) => prop.displayByDefaultOnDetailView,
        );
        this.updateDisplayProps(defaultProps);
    }

    applyColumnParams(params: string): void {
        if (this.state.allProps.length === 0) {
            console.warn("Cannot apply column params: allProps not loaded");
            return;
        }

        if (!params) {
            console.warn("Empty column params provided");
            return;
        }

        const propKeys = params.split(",").filter((key) => key.trim());
        const selectedProps = propKeys
            .map((key) => this.state.allProps.find((prop) => prop.key === key))
            .filter((prop): prop is EventDBPropertyTuple => prop != null);

        if (selectedProps.length > 0) {
            this.updateDisplayProps(selectedProps);
        } else {
            console.warn("No valid columns found in params, applying defaults");
            this.applyDefaultColumns();
        }
    }

    updateColors(colorsEnabled: boolean): void {
        this.updateState({ colorsEnabled });
    }

    updateLive(liveEnabled: boolean): void {
        this.updateState({ liveEnabled });

        if (liveEnabled) {
            this.liveEnabledUpdateTimerCall();
        } else if (this.state.dateTimeRange.newestDateTime == null) {
            const dateTimeRange = {
                ...this.state.dateTimeRange,
                newestDateTime: new Date(),
            };
            this.updateState({ dateTimeRange });
            this.fetchEvents();
        }
    }

    updateAlarmsOnly(alarmsOnlyEnabled: boolean): void {
        this.updateState({ alarmsOnlyEnabled });
        this.fetchEvents();
    }

    updateDisplayProps(displayProps: EventDBPropertyTuple[]): void {
        // Validate the display props
        if (!Array.isArray(displayProps) || displayProps.length === 0) {
            console.warn("Invalid or empty display props provided");
            return;
        }

        // Ensure all props exist in allProps
        const validProps = displayProps.filter((prop) =>
            this.state.allProps.some((p) => p.key === prop.key),
        );

        if (validProps.length === 0) {
            console.warn("No valid display props found");
            return;
        }

        // Only update if the props have actually changed
        const currentKeys = this.state.displayProps
            .map((p) => p.key)
            .sort()
            .join(",");
        const newKeys = validProps
            .map((p) => p.key)
            .sort()
            .join(",");

        if (currentKeys !== newKeys) {
            this.updateState({ displayProps: validProps });
        }
    }

    updateFilter(filter: FilterI): void {
        this.updateState({
            dateTimeRange: filter.dateTimeRange,
            selectedCriterias: filter.criteria,
            alarmsOnlyEnabled: filter.alarmsOnly,
        });
        this.fetchEvents();
    }

    private fetchEvents(): void {
        this.unsubLastEventsSubject.next();
        this.updateState({ isDataLoading: true });

        this.eventService
            .eventTuples(
                this.state.modelSetKey,
                this.state.dateTimeRange,
                this.state.selectedCriterias,
                this.state.alarmsOnlyEnabled,
            )
            .pipe(
                takeUntil(this.destroy$),
                takeUntil(this.unsubLastEventsSubject),
            )
            .subscribe((events: EventDBEventTuple[]) => {
                this.updateState({ events, isDataLoading: false });
            });
    }

    applyRouteParams(params: RouteFilterI): void {
        if (this.state.allProps.length === 0) return;

        const tsUtil = new SerialiseUtil();
        const selectedCriterias = [];
        this.criteriaByPropKey = {};

        // Load in the criteria
        for (let propKey of Object.keys(params.cri || {})) {
            const prop: EventDBPropertyTuple = this.propByKey[propKey];
            if (prop == null) continue;

            const val = params.cri[prop.key];
            const criteria = this.createCriteria(prop);
            criteria.value = val;
            selectedCriterias.push(criteria);
        }

        // Load in the from/to datetimes
        const dateTimeRange = {
            oldestDateTime: this.nullOrDateStr(params.from, tsUtil),
            newestDateTime: this.nullOrDateStr(params.to, tsUtil),
        };

        this.updateState({
            selectedCriterias,
            dateTimeRange,
            liveEnabled: params.live !== false,
            alarmsOnlyEnabled: params.alarmsOnly !== false,
        });

        this.fetchEvents();
    }

    destroy(): void {
        this.destroy$.next();
        this.destroy$.complete();
        if (this.liveUpdateTimer) {
            clearInterval(this.liveUpdateTimer);
        }
        if (this.routeUpdateTimer != null) {
            clearTimeout(this.routeUpdateTimer);
        }
    }

    updateRoute(): void {
        if (this.routeUpdateTimer != null) clearTimeout(this.routeUpdateTimer);
        this.routeUpdateTimer = setTimeout(() => this._updateRoute(), 500);
    }

    getDownloadUrl(): string {
        if (!this.state.displayProps || this.state.displayProps.length === 0) {
            return "";
        }

        const columnPropKeys = this.state.displayProps.map((prop) => prop.key);

        const tupleSelector = this.eventService.eventTupleSelector(
            this.state.modelSetKey,
            this.state.dateTimeRange,
            this.state.selectedCriterias,
            this.state.alarmsOnlyEnabled,
        );

        // Add the column property keys to the selector
        tupleSelector.selector["columnPropKeys"] = columnPropKeys;

        return (
            "/peek_plugin_eventdb/download/events?tupleSelector=" +
            encodeURIComponent(tupleSelector.toOrderedJsonStr())
        );
    }

    private _updateRoute(): void {
        this.routeUpdateTimer = null;

        // Get the base URL without parameters
        let url = this.router.url.split(";")[0];

        if (url.indexOf("peek_plugin_eventdb") == -1) return;

        // Validate display props before including in route
        if (!this.state.displayProps || this.state.displayProps.length === 0) {
            console.warn("No display props available for route update");
            return;
        }

        const params = {
            color: this.state.colorsEnabled,
            modelSetKey: this.state.modelSetKey,
            filter: JSON.stringify({
                live: this.state.liveEnabled,
                alarmsOnly: this.state.alarmsOnlyEnabled,
                cri: this.getCriteria(),
                from: this.state.dateTimeRange?.oldestDateTime?.toISOString(),
                to: this.state.dateTimeRange?.newestDateTime?.toISOString(),
            }),
            columns: this.state.displayProps.map((prop) => prop.key).join(","),
        };

        this.router.navigate([url, params]);
    }

    private getCriteria(): { [key: string]: string | string[] } {
        const cri: { [key: string]: any } = {};
        for (const criteria of this.state.selectedCriterias) {
            if (criteria.value != null && criteria.value.length > 0) {
                cri[criteria.property.key] = criteria.value;
            }
        }
        return cri;
    }

    private updateState(partial: Partial<EventState>): void {
        this.state = { ...this.state, ...partial };
        this.state$.next(this.state);
    }

    private loadProperties(): void {
        this.eventService
            .propertyTuples(this.state.modelSetKey)
            .pipe(takeUntil(this.destroy$))
            .subscribe((props: EventDBPropertyTuple[]) => {
                const allProps = props;
                const filterProps = props
                    .filter((prop) => prop.useForFilter)
                    .sort((a, b) => a.order - b.order);

                this.propByKey = {};
                for (let prop of filterProps) {
                    this.propByKey[prop.key] = prop;
                }

                // First update the allProps and filterProps
                this.updateState({ allProps, filterProps });

                // Then set default display columns if none are set
                if (this.state.displayProps.length === 0) {
                    const defaultProps = allProps.filter(
                        (prop) => prop.displayByDefaultOnDetailView,
                    );
                    this.updateDisplayProps(defaultProps);
                }
            });
    }

    private initializeLiveUpdate(): void {
        this.liveUpdateTimer = setInterval(
            () => this.liveEnabledUpdateTimerCall(),
            10 * 60 * 1000,
        );
    }

    private liveEnabledUpdateTimerCall(): void {
        if (!this.state.liveEnabled) return;

        const dateTimeRange: { [key: string]: any } = {
            oldestDateTime: this.defaultOldestDateTime(),
            newestDateTime: null,
        };

        this.updateState({ dateTimeRange });
        this.fetchEvents();
    }

    private defaultOldestDateTime(): Date {
        const newDate = new Date();
        // Subtract 2 hours
        newDate.setHours(newDate.getHours() - 2);
        // Round down to nearest 5 minutes
        const minute = newDate.getMinutes();
        newDate.setMinutes(minute - (minute % 5));
        newDate.setSeconds(0);
        newDate.setMilliseconds(0);
        return newDate;
    }

    private nullOrDateStr(strIn: string, tsUtil: SerialiseUtil): Date | null {
        if (strIn == null) return null;
        return tsUtil.fromStr(strIn, SerialiseUtil.T_DATETIME);
    }

    private createCriteria(
        prop: EventDBPropertyTuple,
    ): EventDBPropertyCriteriaTuple {
        if (this.criteriaByPropKey[prop.key] == null) {
            this.criteriaByPropKey[prop.key] =
                new EventDBPropertyCriteriaTuple();
            this.criteriaByPropKey[prop.key].property = prop;
        }
        return this.criteriaByPropKey[prop.key];
    }

    private initializeFromRoute(): void {
        let isInitialLoad = true;
        this.route.params
            .pipe(takeUntil(this.destroy$))
            .subscribe((params: Params) => {
                // Add debounce for subsequent updates
                if (!isInitialLoad) {
                    if (this.routeUpdateTimer != null) {
                        clearTimeout(this.routeUpdateTimer);
                    }
                    this.routeUpdateTimer = setTimeout(
                        () => this.processRouteParams(params),
                        100,
                    );
                    return;
                }

                this.processRouteParams(params);

                if (isInitialLoad) {
                    this.fetchEvents();
                }
                isInitialLoad = false;
            });
        let vars: { [key: string]: string } = {};

        if (typeof window !== "undefined") {
            window.location.href.replace(
                /[?&]+([^=&]+)=([^&]*)/gi,
                (m, key, value) => (vars[key] = value),
            );
        }
    }

    private processRouteParams(params: Params): void {
        let vars: { [key: string]: string } = {};

        if (typeof window !== "undefined") {
            window.location.href.replace(
                /[?&]+([^=&]+)=([^&]*)/gi,
                (m, key, value) => (vars[key] = value),
            );
        }

        let columns = params["columns"] || vars["columns"] || "";
        let filter = params["filter"] || vars["filter"] || "{}";
        const modelSetKey =
            params["modelSetKey"] || vars["modelSetKey"] || this.modelSetKey;
        const color = (params["color"] || vars["color"]) == "true";

        filter = JSON.parse(filter);

        this.modelSetKey = modelSetKey;
        this.updateColors(color);

        // Apply column and filter changes
        if (columns) {
            this.applyColumnParams(columns);
        } else {
            this.applyDefaultColumns();
        }

        this.applyRouteParams(filter);

        // Emit state changes to subscribers
        this.updateState({
            modelSetKey: this.modelSetKey,
            colorsEnabled: color,
        });
    }
}
