import logging
from typing import Union

from twisted.internet.defer import Deferred
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

from peek_core_device._private.storage.Setting import FIELD_ENROLLMENT_ENABLED
from peek_core_device._private.storage.Setting import OFFICE_ENROLLMENT_ENABLED
from peek_core_device._private.storage.Setting import (
    OFFLINE_CACHE_REFRESH_SECONDS,
)
from peek_core_device._private.storage.Setting import (
    OFFLINE_MASTER_SWITCH_ENABLED,
    CHECK_BANDWIDTH_SECONDS,
    ABORT_RETRY_SECONDS,
    PAUSE_TIMEOUT_SECONDS,
    SEND_STATS_TO_SERVER_SECONDS,
)
from peek_core_device._private.storage.Setting import (
    SLOW_NETWORK_BANDWIDTH_METRIC_THRESHOLD,
)
from peek_core_device._private.storage.Setting import globalSetting
from peek_core_device._private.tuples.ClientSettingsTuple import (
    ClientSettingsTuple,
)

logger = logging.getLogger(__name__)


class ClientSettingsTupleProvider(TuplesProviderABC):
    def __init__(self, ormSessionCreator):
        self._ormSessionCreator = ormSessionCreator

    @deferToThreadWrapWithLogger(logger)
    def makeVortexMsg(
        self, filt: dict, tupleSelector: TupleSelector
    ) -> Union[Deferred, bytes]:
        ormSession = self._ormSessionCreator()
        try:
            clientSetting = ClientSettingsTuple()

            clientSetting.fieldEnrollmentEnabled = globalSetting(
                ormSession, FIELD_ENROLLMENT_ENABLED
            )

            clientSetting.officeEnrollmentEnabled = globalSetting(
                ormSession, OFFICE_ENROLLMENT_ENABLED
            )

            clientSetting.slowNetworkBandwidthMetricThreshold = globalSetting(
                ormSession, SLOW_NETWORK_BANDWIDTH_METRIC_THRESHOLD
            )

            clientSetting.offlineMasterSwitchEnabled = globalSetting(
                ormSession, OFFLINE_MASTER_SWITCH_ENABLED
            )

            # Timers

            clientSetting.offlineCacheSyncSeconds = globalSetting(
                ormSession, OFFLINE_CACHE_REFRESH_SECONDS
            )

            clientSetting.checkBandwidthSeconds = globalSetting(
                ormSession, CHECK_BANDWIDTH_SECONDS
            )

            clientSetting.abortRetrySeconds = globalSetting(
                ormSession, ABORT_RETRY_SECONDS
            )

            clientSetting.pauseTimeoutSeconds = globalSetting(
                ormSession, PAUSE_TIMEOUT_SECONDS
            )

            clientSetting.sendStateToServerSeconds = globalSetting(
                ormSession, SEND_STATS_TO_SERVER_SECONDS
            )

            # Create the vortex message
            return (
                Payload(filt, tuples=[clientSetting])
                .makePayloadEnvelope()
                .toVortexMsg()
            )

        finally:
            ormSession.close()
