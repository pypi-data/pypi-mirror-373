import logging
from abc import ABCMeta
from typing import Dict
from typing import List

from twisted.internet.defer import Deferred
from vortex.DeferUtil import vortexLogFailure
from vortex.Payload import Payload
from vortex.PayloadEndpoint import PayloadEndpoint
from vortex.VortexFactory import NoVortexException
from vortex.VortexFactory import VortexFactory

from peek_abstract_chunked_index.private.tuples.ACIEncodedChunkTupleABC import (
    ACIEncodedChunkTupleABC,
)


class ACIChunkUpdateHandlerABC(metaclass=ABCMeta):
    """Client Chunked Index Update Controller

    This controller handles sending updates the the client.

    It uses lower level Vortex API

    It does the following a broadcast to all clients:

    1) Sends grid updates to the clients

    2) Sends Lookup updates to the clients

    """

    _ChunkedTuple: ACIEncodedChunkTupleABC = None
    _updateFromLogicFilt: Dict = None
    _logger: logging.Logger = None

    def __init__(self, dbSessionCreator):
        self._dbSessionCreator = dbSessionCreator

        self._registerInterestObserver = PayloadEndpoint(
            self._updateFromLogicFilt, self._processRegisterInterest
        )

        self._vortexUuidsToSendTo = set()

    def shutdown(self):
        pass

    def _processRegisterInterest(self, vortexUuid: str, **kwargs):
        self._logger.debug("Received interest registration from %s", vortexUuid)
        self._vortexUuidsToSendTo.add(vortexUuid)

    def sendChunks(self, lastUpdateByChunkKey: dict[str, str]) -> None:
        """Send Location Indexes

        Send grid updates to the client services

        :param chunkKeys: A list of object buckets that have been updated
        :returns: Nochunked
        """

        if not lastUpdateByChunkKey:
            return

        self._vortexUuidsToSendTo = self._vortexUuidsToSendTo & set(
            VortexFactory.getRemoteVortexUuids()
        )

        if not self._vortexUuidsToSendTo:
            self._logger.debug(
                "No clients are online to send the chunked chunk to, %s",
                list(lastUpdateByChunkKey),
            )
            return

        def send(vortexMsg: bytes):
            assert (
                vortexMsg
            ), "ACIChunkUpdateHandlerABC.sendChunks, vortexMsg is falsy"

            self._logger.debug(
                "Sending chunks %s to %s",
                list(lastUpdateByChunkKey),
                self._vortexUuidsToSendTo,
            )
            for vortexUuid in self._vortexUuidsToSendTo:
                VortexFactory.sendVortexMsg(
                    vortexMsg, destVortexUuid=vortexUuid
                )

        d: Deferred = Payload(
            filt=self._updateFromLogicFilt, tuples=lastUpdateByChunkKey
        ).makePayloadEnvelopeVortexMsgDefer()
        d.addCallback(send)
        d.addErrback(self._sendErrback, lastUpdateByChunkKey)

    def _sendErrback(self, failure, lastUpdateByChunkKey):
        if failure.check(NoVortexException):
            self._logger.debug(
                "No clients are online to send the chunked chunk to, %s",
                lastUpdateByChunkKey,
            )
            return

        vortexLogFailure(failure, self._logger)
