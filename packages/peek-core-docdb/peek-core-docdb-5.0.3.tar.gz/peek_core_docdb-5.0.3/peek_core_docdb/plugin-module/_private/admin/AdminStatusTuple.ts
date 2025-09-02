import { addTupleType, Tuple } from "@synerty/vortexjs";
import { docDbTuplePrefix } from "../PluginNames";

@addTupleType
export class AdminStatusTuple extends Tuple {
    public static readonly tupleName = docDbTuplePrefix + "AdminStatusTuple";

    documentCompilerQueueStatus: boolean;
    documentCompilerQueueSize: number;
    documentCompilerQueueProcessedTotal: number;
    documentCompilerQueueLastError: string;

    constructor() {
        super(AdminStatusTuple.tupleName);
    }
}
