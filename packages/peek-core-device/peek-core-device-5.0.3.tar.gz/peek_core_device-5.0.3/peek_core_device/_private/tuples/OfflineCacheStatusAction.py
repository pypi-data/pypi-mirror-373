from datetime import datetime
from typing import Optional

from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType
from vortex.TupleAction import TupleActionABC

from peek_core_device._private.PluginNames import deviceTuplePrefix
from peek_core_device._private.tuples.OfflineCacheLoaderStatusTuple import (
    OfflineCacheLoaderStatusTuple,
)
from peek_core_device._private.tuples.OfflineCacheStatusTuple import (
    OfflineCacheStatusTuple,
)


@addTupleType
class OfflineCacheStatusAction(TupleActionABC):
    """Offline Cache Status Action

    This tuple is sent from the client to the server periodically when
    an update cycle finishes

    """

    __tupleType__ = deviceTuplePrefix + "OfflineCacheStatusAction"

    deviceToken: str = TupleField()
    encodedCombinedTuplePayload: str = TupleField()
    lastCachingStartDate: Optional[datetime] = TupleField()
