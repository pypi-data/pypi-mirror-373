#!/usr/bin/env python
import logging

from setproctitle import setproctitle
from reactivex import operators

from peek_platform.util.LogUtil import (
    setupPeekLogger,
    updatePeekLoggerHandlers,
    setupLoggingToSyslogServer,
)
from peek_platform.util.ManHoleUtil import start_manhole
from peek_plugin_base.PeekVortexUtil import peekAgentName, peekServerName
from pytmpdir.dir_setting import DirSetting
from twisted.internet import defer
from twisted.internet import reactor
from txhttputil.site.FileUploadRequest import FileUploadRequest
from txhttputil.util.DeferUtil import printFailure
from vortex.DeferUtil import vortexLogFailure
from vortex.VortexFactory import VortexFactory

setupPeekLogger(peekAgentName)

logger = logging.getLogger(__name__)


def setupPlatform():
    from peek_platform import PeekPlatformConfig

    PeekPlatformConfig.componentName = peekAgentName
    setproctitle(PeekPlatformConfig.componentName)

    # Tell the platform classes about our instance of the PluginSwInstallManager
    from peek_agent_service.sw_install.PluginSwInstallManager import (
        PluginSwInstallManager,
    )

    PeekPlatformConfig.pluginSwInstallManager = PluginSwInstallManager()

    # Tell the platform classes about our instance of the PeekSwInstallManager
    from peek_agent_service.sw_install.PeekSwInstallManager import (
        PeekSwInstallManager,
    )

    PeekPlatformConfig.peekSwInstallManager = PeekSwInstallManager()

    # Tell the platform classes about our instance of the PeekLoaderBase
    from peek_agent_service.plugin.AgentPluginLoader import AgentPluginLoader

    PeekPlatformConfig.pluginLoader = AgentPluginLoader()

    # The config depends on the componentName, order is important
    from peek_agent_service.PeekAgentConfig import PeekAgentConfig

    PeekPlatformConfig.config = PeekAgentConfig()

    # Update the version in the config file
    from peek_agent_service import __version__

    PeekPlatformConfig.config.platformVersion = __version__

    # Set default logging level
    logging.root.setLevel(PeekPlatformConfig.config.loggingLevel)

    # PsUtil
    if not PeekPlatformConfig.config.loggingLogSystemMetrics:
        logging.getLogger("peek_plugin_base.util.PeekPsUtil").setLevel(999)

    updatePeekLoggerHandlers(
        PeekPlatformConfig.componentName,
        PeekPlatformConfig.config.daysToKeep,
        PeekPlatformConfig.config.logToStdout,
    )

    if PeekPlatformConfig.config.loggingLogToSyslogHost:
        setupLoggingToSyslogServer(
            PeekPlatformConfig.config.loggingLogToSyslogHost,
            PeekPlatformConfig.config.loggingLogToSyslogPort,
            PeekPlatformConfig.config.loggingLogToSyslogFacility,
        )

    # Enable deferred debugging if DEBUG is on.
    if logging.root.level == logging.DEBUG:
        defer.setDebugging(True)

    # If we need to enable memory debugging, turn that on.
    if PeekPlatformConfig.config.loggingDebugMemoryMask:
        from peek_platform.util.MemUtil import setupMemoryDebugging

        setupMemoryDebugging(
            PeekPlatformConfig.componentName,
            PeekPlatformConfig.config.loggingDebugMemoryMask,
        )

    # Set the reactor thread count
    reactor.suggestThreadPoolSize(
        PeekPlatformConfig.config.twistedThreadPoolSize
    )

    # Initialise the txhttputil Directory object
    DirSetting.defaultDirChmod = PeekPlatformConfig.config.DEFAULT_DIR_CHMOD
    DirSetting.tmpDirPath = PeekPlatformConfig.config.tmpPath
    FileUploadRequest.tmpFilePath = PeekPlatformConfig.config.tmpPath

    # Setup manhole
    if PeekPlatformConfig.config.manholeEnabled:
        start_manhole(
            PeekPlatformConfig.config.manholePort,
            PeekPlatformConfig.config.manholePassword,
            PeekPlatformConfig.config.manholePublicKeyFile,
            PeekPlatformConfig.config.manholePrivateKeyFile,
        )


