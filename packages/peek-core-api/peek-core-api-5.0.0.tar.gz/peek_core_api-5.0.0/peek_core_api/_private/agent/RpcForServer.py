from datetime import datetime

from vortex.rpc.RPC import vortexRPC

from peek_core_api._private.PluginNames import apiFilt
from peek_plugin_base.PeekVortexUtil import peekAgentName


class RpcForServer:
    def __init__(self):
        pass

    def makeHandlers(self):
        yield self.sendHttpRequest.start(funcSelf=self)

    @vortexRPC(
        peekAgentName,
        additionalFilt=apiFilt,
        inlineCallbacks=True,
        timeoutSeconds=30.0,
    )
    def sendHttpRequest(
        self,
        url: str,
        requestBody: bytes,
        requestDate: datetime,
    ) -> CoreApiAgentHttpResultTuple:
        pass
        # twisted http client code here
