import { Observable } from "rxjs";
import { EventDBPropertyCriteriaTuple } from "./tuples/EventDBPropertyCriteriaTuple";
import { EventDBEventTuple } from "./tuples/EventDBEventTuple";
import { EventDBPropertyTuple } from "./tuples/EventDBPropertyTuple";
import { TupleSelector } from "@synerty/vortexjs";

export interface EventDateTimeRangeI {
    oldestDateTime?: Date | null;
    newestDateTime?: Date | null;
}

/** EventDB Service
 *
 * This class is responsible for providing EventDB information to other plugins
 * and the events list in this plugin.
 *
 */
export abstract class EventDBService {
    /** Property Tuples
     *
     * Return an observable that fires with a list of property tuples.
     *
     * @param modelSetKey: The model to observe the data from.
     */
    abstract propertyTuples(
        modelSetKey: string,
    ): Observable<EventDBPropertyTuple[]> | null;

    /** Event Tuples
     *
     *
     * @param modelSetKey: The key of the model set to load data from.
     * @param dateTimeRange: The dateTime window to load events from.
     * @param criteria: Additional criteria to filter out events.
     * @param alarmsOnly: Show only the alarms.
     */
    abstract eventTuples(
        modelSetKey: string,
        dateTimeRange: EventDateTimeRangeI,
        criteria: EventDBPropertyCriteriaTuple[],
        alarmsOnly: boolean,
    ): Observable<EventDBEventTuple[]>;

    /** Event Tuples Selector
     *
     * This method will return a tuple selector used to select the data from the
     * server.
     *
     * This method is provided to allow other plugins to deduplciate calls to
     * eventTuples.
     *
     * @param modelSetKey: The key of the model set to load data from.
     * @param dateTimeRange: The dateTime window to load events from.
     * @param criteria: Additional criteria to filter out events.
     * @param alarmsOnly: Show only the alarms.
     */
    abstract eventTupleSelector(
        modelSetKey: string,
        dateTimeRange: EventDateTimeRangeI,
        criteria: EventDBPropertyCriteriaTuple[],
        alarmsOnly: boolean,
    ): TupleSelector;
}
