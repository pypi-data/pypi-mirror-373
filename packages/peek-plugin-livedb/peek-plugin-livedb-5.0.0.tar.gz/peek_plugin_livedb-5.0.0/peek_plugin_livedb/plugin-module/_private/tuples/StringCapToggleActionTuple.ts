import { addTupleType, TupleActionABC } from "@synerty/vortexjs";
import { livedbTuplePrefix } from "../PluginNames";

@addTupleType
export class StringCapToggleActionTuple extends TupleActionABC {
    static readonly tupleName =
        livedbTuplePrefix + "StringCapToggleActionTuple";

    stringIntId: number;

    constructor() {
        super(StringCapToggleActionTuple.tupleName);
    }
}
