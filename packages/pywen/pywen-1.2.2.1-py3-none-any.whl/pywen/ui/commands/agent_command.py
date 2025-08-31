"""Agent切换命令实现"""

from rich.console import Console
from .base_command import BaseCommand
from pywen.core.session_stats import session_stats
from typing import Dict, Any

# 可用agent配置
AVAILABLE_AGENTS = {
    "qwen": {
        "name": "🤖 Qwen Agent",
        "description": "General purpose conversational and coding assistant"
    },
    "research": {
        "name": "🔬 GeminiResearchDemo",
        "description": "Gemini open-sourced Multi-step research agent demo for comprehensive information gathering"
    },
    "claude": {
        "name": "🧠 Claude Code Agent",
        "description": "AI coding assistant with advanced file operations and project understanding"
    }
}

class AgentCommand(BaseCommand):
    def __init__(self):
        super().__init__("agent", "switch between different agents")
        self.console = Console()
    
    async def execute(self, context: Dict[str, Any], args: str) -> bool:
        """处理agent切换命令"""
        parts = args.strip().split() if args.strip() else []
        
        if len(parts) == 0:
            # 显示可用agent列表
            self._show_available_agents(context)
        elif len(parts) == 1:
            # 切换agent
            await self._switch_agent(context, parts[0])
        else:
            self.console.print("[red]Usage: /agent [agent_type][/red]")
            self.console.print("")
        
        return True
    
    def _show_available_agents(self, context: Dict[str, Any]):
        """显示可用agent列表"""
        current_agent = context.get('agent')
        current_agent_type = self._get_current_agent_type(current_agent)
        
        self.console.print("[bold]Available Agents:[/bold]")
        for agent_type, info in AVAILABLE_AGENTS.items():
            status = "[green]✓ Current[/green]" if agent_type == current_agent_type else ""
            self.console.print(f"  • [cyan]{agent_type}[/cyan]: {info['name']} - {info['description']} {status}")
        self.console.print(f"\n[dim]Usage: /agent <agent_type> to switch[/dim]")
    
    async def _switch_agent(self, context: Dict[str, Any], new_agent_type: str):
        """切换agent"""
        if new_agent_type not in AVAILABLE_AGENTS:
            self.console.print(f"[red]Unknown agent: {new_agent_type}[/red]")
            self.console.print(f"[dim]Available agents: {', '.join(AVAILABLE_AGENTS.keys())}[/dim]")
            return
        
        current_agent = context.get('agent')
        current_agent_type = self._get_current_agent_type(current_agent)
        
        if new_agent_type == current_agent_type:
            self.console.print(f"[yellow]Already using {AVAILABLE_AGENTS[current_agent_type]['name']}[/yellow]")
            return
        
        try:
            # 创建新agent
            new_agent = self._create_agent(context.get('config'), new_agent_type)
            new_agent.set_cli_console(context.get('console'))
            
            # 更新context中的agent
            context['agent'] = new_agent
            context['current_agent_type'] = new_agent_type

            # 更新session stats中的当前agent
            session_stats.set_current_agent(new_agent.type)

            agent_name = AVAILABLE_AGENTS[new_agent_type]["name"]
            self.console.print(f"[green]Switched to {agent_name}[/green]")
            
        except Exception as e:
            self.console.print(f"[red]Failed to switch agent: {e}[/red]")
    
    def _get_current_agent_type(self, agent) -> str:
        """获取当前agent类型"""
        if agent is None:
            return "unknown"

        # 动态导入避免循环依赖
        try:
            from pywen.agents.qwen.qwen_agent import QwenAgent
            from pywen.agents.research.google_research_agent import GeminiResearchDemo
            from pywen.agents.claudecode.claude_code_agent import ClaudeCodeAgent

            if isinstance(agent, QwenAgent):
                return "qwen"
            elif isinstance(agent, GeminiResearchDemo):
                return "research"
            elif isinstance(agent, ClaudeCodeAgent):
                return "claude"
        except ImportError:
            pass

        return "unknown"
    
    def _create_agent(self, config, agent_type: str):
        """创建agent实例"""
        if agent_type == "qwen":
            from pywen.agents.qwen.qwen_agent import QwenAgent
            return QwenAgent(config)
        elif agent_type == "research":
            from pywen.agents.research.google_research_agent import GeminiResearchDemo
            return GeminiResearchDemo(config)
        elif agent_type == "claude":
            from pywen.agents.claudecode.claude_code_agent import ClaudeCodeAgent
            return ClaudeCodeAgent(config)
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")