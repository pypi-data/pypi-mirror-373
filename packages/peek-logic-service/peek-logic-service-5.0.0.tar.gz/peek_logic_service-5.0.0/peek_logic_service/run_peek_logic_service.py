#!/usr/bin/env python
from twisted.internet.error import ReactorAlreadyInstalledError
from twisted.internet import asyncioreactor

try:
    # CRITICAL: Install asyncioreactor BEFORE importing any other twisted modules
    asyncioreactor.install()
except ReactorAlreadyInstalledError:
    # This is a subprocess, so this is expected. Continue running.
    pass


import logging
import os
from pathlib import Path

from pytmpdir.dir_setting import DirSetting
from setproctitle import setproctitle
from txhttputil.site.FileUploadRequest import FileUploadRequest
from txhttputil.util.PemUtil import generateDiffieHellmanParameterBytes
from vortex.DeferUtil import vortexLogFailure

from peek_logic_service import importPackages
from peek_logic_service.storage import setupDbConn
from peek_logic_service.storage.DeclarativeBase import metadata
from peek_platform.file_config.PeekFileConfigWorkerMixin import (
    PeekFileConfigWorkerMixin,
)
from peek_platform.file_config.peek_file_config_worker_task_import_mixin import (
    importWorkerTasks,
)
from peek_platform.util.LogUtil import setupLoggingToSyslogServer
from peek_platform.util.LogUtil import setupPeekLogger
from peek_platform.util.LogUtil import updatePeekLoggerHandlers
from peek_platform.util.ManHoleUtil import start_manhole
from peek_platform.util.os_metrics import OsMetrics
from peek_plugin_base.PeekVortexUtil import peekServerName

setupPeekLogger(peekServerName)

from twisted.internet import reactor, defer

from txhttputil.site.SiteUtil import setupSite

from txhttputil.site.BasicResource import BasicResource

logger = logging.getLogger(__name__)


def setupStorageInit():
    from peek_platform import PeekPlatformConfig

    cfg = PeekPlatformConfig.config

    ###########################################################################
    # BEGIN - INTERIM STORAGE SETUP
    # Force model migration

    from peek_storage_service._private.storage import (
        setupDbConn as storage_setupDbConn,
    )
    from peek_storage_service import _private as storage_private

    from peek_storage_service._private.storage.DeclarativeBase import (
        metadata as storage_metadata,
    )

    storage_setupDbConn(
        metadata=storage_metadata,
        dbEngineArgs=cfg.dbEngineArgs,
        dbConnectString=cfg.dbConnectString,
        alembicDir=os.path.join(
            os.path.dirname(storage_private.__file__), "alembic"
        ),
    )

    # Perform any storage initialisation after the migration is done.
    from peek_storage_service._private.storage import dbConn as storage_dbConn
    from peek_storage_service._private.StorageInit import StorageInit

    storageInit = StorageInit(storage_dbConn)

    # Perform the migration, including and pre and post migration inits.
    storageInit.runPreMigrate()
    storage_dbConn.migrate()
    storageInit.runPostMigrate()

    # END - INTERIM STORAGE SETUP
    ###########################################################################


def _setupWorkerTaskRequestQueue():
    """Setup Worker Task Request Queue"""
    from peek_platform import PeekPlatformConfig
    from peek_worker_service.peek_worker_request_queue import (
        PeekWorkerRequestQueue,
    )
    from peek_worker_service.peek_worker_task import initializeAllTaskMethods

    config = PeekPlatformConfig.config
    assert isinstance(
        config, PeekFileConfigWorkerMixin
    ), "config is not of type PeekFileConfigWorkerMixin"

    importWorkerTasks()

    requestQueue = PeekWorkerRequestQueue(url=config.taskValkeyUrl)
    initializeAllTaskMethods(requestQueue)

    requestQueue.start()

    reactor.addSystemEventTrigger(
        "before", "shutdown", lambda: requestQueue.shutdown()
    )


# ------------------------------------------------------------------------------
# Set the parallelism of the database and reactor


