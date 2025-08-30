from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType
from vortex.TupleAction import TupleActionABC

from peek_core_device._private.PluginNames import deviceTuplePrefix


@addTupleType
class UpdateOfflineCacheSettingAction(TupleActionABC):
    """Update Offline Cache Setting Action

    This action authorises a device to enroll in this peek environment.

    """

    __tupleType__ = deviceTuplePrefix + "UpdateOfflineCacheSettingAction"

    #:  The device info id to authorise
    deviceInfoId: int = TupleField()
    offlineCacheEnabled: bool = TupleField(False)
