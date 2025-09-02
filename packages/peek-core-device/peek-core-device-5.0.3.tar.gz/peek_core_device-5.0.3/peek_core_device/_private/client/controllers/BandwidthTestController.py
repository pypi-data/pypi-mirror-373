import logging
from random import random

from twisted.internet.defer import inlineCallbacks
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.PayloadEndpoint import PayloadEndpoint
from vortex.PayloadEnvelope import PayloadEnvelope
from vortex.VortexABC import SendVortexMsgResponseCallable

from peek_core_device._private.PluginNames import deviceFilt
from peek_core_device._private.tuples.BandwidthTestTuple import (
    BandwidthTestTuple,
)

logger = logging.getLogger(__name__)

deviceBandwidthTestFilt = dict(key="deviceBandwidthTestFilt")
deviceBandwidthTestFilt.update(deviceFilt)


class BandwidthTestController:
    def __init__(self):
        self._vortexMsg = None
        self._cachedEncodedPayload = None

        self._endpoint = None

    @inlineCallbacks
    def start(self):
        self._endpoint = PayloadEndpoint(deviceBandwidthTestFilt, self._process)
        yield self._createTestData()

    def shutdown(self):
        if self._endpoint:
            self._endpoint.shutdown()
            self._endpoint = None

    @deferToThreadWrapWithLogger(logger)
    def _createTestData(self):
        BASE64_SIZE = 1.3
        PACKET_SIZE = int((100.0 * 1024.0) / BASE64_SIZE)

        testData = ""
        while len(testData) < PACKET_SIZE:
            testData += str(random())

        logger.debug(f"Generated testData of size {len(testData)}")

        tuple_ = BandwidthTestTuple(testData=testData)

        self._vortexMsg = PayloadEnvelope(
            filt=deviceBandwidthTestFilt,
            encodedPayload=Payload(
                filt=deviceBandwidthTestFilt, tuples=[tuple_]
            ).toEncodedPayload(compressionLevel=0),
        ).toVortexMsg(base64Encode=False)

    def _process(
        self, sendResponse: SendVortexMsgResponseCallable, *args, **kwargs
    ):
        sendResponse(self._vortexMsg)
