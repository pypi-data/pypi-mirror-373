Overview
--------

The following sections describe the parts of the Peek EventDB plugin.

Importers
`````````

Items in the EventDB must first be "imported" before they are available for use.
The EventDB doesn't not currently support deleting an item.

Data Acquisition
````````````````

The EventDB does not directly acquire the values of any data,
other plugins are responsible for integrating with the EventDB and acquiring item values
from external systems.

The EventDB provides Observables that fire when events are added.


Model Set
`````````

The EventDB can contain multiple data/model sets. Each model set is isolated from any
other model set.

EventDB Event
`````````````

The EventDB stores simple events, Each item has the following properties :

:Date Time: The unique identifier of this item with in the model set.

:Key: The unique identifier of this event with in the model set.

:Value: A json object containing the details of the event.

