import logging
import multiprocessing
import platform
from typing import Optional

from jsoncfg.value_mappers import require_integer
from jsoncfg.value_mappers import require_string

from peek_platform.WindowsPatch import isMacOS

logger = logging.getLogger(__name__)


class PeekFileConfigWorkerMixin:
    @property
    def taskValkeyUrl(self) -> str:
        if platform.system() == "Darwin":
            default = "valkey://localhost:6379/0"
        else:
            default = "unix:///peek/run/valkey/valkey.sock?db=0"

        with self._cfg as c:
            return c.task.valkey.url(default, require_string)

    @property
    def taskWorkerCount(self) -> int:
        # for CELERYD_CONCURRENCY

        # By default, we assume a single server setup.
        # So leave half the CPU threads for the database
        default = multiprocessing.cpu_count()
        with self._cfg as c:
            return c.task.worker.count(default, require_integer)

    @property
    def taskReplaceWorkerAfterTasksCompleted(self) -> Optional[int]:
        # for worker_max_tasks_per_child
        default = 5000
        with self._cfg as c:
            try:
                return int(
                    c.task.worker.replaceAfterTasksCompleted(
                        default, require_integer
                    )
                )
            except (TypeError, ValueError):
                c.task.worker.replaceAfterTasksCompleted = default
                return default

    @property
    def taskReplaceWorkerAfterSeconds(self) -> Optional[int]:
        # for worker_max_tasks_per_child
        default = 1800
        with self._cfg as c:
            try:
                return int(
                    c.task.worker.replaceAfterTaskSeconds(
                        default, require_integer
                    )
                )
            except (TypeError, ValueError):
                c.task.worker.replaceAfterTaskSeconds = default
                return default

    @property
    def taskReplaceWorkerAfterMemUsage(self) -> Optional[int]:
        # for worker_max_memory_per_child
        default = 500
        with self._cfg as c:
            try:
                return int(
                    c.task.worker.replaceAfterMemMbUsage(
                        default, require_integer
                    )
                )
            except (TypeError, ValueError):
                c.task.worker.replaceAfterMemMbUsage = default
                return default
