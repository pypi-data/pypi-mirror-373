"""
 *
 *  Copyright Synerty Pty Ltd 2013
 *
 *  This software is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this software are reserved by 
 *  Synerty Pty Ltd
 *
 * Website : http://www.synerty.com
 * Support : support@synerty.com
 *
"""

import logging
import os
import platform
from abc import ABCMeta
from pathlib import Path

from jsoncfg.functions import ConfigWithWrapper
from jsoncfg.functions import save_config

logger = logging.getLogger(__name__)

PEEK_LOGIC_SERVICE = "peek-logic-service"
PEEK_WORKER_SERVICE = "peek-worker-service"
PEEK_AGENT_SERVICE = "peek-agent-service"
PEEK_OFFICE_SERVICE = "peek-office-service"
PEEK_FIELD_SERVICE = "peek-field-service"
PEEK_SERVICES = (
    PEEK_LOGIC_SERVICE,
    PEEK_WORKER_SERVICE,
    PEEK_AGENT_SERVICE,
    PEEK_OFFICE_SERVICE,
    PEEK_FIELD_SERVICE,
)


class PeekFileConfigABC(metaclass=ABCMeta):
    """
    This class creates a basic agent configuration
    """

    DEFAULT_FILE_CHMOD = 0o600
    DEFAULT_DIR_CHMOD = 0o700

    __instance = None

    def __new__(cls):
        if cls.__instance is not None:
            return cls.__instance

        self = super(PeekFileConfigABC, cls).__new__(cls)
        cls.__instance = self
        return self

    def _migrate(self):
        pass

    def __init__(self):
        """
        Constructor
        """
        from peek_platform import PeekPlatformConfig

        assert PeekPlatformConfig.componentName is not None

        serviceNameNoService = PeekPlatformConfig.componentName.replace(
            "-service", ""
        )
        basePath = (
            Path("~/peek").expanduser()
            if platform.system() == "Darwin"
            else Path("~").expanduser()
        )
        self._configPath = str(basePath / "etc" / serviceNameNoService)
        self._sslPath = str(basePath / "etc" / "ssl" / serviceNameNoService)
        self._dataPath = str(basePath / "var" / serviceNameNoService)
        self._logPath = str(basePath / "log" / serviceNameNoService)
        self._tmpPath = str(basePath / "tmp" / serviceNameNoService)

        self._migrate()

        for path in (
            self._configPath,
            self._dataPath,
            self._logPath,
            self._tmpPath,
        ):
            if not os.path.isdir(path):
                assert not os.path.exists(path)
                Path(path).mkdir(
                    mode=self.DEFAULT_DIR_CHMOD, parents=True, exist_ok=True
                )

        self._configFilePath = os.path.join(self._configPath, "config.json")

        if not os.path.isfile(self._configFilePath):
            assert not os.path.exists(self._configFilePath)
            with open(self._configFilePath, "w") as fobj:
                fobj.write("{}")

        self._cfg = ConfigWithWrapper(self._configFilePath)

        self._hp = "%(" + self._configPath + ")s"

    def _save(self):
        save_config(self._configFilePath, self._cfg)

    def _chkDir(self, path):
        if not os.path.isdir(path):
            assert not os.path.exists(path)
            os.makedirs(path, self.DEFAULT_DIR_CHMOD)
        return path
