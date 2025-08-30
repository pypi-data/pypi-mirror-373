from typing import Type

from peek_plugin_base.agent.PluginAgentEntryHookABC import (
    PluginAgentEntryHookABC,
)
from peek_plugin_base.server.PluginLogicEntryHookABC import (
    PluginLogicEntryHookABC,
)

__version__ = '5.0.0'


def peekLogicEntryHook() -> Type[PluginLogicEntryHookABC]:
    from ._private.logic.LogicEntryHook import LogicEntryHook

    return LogicEntryHook


def peekAgentEntryHook() -> Type[PluginAgentEntryHookABC]:
    from ._private.agent.AgentEntryHook import AgentEntryHook

    return AgentEntryHook
