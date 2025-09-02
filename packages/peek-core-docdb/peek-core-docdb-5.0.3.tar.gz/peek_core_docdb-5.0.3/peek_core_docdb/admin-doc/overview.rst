Overview
--------

The following sections describe the parts of the DocDB plugin.

Importers
`````````

The DocDB is populated by other plugins. Other plugins can call the import APIs for
DocDB.

Document contents are replaced, they are not updated or merged when imported from
multiple sources.

Client Cache
````````````

The DocDB caches all documents in memory in the Peek Client service
as compressed chunks/blocks of data.

Model Set
`````````

The DocDB plugin supports multiple model sets. Each model set has it's own unique
set of documents.

Document
````````

The Document is the DocDBs sole reason for existing.

A document is generic JSON like object, this is ideal for providing arbitrary
object information. For example, Equipment details that are shown to the user, but are
not required in a connectivity model, diagram or search index.

An object stored in the GraphDB, Diagram and Search plugins can be stored in those
plugins using only the data required in those plugins. While DocDB provides informational
attributes for the object.

Document Type
`````````````

Documents can have document types. Nice names for these document types can be set
from the Peek Admin interface.

Document Properties
```````````````````

The DocDB plugin provides a list of property type names, so the user can see a nicer name
than the keys in the document.

This also allows shorter value keys to be imported as this key is stored in every
document, a shorter key requires less storage and data transfer.



