from typing import Optional

from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType
from vortex.TupleAction import TupleActionABC

from peek_core_device._private.PluginNames import deviceTuplePrefix


@addTupleType
class BandwidthTestResultTuple(TupleActionABC):
    __tupleType__ = deviceTuplePrefix + "BandwidthTestResultTuple"

    deviceToken: str = TupleField()
    metric: Optional[int] = TupleField()

    @property
    def timedOut(self) -> bool:
        return self.metric is None
