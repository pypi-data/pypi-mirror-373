from datetime import datetime

from vortex.Tuple import Tuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

from peek_core_device._private.PluginNames import deviceTuplePrefix


@addTupleType
class OfflineCacheLoaderStatusTuple(Tuple):
    """Offline Cache Status Tuple

    This tuple represents the load status of the mobile device.

    """

    __tupleType__ = deviceTuplePrefix + "OfflineCacheLoaderStatusTuple"

    pluginName: str = TupleField()
    indexName: str = TupleField()
    loadingQueueCount: int = TupleField()
    totalLoadedCount: int = TupleField()
    lastCheckDate: datetime = TupleField()
    initialFullLoadComplete: bool = TupleField()
