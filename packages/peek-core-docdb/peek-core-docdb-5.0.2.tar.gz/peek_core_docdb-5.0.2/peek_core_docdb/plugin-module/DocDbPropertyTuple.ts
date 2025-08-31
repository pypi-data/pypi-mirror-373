import { addTupleType, Tuple } from "@synerty/vortexjs";
import { docDbTuplePrefix } from "./_private/PluginNames";

@addTupleType
export class DocDbPropertyTuple extends Tuple {
    public static readonly tupleName = docDbTuplePrefix + "DocDbPropertyTuple";

    //  The id
    id: number;

    //  The modelSetId of the document property
    modelSetId: number;

    //  The name of the document property
    name: string;

    //  The title of the document property
    title: string;

    //  The order of the document property
    order: number;

    // Show on Tooltip Popup
    showOnTooltip: boolean;

    // Show on Summary Popup
    showOnSummary: boolean;

    // Show on Detail Popup
    showOnDetail: boolean;

    // Show on the header of any popup screen
    showInHeader: boolean;

    constructor() {
        super(DocDbPropertyTuple.tupleName);
    }
}
