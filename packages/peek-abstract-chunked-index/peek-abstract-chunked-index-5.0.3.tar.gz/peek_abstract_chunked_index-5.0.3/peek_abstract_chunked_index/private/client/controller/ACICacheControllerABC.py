import logging
from abc import ABCMeta
from datetime import datetime
from pathlib import Path
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import List

import pytz
from reactivex import operators

from twisted.internet.defer import DeferredSemaphore
from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import LoopingCall
from vortex.DeferUtil import vortexLogFailure
from vortex.Payload import Payload
from vortex.PayloadEndpoint import PayloadEndpoint
from vortex.PayloadEnvelope import PayloadEnvelope
from vortex.VortexFactory import VortexFactory

from peek_abstract_chunked_index.private.tuples.ACIEncodedChunkTupleABC import (
    ACIEncodedChunkTupleABC,
)
from peek_abstract_chunked_index.private.tuples.ACIUpdateDateTupleABC import (
    ACIUpdateDateTupleABC,
)
from peek_plugin_base.LoopingCallUtil import peekCatchErrbackWithLogger
from peek_plugin_base.PeekVortexUtil import peekServerName


ChunkedIndexChunkLoadRpcMethodType = Callable[
    [list[str]], list[ACIEncodedChunkTupleABC]
]

ChunkedIndexDeltaRpcMethodType = Callable[[bytes], bytes]


