import logging
from typing import Any

from twisted.internet.defer import inlineCallbacks
from txhttputil.site.FileUnderlayResource import FileUnderlayResource
from vortex.handler.TupleActionProcessorProxy import TupleActionProcessorProxy
from vortex.handler.TupleDataObservableProxyHandler import (
    TupleDataObservableProxyHandler,
)
from vortex.handler.TupleDataObserverClient import TupleDataObserverClient

from peek_core_docdb._private.PluginNames import docDbActionProcessorName
from peek_core_docdb._private.PluginNames import docDbFilt
from peek_core_docdb._private.PluginNames import docDbObservableName
from peek_core_docdb._private.client.TupleDataObservable import (
    makeClientTupleDataObservableHandler,
)
from peek_core_docdb._private.client.controller.DocumentCacheController import (
    DocumentCacheController,
)
from peek_core_docdb._private.client.handlers.DocumentCacheHandler import (
    DocumentCacheHandler,
)
from peek_core_docdb._private.storage.DeclarativeBase import loadStorageTuples
from peek_core_docdb._private.tuples import loadPrivateTuples
from peek_core_docdb.tuples import loadPublicTuples
from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_plugin_base.client.PluginClientEntryHookABC import (
    PluginClientEntryHookABC,
)

logger = logging.getLogger(__name__)


class ClientEntryHook(PluginClientEntryHookABC):
    def __init__(self, *args, **kwargs):
        """ " Constructor"""
        # Call the base classes constructor
        PluginClientEntryHookABC.__init__(self, *args, **kwargs)

        #: Loaded Objects, This is a list of all objects created when we start
        self._loadedObjects = []

    @classmethod
    def setupStaticWebResources(cls, platformApi: Any):
        from peek_plugin_base.client.PeekClientPlatformHookABC import (
            PeekClientPlatformHookABC,
        )

        assert isinstance(
            platformApi, PeekClientPlatformHookABC
        ), "We received the wrong platform API"

        from peek_abstract_chunked_index.private.client.controller.ACICacheControllerABC import (
            ACICacheControllerABC,
        )

        relativeDir = ACICacheControllerABC.appDownloadPluginDirRelativeDir()
        dirPath = platformApi.fileStorageDirectory / relativeDir
        dirPath.mkdir(exist_ok=True, parents=True)

        resource = FileUnderlayResource()
        resource.addFileSystemRoot(dirPath)

        platformApi.addFieldResource(relativeDir.encode(), resource)
        platformApi.addOfficeResource(relativeDir.encode(), resource)

    def load(self) -> None:
        """Load

        This will be called when the plugin is loaded,
         just after the db is migrated.
        Place any custom initialiastion steps here.

        """

        loadStorageTuples()

        loadPrivateTuples()
        loadPublicTuples()

        logger.debug("Loaded")

    @inlineCallbacks
    def start(self):
        """Load

        This will be called when the plugin is loaded, just after the db is migrated.
        Place any custom initialisation steps here.

        """

        # ----------------
        # Proxy actions back to the server, we don't process them at all
        self._loadedObjects.append(
            TupleActionProcessorProxy(
                tupleActionProcessorName=docDbActionProcessorName,
                proxyToVortexName=peekServerName,
                additionalFilt=docDbFilt,
            )
        )

        # ----------------
        # Provide the devices access to the servers observable
        tupleDataObservableProxyHandler = TupleDataObservableProxyHandler(
            observableName=docDbObservableName,
            proxyToVortexName=peekServerName,
            additionalFilt=docDbFilt,
            observerName="Proxy to devices",
        )
        self._loadedObjects.append(tupleDataObservableProxyHandler)

        # ----------------
        #: This is an observer for us (the client) to use to observe data
        # from the server
        serverTupleObserver = TupleDataObserverClient(
            observableName=docDbObservableName,
            destVortexName=peekServerName,
            additionalFilt=docDbFilt,
            observerName="Data for client",
        )
        self._loadedObjects.append(serverTupleObserver)

        # ----------------
        # Document Cache Controller

        documentCacheController = DocumentCacheController(
            self.platform.serviceId, self.platform.fileStorageDirectory
        )
        self._loadedObjects.append(documentCacheController)

        # ----------------
        # Document Cache Handler

        documentHandler = DocumentCacheHandler(
            cacheController=documentCacheController,
            clientId=self.platform.serviceId,
        )
        self._loadedObjects.append(documentHandler)

        # ----------------
        # Set the caches reference to the handler
        documentCacheController.setCacheHandler(documentHandler)

        # ----------------
        # Create the Tuple Observer
        makeClientTupleDataObservableHandler(
            tupleDataObservableProxyHandler, documentCacheController
        )

        # ----------------
        # Start the compiler controllers
        yield documentHandler.start()
        yield documentCacheController.start()

        logger.debug("Started")

    def stop(self):
        """Stop

        This method is called by the platform to tell the peek app to shutdown and stop
        everything it's doing
        """
        # Shutdown and dereference all objects we constructed when we started
        while self._loadedObjects:
            self._loadedObjects.pop().shutdown()

        logger.debug("Stopped")

    def unload(self):
        """Unload

        This method is called after stop is called, to unload any last resources
        before the PLUGIN is unlinked from the platform

        """
        logger.debug("Unloaded")
