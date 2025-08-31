import { addTupleType, Tuple } from "@synerty/vortexjs";
import { eventdbTuplePrefix } from "../_private/PluginNames";

@addTupleType
export class EventDBEventTuple extends Tuple {
    public static readonly tupleName = eventdbTuplePrefix + "EventDBEventTuple";

    //  The datetime of the event or alarm
    dateTime: Date;

    //  The unique id of this event / alarm
    key: string;

    //  Is this alarm/event an alarm
    isAlarm: boolean;

    //  A json object storing the alarm / event data
    value: any;

    color: string | null;

    constructor() {
        super(EventDBEventTuple.tupleName);
    }
}