def setupPlatform():
    from peek_platform import PeekPlatformConfig

    PeekPlatformConfig.componentName = peekServerName
    setproctitle(PeekPlatformConfig.componentName)

    # Tell the platform classes about our instance of the pluginSwInstallManager
    from peek_logic_service.server.sw_install.PluginSwInstallManager import (
        PluginSwInstallManager,
    )

    PeekPlatformConfig.pluginSwInstallManager = PluginSwInstallManager()

    # Tell the platform classes about our instance of the PeekSwInstallManager
    from peek_logic_service.server.sw_install.PeekSwInstallManager import (
        PeekSwInstallManager,
    )

    PeekPlatformConfig.peekSwInstallManager = PeekSwInstallManager()

    # Tell the platform classes about our instance of the PeekLoaderBase
    from peek_logic_service.plugin.ServerPluginLoader import ServerPluginLoader

    PeekPlatformConfig.pluginLoader = ServerPluginLoader()

    # The config depends on the componentName, order is important
    from peek_logic_service.PeekServerConfig import PeekServerConfig

    PeekPlatformConfig.config = PeekServerConfig()

    # Initialise the recovery user
    # noinspection PyStatementEffect
    PeekPlatformConfig.config.adminUser
    # noinspection PyStatementEffect
    PeekPlatformConfig.config.adminPass

    # Update the version in the config file
    from peek_logic_service import __version__

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

    # Set paths for the Directory object
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


class HACK_AllowJsFilesUnauthed(BasicResource):
    """HACK Allow JS Files Un-Authenticated

    This class is a temporary class that must be cleaned up when
    PEEK-666 is resolved.

    It solves an issue caused by old browsers and angular9.

    """

    def __init__(self, fileUnderlayResource, adminAuthRealm):
        self._fileUnderlayResource = fileUnderlayResource
        self._adminAuthRealm = adminAuthRealm

    def getChildWithDefault(self, path, request):
        """Get Child With Default

        Allow .js files to bypass the authentication

        """
        if path.lower().endswith(b".js"):
            return self._fileUnderlayResource.getChildWithDefault(path, request)

        return self._adminAuthRealm.getChildWithDefault(path, request)

    def getChild(self, path, request):
        """Get Child

        Allow .js files to bypass the authentication

        """
        if path.lower().endswith(b".js"):
            return self._fileUnderlayResource.getChildWithDefault(path, request)

        return self._adminAuthRealm.getChildWithDefault(path, request)


def startListening():
    from peek_logic_service.backend.AdminSiteResource import (
        setupAdminSite,
        adminSiteRoot,
    )
    from peek_logic_service.backend.auth.AdminAuthChecker import (
        AdminAuthChecker,
    )
    from peek_logic_service.backend.auth.AdminAuthRealm import AdminAuthRealm
    from peek_platform import PeekPlatformConfig

    from peek_logic_service.server.PlatformSiteResource import setupPlatformSite
    from peek_logic_service.server.PlatformSiteResource import platformSiteRoot

    setupPlatformSite()

    dataExchangeCfg = PeekPlatformConfig.config.dataExchangeHttpServer

    # generate diffie-hellman parameter for tls v1.2 if not exists
    dhPemFile = Path(PeekPlatformConfig.config._configPath) / Path(
        "./dhparam.pem"
    )
    dhPemFilePath = str(dhPemFile.absolute())

    if dataExchangeCfg.useSsl and not dhPemFile.exists():
        logger.info(
            "generating diffie-hellman parameter - this is one-off and "
            "may take a while"
        )
        generateDiffieHellmanParameterBytes(dhPemFilePath)

    setupSite(
        "Peek Platform Data Exchange",
        platformSiteRoot,
        portNum=dataExchangeCfg.sitePort,
        enableLogin=False,
        enableSsl=dataExchangeCfg.useSsl,
        sslBundleFilePath=dataExchangeCfg.sslBundleFilePath,
        sslEnableMutualTLS=dataExchangeCfg.sslEnableMutualTLS,
        sslMutualTLSCertificateAuthorityBundleFilePath=dataExchangeCfg.sslMutualTLSCertificateAuthorityBundleFilePath,
        sslMutualTLSTrustedPeerCertificateBundleFilePath=dataExchangeCfg.sslMutualTLSTrustedPeerCertificateBundleFilePath,
        dhParamPemFilePath=dhPemFilePath,
    )

    setupAdminSite()

    adminAuthChecker = AdminAuthChecker()
    adminAuthRealm = AdminAuthRealm(adminSiteRoot, adminAuthChecker)
    hackMixedAuthRealm = HACK_AllowJsFilesUnauthed(
        adminSiteRoot, adminAuthRealm
    )

    adminSiteCfg = PeekPlatformConfig.config.adminHttpServer
    setupSite(
        "Peek Admin",
        (
            adminSiteRoot
            if os.environ.get("PEEK_ADMIN_DISABLE_AUTH")
            else hackMixedAuthRealm
        ),
        portNum=adminSiteCfg.sitePort,
        enableLogin=False,
        redirectFromHttpPort=adminSiteCfg.redirectFromHttpPort,
        enableSsl=adminSiteCfg.useSsl,
        sslEnableMutualTLS=False,
        sslBundleFilePath=adminSiteCfg.sslBundleFilePath,
    )


