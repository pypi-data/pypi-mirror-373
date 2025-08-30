import { addTupleType, Tuple } from "@synerty/vortexjs";
import { eventdbTuplePrefix } from "../PluginNames";
import { EventDBPropertyValueTableTuple } from "./EventDBPropertyValueTableTuple";

@addTupleType
export class EventDBPropertyTableTuple extends Tuple {
    public static readonly tupleName =
        eventdbTuplePrefix + "EventDBPropertyTable";

    id: number;
    modelSetId: number;

    key: string;
    name: string;
    order: number;
    comment: string | null;

    useForFilter: boolean | null;
    useForDisplay: boolean | null;
    useForPopup: boolean | null;

    displayByDefaultOnSummaryView: boolean | null;
    displayByDefaultOnDetailView: boolean | null;

    showFilterAs: number | null;

    valuesFromAdminUi: EventDBPropertyValueTableTuple[] = [];

    // UI state properties, not for storage
    uiExpandValues = false;

    constructor() {
        super(EventDBPropertyTableTuple.tupleName);
    }

    get isValid(): boolean {
        return (
            this.modelSetId != null &&
            this.key != null &&
            this.key.length !== 0 &&
            this.name != null &&
            this.name.length !== 0 &&
            this.order != null
        );
    }

    get enableValues(): boolean {
        return this.showFilterAs === 2 || this.showFilterAs === 3;
    }
}
