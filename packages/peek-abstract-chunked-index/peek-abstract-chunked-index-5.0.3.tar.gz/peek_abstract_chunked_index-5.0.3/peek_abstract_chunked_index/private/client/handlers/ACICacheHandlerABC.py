import logging
from abc import ABCMeta
from collections import defaultdict
from datetime import datetime
from typing import Dict
from typing import List

import pytz
from peek_abstract_chunked_index.private.client.controller.ACICacheControllerABC import (
    ACICacheControllerABC,
)

# ModelSet HANDLER
from peek_abstract_chunked_index.private.tuples.ACIUpdateDateTupleABC import (
    ACIUpdateDateTupleABC,
)
from twisted.internet.defer import DeferredSemaphore
from twisted.internet.defer import inlineCallbacks
from txhttputil.util.DeferUtil import vortexLogFailure
from vortex.PayloadEndpoint import PayloadEndpoint
from vortex.PayloadEnvelope import PayloadEnvelope
from vortex.VortexABC import SendVortexMsgResponseCallable
from vortex.VortexFactory import NoVortexException
from vortex.VortexFactory import VortexFactory
from vortex.VortexUtil import limitConcurrency

cacheHandlerLogger = logging.getLogger(__name__)


def _dedupOACICacheHandlerABCCallKeys(
    payloadEnvelope: PayloadEnvelope, vortexUuid: str, *args, **kwargs
):
    filt = payloadEnvelope.filt.copy()
    filt.pop(PayloadResponse.MESSAGE_ID_KEY, None)
    return vortexUuid, str(filt)


