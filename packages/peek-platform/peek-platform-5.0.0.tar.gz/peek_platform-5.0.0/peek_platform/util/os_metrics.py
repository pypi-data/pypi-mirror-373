import json
import logging
import socket
from datetime import datetime
from pathlib import Path

import psutil
import pytz
from twisted.internet.task import LoopingCall
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.DeferUtil import vortexLogFailure
from vortex.Tuple import Tuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

from peek_plugin_base.LoopingCallUtil import peekCatchErrbackWithLogger

logger = logging.getLogger(__name__)

# You can replace this prefix with your actual prefix
_osMetricsTuplePrefix = "system.metrics."


@addTupleType
class _OsMetricsTuple(Tuple):
    __tupleType__ = _osMetricsTuplePrefix + "_OsMetricsTuple"

    lastUpdateDate: datetime = TupleField()
    hostFqdn: str = TupleField()
    cpu15MinuteLoadPercent: int = TupleField()
    maxLocalDiskUsagePercent: int = TupleField()
    memoryBufferCacheMb: int = TupleField()
    memoryFreeMb: int = TupleField()
    swapUsageMb: int = TupleField()
    swapUsedPercent: int = TupleField()
    memoryUsedPercent: int = TupleField()
    systemCpuCount: int = TupleField()
    systemMemorySizeMb: int = TupleField()
    systemSwapSizeMb: int = TupleField()
    enabledPlugins: list[str] = TupleField([])
    serviceStartDate: datetime = TupleField()
    serviceUptimeHours: float = TupleField()


class OsMetrics:
    LOOPING_CALL_PERIOD = 30.0
    """Collects and writes system metrics to a JSON file."""

    def __init__(self, writeDir: Path, enabledPlugins: list[str]):
        self._writeDir = writeDir
        self._enabledPlugins = enabledPlugins
        self._serviceStartDate = datetime.now(pytz.utc)
        self._loopingCall = LoopingCall(
            peekCatchErrbackWithLogger(logger)(self.writeMetrics)
        )

    def start(self):
        d = self._loopingCall.start(self.LOOPING_CALL_PERIOD, now=True)
        d.addErrback(vortexLogFailure, logger, consumeError=True)

    def stop(self):
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
            jsonFilePath = self._writeDir / "system_metrics.json"
            hostnameTxtPath = self._writeDir / "hostname.txt"

            # Convert datetime to string for JSON serialization
            metricsDict = metrics.tupleToRestfulJsonDict()

            with jsonFilePath.open("w") as f:
                json.dump(metricsDict, f, indent=4)

            with hostnameTxtPath.open("w") as f:
                f.write(metrics.hostFqdn)

        except Exception as e:
            print(f"Error writing system metrics: {e}")
            raise

    def _getCpuLoadPercent(self) -> int:
        """Get 15-minute CPU load average as a percentage normalized across all CPUs."""
        cpuCount = psutil.cpu_count()
        loadAvg = psutil.getloadavg()[2]  # 15-minute load average
        loadPercent = (loadAvg / cpuCount) * 100
        return int(min(loadPercent, 100))

    def _getMaxDiskUsagePercent(self) -> int:
        """Get maximum disk usage percentage across all mounted filesystems."""
        maxPercent = 0.0
        for partition in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                maxPercent = int(max(maxPercent, usage.percent))
            except PermissionError:
                continue
        return maxPercent

    def _getMemoryMetrics(self, metrics: _OsMetricsTuple) -> None:
        """Get memory-related metrics including swap usage."""
        virtualMemory = psutil.virtual_memory()
        swap = psutil.swap_memory()

        # Get buffer/cache memory - handle different system reporting methods
        buffersAndCached = getattr(virtualMemory, "buffers", 0) + getattr(
            virtualMemory, "cached", 0
        )
        if buffersAndCached == 0:  # If neither attribute exists
            # On some systems, cached might be calculated from total - used - free - buffers
            buffersAndCached = (
                virtualMemory.total - virtualMemory.used - virtualMemory.free
            )

        metrics.memoryBufferCacheMb = int(buffersAndCached / 1024 / 1024)
        metrics.memoryFreeMb = int(virtualMemory.available / 1024 / 1024)
        metrics.swapUsageMb = int(swap.used / 1024 / 1024)
        metrics.swapUsedPercent = int(swap.percent)
        metrics.memoryUsedPercent = int(virtualMemory.percent)

        # Add the new system memory and swap size metrics
        metrics.systemMemorySizeMb = int(virtualMemory.total / 1024 / 1024)
        metrics.systemSwapSizeMb = int(swap.total / 1024 / 1024)

    def _collectMetrics(self) -> _OsMetricsTuple:
        """Collect all system metrics and return as an OsMetricsTuple."""
        hours = round(
            int(
                (
                    datetime.now(pytz.utc) - self._serviceStartDate
                ).total_seconds()
                / 60
            )
            / 60,
            4,
        )

        metrics = _OsMetricsTuple(
            hostFqdn=socket.gethostname(),
            cpu15MinuteLoadPercent=self._getCpuLoadPercent(),
            maxLocalDiskUsagePercent=self._getMaxDiskUsagePercent(),
            lastUpdateDate=datetime.now(pytz.utc),
            systemCpuCount=psutil.cpu_count(),
            enabledPlugins=self._enabledPlugins,
            serviceStartDate=self._serviceStartDate,
            serviceUptimeHours=hours,
        )
        self._getMemoryMetrics(metrics)
        return metrics
