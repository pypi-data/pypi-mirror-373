import { addTupleType, Tuple } from "@synerty/vortexjs";
import { chunkedIndexTuplePrefix } from "../PluginNames";

@addTupleType
export class ChunkedIndexUpdateDateTuple extends Tuple {
    public static readonly tupleName =
        chunkedIndexTuplePrefix + "ChunkedIndexUpdateDateTuple";
    initialLoadComplete: boolean = false;
    updateDateByChunkKey: {} = {};
    // Improve performance of the JSON serialisation
    protected _rawJonableFields = [
        "initialLoadComplete",
        "updateDateByChunkKey",
    ];

    constructor() {
        super(ChunkedIndexUpdateDateTuple.tupleName);
    }
}
