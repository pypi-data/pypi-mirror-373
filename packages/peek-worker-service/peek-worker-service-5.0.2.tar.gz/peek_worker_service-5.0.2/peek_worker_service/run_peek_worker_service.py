#!/usr/bin/env python
from twisted.internet import asyncioreactor
from twisted.internet.defer import inlineCallbacks

# CRITICAL: Install asyncioreactor BEFORE importing any other twisted modules
asyncioreactor.install()

import logging

from reactivex import operators
from twisted.internet import reactor
from vortex.DeferUtil import vortexLogFailure
from vortex.VortexFactory import VortexFactory

from peek_platform.file_config.PeekFileConfigWorkerMixin import (
    PeekFileConfigWorkerMixin,
)
from peek_platform.platform_init.init_platform import InitPlatform
from peek_platform.util.LogUtil import setupPeekLogger
from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_plugin_base.PeekVortexUtil import peekWorkerName
from peek_worker_service.peek_worker_manager import PeekWorkerManager
from peek_worker_service.peek_worker_manager import WorkerConfig


logger = logging.getLogger(__name__)


def main():
    # Setup the logger here, otherwise subprocsseses will call it
    setupPeekLogger(peekWorkerName)
    # defer.setDebugging(True)
    # sys.argv.remove(DEBUG_ARG)
    # import pydevd
    # pydevd.settrace(suspend=False)

    platformIniter = InitPlatform(peekWorkerName)

    platformIniter.setupPlatform()

    from peek_platform import PeekPlatformConfig

    config = PeekPlatformConfig.config
    assert isinstance(
        config, PeekFileConfigWorkerMixin
    ), "config is not of type PeekFileConfigWorkerMixin"

    workerConfig = WorkerConfig(
        url=config.taskValkeyUrl,
        numWorkers=config.taskWorkerCount,
        maxWorkerTasksCompleted=config.taskReplaceWorkerAfterTasksCompleted,
        maxWorkerAgeSeconds=config.taskReplaceWorkerAfterSeconds,
        maxMemoryMb=config.taskReplaceWorkerAfterMemUsage,
        enabledPlugins=PeekPlatformConfig.config.pluginsEnabled,
    )
    workerProcess = PeekWorkerManager(workerConfig)

    @inlineCallbacks
    def startTasks():
        yield workerProcess.start()

        reactor.addSystemEventTrigger(
            "before", "shutdown", lambda: workerProcess.shutdown()
        )

    @inlineCallbacks
    def restart():
        yield workerProcess.shutdown()
        yield platformIniter.stopAndShutdownPluginsAndVortex()
        PeekPlatformConfig.peekSwInstallManager.restartProcess()

    (
        VortexFactory.subscribeToVortexStatusChange(peekServerName)
        .pipe(operators.filter(lambda online: online == False))
        .subscribe(on_next=lambda _: reactor.callLater(0, restart))
    )

    # Start Update Handler,
    # Add both, The peek client might fail to connect, and if it does, the payload
    # sent from the peekSwUpdater will be queued and sent when it does connect.

    # Software update check is not a thing any more
    # d.addErrback(vortexLogFailure, logger, consumeError=True)
    # d.addCallback(lambda _: peekSwVersionPollHandler.start())

    # Start client main data observer, this is not used by the plugins
    # (Initialised now, not as a callback)

    # Load all Plugins
    d = platformIniter.connectVortexClient()
    d.addCallback(lambda _: platformIniter.loadAndStartupPlugins())
    d.addCallback(lambda _: startTasks())

    def startedSuccessfully(_):
        logger.info(
            "Peek Worker is running, version=%s",
            PeekPlatformConfig.config.platformVersion,
        )
        return _

    d.addErrback(vortexLogFailure, logger, consumeError=False)
    d.addErrback(lambda _: restart())
    d.addCallback(startedSuccessfully)

    reactor.addSystemEventTrigger(
        "before", "shutdown", platformIniter.stopAndShutdownPluginsAndVortex
    )

    reactor.run()


if __name__ == "__main__":
    main()
