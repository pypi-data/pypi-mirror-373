"""Base Agent implementation for shared components."""

import asyncio
import fnmatch
from typing import Callable, Iterable, Optional
from abc import ABC, abstractmethod
from typing import List, Dict, Any

from pydantic import functional_serializers

from pywen.config.config import Config
from pywen.core.client import LLMClient
from pywen.core.trajectory_recorder import TrajectoryRecorder
from pywen.core.tool_registry import ToolRegistry
from pywen.core.tool_executor import NonInteractiveToolExecutor
from pywen.utils.llm_basics import LLMMessage
from pywen.tools.mcp_tool import MCPServerManager, sync_mcp_server_tools_into_registry


class BaseAgent(ABC):
    """Base class providing shared components for all agent implementations."""
    
    def __init__(self, config: Config, cli_console=None):
        self.config = config
        self.cli_console = cli_console
        self.type = "BaseAgent"
        
        self.llm_client = LLMClient(config.model_config)

        self.conversation_history: List[LLMMessage] = []
        
        self.trajectory_recorder = TrajectoryRecorder()
        
        # Initialize tools with agent-specific configuration
        self.tool_registry = ToolRegistry()
        self.setup_tools()
        
        # Initialize tool executor
        self.tool_executor = NonInteractiveToolExecutor(self.tool_registry)

        self._closed = False 
        self._mcp_mgr = None
        self._mcp_init_lock = asyncio.Lock()

    def setup_tools(self):
        enabled_tools = self.get_enabled_tools()

        # Use the new ToolRegistry method to register tools by names
        registered_tools = self.tool_registry.register_tools_by_names(enabled_tools, self.config)

        # Report any tools that failed to register
        failed_tools = set(enabled_tools) - set(registered_tools)
        if failed_tools and self.cli_console:
            for tool_name in failed_tools:
                self.cli_console.print(f"Failed to register tool: {tool_name}", "yellow")


    async def setup_tools_mcp(self):
        """Setup tools based on agent configuration."""
        
        await self._ensure_mcp_synced()
    
    
    @abstractmethod
    def get_enabled_tools(self) -> List[str]:
        """Return list of enabled tool names for this agent."""
        pass
    
    def get_tool_configs(self) -> Dict[str, Dict[str, Any]]:
        """Return tool-specific configurations. Override if needed."""
        return {}
    
    def set_cli_console(self, console):
        """Set the CLI console for progress updates."""
        self.cli_console = console
    
    @abstractmethod
    async def run(self, user_message: str):
        """Run the agent - must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def _build_system_prompt(self) -> str:
        """Build system prompt with tool descriptions."""
        pass

    def reload_config(self):
        """重新加载配置"""
        try:
            # 从正确的模块导入配置加载函数
            from pywen.config.loader import load_config_from_file
            
            # 重新读取配置文件
            new_config = load_config_from_file("pywen_config.json")
            
            # 保存旧的会话ID
            old_session_id = getattr(self.config, 'session_id', None)
            
            # 更新配置
            self.config = new_config
            
            # 更新 max_iterations (如果 Agent 有这个属性)
            if hasattr(self, 'max_iterations'):
                self.max_iterations = new_config.max_iterations
            
            # 恢复会话ID
            if old_session_id:
                self.config.session_id = old_session_id
            
            # 重新初始化LLM客户端
            self.llm_client = LLMClient(new_config.model_config)
            
            # 重新初始化task continuation checker (如果存在)
            if hasattr(self, 'task_continuation_checker'):
                from pywen.agents.qwen.task_continuation_checker import TaskContinuationChecker
                self.task_continuation_checker = TaskContinuationChecker(self.llm_client, new_config)
            
            # 重建系统提示 (如果子类实现了该方法)
            if hasattr(self, '_build_system_prompt'):
                self.system_prompt = self._build_system_prompt()
            
            self.cli_console.print(f"Config reloaded - Model: {new_config.model_config.model}, Max Steps: {new_config.max_iterations}")
            return True
        except Exception as e:
            self.cli_console.print(f"Failed to reload config: {e}")
            return False

    def __make_include_predicate(self, patterns: Optional[Iterable[str]]) -> Optional[Callable[[str], bool]]:
        if not patterns:
            return None
        pats = [p for p in patterns if isinstance(p, str) and p.strip()]
        if not pats:
            return None
    
        def _pred(name: str) -> bool:
            return any(fnmatch.fnmatch(name, p) for p in pats)
        return _pred

    async def _ensure_mcp_synced(self):
        if self._mcp_mgr is not None:
            return

        async with self._mcp_init_lock:
            if self._mcp_mgr is not None:
                return

            mcp_cfg = self.config.mcp or []
            if not mcp_cfg.enabled:
                self._mcp_mgr = MCPServerManager()
                return

            servers = mcp_cfg.servers or []
            if not servers:
                self._mcp_mgr = MCPServerManager()
                return

            mgr = MCPServerManager()

            global_isolated = bool(mcp_cfg.isolated)

            for s in servers:
                if not s.enabled:
                    continue
                name = s.name 
                command = s.command or "npx"
                args = list(s.args or [])

                server_isolated = s.isolated and global_isolated
                if server_isolated and not any(a == "--isolated" for a in args):
                    args.append("--isolated")

                try:
                    await mgr.add_stdio_server(name, command, args)
                except Exception as e:
                    self.cli_console.print(f"[MCP] Failed to start server: {e}", "yellow")

            for s in servers:
                if not s.enabled:
                    continue
                name = s.name
                include_pred = self.__make_include_predicate(s.include)
                save_dir = s.save_images_dir

                await sync_mcp_server_tools_into_registry(
                    server_name=name,
                    manager=mgr,
                    tool_registry=self.tool_registry,
                    include=include_pred,
                    save_images_dir=save_dir,
                )

            self._mcp_mgr = mgr

    async def aclose(self):
        if self._closed:
            return 
        self._closed = True 
        if self._mcp_mgr:
            try:
                await self._mcp_mgr.close()
            finally:
                self._mcp_mgr = None

    async def __aenter__(self):
        await self._ensure_mcp_synced()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.aclose()

