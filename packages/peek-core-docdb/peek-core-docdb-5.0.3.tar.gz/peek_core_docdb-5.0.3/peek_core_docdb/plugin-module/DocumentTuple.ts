import { addTupleType, Tuple } from "@synerty/vortexjs";
import { docDbTuplePrefix } from "./_private/PluginNames";
import { DocDbDocumentTypeTuple } from "./DocDbDocumentTypeTuple";
import { DocDbModelSetTuple } from "./DocDbModelSetTuple";

@addTupleType
export class DocumentTuple extends Tuple {
    public static readonly tupleName = docDbTuplePrefix + "DocumentTuple";

    //  The unique key of this document
    key: string;

    //  The modelSetId for this document.
    modelSet: DocDbModelSetTuple = new DocDbModelSetTuple();

    // This Document Type ID
    documentType: DocDbDocumentTypeTuple = new DocDbDocumentTypeTuple();

    // The document data
    document: {} = {};

    constructor() {
        super(DocumentTuple.tupleName);
    }
}
