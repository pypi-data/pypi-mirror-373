import { addTupleType, Tuple } from "@synerty/vortexjs";
import { eventdbTuplePrefix } from "../PluginNames";

@addTupleType
export class EventDBModelSetTableTuple extends Tuple {
    public static readonly tupleName =
        eventdbTuplePrefix + "EventDBModelSetTable";

    id: number;
    key: string;
    name: string;
    comment: string;
    propsJson: object;

    constructor() {
        super(EventDBModelSetTableTuple.tupleName);
    }
}