def main():
    defer.setDebugging(True)
    # sys.argv.remove(DEBUG_ARG)
    # import pydevd
    # pydevd.settrace(suspend=False)

    setupPlatform()

    # Make the agent restart when the server restarts, or when it looses connection
    def restart(_=None):
        from peek_platform import PeekPlatformConfig

        PeekPlatformConfig.peekSwInstallManager.restartProcess()

    (
        VortexFactory.subscribeToVortexStatusChange(peekServerName)
        .pipe(operators.filter(lambda online: online == False))
        .subscribe(on_next=restart)
    )

    # First, setup the VortexServer Agent

    from peek_platform import PeekPlatformConfig

    dataExchangeCfg = PeekPlatformConfig.config.dataExchange

    scheme = "wss" if dataExchangeCfg.peekServerUseSSL else "ws"
    host = dataExchangeCfg.peekServerHost
    port = dataExchangeCfg.peekServerHttpPort

    def start():
        d = VortexFactory.createWebsocketClient(
            PeekPlatformConfig.componentName,
            host,
            port,
            url=f"{scheme}://{host}:{port}/vortexws",
            sslEnableMutualTLS=dataExchangeCfg.peekServerSSLEnableMutualTLS,
            sslClientCertificateBundleFilePath=dataExchangeCfg.peekServerSSLClientBundleFilePath,
            sslMutualTLSCertificateAuthorityBundleFilePath=dataExchangeCfg.peekServerSSLClientMutualTLSCertificateAuthorityBundleFilePath,
            sslMutualTLSTrustedPeerCertificateBundleFilePath=dataExchangeCfg.peekServerSSLMutualTLSTrustedPeerCertificateBundleFilePath,
        )

        d.addErrback(printFailure)

        # Software update check is not a thing any more
        # Start Update Handler,
        # Add both, The peek client might fail to connect, and if it does, the payload
        # sent from the peekSwUpdater will be queued and sent when it does connect.
        # d.addBoth(lambda _: peekSwVersionPollHandler.start())

        # Load all Plugins
        d.addBoth(lambda _: PeekPlatformConfig.pluginLoader.loadCorePlugins())
        d.addBoth(
            lambda _: PeekPlatformConfig.pluginLoader.loadOptionalPlugins()
        )
        d.addBoth(lambda _: PeekPlatformConfig.pluginLoader.startCorePlugins())
        d.addBoth(
            lambda _: PeekPlatformConfig.pluginLoader.startOptionalPlugins()
        )

        def startedSuccessfully(_):
            logger.info(
                "Peek Agent is running, version=%s",
                PeekPlatformConfig.config.platformVersion,
            )
            return _

        d.addErrback(vortexLogFailure, logger, consumeError=False)
        d.addErrback(lambda _: restart())
        d.addCallback(startedSuccessfully)

    reactor.addSystemEventTrigger(
        "before",
        "shutdown",
        PeekPlatformConfig.pluginLoader.stopOptionalPlugins,
    )
    reactor.addSystemEventTrigger(
        "before", "shutdown", PeekPlatformConfig.pluginLoader.stopCorePlugins
    )

    reactor.addSystemEventTrigger(
        "before",
        "shutdown",
        PeekPlatformConfig.pluginLoader.unloadOptionalPlugins,
    )
    reactor.addSystemEventTrigger(
        "before", "shutdown", PeekPlatformConfig.pluginLoader.unloadCorePlugins
    )
    reactor.addSystemEventTrigger("before", "shutdown", VortexFactory.shutdown)

    reactor.callLater(0, start)
    reactor.run()


if __name__ == "__main__":
    main()
