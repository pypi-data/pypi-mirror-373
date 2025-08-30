import { addTupleType, Tuple } from "@synerty/vortexjs";
import { livedbTuplePrefix } from "../PluginNames";

@addTupleType
export class StringIntTuple extends Tuple {
    public static readonly tupleName = livedbTuplePrefix + "StringIntTuple";

    //  Description of date1
    id: number;

    //  Description of string1
    string1: string;

    //  Description of int1
    int1: number;

    constructor() {
        super(StringIntTuple.tupleName);
    }
}
