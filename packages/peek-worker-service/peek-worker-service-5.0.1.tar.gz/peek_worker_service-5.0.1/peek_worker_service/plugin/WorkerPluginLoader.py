import logging
from typing import List
from typing import Tuple
from typing import Type

from twisted.internet.defer import inlineCallbacks

from peek_platform.file_config.peek_file_config_worker_task_import_mixin import (
    WorkerTaskPluginLoaderMixin,
)
from peek_platform.plugin.PluginLoaderABC import PluginLoaderABC
from peek_plugin_base.PluginCommonEntryHookABC import PluginCommonEntryHookABC
from peek_plugin_base.worker.plugin_worker_entry_hook_abc import (
    PluginWorkerEntryHookABC,
)
from peek_worker_service.plugin.PeekWorkerPlatformHook import (
    PeekWorkerPlatformHook,
)

logger = logging.getLogger(__name__)


class WorkerPluginLoader(PluginLoaderABC, WorkerTaskPluginLoaderMixin):
    _instance = None

    def __new__(cls, *args, **kwargs):
        assert (
            cls._instance is None
        ), "WorkerPluginLoader is a singleton, don't construct it"
        cls._instance = PluginLoaderABC.__new__(cls)
        return cls._instance

    @property
    def _entryHookFuncName(self) -> str:
        return "peekWorkerEntryHook"

    @property
    def _entryHookClassType(self):
        return PluginWorkerEntryHookABC

    @property
    def _platformServiceNames(self) -> List[str]:
        return ["worker"]

    @inlineCallbacks
    def _loadPluginThrows(
        self,
        pluginName: str,
        EntryHookClass: Type[PluginCommonEntryHookABC],
        pluginRootDir: str,
        requiresService: Tuple[str, ...],
    ) -> PluginCommonEntryHookABC:
        # Everyone gets their own instance of the plugin API
        platformApi = PeekWorkerPlatformHook()

        pluginMain = EntryHookClass(
            pluginName=pluginName,
            pluginRootDir=pluginRootDir,
            platform=platformApi,
        )

        # Load the plugin
        yield pluginMain.load()

        self._loadedPlugins[pluginName] = pluginMain
