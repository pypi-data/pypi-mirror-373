#!/usr/bin/env python
from typing import Optional

from pytmpdir.dir_setting import DirSetting
from reactivex import operators
from setproctitle import setproctitle
from txhttputil.site.FileUploadRequest import FileUploadRequest
from txhttputil.site.SiteUtil import setupSite
from vortex.DeferUtil import vortexLogFailure
from vortex.VortexFactory import VortexFactory

from peek_platform.file_config.PeekFileConfigHttpServerMixin import (
    PeekFileConfigHttpMixin,
)
from peek_platform.util.LogUtil import setupLoggingToSyslogServer
from peek_platform.util.LogUtil import setupPeekLogger
from peek_platform.util.LogUtil import updatePeekLoggerHandlers
from peek_platform.util.ManHoleUtil import start_manhole
from peek_plugin_base.PeekVortexUtil import peekFieldName
from peek_plugin_base.PeekVortexUtil import peekServerName

setupPeekLogger(peekFieldName)

from twisted.internet import reactor, defer

import logging

# EXAMPLE LOGGING CONFIG
# Hide messages from vortex
# logging.getLogger('txhttputil.vortex.VortexClient').setLevel(logging.INFO)

# logging.getLogger('peek_field_service_pof.realtime.RealtimePollerEcomProtocol'
#                   ).setLevel(logging.INFO)

logger = logging.getLogger(__name__)


def setupPlatform(serveManhole: bool):
    from peek_platform import PeekPlatformConfig

    PeekPlatformConfig.componentName = peekFieldName
    setproctitle(PeekPlatformConfig.componentName)

    # Tell the platform classes about our instance of the PluginSwInstallManager
    from peek_field_service.sw_install.PluginSwInstallManager import (
        PluginSwInstallManager,
    )

    PeekPlatformConfig.pluginSwInstallManager = PluginSwInstallManager()

    # Tell the platform classes about our instance of the PeekSwInstallManager
    from peek_field_service.sw_install.PeekSwInstallManager import (
        PeekSwInstallManager,
    )

    PeekPlatformConfig.peekSwInstallManager = PeekSwInstallManager()

    # Tell the platform classes about our instance of the PeekLoaderBase
    from peek_field_service.plugin.ClientPluginLoader import ClientPluginLoader

    PeekPlatformConfig.pluginLoader = ClientPluginLoader()

    # The config depends on the componentName, order is important
    from peek_field_service.PeekClientConfig import PeekClientConfig

    PeekPlatformConfig.config = PeekClientConfig()

    # Update the version in the config file
    from peek_field_service import __version__

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
    if PeekPlatformConfig.config.manholeEnabled and serveManhole:
        start_manhole(
            PeekPlatformConfig.config.manholePort,
            PeekPlatformConfig.config.manholePassword,
            PeekPlatformConfig.config.manholePublicKeyFile,
            PeekPlatformConfig.config.manholePrivateKeyFile,
        )


