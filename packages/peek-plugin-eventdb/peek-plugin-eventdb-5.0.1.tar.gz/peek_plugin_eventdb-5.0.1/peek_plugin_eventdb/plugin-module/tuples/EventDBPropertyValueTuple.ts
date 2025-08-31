import { addTupleType, Tuple } from "@synerty/vortexjs";
import { eventdbTuplePrefix } from "../_private/PluginNames";

/** Event DB Property Value Tuple
 
 This tuple is an option that the user can select for each property.
 
 For example:
 
 Property = Alarm Class
 Property Value = Class 1
 Property Value = Class 2
 
 */
@addTupleType
export class EventDBPropertyValueTuple extends Tuple {
    public static readonly tupleName =
        eventdbTuplePrefix + "EventDBPropertyValueTuple";

    // name: The name of this property value that is displayed to the user.
    name: string;

    // value: The value that matches
    //        EvenDBEventTuple.value[property.key] == propertyValue.value
    value: string;

    // color: If this property has a color then define it here.
    //        the first property value with a color will be applied
    //        ordered by property.order
    color: string;

    // comment: The tooltip to display to the user in a UI.
    comment: string;

    constructor() {
        super(EventDBPropertyValueTuple.tupleName);
    }
}
