import { addTupleType, Tuple } from "@synerty/vortexjs";
import { docDbTuplePrefix } from "./_private/PluginNames";

@addTupleType
export class DocDbModelSetTuple extends Tuple {
    public static readonly tupleName = docDbTuplePrefix + "DocDbModelSet";

    //  The unique key of this document
    id: number;

    //  The unique key of this document
    key: string;

    //  The unique key of this document
    name: string;

    constructor() {
        super(DocDbModelSetTuple.tupleName);
    }
}
