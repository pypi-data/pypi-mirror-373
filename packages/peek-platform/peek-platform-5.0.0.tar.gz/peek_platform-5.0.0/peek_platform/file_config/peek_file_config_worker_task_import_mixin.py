import logging
import sys
from importlib.util import find_spec


logger = logging.getLogger(__name__)


class WorkerTaskPluginLoaderMixin:
    """Worker Loader Mixin‰

    Separate some logic out into this class

    """

    @property
    def taskImports(self):
        includes = []
        for pluginWorkerMain in list(self._loadedPlugins.values()):
            from peek_plugin_base.server.PluginServerWorkerEntryHookABC import (
                PluginServerWorkerEntryHookABC,
            )

            if isinstance(pluginWorkerMain, PluginServerWorkerEntryHookABC):
                desc = str(pluginWorkerMain).split(" ")[0].strip("<")
                try:
                    imports = pluginWorkerMain.workerTaskImports
                    if imports:
                        logger.debug("Loading tasks for %s", desc)
                        includes.extend(imports)
                    else:
                        logger.debug("No tasks defined for %s", desc)
                except Exception as e:
                    logger.exception(
                        "Failed to load tasks for %s: %s", desc, str(e)
                    )

        return includes


def importWorkerTasks():
    from peek_platform import PeekPlatformConfig

    loader = PeekPlatformConfig.pluginLoader

    assert isinstance(loader, WorkerTaskPluginLoaderMixin), (
        "%s is not a " "WorkerTaskPluginLoaderMixin"
    ) % loader

    for task in loader.taskImports:
        modName, functionName = task.rsplit(".", 1)

        if modName in sys.modules:
            module = sys.modules[modName]
        else:
            modSpec = find_spec(modName)
            if not modSpec or not modSpec.loader:
                raise Exception(
                    f"Failed to find module {modName}, is the python package installed?"
                )

            # Load the module.
            # This will call the decorator and register the task
            modSpec.loader.load_module()
