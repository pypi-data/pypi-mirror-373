import { addTupleType, Tuple } from "@synerty/vortexjs";
import { chunkedIndexTuplePrefix } from "./_private/PluginNames";

@addTupleType
export class ChunkedIndexModelSetTuple extends Tuple {
    public static readonly tupleName =
        chunkedIndexTuplePrefix + "ModelSetTuple";

    //  A protected variable
    id__: number;

    //  The unique key of this ModelSet
    key: string;

    //  The unique name of this ModelSet
    name: string;

    constructor() {
        super(ChunkedIndexModelSetTuple.tupleName);
    }
}
