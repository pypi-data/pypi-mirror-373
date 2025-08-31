import logging
import platform

logger = logging.getLogger(__name__)

isLinux = platform.system() == "Linux"
isWindows = platform.system() == "Windows"
isMacOS = platform.system() == "Darwin"
