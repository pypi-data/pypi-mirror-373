import logging
from datetime import datetime
from typing import Iterable

import pytz
from peek_plugin_base.util.PeekPsUtil import PeekPsUtil
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import deferLater
from vortex.DeferUtil import nonConcurrentMethod

from peek_abstract_chunked_index.private.client.controller.ACICacheControllerABC import (
    ACICacheControllerABC,
)


# noinspection PyProtectedMember
class ACICacheControllerNotifyMixin:
    _NOTIFY_CHUNK_SIZE = 24
    _NOTIFY_BACKOFF_CPU_PERCENT_AFTER_START = 70
    _NOTIFY_BACKOFF_CPU_PERCENT = 200
    _NOTIFY_BACKOFF_TIME_SECONDS = 1.0

    def __init__(
        self, controller: ACICacheControllerABC, logger: logging.Logger
    ):
        self._controller = controller
        self._logger: logging.Logger = logger
        self._notifyOfChunkKeysUpdatedQueue = set()

    def start(self):
        self._NOTIFY_BACKOFF_CPU_PERCENT = (
            self._NOTIFY_BACKOFF_CPU_PERCENT_AFTER_START
        )

    def shutdown(self):
        pass

    def addToNotifyOfChunkKeysUpdatedQueue(self, chunkKeys: Iterable[str]):
        self._notifyOfChunkKeysUpdatedQueue.update(chunkKeys)

    @nonConcurrentMethod
    @inlineCallbacks
    def _processNotifyOfChunkKeysUpdatedQueue(self):
        queue = list(self._notifyOfChunkKeysUpdatedQueue)
        self._notifyOfChunkKeysUpdatedQueue = set()

        if not queue:
            return

        if self._controller._DEBUG_LOGGING:
            self._logger.debug(
                "Started notify of handlers for chunkKeys %s", queue
            )
        startTime = datetime.now(pytz.utc)

        for i in range(0, len(queue), self._NOTIFY_CHUNK_SIZE):
            while PeekPsUtil().cpuPercent > self._NOTIFY_BACKOFF_CPU_PERCENT:
                # Give the reactor time to work
                yield deferLater(
                    reactor, self._NOTIFY_BACKOFF_TIME_SECONDS, lambda: None
                )

            keys = queue[i : i + self._NOTIFY_CHUNK_SIZE]
            notifyStartTime = datetime.now(pytz.utc)

            # For all the keys we're about to process, pop them from the queue
            self._notifyOfChunkKeysUpdatedQueue -= set(keys)
            yield self._controller._notifyOfChunkKeysUpdated(keys)

            timeTaken = datetime.now(pytz.utc) - notifyStartTime
            # Only log if it took longer than 10ms
            if 0.01 < timeTaken.total_seconds():
                self._logger.debug(
                    "Notifying handlers of chunkKeys, %s to %s out of %s,"
                    " took %s",
                    i,
                    min(i + self._NOTIFY_CHUNK_SIZE, len(queue)),
                    len(queue),
                    timeTaken,
                )

        self._logger.debug(
            "Completed notifying handlers of %s chunkKeys in %s",
            len(queue),
            datetime.now(pytz.utc) - startTime,
        )
