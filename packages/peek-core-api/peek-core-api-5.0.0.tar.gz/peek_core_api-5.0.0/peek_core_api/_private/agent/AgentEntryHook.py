import logging

from twisted.internet.defer import inlineCallbacks

from peek_core_api._private.agent.AgentTupleDataObserver import (
    makeTupleDataObserverClient,
)
from peek_core_api._private.agent.controller.OutboundMessageController import (
    OutboundMessageController,
)
from peek_plugin_base.agent.PluginAgentEntryHookABC import (
    PluginAgentEntryHookABC,
)

logger = logging.getLogger(__name__)


class AgentEntryHook(PluginAgentEntryHookABC):
    def __init__(self, *args, **kwargs):
        PluginAgentEntryHookABC.__init__(self, *args, **kwargs)

        self._loadedObjects = []
        self._outboundMessageController = None

    def load(self) -> None:
        # Load public tuples so they can be serialised in the agent
        # # loadPublicTuples()
        self._outboundMessageController = OutboundMessageController()
        self._loadedObjects.append(self._outboundMessageController)

        logicObserver = makeTupleDataObserverClient(
            self._outboundMessageController
        )
        self._loadedObjects.append(logicObserver)
        logger.debug("Loaded")

    @inlineCallbacks
    def start(self):
        yield self._outboundMessageController.start()
        logger.debug("Started")

    def stop(self):
        self._outboundMessageController = None
        while self._loadedObjects:
            self._loadedObjects.pop().shutdown()
        logger.debug("Stopped")

    def unload(self):
        logger.debug("Unloaded")
