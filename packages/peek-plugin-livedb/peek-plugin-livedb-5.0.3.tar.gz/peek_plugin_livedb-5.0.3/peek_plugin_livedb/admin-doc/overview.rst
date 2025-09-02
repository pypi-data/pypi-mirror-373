Overview
--------

The following sections describe the parts of the Peek LiveDB plugin.

Importers
`````````

Items in the LiveDB must first be "imported" before they are available for use.
The LiveDB doesn't not currently support deleting an item.

Data Acquisition
````````````````

The LiveDB does not directly acquire the values of any data,
other plugins are responsible for integrating with the LiveDB and acquiring item values
from external systems.

The LiveDB provides Observables that fire when items are added, deleted or a force poll
is required.

The LiveDB supports a list of priority items, allowing data acquisition plugins to
prioritise these values in their polling schemes.

Model Set
`````````

The LiveDB can contain multiple data/model sets. Each model set is isolated from any
other model set.

LiveDB Item
```````````

The LiveDB stores simple items which are similar to key/value pairs.

Each item has the following properties :

:Model Set: The model set this item belongs to.

:Key: The unique identifier of this item with in the model set.

:Data Type: The type of data that this item represents, this can be,
    Number, String, Colour, Line Width, Line Style, Group Ptr

:Raw Value: The raw value aquired from the data source, (SCADA, etc)

:Display Value: The converted display value, typically used by the Diagram plugin.

Value Observers
```````````````

The LiveDB glues data from other plugins together with heavy use of observables.

For example, the Peek Diagram plugin observes all display value changes for a model set.




