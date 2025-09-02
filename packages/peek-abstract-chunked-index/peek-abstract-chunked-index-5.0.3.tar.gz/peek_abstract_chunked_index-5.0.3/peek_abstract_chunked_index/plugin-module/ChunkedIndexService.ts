import { Injectable } from "@angular/core";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import {
    ChunkedIndexLoaderService,
    ChunkedIndexResultI,
} from "./_private/chunked-index-loader";

// ----------------------------------------------------------------------------
/** ChunkedIndex Cache
 *
 * This class has the following responsibilities:
 *
 * 1) Maintain a local storage of the index
 *
 * 2) Return DispKey locations based on the index.
 *
 */
@Injectable()
export class ChunkedIndexService extends NgLifeCycleEvents {
    constructor(private chunkedIndexLoader: ChunkedIndexLoaderService) {
        super();
    }

    /** Get Chunkeds
     *
     * Get the objects for key from the index..
     *
     */
    getChunkeds(
        modelSetKey: string,
        keys: string[],
    ): Promise<ChunkedIndexResultI> {
        return this.chunkedIndexLoader.getChunkeds(modelSetKey, keys);
    }
}
