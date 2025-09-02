#!/usr/bin/env python
from reactivex import operators
from txhttputil.site.SiteUtil import setupSite
from vortex.DeferUtil import vortexLogFailure
from vortex.VortexFactory import VortexFactory

from peek_platform.platform_init.init_platform import InitPlatform
from peek_platform.util.LogUtil import setupPeekLogger
from peek_plugin_base.PeekVortexUtil import peekOfficeName
from peek_plugin_base.PeekVortexUtil import peekServerName

setupPeekLogger(peekOfficeName)

from twisted.internet import reactor

import logging

# EXAMPLE LOGGING CONFIG
# Hide messages from vortex
# logging.getLogger('txhttputil.vortex.VortexClient').setLevel(logging.INFO)

# logging.getLogger('peek_office_service_pof.realtime.RealtimePollerEcomProtocol'
#                   ).setLevel(logging.INFO)

logger = logging.getLogger(__name__)


def main():
    # defer.setDebugging(True)
    # sys.argv.remove(DEBUG_ARG)
    # import pydevd
    # pydevd.settrace(suspend=False)

    from peek_platform import PeekPlatformConfig

    platformIniter = InitPlatform(peekOfficeName)

    platformIniter.setupPlatform()

    # Import remaining components
    from peek_office_service import importPackages

    importPackages()

    # Make the agent restart when the server restarts, or when it looses connection
    def restart(_=None):
        from peek_platform import PeekPlatformConfig

        PeekPlatformConfig.peekSwInstallManager.restartProcess()

    (
        VortexFactory.subscribeToVortexStatusChange(peekServerName)
        .pipe(operators.filter(lambda online: online == False))
        .subscribe(on_next=restart)
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

    def startSite(_):
        from peek_office_service.backend.SiteRootResource import (
            setupOffice,
            officeRoot,
        )

        setupOffice()

        # Create the desktop vortex server
        httpServerConfig = PeekPlatformConfig.config.officeHttpServer

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
            "Peek Office Site",
            officeRoot,
            portNum=httpServerConfig.sitePort,
            enableLogin=False,
            redirectFromHttpPort=httpServerConfig.redirectFromHttpPort,
            sslBundleFilePath=httpServerConfig.sslBundleFilePath,
            enableSsl=httpServerConfig.useSsl,
        )

    d.addCallback(startSite)

    def startedSuccessfully(_):
        logger.info(
            "Peek Office is running, version=%s",
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
