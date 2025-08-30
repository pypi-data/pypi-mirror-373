import { addTupleType, TupleActionABC } from "@synerty/vortexjs";
import { livedbTuplePrefix } from "../PluginNames";

@addTupleType
export class AddIntValueActionTuple extends TupleActionABC {
    static readonly tupleName = livedbTuplePrefix + "AddIntValueActionTuple";

    stringIntId: number;
    offset: number;

    constructor() {
        super(AddIntValueActionTuple.tupleName);
    }
}