class ACICacheHandlerABC(metaclass=ABCMeta):
    _UpdateDateTuple: ACIUpdateDateTupleABC = None
    _updateFromDeviceFilt: Dict = None
    _updateFromLogicFilt: Dict = None
    _logger: logging.Logger = None

    _DEBUG_LOGGING = False

    def __init__(self, cacheController: ACICacheControllerABC, clientId: str):
        """App ChunkedIndex Handler

        This class handles the custom needs of the desktop/mobile apps
         observing chunkedIndexes.

        """
        self._cacheController = cacheController
        self._clientId = clientId

        self._epObserve = PayloadEndpoint(
            self._updateFromDeviceFilt, self._processObserveLimited
        )

        self._uuidsObserving = set()

    @inlineCallbacks
    def start(self):
        yield None

    def shutdown(self):
        self._epObserve.shutdown()
        self._epObserve = None

    def _filterOutOfflineVortexes(self):
        # TODO, Change this to observe offline vortexes
        # This depends on the VortexFactory offline observable implementation.
        # Which is incomplete at this point :-|

        vortexUuids = (
            set(VortexFactory.getRemoteVortexUuids()) & self._uuidsObserving
        )
        self._uuidsObserving = vortexUuids

    # ---------------
    # Process update from the server

    def notifyOfUpdateBeforeSemaphore(self, chunkKeys: list[str]):
        return self._notifyOfUpdateLimitedDecorated(chunkKeys)

    @limitConcurrency(cacheHandlerLogger, 10)
    def _notifyOfUpdateLimitedDecorated(self, *args, **kwargs):
        return self.notifyOfUpdate(*args, **kwargs)

    @inlineCallbacks
    def notifyOfUpdate(self, chunkKeys: List[str]):
        """Notify of ChunkedIndex Updates

        This method is called by the client.ChunkedIndexCacheController
         when it receives updates from the server.

        """
        self._filterOutOfflineVortexes()

        if not self._uuidsObserving:
            return

        def cratePayloadEnvelope():
            payloadEnvelope = PayloadEnvelope()
            payloadEnvelope.data = []
            return payloadEnvelope

        payloadsByVortexUuid = defaultdict(cratePayloadEnvelope)

        for chunkKey in chunkKeys:
            encodedChunkedIndexChunk = self._cacheController.encodedChunk(
                chunkKey
            )

            # Queue up the required client notifications
            for vortexUuid in self._uuidsObserving:
                self._logger.debug(
                    "Sending unsolicited chunkedIndex %s to vortex %s",
                    chunkKey,
                    vortexUuid,
                )
                payloadsByVortexUuid[vortexUuid].data.append(
                    encodedChunkedIndexChunk
                )

        # Send the updates to the clients
        for vortexUuid, payloadEnvelope in list(payloadsByVortexUuid.items()):
            payloadEnvelope.filt = self._updateFromDeviceFilt

            vortexMsg = yield payloadEnvelope.toVortexMsgDefer(
                base64Encode=False
            )

            try:
                yield VortexFactory.sendVortexMsg(
                    vortexMsg, destVortexUuid=vortexUuid
                )

            except NoVortexException:
                pass

            except Exception as e:
                self._logger.exception(e)

    # ---------------
    # Process observes from the devices

    def _processObserveLimited(self, *args, **kwargs):
        d = self._processObserveLimitedDecorated(*args, **kwargs)
        d.addErrback(vortexLogFailure, self._logger, consumeError=True)

    @limitConcurrency(cacheHandlerLogger, 50)
    def _processObserveLimitedDecorated(self, *args, **kwargs):
        return self._processObserve(*args, **kwargs)

    @inlineCallbacks
    def _processObserve(
        self,
        payloadEnvelope: PayloadEnvelope,
        vortexUuid: str,
        sendResponse: SendVortexMsgResponseCallable,
        **kwargs,
    ):
        cacheAll = payloadEnvelope.filt.get("cacheAll") is True

        payload = yield payloadEnvelope.decodePayloadDefer()

        updateDatesTuples: ACIUpdateDateTupleABC = payload.tuples[0]

        if updateDatesTuples.ckiUpdateDateByChunkKey is None:
            self._logger.debug(
                "BUG: " "updateDatesTuples.ckiUpdateDateByChunkKey is " "None"
            )
            return

        if not cacheAll:
            self._uuidsObserving.add(vortexUuid)

        yield self._replyToObserve(
            payloadEnvelope.filt,
            updateDatesTuples.ckiUpdateDateByChunkKey,
            sendResponse,
            vortexUuid=vortexUuid,
            cacheAll=cacheAll,
        )

    # ---------------
    # Reply to device observe

    @inlineCallbacks
    def _replyToObserve(
        self,
        filt,
        lastUpdateByChunkedIndexKey: Dict[str, str],
        sendResponse: SendVortexMsgResponseCallable,
        vortexUuid: str,
        cacheAll=False,
    ) -> None:
        """Reply to Observe

        The client has told us that it's observing a new set of chunkedIndexes,
        and the lastUpdate it has for each of those chunkedIndexes. We will
        send them the chunkedIndexes that are out of date
        or missing.

        :param filt: The payload filter to respond to.
        :param lastUpdateByChunkedIndexKey:
            The dict of chunkedIndexKey:lastUpdate
        :param sendResponse: The callable provided by the Vortex (handy)
        :returns: None

        """
        startTime = datetime.now(pytz.utc)
        yield None

        chunkedIndexTuplesToSend = []
        updateCount = 0
        sameCount = 0
        missingCount = 0

        # Check and send any updates
        for chunkedIndexKey, lastUpdate in lastUpdateByChunkedIndexKey.items():
            if vortexUuid not in VortexFactory.getRemoteVortexUuids():
                self._logger.debug(
                    "Vortex %s is offline, stopping update", vortexUuid
                )
                return

            # NOTE: lastUpdate can be null.
            encodedChunkedIndexTuple = self._cacheController.encodedChunk(
                chunkedIndexKey
            )
            if not encodedChunkedIndexTuple:
                missingCount += 1
                if self._DEBUG_LOGGING:
                    self._logger.debug(
                        "ChunkedIndex %s is not in the cache" % chunkedIndexKey
                    )
                continue

            # We are king, If it's not our version, it's the wrong version
            if self._DEBUG_LOGGING:
                self._logger.debug(
                    "%s, %s,  %s",
                    encodedChunkedIndexTuple.ckiLastUpdate == lastUpdate,
                    encodedChunkedIndexTuple.ckiLastUpdate,
                    lastUpdate,
                )

            if encodedChunkedIndexTuple.ckiLastUpdate == lastUpdate:
                sameCount += 1
                if self._DEBUG_LOGGING:
                    self._logger.debug(
                        "ChunkedIndex %s matches the cache" % chunkedIndexKey
                    )
                continue

            updateCount += 1
            chunkedIndexTuplesToSend.append(encodedChunkedIndexTuple)
            if self._DEBUG_LOGGING:
                self._logger.debug(
                    "Sending chunkedIndex %s from the cache" % chunkedIndexKey
                )

        yield self._sendData(
            sendResponse, filt, cacheAll, chunkedIndexTuplesToSend
        )

        self._logger.debug(
            "Chunk request, %s same, %s not in cache,"
            " %s updates sent to %s in %s",
            sameCount,
            missingCount,
            updateCount,
            vortexUuid,
            datetime.now(pytz.utc) - startTime,
        )

    @inlineCallbacks
    def _sendData(
        self,
        sendResponse: SendVortexMsgResponseCallable,
        filt: dict,
        cacheAll: bool,
        chunksToSend: list,
    ):
        if not chunksToSend and not cacheAll:
            return

        payloadEnvelope = PayloadEnvelope(filt=filt, data=chunksToSend)
        vortexMsg = yield payloadEnvelope.toVortexMsgDefer(base64Encode=False)
        yield sendResponse(vortexMsg)
