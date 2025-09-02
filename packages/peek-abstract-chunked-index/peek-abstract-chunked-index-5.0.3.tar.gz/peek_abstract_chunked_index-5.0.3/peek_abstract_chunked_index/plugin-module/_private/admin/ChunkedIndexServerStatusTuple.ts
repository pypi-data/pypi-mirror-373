import { addTupleType, Tuple } from "@synerty/vortexjs";

@addTupleType
export class ChunkedIndexServerStatusTuple extends Tuple {
    public static readonly tupleName =
        chunkedIndexTuplePrefix + "ChunkedIndexServerStatusTuple";

    chunkedIndexCompilerQueueStatus: boolean;
    chunkedIndexCompilerQueueSize: number;
    chunkedIndexCompilerQueueProcessedTotal: number;
    chunkedIndexCompilerQueueLastError: string;

    constructor() {
        super(ChunkedIndexServerStatusTuple.tupleName);
    }
}
