import { addTupleType, Tuple } from "@synerty/vortexjs";
import { eventdbTuplePrefix } from "../PluginNames";

@addTupleType
export class EventDBPropertyValueTableTuple extends Tuple {
    public static readonly tupleName =
        eventdbTuplePrefix + "EventDBPropertyValueTable";

    id: number;
    name: string;
    value: string;
    color: string;
    comment: string | null;

    propertyId: number;

    constructor() {
        super(EventDBPropertyValueTableTuple.tupleName);
    }

    get isValid(): boolean {
        return (
            this.value != null &&
            this.value.length !== 0 &&
            this.name != null &&
            this.name.length !== 0
        );
    }
}
