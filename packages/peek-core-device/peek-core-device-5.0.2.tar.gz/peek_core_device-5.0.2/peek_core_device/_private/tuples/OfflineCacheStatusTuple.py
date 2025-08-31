from datetime import datetime
from typing import Optional

from vortex.Tuple import Tuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

from peek_core_device._private.PluginNames import deviceTuplePrefix


@addTupleType
class OfflineCacheStatusTuple(Tuple):
    """Offline Cache Status Tuple

    This tuple represents the load status of the mobile device.

    """

    __tupleType__ = deviceTuplePrefix + "OfflineCacheStatusTuple"

    STATUS_LOADING_SETTINGS = 1
    STATUS_DISABLED = 2
    STATUS_SCHEDULE_NEXT_RUN = 3
    STATUS_ENABLED = 4
    STATUS_START_RUNNING = 5
    STATUS_RUNNING = 6
    STATUS_START_PAUSING = 7
    STATUS_PAUSING = 8
    STATUS_START_BANDWIDTH_TEST = 9
    STATUS_PAUSED_FOR_BANDWIDTH_TEST = 10
    STATUS_START_ABORTING = 11
    STATUS_ABORTED_DUE_TO_VORTEX_OFFLINE = 12
    STATUS_ABORTED_DUE_TO_SLOW_NETWORK = 13

    # Checking occurs on start
    lastCachingCheckDate: Optional[datetime] = TupleField()
    lastCachingStartDate: Optional[datetime] = TupleField()
    lastCachingCompleteDate: Optional[datetime] = TupleField()
    lastCachingAbortDate: Optional[datetime] = TupleField()
    nextStateCheckDate: Optional[datetime] = TupleField()

    # The state machine state
    state: int = TupleField()
    nextState: int = TupleField()

    # Copied from the Testing service for data simplicity
    isSlowNetwork: Optional[bool] = TupleField()
    lastMetric: Optional[int] = TupleField()