def main():
    setupPlatform()
    from peek_platform import PeekPlatformConfig
    import peek_logic_service

    cfg = PeekPlatformConfig.config

    # Configure sqlalchemy
    setupDbConn(
        metadata=metadata,
        dbEngineArgs=cfg.dbEngineArgs,
        dbConnectString=cfg.dbConnectString,
        alembicDir=os.path.join(
            os.path.dirname(peek_logic_service.__file__), "alembic"
        ),
    )

    osMetrics = OsMetrics(
        cfg.platformMetricsPath, enabledPlugins=cfg.pluginsEnabled
    )

    # Force model migration
    from peek_logic_service.storage import dbConn

    dbConn.migrate()

    # Import remaining components
    importPackages()

    setupStorageInit()

    def stop():
        def stoppedSuccessfully(_):
            logger.info("Peek Logic is stopped")
            return None

        d = defer.succeed(None)
        d.addCallback(lambda _: osMetrics.stop())
        d.addCallback(
            lambda _: PeekPlatformConfig.pluginLoader.stopOptionalPlugins()
        )
        d.addCallback(
            lambda _: PeekPlatformConfig.pluginLoader.stopCorePlugins()
        )
        d.addCallback(
            lambda _: PeekPlatformConfig.pluginLoader.unloadOptionalPlugins()
        )
        d.addCallback(
            lambda _: PeekPlatformConfig.pluginLoader.unloadCorePlugins()
        )
        d.addErrback(vortexLogFailure, logger, consumeError=True)
        d.addCallback(stoppedSuccessfully)

        return d

    reactor.addSystemEventTrigger("before", "shutdown", stop)

    def start():
        def startedSuccessfully(_):
            logger.info(
                "Peek Logic is running, version=%s", cfg.platformVersion
            )
            return None

        d = defer.succeed(None)
        d.addCallback(lambda _: osMetrics.start())
        # Load all plugins
        d.addCallback(
            lambda _: PeekPlatformConfig.pluginLoader.loadCorePlugins()
        )
        d.addCallback(
            lambda _: PeekPlatformConfig.pluginLoader.loadOptionalPlugins()
        )
        d.addCallback(lambda _: startListening())
        d.addCallback(
            lambda _: PeekPlatformConfig.pluginLoader.startCorePlugins()
        )
        d.addCallback(
            lambda _: PeekPlatformConfig.pluginLoader.startOptionalPlugins()
        )
        d.addCallback(lambda _: _setupWorkerTaskRequestQueue())
        d.addCallback(
            lambda _: PeekPlatformConfig.pluginLoader.buildAdminSite()
        )
        d.addCallback(
            lambda _: PeekPlatformConfig.pluginLoader.buildAdminDocs()
        )

        d.addErrback(vortexLogFailure, logger, consumeError=True)
        d.addCallback(startedSuccessfully)

    reactor.callLater(0, start)
    reactor.run()


if __name__ == "__main__":
    main()
