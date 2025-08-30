import { Tuple } from "@synerty/vortexjs";
import { ChunkedTypeTuple } from "./ChunkedTypeTuple";
import { ChunkedIndexModelSetTuple } from "./ChunkedIndexModelSetTuple";
import { chunkedIndexTuplePrefix } from "./_private/PluginNames";

export abstract class ChunkedTuple extends Tuple {
    public static readonly tupleName = chunkedIndexTuplePrefix + "ChunkedTuple";

    //  The unique key of this chunkedIndex
    key: string;

    //  The modelSetId for this chunkedIndex.
    modelSet: ChunkedIndexModelSetTuple = new ChunkedIndexModelSetTuple();

    // This ChunkedIndex Type ID
    chunkedType: ChunkedTypeTuple = new ChunkedTypeTuple();

    // // A string value of the chunked
    // valueStr: string;
    //
    // // An int value of the chunked
    // valueInt: number;
    //
    // // Add more values here

    constructor() {
        super(ChunkedTuple.tupleName);
    }

    abstract unpackJson(key: string, packedJson: string): ChunkedTuple;
}
