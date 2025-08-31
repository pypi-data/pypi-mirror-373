from vortex.Tuple import Tuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

from peek_core_device._private.PluginNames import deviceTuplePrefix


@addTupleType
class ClientSettingsTuple(Tuple):
    """Client Settings Tuple

    This tuple is for the client UI settings.

    """

    __tupleType__ = deviceTuplePrefix + "ClientSettingsTuple"

    fieldEnrollmentEnabled: bool = TupleField()
    officeEnrollmentEnabled: bool = TupleField()
    slowNetworkBandwidthMetricThreshold: int = TupleField()
    offlineMasterSwitchEnabled: bool = TupleField()

    offlineCacheSyncSeconds: int = TupleField()
    checkBandwidthSeconds: int = TupleField()
    abortRetrySeconds: int = TupleField()
    pauseTimeoutSeconds: int = TupleField()
    sendStateToServerSeconds: int = TupleField()
