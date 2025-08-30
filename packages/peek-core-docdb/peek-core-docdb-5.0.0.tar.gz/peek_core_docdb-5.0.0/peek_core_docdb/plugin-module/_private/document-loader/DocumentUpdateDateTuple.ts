import { addTupleType, Tuple } from "@synerty/vortexjs";
import { docDbTuplePrefix } from "../PluginNames";

@addTupleType
export class DocumentUpdateDateTuple extends Tuple {
    public static readonly tupleName =
        docDbTuplePrefix + "DocumentUpdateDateTuple";
    initialLoadComplete: boolean = false;
    updateDateByChunkKey: {} = {};
    // Improve performance of the JSON serialisation
    protected override _rawJonableFields = [
        "initialLoadComplete",
        "updateDateByChunkKey",
    ];

    constructor() {
        super(DocumentUpdateDateTuple.tupleName);
    }
}