# noinspection PyProtectedMember
class ACICacheControllerABC(metaclass=ABCMeta):
    """Chunked Index Cache Controller

    The Chunked Index cache controller stores all the chunks in memory,
    allowing fast access from the mobile and desktop devices.

    """

    _CACHE_CHECK_PERIOD_SECONDS = 6 * 60 * 60  # 6 hours

    # The number of tuples to put in one payload

    _backgroundTaskSemaphore = DeferredSemaphore(tokens=1)

    # Ensure that for this process, only one background task is run at once

    _DEBUG_LOGGING = False

    _logger: logging.Logger = None
    _updateFromLogicFilt: Dict = None
    _chunkIndexDeltaRpcMethod: ChunkedIndexDeltaRpcMethodType = None
    _chunkLoadRpcMethod: ChunkedIndexChunkLoadRpcMethodType = None
    _UpdateDateTupleABC: ACIUpdateDateTupleABC = None
    _ChunkedTuple: ACIEncodedChunkTupleABC = None

    _cache: Dict[str, ACIEncodedChunkTupleABC] = None
    _initialLoadComplete: bool = None
    _pluginDataDir: Path = None
    _indexTuple: ACIUpdateDateTupleABC = None

    def __init__(self, clientId: str, pluginDataDir: Path):
        assert self._ChunkedTuple, "_ChunkedTuple is None"
        assert self._chunkLoadRpcMethod, "_chunkLoadRpcMethod is None"
        assert self._updateFromLogicFilt, "_updateFromDeviceFilt is None"
        assert self._logger, "_logger is None"

        self._clientId = clientId
        self._webAppHandler = None

        self._cache = {}
        self._initialLoadComplete = False
        self._pluginDataDir = pluginDataDir

        self._indexTuple = self._UpdateDateTupleABC()
        self._indexTuple.ckiSetUpdateDateByChunkKey({})

        # This is a queue of chunkKeys that we need to notify the handlers
        # of

        # This is a queue of chunkKeys that we to load from the server
        # The queue is populated only when getting updates from the server,
        # not during the initial load.

        self._cacheIntegrityCheckLoopingCall = None

        # If the vortex goes online, check the cache.
        # Before this line of code, the vortex is already online.
        wrappedCacheCall = lambda _: self._backgroundTaskSemaphore.run(
            self._checkCache
        )

        (
            VortexFactory.subscribeToVortexStatusChange(peekServerName)
            .pipe(operators.filter(lambda online: online is True))
            .subscribe(on_next=wrappedCacheCall)
        )

        from .ACICacheControllerLoadFromLogicMixin import (
            ACICacheControllerLoadFromLogicMixin,
        )
        from .ACICacheControllerNotifyMixin import ACICacheControllerNotifyMixin
        from .ACICacheControllerOfflineIndexMixin import (
            ACICacheControllerOfflineIndexMixin,
        )
        from .ACICacheControllerSqliteAppDbMixin import (
            ACICacheControllerSqliteAppDbMixin,
        )
        from .ACICacheControllerSqliteCacheMixin import (
            ACICacheControllerSqliteCacheMixin,
        )

        self._sqliteCacheMixin = ACICacheControllerSqliteCacheMixin(
            self, self._logger
        )
        # self._sqliteAppDbMixin = ACICacheControllerSqliteAppDbMixin(
        #     self, self._logger
        # )
        self._notifyMixin = ACICacheControllerNotifyMixin(self, self._logger)
        self._offlineIndexMixin = ACICacheControllerOfflineIndexMixin(
            self, self._logger
        )
        self._loadFromLogicMixin = ACICacheControllerLoadFromLogicMixin(
            self, self._logger
        )

    @property
    def starting(self) -> bool:
        return not self._initialLoadComplete

    @staticmethod
    def appDownloadPluginDirRelativeDir() -> str:
        return "app_download"

    @classmethod
    def appDownloadFileName(cls):
        return f"{cls._ChunkedTuple.__name__.lower()}_for_app_download.sqlite"

    def appDownloadPluginDirFullPath(self) -> Path:
        return (
            self._pluginDataDir
            / self.appDownloadPluginDirRelativeDir()
            / self.appDownloadFileName()
        )

    def _addToNotifyOfChunkKeysUpdatedQueue(self, chunkKeys: Iterable[str]):
        self._notifyMixin.addToNotifyOfChunkKeysUpdatedQueue(chunkKeys)

    def _processNotifyOfChunkKeysUpdatedQueue(self):
        return self._notifyMixin._processNotifyOfChunkKeysUpdatedQueue()

    @inlineCallbacks
    def _notifyOfChunkKeysUpdated(self, chunkKeys: list[str]):
        # Do not override this method
        yield self._webAppHandler.notifyOfUpdateBeforeSemaphore(chunkKeys)

    def setCacheHandler(self, handler):
        self._webAppHandler = handler

    @inlineCallbacks
    def start(self):
        startTime = datetime.now(pytz.utc)

        # First, load the cache
        yield self.reloadCache()

        counterCheckCount = 0
        while 100 < (yield self._checkCache()):
            counterCheckCount += 1

        # Now enable the updates
        self._loadFromLogicMixin.start()

        # And do a second cache check, once the updates have been enabled
        yield self._checkCache()

        self._initialLoadComplete = True

        self._notifyMixin.start()
        # self._sqliteAppDbMixin._startAppSnapshotLoopingCall()
        self._startCacheIntegrityCheckLoopingCall()
        self._offlineIndexMixin._startOfflineIndexStateLoopingCall()
        self._sqliteCacheMixin._startSqliteCacheWriteLoopingCall()

        self._logger.info(
            "Completed starting cache, we had to recheck %s times, in %s",
            counterCheckCount,
            datetime.now(pytz.utc) - startTime,
        )

    def _startCacheIntegrityCheckLoopingCall(self):
        wrappedCall = peekCatchErrbackWithLogger(self._logger)(self._checkCache)
        self._cacheIntegrityCheckLoopingCall = LoopingCall(
            self._backgroundTaskSemaphore.run, wrappedCall
        )
        d = self._cacheIntegrityCheckLoopingCall.start(
            self._CACHE_CHECK_PERIOD_SECONDS, now=False
        )
        d.addErrback(vortexLogFailure, self._logger)

    def shutdown(self):
        self._cache = {}

        self._sqliteCacheMixin.shutdown()
        # self._sqliteAppDbMixin.shutdown()
        self._notifyMixin.shutdown()
        self._offlineIndexMixin.shutdown()
        self._loadFromLogicMixin.shutdown()

    @inlineCallbacks
    def reloadCache(self):
        self._cache = {}

        startTime = datetime.now(pytz.utc)
        yield self._sqliteCacheMixin._loadStartupCache()
        yield self._checkCache()
        yield self._updateOnlineIndexState()
        yield self._offlineIndexMixin._updateOfflineIndexState()

        self._logger.info(
            "Completed Reload Cache in %s", datetime.now(pytz.utc) - startTime
        )

    @inlineCallbacks
    def _checkCache(self, *args):
        self._logger.debug("Started Cache Integrity Check")
        startTime = datetime.now(pytz.utc)

        # Make sure the cache is up to date (it should be)
        yield self._updateOnlineIndexState()

        # Find out what we need to reload
        deltaIndexPayload = yield self._chunkIndexDeltaRpcMethod(
            (yield Payload(tuples=[self._indexTuple]).toEncodedPayloadDefer())
        )
        deltaIndex = (
            yield Payload().fromEncodedPayloadDefer(deltaIndexPayload)
        ).tuples[0]

        # Make node of the actions required, and delete the deletes
        # from the cache
        chunkKeysToLoad = []
        chunkKeysToDelete = []
        # Delete all the deltas we need to
        for chunkKey, lastUpdate in deltaIndex.ckiUpdateDateByChunkKey.items():
            if lastUpdate is None:
                self._sqliteCacheMixin._sqliteCacheWriteQueue[chunkKey] = None
                del self._cache[chunkKey]
                chunkKeysToDelete.append(chunkKey)

            else:
                chunkKeysToLoad.append(chunkKey)

        chunkKeysKept = list(self._cache)
        chunkKeysUnchanged = list(set(self._cache) - set(chunkKeysToLoad))
        yield self._updateOnlineIndexState()

        # Notify any memory resident models that we need to delete these
        self._addToNotifyOfChunkKeysUpdatedQueue(chunkKeysToDelete)

        self._logger.debug(
            "Integrity checked index in %s,"
            " %s deleted, %s unchanged, %s to load",
            datetime.now(pytz.utc) - startTime,
            len(chunkKeysToDelete),
            len(chunkKeysUnchanged),
            len(chunkKeysToLoad),
        )

        yield from self._loadFromLogicMixin._loadChunksFromServer(
            chunkKeysToLoad
        )

        self._logger.info(
            "Completed Cache Integrity Check in %s",
            datetime.now(pytz.utc) - startTime,
        )

        return len(chunkKeysToLoad)

    def _loadDataIntoCache(
        self, encodedChunkTuples: List[ACIEncodedChunkTupleABC]
    ):
        startTime = datetime.now(pytz.utc)

        chunkKeysUpdated: List[str] = []
        deletedCount = 0
        updatedCount = 0
        sameCount = 0

        for t in encodedChunkTuples:
            if not t.ckiHasEncodedData:
                if t.ckiChunkKey in self._cache:
                    deletedCount += 1
                    del self._cache[t.ckiChunkKey]
                    del self._indexTuple.ckiUpdateDateByChunkKey[t.ckiChunkKey]
                    self._sqliteCacheMixin._sqliteCacheWriteQueue[
                        t.ckiChunkKey
                    ] = None
                    chunkKeysUpdated.append(t.ckiChunkKey)

                else:
                    # It's already deleted
                    sameCount += 1

                continue

            if (
                not t.ckiChunkKey in self._cache
                or self._cache[t.ckiChunkKey].ckiLastUpdate != t.ckiLastUpdate
            ):
                updatedCount += 1
                self._cache[t.ckiChunkKey] = t
                self._indexTuple.ckiUpdateDateByChunkKey[t.ckiChunkKey] = (
                    t.ckiLastUpdate
                )
                self._sqliteCacheMixin._sqliteCacheWriteQueue[t.ckiChunkKey] = t
                chunkKeysUpdated.append(t.ckiChunkKey)
                continue

            sameCount += 1

        self._logger.debug(
            "Received %s updates from server"
            ", %s had changed"
            ", %s were deleted"
            ", %s are identical"
            ", processed in %s",
            len(encodedChunkTuples),
            updatedCount,
            deletedCount,
            sameCount,
            datetime.now(pytz.utc) - startTime,
        )

        self._addToNotifyOfChunkKeysUpdatedQueue(chunkKeysUpdated)

    def _updateOnlineIndexState(self):
        self._indexTuple.ckiSetUpdateDateByChunkKey(
            {g.ckiChunkKey: g.ckiLastUpdate for g in self._cache.values()}
        )

    def encodedChunk(self, chunkKey) -> ACIEncodedChunkTupleABC:
        return self._cache.get(chunkKey)

    def encodedChunkKeys(self) -> Iterable[int]:
        # Wrapping this in a list is expensive
        return self._cache.keys()

    def encodedChunkLastUpdateByKey(self):
        return self._indexTuple.ckiUpdateDateByChunkKey

    def offlineUpdateDateByChunkKeyPayload(self, index):
        return self._offlineIndexMixin._offlineUpdateDateByChunkKeyPayloads[
            int(index)
        ]

    def offlineUpdateDateTuplePayload(self):
        return self._offlineIndexMixin._offlineUpdateDateTuplePayload
