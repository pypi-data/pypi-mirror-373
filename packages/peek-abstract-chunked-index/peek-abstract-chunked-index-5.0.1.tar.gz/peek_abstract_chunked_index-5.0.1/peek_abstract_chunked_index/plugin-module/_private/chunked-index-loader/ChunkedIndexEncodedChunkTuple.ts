import { addTupleType, Tuple } from "@synerty/vortexjs";

@addTupleType
export class ChunkedIndexEncodedChunkTuple extends Tuple {
    public static readonly tupleName =
        chunkedIndexTuplePrefix + "ChunkedIndexEncodedChunkTuple";

    chunkKey: string;
    lastUpdate: string;
    encodedData: string;

    constructor() {
        super(ChunkedIndexEncodedChunkTuple.tupleName);
    }
}
