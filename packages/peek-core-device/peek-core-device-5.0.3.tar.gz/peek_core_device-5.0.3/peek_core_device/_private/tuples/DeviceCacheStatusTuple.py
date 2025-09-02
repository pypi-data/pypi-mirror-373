from vortex.Tuple import Tuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

from peek_core_device._private.PluginNames import deviceTuplePrefix
from peek_core_device._private.tuples.OfflineCacheLoaderStatusTuple import (
    OfflineCacheLoaderStatusTuple,
)


@addTupleType
class DeviceCacheStatusTuple(Tuple):
    """Device Cache Status Tuple

    This is an Admin tuple

    """

    __tupleType__ = deviceTuplePrefix + "DeviceCacheStatusTuple"

    statusList: list[OfflineCacheLoaderStatusTuple] = TupleField()
