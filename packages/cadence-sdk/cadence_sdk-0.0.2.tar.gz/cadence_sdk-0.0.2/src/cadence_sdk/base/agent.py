"""Base agent interface for Cadence plugin agents."""

import logging
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.tools import Tool

from ..tools import AgentTool
from .metadata import PluginMetadata

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for plugin agents used as LangGraph nodes.

    This replaces the direct dependency on cadence.plugins.base.BasePluginAgent
    and provides the same interface through the SDK.

    Plugin agents are the core units of work in Cadence. Each agent:
    1. Provides tools for specific domain functionality
    2. Defines a system prompt for LLM behavior
    3. Can be bound to an LLM model with tools attached
    4. Creates a LangGraph node function for orchestration
    """

    def __init__(self, metadata: PluginMetadata):
        """Initialize the plugin agent.

        Args:
            metadata: Plugin metadata containing configuration
        """
        self.metadata = metadata
        self._tools = None
        self._bound_model = None
        self._initialized = False

    @property
    def max_tool_hops(self) -> int:
        """Get the maximum number of tool calls allowed for this agent.

        Can be configured via CADENCE_MAX_TOOL_HOPS environment variable.
        Defaults to 25 if not set.
        """
        return int(os.getenv("CADENCE_MAX_TOOL_HOPS", "25"))

    @abstractmethod
    def get_tools(self) -> List[AgentTool]:
        """Return the tools that this agent exposes.

        Tools are LangChain Tool instances that define the specific
        functionality this agent can perform (e.g., math operations,
        web search, database queries).

        Returns:
            List[Tool]: Tools to be bound to the LLM
        """
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt used by this agent.

        The system prompt defines the agent's behavior, role, and
        instructions for using its tools effectively.

        Returns:
            str: System prompt for the LLM
        """
        pass

    def bind_model(self, model: BaseChatModel, callbacks: List = None) -> BaseChatModel:
        """Bind the agent's tools to the provided chat model.

        This method is called by the Cadence core system to create
        a specialized model for this agent with its tools attached.

        Args:
            model: Base chat model to be specialized
            callbacks: Optional list of callbacks for tool tracking

        Returns:
            BaseChatModel: Tool-bound chat model
        """
        tools = self.get_tools()
        if callbacks:
            self._bound_model = model.bind_tools(tools, callbacks=callbacks)
        else:
            self._bound_model = model.bind_tools(tools)
        return self._bound_model

    @staticmethod
    def should_continue(state: Dict[str, Any]) -> str:
        """Decide whether to call tools or return to the coordinator.

        This method implements the standard Cadence pattern for agent
        decision-making in the LangGraph workflow.

        Args:
            state: Current graph state (expects a 'messages' list)

        Returns:
            str: "continue" to call tools, "back" to return to coordinator
        """
        last_msg = state.get("messages", [])[-1] if state.get("messages") else None
        if not last_msg:
            return "back"

        tool_calls = getattr(last_msg, "tool_calls", None)
        return "continue" if tool_calls else "back"

    def create_agent_node(self):
        """Create the callable used as this plugin's agent node.

        This method creates a LangGraph node function that:
        1. Applies the agent's system prompt
        2. Invokes the bound model
        3. Returns appropriate state updates

        Returns:
            callable: Function with signature fn(state: Dict[str, Any]) -> Dict[str, Any]
        """

        def agent_node(state):
            """Agent node function for LangGraph integration."""
            try:
                if not hasattr(self, "_bound_model") or self._bound_model is None:
                    raise RuntimeError(f"No bound model for agent {self.metadata.name}")

                if state.get("tool_hops", 0) >= self.max_tool_hops:
                    return {
                        "messages": [
                            AIMessage(
                                content=f"Maximum tool calls reached ({self.max_tool_hops} times). Cannot execute more operations."
                            )
                        ],
                        "tool_hops": state.get("tool_hops", 0),
                        "agent_hops": state.get("agent_hops", 0),
                        "current_agent": self.metadata.name,
                        "plugin_context": state.get("plugin_context", {}),
                    }

                system = SystemMessage(content=self.get_system_prompt())

                response = self._bound_model.invoke([system] + state["messages"])

                tool_calls = getattr(response, "tool_calls", [])

                if tool_calls:
                    logger.info(
                        f"Agent {self.metadata.name} generated {len(tool_calls)} tool calls. Tool execution will increment tool_hops."
                    )

                plugin_context = state.get("plugin_context", {})
                plugin_context["last_plugin"] = self.metadata.name
                if "routing_history" not in plugin_context:
                    plugin_context["routing_history"] = []
                plugin_context["routing_history"] = plugin_context["routing_history"] + [self.metadata.name]

                agent_hops = state.get("agent_hops", 0) + 1
                current_tool_hops = state.get("tool_hops", 0)

                logger.info(
                    f"Agent {self.metadata.name}: agent_hops {agent_hops - 1} -> {agent_hops}, preserving tool_hops {current_tool_hops}"
                )

                return {
                    "messages": [response],
                    "agent_hops": agent_hops,
                    "current_agent": self.metadata.name,
                    "plugin_context": plugin_context,
                    "tool_hops": current_tool_hops,
                }
            except Exception as e:
                raise RuntimeError(f"Error in agent node for {self.metadata.name}: {e}") from e

        return agent_node

    def initialize(self) -> None:
        """Initialize agent resources (e.g., cache tools).

        Override this method to perform any setup required by your agent,
        such as loading models, connecting to databases, etc.
        """
        self._tools = self.get_tools()
        self._initialized = True

    def cleanup(self) -> None:
        """Cleanup agent resources.

        Override this method to clean up resources when the agent
        is being shut down or reloaded.
        """
        pass
