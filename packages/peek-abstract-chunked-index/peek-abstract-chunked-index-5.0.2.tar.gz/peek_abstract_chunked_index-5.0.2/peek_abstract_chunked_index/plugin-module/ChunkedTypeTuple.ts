import { addTupleType, Tuple } from "@synerty/vortexjs";
import { chunkedIndexTuplePrefix } from "./_private/PluginNames";

@addTupleType
export class ChunkedTypeTuple extends Tuple {
    public static readonly tupleName =
        chunkedIndexTuplePrefix + "ChunkedTypeTuple";

    //  A protected variable
    id__: number;

    //  The key of this ChunkedType
    key: string;

    //  The key of the model set
    modelSetKey: string;

    //  The name of the ChunkedType
    name: string;

    constructor() {
        super(ChunkedTypeTuple.tupleName);
    }
}
