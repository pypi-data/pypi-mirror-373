from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType
from vortex.TupleAction import TupleActionABC

from peek_core_device._private.PluginNames import deviceTuplePrefix


@addTupleType
class BandwidthTestTuple(TupleActionABC):
    __tupleType__ = deviceTuplePrefix + "BandwidthTestTuple"

    testData: str = TupleField()
