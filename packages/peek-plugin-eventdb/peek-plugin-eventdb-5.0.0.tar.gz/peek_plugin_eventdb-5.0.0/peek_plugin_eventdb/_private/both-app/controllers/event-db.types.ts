import {
    EventDBEventTuple,
    EventDBPropertyCriteriaTuple,
    EventDBPropertyTuple,
} from "@peek/peek_plugin_eventdb/tuples";
import { EventDateTimeRangeI } from "@peek/peek_plugin_eventdb";

export interface ColumnI {
    selectedProps: EventDBPropertyTuple[];
}

export interface FilterI {
    modelSetKey: string;
    alarmsOnly: boolean;
    dateTimeRange: EventDateTimeRangeI;
    criteria: EventDBPropertyCriteriaTuple[];
}

export interface RouteFilterI {
    live: boolean;
    alarmsOnly: boolean;
    cri: { [key: string]: string | string[] };
    from: string;
    to: string;
    dateTimeRange?: EventDateTimeRangeI;
    criteria?: EventDBPropertyCriteriaTuple[];
}

export interface EventState {
    modelSetKey: string;
    events: EventDBEventTuple[];
    isDataLoading: boolean;
    colorsEnabled: boolean;
    displayProps: EventDBPropertyTuple[];
    allProps: EventDBPropertyTuple[];
    filterProps: EventDBPropertyTuple[];
    liveEnabled: boolean;
    alarmsOnlyEnabled: boolean;
    dateTimeRange: EventDateTimeRangeI;
    selectedCriterias: EventDBPropertyCriteriaTuple[];
}
