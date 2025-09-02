import logging
import os
import random
import string
from abc import ABCMeta
from pathlib import Path
from typing import Optional

from jsoncfg.value_mappers import RequireType
from jsoncfg.value_mappers import require_bool
from jsoncfg.value_mappers import require_integer
from jsoncfg.value_mappers import require_list
from jsoncfg.value_mappers import require_string

from peek_platform.file_config.PeekFileConfigABC import PEEK_AGENT_SERVICE
from peek_platform.file_config.PeekFileConfigABC import PEEK_FIELD_SERVICE
from peek_platform.file_config.PeekFileConfigABC import PEEK_LOGIC_SERVICE
from peek_platform.file_config.PeekFileConfigABC import PEEK_OFFICE_SERVICE
from peek_platform.file_config.PeekFileConfigABC import PEEK_WORKER_SERVICE

logger = logging.getLogger(__name__)

_PLUGIN_RENAMES = (
    ("peek_plugin_osm_diagram_loader", "peek_plugin_diagram_geojson_loader"),
)


class PeekFileConfigPlatformMixin(metaclass=ABCMeta):
    # --- Platform Logging

    @property
    def loggingDebugMemoryMask(self) -> int:
        with self._cfg as c:
            return c.logging.debugMemoryMask(0, require_integer)

    @property
    def loggingLevel(self) -> str:
        with self._cfg as c:
            lvl = c.logging.level("INFO", require_string)
            if lvl in logging._nameToLevel:
                return lvl

            logger.warning(
                "Logging level %s is not valid, defaulting to INFO", lvl
            )
            return "INFO"

    @property
    def logToStdout(self) -> str:
        with self._cfg as c:
            return c.logging.logToStdout(False, require_bool)

    @property
    def daysToKeep(self) -> int:
        with self._cfg as c:
            val = c.logging.daysToKeep(14, require_integer)

            # As of v3.1+ cleanup the old log file properties
            for prop in ("rotateSizeMb", "rotationsToKeep"):
                if prop in c.logging:
                    logging = {}
                    logging.update(iter(c.logging))
                    del logging[prop]
                    c.logging = logging

            return val

    @property
    def loggingLogToSyslogHost(self) -> Optional[str]:
        with self._cfg as c:
            return c.logging.syslog.logToSysloyHost(None)

    @property
    def loggingLogToSyslogPort(self) -> int:
        with self._cfg as c:
            return c.logging.syslog.logToSysloyPort(514, require_integer)

    @property
    def loggingLogToSyslogFacility(self) -> str:
        with self._cfg as c:
            return c.logging.syslog.logToSysloyProtocol("user", require_string)

    @property
    def loggingLogSystemMetrics(self) -> bool:
        with self._cfg as c:
            return c.logging.logSystemMetrics(True, require_bool)

    @property
    def twistedThreadPoolSize(self) -> int:
        with self._cfg as c:
            count = c.twisted.threadPoolSize(500, require_integer)

        # Ensure the thread count is high
        if count < 50:
            logger.info("Upgrading thread count from %s to %s", count, 500)
            count = 500
            with self._cfg as c:
                c.twisted.threadPoolSize = count

        return count

    @property
    def autoPackageUpdate(self):
        with self._cfg as c:
            return c.platform.autoPackageUpdate(True, require_bool)

    # --- Platform Tmp Path
    @property
    def tmpPath(self):
        default = str(self._tmpPath)
        with self._cfg as c:
            return self._chkDir(c.disk.tmp(default, require_string))

    # --- Platform Software Path
    @property
    def platformSoftwarePath(self):
        raise NotImplementedError("platformSoftwarePath")
        default = os.path.join(self._tmpPath, "platform_software")
        with self._cfg as c:
            return self._chkDir(
                c.platform.softwarePath(default, require_string)
            )

    # --- Platform Software Path
    @property
    def platformMetricsPath(self) -> Path:
        default = os.path.join(self._dataPath, "metrics")
        with self._cfg as c:
            metricsPath = self._chkDir(
                c.platform.metricsPath(default, require_string)
            )

        if metricsPath == default:
            self._ensureMetricsGroupReadable_updateDir(self._dataPath)

        self._ensureMetricsGroupReadable_updateDir(metricsPath)

        return Path(metricsPath)

    # --- Platform Version
    @property
    def platformVersion(self):
        with self._cfg as c:
            return c.platform.version("0.0.0", require_string)

    @platformVersion.setter
    def platformVersion(self, value):
        with self._cfg as c:
            c.platform.version = value

    # --- Plugin Software Path
    @property
    def pluginSoftwarePath(self):
        raise NotImplementedError("pluginSoftwarePath")
        default = os.path.join(self._tmpPath, "plugin_software")
        with self._cfg as c:
            return self._chkDir(c.plugin.softwarePath(default, require_string))

    # --- Plugin Data Path
    def pluginDataPath(self, pluginName):
        default = self._dataPath

        with self._cfg as c:
            pluginData = c.plugin.dataPath(default, require_string)

        return self._chkDir(os.path.join(pluginData, pluginName))

    def _ensureMetricsGroupReadable_updateDir(self, path: Path) -> None:
        mode = os.stat(path).st_mode
        if (mode & 0o050) != 0o050:
            os.chmod(path, mode | 0o050)

    def _ensureMetricsGroupReadable_updateFile(self, path: Path) -> None:
        mode = os.stat(path).st_mode
        if (mode & 0o040) != 0o040:
            os.chmod(path, mode | 0o040)

    def _ensureMetricsGroupReadable(self, dir: Path):

        for root, dirs, files in os.walk(dir):
            root = Path(root)
            for d in dirs:
                self._ensureMetricsGroupReadable_updateDir(root / d)
            for f in files:
                self._ensureMetricsGroupReadable_updateFile(root / f)

    # --- Plugin Data Path
    def pluginMetricsPath(self, pluginName):
        metricsPath = self.platformMetricsPath
        pluginMetricsDir = self._chkDir(os.path.join(metricsPath, pluginName))
        self._ensureMetricsGroupReadable(pluginMetricsDir)
        return pluginMetricsDir

    # --- Plugin Software Version
    def pluginVersion(self, pluginName):
        """Plugin Version

        The last version that we know about
        """
        with self._cfg as c:
            return c.plugin[pluginName].version(
                None, RequireType(type(None), str)
            )

    def setPluginVersion(self, pluginName, version):
        with self._cfg as c:
            c.plugin[pluginName].version = version

    # --- Plugins Installed
    @property
    def pluginsEnabled(self):
        with self._cfg as c:
            plugins = c.plugin.enabled([], require_list)

            for from_, to_ in _PLUGIN_RENAMES:
                if from_ in plugins:
                    logger.info("Renaming plugin %s to %s", from_, to_)
                    plugins[plugins.index(from_)] = to_
                    c.plugin.enabled = plugins

        return plugins

    @pluginsEnabled.setter
    def pluginsEnabled(self, value):
        with self._cfg as c:
            c.plugin.enabled = value

    # --- Manhole
    @property
    def manholeEnabled(self) -> str:
        with self._cfg as c:
            return c.logging.manhole.enabled(True, require_bool)

    @property
    def manholePort(self) -> int:
        from peek_platform import PeekPlatformConfig

        port = {
            PEEK_LOGIC_SERVICE: 2201,
            PEEK_WORKER_SERVICE: 2202,
            PEEK_AGENT_SERVICE: 2203,
            PEEK_FIELD_SERVICE: 2204,
            PEEK_OFFICE_SERVICE: 2205,
        }[PeekPlatformConfig.componentName]
        with self._cfg as c:
            return c.logging.manhole.port(port, require_integer)

    @property
    def manholePassword(self) -> str:
        # Define the characters that can be used in the password
        characters = string.ascii_letters + string.digits + string.punctuation

        # Generate a random password with 32 characters
        default = "".join(random.choice(characters) for _ in range(32))
        with self._cfg as c:
            return c.logging.manhole.password(default, require_string)

    @property
    def manholePublicKeyFile(self) -> str:
        return self._ensureMaholeKeysExist()[0]

    @property
    def manholePrivateKeyFile(self) -> str:
        return self._ensureMaholeKeysExist()[1]

    def _ensureMaholeKeysExist(self) -> (str, str):
        with self._cfg as c:
            privateDefault = os.path.join(self._configPath, "manhole-key")
            priFile = c.logging.manhole.privateKeyFile(
                privateDefault, require_string
            )

            publicDefault = os.path.join(self._configPath, "manhole-key.pub")
            pubFile = c.logging.manhole.publicKeyFile(
                publicDefault, require_string
            )

            if not os.path.exists(priFile) or not os.path.exists(pubFile):
                self._manholeCreateKeys(priFile, pubFile)

            return pubFile, priFile

    def _manholeCreateKeys(self, priFile, pubFile):
        logger.info("(Re)Creating Manhole SSH Server Keys")

        from cryptography.hazmat.primitives import (
            serialization as crypto_serialization,
        )
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.backends import (
            default_backend as crypto_default_backend,
        )

        key = rsa.generate_private_key(
            backend=crypto_default_backend(),
            public_exponent=65537,
            key_size=2048,
        )
        privateKey = key.private_bytes(
            crypto_serialization.Encoding.PEM,
            crypto_serialization.PrivateFormat.TraditionalOpenSSL,
            crypto_serialization.NoEncryption(),
        ).decode()
        publicKey = (
            key.public_key()
            .public_bytes(
                crypto_serialization.Encoding.OpenSSH,
                crypto_serialization.PublicFormat.OpenSSH,
            )
            .decode()
        )

        from peek_platform import PeekPlatformConfig

        publicKey += " Peek %s Manhole" % PeekPlatformConfig.componentName

        with open(pubFile, "w") as f:
            f.write(publicKey)

        with open(priFile, "w") as f:
            f.write(privateKey)
