import json
import logging
from datetime import datetime
from typing import List

import pytz
from twisted.internet import reactor
from twisted.internet.defer import DeferredList
from twisted.internet.defer import DeferredSemaphore
from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import LoopingCall
from twisted.internet.task import deferLater
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.DeferUtil import vortexLogFailure
from vortex.Payload import Payload
from vortex.PayloadEndpoint import PayloadEndpoint
from vortex.PayloadEnvelope import PayloadEnvelope
from vortex.VortexFactory import VortexFactory

from peek_abstract_chunked_index.private.client.controller.ACICacheControllerABC import (
    ACICacheControllerABC,
)
from peek_abstract_chunked_index.private.tuples.ACIEncodedChunkTupleABC import (
    ACIEncodedChunkTupleABC,
)
from peek_plugin_base.LoopingCallUtil import peekCatchErrbackWithLogger
from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_plugin_base.util.PeekPsUtil import PeekPsUtil


# noinspection PyProtectedMember
class ACICacheControllerLoadFromLogicMixin:
    _LOAD_CHUNK_SIZE = 24
    _LOAD_CHUNK_INITIAL_PARALLELISM = 6
    _LOAD_CHUNK_UPDATE_PARALLELISM = 2
    _LOAD_UPDATE_FROM_LOGIC_BACKOFF_TIME_SECONDS = 1.0
    _LOAD_UPDATE_FROM_LOGIC_BACKOFF_CPU_PERCENT = 80

    # Batch these updates, we can load more in a larger chunk
    # This will add a delay to the screen update time.
    _LOAD_UPDATE_LOAD_PERIOD_SECONDS = 0.5

    # Two loaders can be loading updates at any one time.
    _updateLoadTaskSemaphore = DeferredSemaphore(tokens=2)

    def __init__(
        self, controller: ACICacheControllerABC, logger: logging.Logger
    ):
        self._endpoint = None
        self._controller = controller
        self._logger: logging.Logger = logger
        self._updatesFromLogicQueue = set()
        self._loadUpdatesLoopingCall = None

    def start(self):
        # Tell the logic service that this vortexUuid is interested in its data

        self._endpoint = PayloadEndpoint(
            self._controller._updateFromLogicFilt, self._processUpdatesFromLogic
        )

        VortexFactory.sendVortexMsg(
            vortexMsgs=PayloadEnvelope(
                filt=self._controller._updateFromLogicFilt
            ).toVortexMsg(),
            destVortexName=peekServerName,
        )

        self._startLoadUpdatesLoopingCall()

    def shutdown(self):
        if self._endpoint:
            self._endpoint.shutdown()
            self._endpoint = None

        if self._loadUpdatesLoopingCall:
            self._loadUpdatesLoopingCall.stop()
            self._loadUpdatesLoopingCall = None

    def _startLoadUpdatesLoopingCall(self):
        wrappedCall = peekCatchErrbackWithLogger(self._logger)(
            self._processUpdatesFromLogicQueue
        )
        self._loadUpdatesLoopingCall = LoopingCall(
            self._updateLoadTaskSemaphore.run, wrappedCall
        )
        d = self._loadUpdatesLoopingCall.start(
            self._LOAD_UPDATE_LOAD_PERIOD_SECONDS, now=False
        )
        d.addErrback(vortexLogFailure, self._logger)

    @inlineCallbacks
    def _loadChunksFromServer(self, chunkKeysToLoad):
        # Start loading the detlas
        chunkStartTime = datetime.now(pytz.utc)

        yield DeferredList(
            [
                self._loadChunksFromLogicStrand(chunkKeysToLoad, index)
                for index in range(self._LOAD_CHUNK_INITIAL_PARALLELISM)
            ],
            fireOnOneErrback=True,
        )

        # Notify any memory resident models of our changes
        yield self._controller._processNotifyOfChunkKeysUpdatedQueue()

        self._logger.debug(
            "Finished loading %s chunks in %s",
            len(chunkKeysToLoad),
            datetime.now(pytz.utc) - chunkStartTime,
        )

    @inlineCallbacks
    def _loadChunksFromLogicStrand(
        self, chunkKeysToLoad: list[str], threadIndex: int
    ):
        offset = self._LOAD_CHUNK_SIZE * threadIndex
        while True:
            chunkKeysChunk = chunkKeysToLoad[
                offset : offset + self._LOAD_CHUNK_SIZE
            ]
            if not chunkKeysChunk:
                break

            startDate = datetime.now(pytz.utc)
            if self._controller._DEBUG_LOGGING:
                self._logger.debug(
                    "Loading %s to %s" % (offset, offset + len(chunkKeysChunk))
                )

            # We're loading this chunk now, make sure it's not queued to
            # load any more.
            self._updatesFromLogicQueue -= set(chunkKeysChunk)

            payloadJsonStr = yield self._controller._chunkLoadRpcMethod(
                chunkKeysChunk
            )

            if not payloadJsonStr:
                break

            encodedChunkTuples: List[
                ACIEncodedChunkTupleABC
            ] = yield deferToThreadWrapWithLogger(self._logger)(
                self._payloadFromJsonStrBlocking
            )(
                payloadJsonStr
            )

            if not encodedChunkTuples:
                break

            yield self._controller._loadDataIntoCache(encodedChunkTuples)

            self._logger.info(
                "Loaded %s chunks, %s to %s of %s, in %s",
                len(chunkKeysChunk),
                offset,
                offset + len(chunkKeysChunk),
                len(chunkKeysToLoad),
                datetime.now(pytz.utc) - startDate,
            )

            offset += (
                self._LOAD_CHUNK_SIZE * self._LOAD_CHUNK_INITIAL_PARALLELISM
            )

    def _payloadFromJsonStrBlocking(
        self, payloadJsonStr
    ) -> list[ACIEncodedChunkTupleABC]:
        return Payload().fromJsonDict(json.loads(payloadJsonStr)).tuples

    @inlineCallbacks
    def _processUpdatesFromLogic(
        self, payloadEnvelope: PayloadEnvelope, **kwargs
    ):
        # noinspection PyTypeChecker
        payload = yield payloadEnvelope.decodePayloadDefer()
        lastUpdateByChunkKey: dict[str, str] = payload.tuples[0]

        # Find out which chunks we need to load.
        chunkKeys = []
        for chunkKey, lastUpdate in lastUpdateByChunkKey.items():
            if (
                chunkKey not in self._controller._cache
                or self._controller._cache[chunkKey].ckiLastUpdate != lastUpdate
            ):
                chunkKeys.append(chunkKey)

        if chunkKeys:
            self._updatesFromLogicQueue.update(chunkKeys)

        self._logger.debug(
            "Received notification of %s updates from logic,"
            " %s had changed, queue is now %s",
            len(lastUpdateByChunkKey),
            len(chunkKeys),
            len(self._updatesFromLogicQueue),
        )

    @inlineCallbacks
    def _processUpdatesFromLogicQueue(self):
        startTime = datetime.now(pytz.utc)
        CHUNK_SIZE = self._LOAD_CHUNK_SIZE * self._LOAD_CHUNK_UPDATE_PARALLELISM

        queue = list(self._updatesFromLogicQueue)
        self._updatesFromLogicQueue = set()

        if not queue:
            return

        if self._controller._DEBUG_LOGGING:
            self._logger.debug(
                "Started loading updates from logic for chunkKeys, %s", queue
            )

        for i in range(0, len(queue), CHUNK_SIZE):
            while (
                PeekPsUtil().cpuPercent
                > self._LOAD_UPDATE_FROM_LOGIC_BACKOFF_CPU_PERCENT
            ):
                # Give the reactor time to work
                yield deferLater(
                    reactor,
                    self._LOAD_UPDATE_FROM_LOGIC_BACKOFF_TIME_SECONDS,
                    lambda: None,
                )

            keys = queue[i : i + CHUNK_SIZE]
            notifyStartTime = datetime.now(pytz.utc)

            yield self._loadChunksFromServer(keys)

            if self._controller._DEBUG_LOGGING:
                self._logger.debug(
                    "Loading updates from server of chunkKeys,"
                    " %s to %s out of %s,"
                    " took %s",
                    i,
                    min(i + self._LOAD_CHUNK_SIZE, len(queue)),
                    len(queue),
                    datetime.now(pytz.utc) - notifyStartTime,
                )

        if self._controller._DEBUG_LOGGING:
            self._logger.debug(
                "Completed loading updates from server of %s chunkKeys in %s",
                len(queue),
                datetime.now(pytz.utc) - startTime,
            )