def main(
    loadPlugins=True,
    startPlugins=True,
    serveSite=True,
    serveWebsocket=True,
    httpServerConfig: Optional[PeekFileConfigHttpMixin] = None,
    siteName="Peek Field Site",
    serveManhole=True,
    buildOnly=False,
):
    # defer.setDebugging(True)
    # sys.argv.remove(DEBUG_ARG)
    # import pydevd
    # pydevd.settrace(suspend=False)
    setupPlatform(serveManhole=serveManhole)

    # Import remaining components
    from peek_field_service import importPackages

    importPackages()

    # Make the agent restart when the server restarts, or when it looses connection
    def restart(_=None):
        from peek_platform import PeekPlatformConfig

        PeekPlatformConfig.peekSwInstallManager.restartProcess()

    if loadPlugins or startPlugins:
        (
            VortexFactory.subscribeToVortexStatusChange(peekServerName)
            .pipe(operators.filter(lambda online: online == False))
            .subscribe(on_next=restart)
        )

    # First, setup the VortexServer Agent
    from peek_platform import PeekPlatformConfig

    # Create the mobile vortex server
    if not httpServerConfig:
        httpServerConfig = PeekPlatformConfig.config.fieldHttpServer

    def start():
        if not startPlugins:
            d = defer.succeed(None)

        else:
            dataExchangeCfg = PeekPlatformConfig.config.dataExchange

            scheme = "wss" if dataExchangeCfg.peekServerUseSSL else "ws"
            host = dataExchangeCfg.peekServerHost
            port = dataExchangeCfg.peekServerHttpPort

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

        # Start Update Handler,
        # Add both, The peek client might fail to connect, and if it does, the payload
        # sent from the peekSwUpdater will be queued and sent when it does connect.

        # Software update check is not a thing any more
        # d.addErrback(vortexLogFailure, logger, consumeError=True)
        # d.addCallback(lambda _: peekSwVersionPollHandler.start())

        # Start client main data observer, this is not used by the plugins
        # (Initialised now, not as a callback)

        # Load all Plugins
        d.addErrback(vortexLogFailure, logger, consumeError=True)
        if loadPlugins:
            d.addCallback(
                lambda _: PeekPlatformConfig.pluginLoader.loadCorePlugins()
            )
            d.addCallback(
                lambda _: PeekPlatformConfig.pluginLoader.loadOptionalPlugins()
            )

        if startPlugins:
            d.addCallback(
                lambda _: PeekPlatformConfig.pluginLoader.startCorePlugins()
            )
            d.addCallback(
                lambda _: PeekPlatformConfig.pluginLoader.startOptionalPlugins()
            )

        def startSite(_):
            from peek_field_service.backend.SiteRootResource import (
                setupField,
                fieldRoot,
            )

            setupField(serveWebsocket=serveWebsocket)

            VortexFactory.setPeerConnectionLimitPerIp(
                httpServerConfig.concurrentPeerIpConnectionLimit
            )
            VortexFactory.setNewConnectionsPerWindow(
                httpServerConfig.newConnectionsPerWindow
            )
            VortexFactory.setRollingNewConnectionWindowSeconds(
                httpServerConfig.rollingNewConnectionWindowSeconds
            )

            setupSite(
                siteName,
                fieldRoot,
                portNum=httpServerConfig.sitePort,
                enableLogin=False,
                redirectFromHttpPort=httpServerConfig.redirectFromHttpPort,
                sslBundleFilePath=httpServerConfig.sslBundleFilePath,
                enableSsl=httpServerConfig.useSsl,
            )

        if serveSite:
            d.addCallback(startSite)

        def startedSuccessfully(_):
            logger.info(
                "Peek Field is running, version=%s",
                PeekPlatformConfig.config.platformVersion,
            )
            logger.info(
                "Status - Plugins %s, %s, Site %s, Websocket %s",
                ("LOADED" if loadPlugins else "NOT LOADED"),
                ("STARTED" if startPlugins else "NOT STARTED"),
                ("LISTENING" if serveSite else "DISABLED"),
                ("LISTENING" if serveWebsocket else "DISABLED"),
            )
            return _

        d.addErrback(vortexLogFailure, logger, consumeError=False)
        d.addErrback(lambda _: restart())
        d.addCallback(startedSuccessfully)

        if buildOnly and not (
            PeekPlatformConfig.config.feSyncFilesForDebugEnabled
            or PeekPlatformConfig.config.docSyncFilesForDebugEnabled
        ):
            d.addBoth(lambda _: reactor.stop())

    if startPlugins:
        reactor.addSystemEventTrigger(
            "before",
            "shutdown",
            PeekPlatformConfig.pluginLoader.stopOptionalPlugins,
        )
        reactor.addSystemEventTrigger(
            "before",
            "shutdown",
            PeekPlatformConfig.pluginLoader.stopCorePlugins,
        )

    if loadPlugins:
        reactor.addSystemEventTrigger(
            "before",
            "shutdown",
            PeekPlatformConfig.pluginLoader.unloadOptionalPlugins,
        )
        reactor.addSystemEventTrigger(
            "before",
            "shutdown",
            PeekPlatformConfig.pluginLoader.unloadCorePlugins,
        )

    if startPlugins:
        reactor.addSystemEventTrigger(
            "before", "shutdown", VortexFactory.shutdown
        )

    reactor.callLater(0, start)
    reactor.run()


if __name__ == "__main__":
    # defer.setDebugging(True)
    # sys.argv.remove(DEBUG_ARG)
    # import pydevd
    # pydevd.settrace(suspend=False)

    main()
