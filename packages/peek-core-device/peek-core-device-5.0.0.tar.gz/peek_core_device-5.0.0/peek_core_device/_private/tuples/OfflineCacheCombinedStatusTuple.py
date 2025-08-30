from vortex.Tuple import Tuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

from peek_core_device._private.PluginNames import deviceTuplePrefix
from peek_core_device._private.tuples.OfflineCacheLoaderStatusTuple import (
    OfflineCacheLoaderStatusTuple,
)
from peek_core_device._private.tuples.OfflineCacheStatusTuple import (
    OfflineCacheStatusTuple,
)


@addTupleType
class OfflineCacheCombinedStatusTuple(Tuple):
    """Offline Cache Status Action

    This tuple is sent from the client to the server periodically when
    an update cycle finishes

    """

    __tupleType__ = deviceTuplePrefix + "OfflineCacheCombinedStatusTuple"

    deviceToken: str = TupleField()
    loaderStatusList: list[OfflineCacheLoaderStatusTuple] = TupleField([])
    offlineCacheStatus: OfflineCacheStatusTuple = TupleField()
