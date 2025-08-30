import { addTupleType, Tuple } from "@synerty/vortexjs";

@addTupleType
export class OfflineConfigTuple extends Tuple {
    public static readonly tupleName =
        chunkedIndexTuplePrefix + "OfflineConfigTuple";

    cacheChunksForOffline: boolean = false;

    constructor() {
        super(OfflineConfigTuple.tupleName);
    }
}
