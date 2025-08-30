import logging
from typing import Union

from twisted.internet.defer import Deferred
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.PayloadEnvelope import PayloadEnvelope
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

from peek_core_device._private.server.controller.OfflineCacheController import (
    OfflineCacheController,
)
from peek_core_device._private.tuples.DeviceCacheStatusTuple import (
    DeviceCacheStatusTuple,
)

logger = logging.getLogger(__name__)


class OfflineCacheCombinedStatusTupleProvider(TuplesProviderABC):
    def __init__(self, offlineCacheController: OfflineCacheController):
        self._offlineCacheController = offlineCacheController

    @deferToThreadWrapWithLogger(logger)
    def makeVortexMsg(
        self, filt: dict, tupleSelector: TupleSelector
    ) -> Union[Deferred, bytes]:
        deviceToken = tupleSelector.selector.get("deviceToken")

        encodedPayload = (
            self._offlineCacheController.lastCacheStatusEncodedPayload(
                deviceToken
            )
        )

        # Create the vortex message
        return PayloadEnvelope(
            filt=filt, encodedPayload=encodedPayload
        ).toVortexMsg()
