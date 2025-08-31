import json
import logging
from collections import Counter
from datetime import datetime
from datetime import timedelta
from pathlib import Path

import pytz
from twisted.internet.task import LoopingCall
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.DeferUtil import vortexLogFailure
from vortex.Tuple import Tuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

from peek_core_device._private.PluginNames import deviceTuplePrefix
from peek_core_device._private.storage.DeviceInfoTable import DeviceInfoTable
from peek_plugin_base.LoopingCallUtil import peekCatchErrbackWithLogger

logger = logging.getLogger(__name__)


@addTupleType
class DeviceMetricsTuple(Tuple):
    __tupleType__ = deviceTuplePrefix + "DeviceMetricsTuple"

    lastUpdateDate: datetime = TupleField()
    totalDevices: int = TupleField()
    devicesOnlineLast365Days: int = TupleField()
    devicesOnlineLast30Days: int = TupleField()
    devicesOnlineLast7Days: int = TupleField()
    devicesOnlineLast24Hours: int = TupleField()
    deviceTypeCount: dict[str, int] = TupleField()


class MetricsController:
    LOOPING_CALL_PERIOD = 30.0 * 60  # 30 minutes
    """Collects and writes system metrics to a JSON file."""

    def __init__(self, writeDir: Path, ormSessionCreator):
        self._writeDir = writeDir
        self._ormSessionCreator = ormSessionCreator
        self._loopingCall = LoopingCall(
            peekCatchErrbackWithLogger(logger)(self.writeMetrics)
        )

    def start(self):
        d = self._loopingCall.start(self.LOOPING_CALL_PERIOD, now=True)
        d.addErrback(vortexLogFailure, logger, consumeError=True)

    def shutdown(self):
        if self._loopingCall is not None:
            self._loopingCall.stop()
            self._loopingCall = None

    @deferToThreadWrapWithLogger(logger)
    def writeMetrics(self) -> None:
        """Collect and write system metrics to a JSON file.

        Raises:
            OSError: If there are file permission issues
            psutil.Error: If there are errors collecting system metrics
        """
        try:
            metrics = self._collectMetrics()
            jsonFilePath = self._writeDir / "metrics.json"

            # Convert datetime to string for JSON serialization
            metricsDict = metrics.tupleToRestfulJsonDict()

            with jsonFilePath.open("w") as f:
                json.dump(metricsDict, f, indent=4)

        except Exception as e:
            logger.exception(f"Error writing metrics: {e}")
            raise

    def _addDeviceMetrics(self, metrics: DeviceMetricsTuple) -> None:
        """Get memory-related metrics including swap usage."""
        ormSession = self._ormSessionCreator()
        try:

            devices = list(
                ormSession.query(
                    DeviceInfoTable.lastOnline, DeviceInfoTable.deviceType
                )
            )
            now = datetime.now(pytz.utc)

            # Time thresholds
            one_year_ago = now - timedelta(days=365)
            one_month_ago = now - timedelta(days=30)
            one_week_ago = now - timedelta(days=7)
            today_start = now - timedelta(days=1)

            # Calculate metrics
            metrics.totalDevices = len(devices)
            metrics.devicesOnlineLast365Days = sum(
                1 for device in devices if device.lastOnline >= one_year_ago
            )
            metrics.devicesOnlineLast30Days = sum(
                1 for device in devices if device.lastOnline >= one_month_ago
            )
            metrics.devicesOnlineLast7Days = sum(
                1 for device in devices if device.lastOnline >= one_week_ago
            )
            metrics.devicesOnlineLast24Hours = sum(
                1 for device in devices if device.lastOnline >= today_start
            )
            metrics.deviceTypeCount = dict(
                Counter(device.deviceType for device in devices)
            )

        finally:
            ormSession.close()

    def _collectMetrics(self) -> DeviceMetricsTuple:
        """Collect all system metrics and return as an OsMetricsTuple."""

        metrics = DeviceMetricsTuple(lastUpdateDate=datetime.now(pytz.utc))
        self._addDeviceMetrics(metrics)
        return metrics
