import logging
from datetime import datetime

import pytz
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import LoopingCall
from twisted.internet.task import deferLater
from vortex.DeferUtil import vortexLogFailure
from vortex.Payload import Payload
from vortex.storage.TupleStorageSqlite import TupleStorageBatchSaveArguments
from vortex.storage.TupleStorageSqlite import TupleStorageSqlite

from peek_abstract_chunked_index.private.client.controller.ACICacheControllerABC import (
    ACICacheControllerABC,
)
from peek_plugin_base.LoopingCallUtil import peekCatchErrbackWithLogger
from peek_plugin_base.util.PeekPsUtil import PeekPsUtil


# noinspection PyProtectedMember
class ACICacheControllerSqliteCacheMixin:
    _SQLITE_CACHE_WRITE_BACKOFF_TIME_SECONDS = 0.5
    _SQLITE_CACHE_WRITE_BACKOFF_CPU_PERCENT = 50.0
    _SQLITE_CACHE_WRITE_SECONDS = 15 * 60  # 15 minutes

    # We create large bytes objects
    # No memory overhead
    _SQLITE_CACHE_WRITE_BATCH_SIZE = 50

    _SQLITE_CACHE_READ_BATCH_SIZE = 250

    def __init__(
        self, controller: ACICacheControllerABC, logger: logging.Logger
    ):
        self._controller = controller
        self._logger: logging.Logger = logger
        self._sqliteCacheWriteQueue = {}
        self._sqliteCacheWriteLoopingCall = None

    def shutdown(self):
        if self._sqliteCacheWriteLoopingCall:
            self._sqliteCacheWriteLoopingCall.stop()
            self._sqliteCacheWriteLoopingCall = None

    def __constructOfflineCacheSqliteStorage(self) -> TupleStorageSqlite:
        return TupleStorageSqlite(
            databaseDirectory=self._controller._pluginDataDir,
            databaseName=self._controller._ChunkedTuple.__name__,
        )

    def _startSqliteCacheWriteLoopingCall(self):
        wrappedCall = peekCatchErrbackWithLogger(self._logger)(
            self._sqliteCacheWrite
        )
        self._sqliteCacheWriteLoopingCall = LoopingCall(
            self._controller._backgroundTaskSemaphore.run, wrappedCall
        )
        d = self._sqliteCacheWriteLoopingCall.start(
            self._SQLITE_CACHE_WRITE_SECONDS, now=True
        )
        d.addErrback(vortexLogFailure, self._logger)

    @inlineCallbacks
    def _loadStartupCache(self):
        tupleStorage = self.__constructOfflineCacheSqliteStorage()
        try:
            yield tupleStorage.open()
            encodedChunkTuples = (
                yield tupleStorage.loadTuplesAndAggregateAllTuples(
                    batchSize=self._SQLITE_CACHE_READ_BATCH_SIZE
                )
            )
            yield tupleStorage.close()

            self._controller._cache = {
                e.ckiChunkKey: e
                for e in encodedChunkTuples
                if isinstance(e, self._controller._ChunkedTuple)
            }

            self._controller._addToNotifyOfChunkKeysUpdatedQueue(
                self._controller._cache
            )

        except Exception as e:
            self._logger.error(
                "The startup state db is broken, Deleting it, %s", str(e)
            )
            yield tupleStorage.truncateStorage()
            yield tupleStorage.close()

        yield self._controller._updateOnlineIndexState()

    @inlineCallbacks
    def _sqliteCacheWrite(self):
        queue, self._sqliteCacheWriteQueue = self._sqliteCacheWriteQueue, {}

        if not queue:
            return

        startTime = datetime.now(pytz.utc)
        self._logger.debug(
            "Started sqlite write of cache, we have %s items", len(queue)
        )

        tupleStorage = self.__constructOfflineCacheSqliteStorage()
        yield tupleStorage.open()

        def yieldData():
            while queue:
                data = []
                while len(data) < self._SQLITE_CACHE_WRITE_BATCH_SIZE and queue:
                    key, chunkTuple_ = queue.popitem()
                    # Filter out the deletes
                    if chunkTuple_:
                        data.append(chunkTuple_)
                yield data

        chunkKeysToDelete = [k for k, v in queue.items() if not v]
        if chunkKeysToDelete:
            yield tupleStorage.batchDeleteTuples(chunkKeysToDelete)
            self._logger.debug(
                "Progressed sqlite write of cache, deleted %s items",
                len(chunkKeysToDelete),
            )

        totalToWrite = len(queue) - len(chunkKeysToDelete)
        totalWritten = 0

        for data in yieldData():
            while (
                PeekPsUtil().cpuPercent
                > self._SQLITE_CACHE_WRITE_BACKOFF_CPU_PERCENT
            ):
                # Give the reactor time to work
                yield deferLater(
                    reactor,
                    self._SQLITE_CACHE_WRITE_BACKOFF_TIME_SECONDS,
                    lambda: None,
                )

            inserts = []
            for chunkTuple in data:
                # Since the write process is a background task that takes a
                # while, a newer chunk may have come in since we started
                # writing. If we havw a newer one to write, prefer that.
                if self._sqliteCacheWriteQueue.get(chunkTuple.ckiChunkKey):
                    chunkTuple = self._sqliteCacheWriteQueue.pop(
                        chunkTuple.ckiChunkKey
                    )

                # Create the insert
                inserts.append(
                    TupleStorageBatchSaveArguments(
                        tupleSelector=chunkTuple.ckiChunkKey,
                        encodedPayload=(
                            yield Payload(
                                tuples=[chunkTuple]
                            ).toEncodedPayloadDefer(compressionLevel=-1)
                        ),
                    )
                )

            yield tupleStorage.batchSaveTuplesEncoded(inserts)
            totalWritten += len(inserts)
            self._logger.debug(
                "Progressed sqlite write of cache, written %s of %s items",
                totalWritten,
                totalToWrite,
            )

        yield tupleStorage.close()

        self._logger.info(
            "Completed sqlite write of cache, wrote %s items in %s",
            totalWritten,
            datetime.now(pytz.utc) - startTime,
        )
