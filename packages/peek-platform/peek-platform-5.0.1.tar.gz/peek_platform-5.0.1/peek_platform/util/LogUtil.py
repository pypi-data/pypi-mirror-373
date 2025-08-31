import gzip
import logging
import os
import platform
import sys
import warnings
from logging.handlers import SysLogHandler
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Optional

from cryptography.utils import CryptographyDeprecationWarning

warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)

LOG_FORMAT = "%(asctime)s %(levelname)s #%(name)s:%(message)s"
DATE_FORMAT = "%d-%b-%Y %H:%M:%S"


def _makeFormat(childIdentifier: str | None):
    if childIdentifier:
        return LOG_FORMAT.replace("#", childIdentifier + " ")
    else:
        return LOG_FORMAT.replace("#", "")


logger = logging.getLogger(__name__)


def setupPeekLogger(
    serviceName: Optional[str] = None,
    childIdentifier: str | None = None,
    logToStdout=True,
):
    logging.basicConfig(
        stream=sys.stdout,
        format=_makeFormat(childIdentifier),
        datefmt=DATE_FORMAT,
        level=logging.DEBUG,
    )

    logging.getLogger("peek_plugin_worker.peek_worker_process").setLevel(
        logging.INFO
    )
    logging.getLogger("peek_worker_service.peek_worker_request_queue").setLevel(
        logging.INFO
    )

    if serviceName:
        updatePeekLoggerHandlers(
            serviceName,
            childIdentifier=childIdentifier,
            logToStdout=logToStdout,
        )


def _namer(name):
    return name + ".gz"


def _rotator(source, dest):
    READ_CHUNK = 512 * 1024
    if not os.path.exists(source):
        return
    if os.path.exists(dest):
        return

    with open(source, "rb") as sf:
        with gzip.open(dest, "wb") as f:
            data = sf.read(READ_CHUNK)
            while data:
                f.write(data)
                data = sf.read(READ_CHUNK)

    if os.path.exists(source):
        os.remove(source)


def updatePeekLoggerHandlers(
    serviceName: Optional[str] = None,
    daysToKeep=28,
    logToStdout=True,
    childIdentifier: str | None = None,
):
    rootLogger = logging.getLogger()
    logFormatter = logging.Formatter(_makeFormat(childIdentifier), DATE_FORMAT)

    for handler in list(rootLogger.handlers):
        if isinstance(handler, TimedRotatingFileHandler):
            # Setup the file logging output
            rootLogger.removeHandler(handler)

        elif not sys.stdout.isatty() and not logToStdout:
            # Remove the stdout handler
            logger.info(
                "Logging to stdout disabled, see 'logToStdout' in config.json"
            )
            rootLogger.removeHandler(handler)

    serviceNameNoService = serviceName.replace("-service", "")
    fileName = (
        (
            Path("~/peek/log").expanduser()
            if platform.system() == "Darwin"
            else Path("~/log").expanduser()
        )
        / serviceNameNoService
        / ("%s.log" % serviceNameNoService)
    )
    fileName.parent.mkdir(parents=True, exist_ok=True)

    fh = TimedRotatingFileHandler(
        str(fileName), when="midnight", backupCount=daysToKeep
    )
    fh.setFormatter(logFormatter)
    fh.rotator = _rotator
    fh.namer = _namer
    rootLogger.addHandler(fh)


def setupLoggingToSyslogServer(host: str, port: int, facility: str):
    rootLogger = logging.getLogger()
    # TODO, Syslog server needs _makeFormat(childIdentifier)
    logFormatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

    logging.getLogger().addHandler(logging.StreamHandler())

    if facility not in SysLogHandler.facility_names:
        logger.info(list(SysLogHandler.facility_names))
        raise Exception("Syslog facility name is a valid facility")

    facilityNum = SysLogHandler.facility_names[facility]

    fh = SysLogHandler(address=(host, port), facility=facilityNum)
    fh.setFormatter(logFormatter)
    rootLogger.addHandler(fh)
