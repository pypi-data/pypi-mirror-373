import logging
from datetime import datetime

import pytz
from twisted.internet.task import LoopingCall
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.DeferUtil import vortexLogFailure
from vortex.Payload import Payload

from peek_abstract_chunked_index.private.client.controller.ACICacheControllerABC import (
    ACICacheControllerABC,
)
from peek_plugin_base.LoopingCallUtil import peekCatchErrbackWithLogger


# noinspection PyProtectedMember
class ACICacheControllerOfflineIndexMixin:
    _OFFLINE_INDEX_CHUNK_SIZE = 20000
    _OFFLINE_INDEX_BUILD_SECONDS = 30 * 60  # 30 minutes

    def __init__(
        self, controller: ACICacheControllerABC, logger: logging.Logger
    ):
        self._controller = controller
        self._logger: logging.Logger = logger
        self._offlineIndexStateLoopingCall = None

        # Used for indexes that take list of [chunkKey,dateTime] tuples
        self._offlineUpdateDateByChunkKeyPayloads = []

        # Used for loaders that take the whole index tuple
        self._offlineUpdateDateTuplePayload = []

    def shutdown(self):
        if self._offlineIndexStateLoopingCall:
            self._offlineIndexStateLoopingCall.stop()
            self._offlineIndexStateLoopingCall = None

    def _startOfflineIndexStateLoopingCall(self):
        wrappedCall = peekCatchErrbackWithLogger(self._logger)(
            self._updateOfflineIndexState
        )
        self._offlineIndexStateLoopingCall = LoopingCall(
            self._controller._backgroundTaskSemaphore.run, wrappedCall
        )
        d = self._offlineIndexStateLoopingCall.start(
            self._OFFLINE_INDEX_BUILD_SECONDS, now=False
        )
        d.addErrback(vortexLogFailure, self._logger)

    def _updateOfflineIndexState(self):
        return deferToThreadWrapWithLogger(self._logger)(
            self._updateOfflineIndexStateBlocking
        )()

    def _updateOfflineIndexStateBlocking(self):
        self._logger.debug("Started build of offline index")
        # The _ argument is to make sure calls to debounce work for each index
        startTime = datetime.now(pytz.utc)

        tuples = [
            [i[0], i[1]]
            for i in self._controller._indexTuple.ckiUpdateDateByChunkKey.items()
        ]
        sorted(tuples, key=lambda i: i[0])

        encodedPayloads = []
        for i in range(0, len(tuples), self._OFFLINE_INDEX_CHUNK_SIZE):
            encodedPayloads.append(
                Payload(
                    tuples=tuples[i : i + self._OFFLINE_INDEX_CHUNK_SIZE]
                ).toEncodedPayload()
            )

        self._offlineUpdateDateByChunkKeyPayloads = encodedPayloads

        self._offlineUpdateDateTuplePayload = Payload(
            tuples=[self._controller._indexTuple]
        ).toEncodedPayload()

        self._logger.info(
            "Completed building offline index, %s groups, %s chunks, in %s",
            len(encodedPayloads),
            len(self._controller._indexTuple.ckiUpdateDateByChunkKey),
            datetime.now(pytz.utc) - startTime,
        )
