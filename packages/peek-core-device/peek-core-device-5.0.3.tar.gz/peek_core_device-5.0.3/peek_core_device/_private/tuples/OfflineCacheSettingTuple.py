from vortex.Tuple import Tuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

from peek_core_device._private.PluginNames import deviceTuplePrefix


@addTupleType
class OfflineCacheSettingTuple(Tuple):
    """Offline Cache Setting Tuple

    This tuple is for the client UI settings.

    """

    __tupleType__ = deviceTuplePrefix + "OfflineCacheSettingTuple"

    offlineEnabled: bool = TupleField(defaultValue=False)
