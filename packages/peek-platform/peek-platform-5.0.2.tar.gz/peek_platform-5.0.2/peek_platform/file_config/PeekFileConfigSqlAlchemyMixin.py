import logging
import os

from jsoncfg.value_mappers import require_dict
from jsoncfg.value_mappers import require_string

logger = logging.getLogger(__name__)


class PeekFileConfigSqlAlchemyMixin:
    @property
    def dbConnectString(self):

        with self._cfg as c:
            if "PGHOST" in os.environ:
                eePgSocket = f"{os.environ['PGHOST']}"
                default = f"postgresql+psycopg://peek@/peek?host={eePgSocket}"
            else:
                default = "postgresql+psycopg://peek:PASSWORD@127.0.0.1/peek"

            return c.sqlalchemy.connectUrl(default, require_string)

    @property
    def dbEngineArgs(self):
        default = {
            "echo": False,  # Print every SQL statement executed
            "pool_size": 20,  # Number of connections to keep open
            "max_overflow": 50,
            # Number that the pool size can exceed when required
            "pool_timeout": 60,  # Timeout for getting conn from pool
            "pool_recycle": 600,  # Reconnect?? after 10 minutes
            # This supersedes 'use_batch_mode': True,
        }
        with self._cfg as c:
            val = c.sqlalchemy.engineArgs(default, require_dict)
            # Upgrade depreciated psycopg setting.
            if val.get("use_batch_mode") == True:
                del val["use_batch_mode"]
                c.sqlalchemy.engineArgs = val

            if "client_encoding" not in val:
                val["client_encoding"] = "utf8"
                c.sqlalchemy.engineArgs = val

            if "executemany_mode" in val:
                del val["executemany_mode"]

            return val
