import logging
from datetime import datetime
from pathlib import Path

import pytz
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import LoopingCall
from twisted.internet.task import deferLater
from vortex.DeferUtil import vortexLogFailure
from vortex.TupleSelector import TupleSelector
from vortex.storage.TupleStorageSqlite import TupleStorageBatchSaveArguments
from vortex.storage.TupleStorageSqlite import TupleStorageSqlite

from peek_abstract_chunked_index.private.client.controller.ACICacheControllerABC import (
    ACICacheControllerABC,
)
from peek_plugin_base.LoopingCallUtil import peekCatchErrbackWithLogger
from peek_plugin_base.util.PeekPsUtil import PeekPsUtil


# noinspection PyUnresolvedReferences,PyProtectedMember
class ACICacheControllerSqliteAppDbMixin:
    _SQL_APP_DOWNLOAD_BACKOFF_TIME_SECONDS = 0.5
    _SQL_APP_DOWNLOAD_BACKOFF_CPU_PERCENT = 50.0
    _SQL_APP_DOWNLOAD_WRITE_BATCH_SIZE = 500
    _SNAPSHOT_PERIOD_SECONDS = 60 * 60  # 1 hour

    def __init__(
        self, controller: ACICacheControllerABC, logger: logging.Logger
    ):
        self._controller = controller
        self._logger: logging.Logger = logger
        self._appDownloadSnapshotLoopingCall = None

    def shutdown(self):
        if self._appDownloadSnapshotLoopingCall:
            self._appDownloadSnapshotLoopingCall.stop()
            self._appDownloadSnapshotLoopingCall = None

    def _startAppSnapshotLoopingCall(self):
        wrappedCall = peekCatchErrbackWithLogger(self._logger)(
            self._snapshotToSqliteForAppDownload
        )
        self._appDownloadSnapshotLoopingCall = LoopingCall(
            self._controller._backgroundTaskSemaphore.run, wrappedCall
        )
        d = self._appDownloadSnapshotLoopingCall.start(
            self._SNAPSHOT_PERIOD_SECONDS, now=True
        )
        d.addErrback(vortexLogFailure, self._logger)

    @inlineCallbacks
    def _snapshotToSqliteForAppDownload(self, throttle=True) -> Path:
        self._logger.debug("Started Snapshot to SQLite for App Download")
        startTime = datetime.now(pytz.utc)

        db = TupleStorageSqlite(
            databaseDirectory=self._controller._pluginDataDir,
            databaseName=(
                self._controller._ChunkedTuple.__name__.lower()
                + "_for_app_download.tmp"
            ),
        )
        dbPath = db.databasePath

        yield db.open()
        yield db.truncateStorage()

        indexDict = {}
        data = []

        # Interate through the chunks and create the storage arguments
        for e in self._controller._cache.values():
            indexDict[e.ckiChunkKey] = e.ckiLastUpdate
            data.append(
                TupleStorageBatchSaveArguments(
                    tupleSelector=e.ckiChunkKey, encodedPayload=e.ckiEncodedData
                )
            )

        # Save the data in chunks, to allow the reactor to pro
        for index in range(
            0, len(data), self._SQL_APP_DOWNLOAD_WRITE_BATCH_SIZE
        ):
            yield db.batchSaveTuplesEncoded(
                data[index : index + self._SQL_APP_DOWNLOAD_WRITE_BATCH_SIZE]
            )
            while (
                PeekPsUtil().cpuPercent
                > self._SQL_APP_DOWNLOAD_BACKOFF_CPU_PERCENT
                and throttle
            ):
                # Give the reactor time to work
                yield deferLater(
                    reactor,
                    self._SQL_APP_DOWNLOAD_BACKOFF_TIME_SECONDS,
                    lambda: None,
                )

        # Snapshot the index first, we want to make sure it's older than the
        # data
        indexTuple = self._controller._UpdateDateTupleABC()
        indexTuple.ckiSetUpdateDateByChunkKey(indexDict)

        ts = TupleSelector(indexTuple.tupleName(), {})
        yield db.saveTuples(ts, [indexTuple])

        yield db.close()
        del db

        # Move the new DB into place
        finalName = self._controller.appDownloadPluginDirFullPath()
        finalName.unlink(missing_ok=True)
        dbPath.rename(finalName)

        self._logger.info(
            "Completed creating new app database for download in %s, path %s",
            datetime.now(pytz.utc) - startTime,
            finalName,
        )

        return finalName
