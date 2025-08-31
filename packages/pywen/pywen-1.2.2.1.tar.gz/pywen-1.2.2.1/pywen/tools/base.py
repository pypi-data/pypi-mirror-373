"""Enhanced base tool classes matching TypeScript version."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from enum import Enum
from pywen.utils.tool_basics import ToolCallConfirmationDetails, ToolResult


class ToolRiskLevel(Enum):
    """Tool risk levels for permission control."""
    SAFE = "safe"           # 只读操作，自动执行
    LOW = "low"             # 低风险操作，简单确认
    MEDIUM = "medium"       # 中等风险，详细确认
    HIGH = "high"           # 高风险操作，强制确认


class BaseTool(ABC):
    """Enhanced base class matching TypeScript BaseTool."""
    
    def __init__(
        self,
        name: str,
        display_name: str,
        description: str,
        parameter_schema: Dict[str, Any],
        is_output_markdown: bool = False,
        can_update_output: bool = False,
        config: Optional[Any] = None,
        risk_level: ToolRiskLevel = ToolRiskLevel.SAFE
    ):
        self.name = name
        self.display_name = display_name
        self.description = description
        self.parameter_schema = parameter_schema
        self.parameters = parameter_schema  # Add alias for backward compatibility
        self.is_output_markdown = is_output_markdown
        self.can_update_output = can_update_output
        self.config = config
        self.risk_level = risk_level
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool."""
        pass
    
    def validate_parameters(self, **kwargs) -> bool:
        """Validate tool parameters."""
        # Basic validation - can be overridden by subclasses
        return True
    
    def get_risk_level(self, **kwargs) -> ToolRiskLevel:
        """Get the risk level for this tool call."""
        return self.risk_level

    def is_risky(self, **kwargs) -> bool:
        """Determine if this tool call is risky and needs approval."""
        return self.get_risk_level(**kwargs) != ToolRiskLevel.SAFE

    async def get_confirmation_details(self, **kwargs) -> Optional[ToolCallConfirmationDetails]:
        """Get details for user confirmation."""
        risk_level = self.get_risk_level(**kwargs)
        if risk_level == ToolRiskLevel.SAFE:
            return None

        # Generate detailed confirmation message
        confirmation_message = await self._generate_confirmation_message(**kwargs)

        return ToolCallConfirmationDetails(
            type="exec",
            message=confirmation_message,
            is_risky=risk_level in [ToolRiskLevel.MEDIUM, ToolRiskLevel.HIGH],
            metadata={
                "tool_name": self.name,
                "parameters": kwargs,
                "risk_level": risk_level.value
            }
        )

    async def _generate_confirmation_message(self, **kwargs) -> str:
        """Generate detailed confirmation message. Override in subclasses."""
        return f"Execute {self.display_name}: {kwargs}"
    
    def get_function_declaration(self) -> Dict[str, Any]:
        """Get function declaration for LLM."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameter_schema
        }


# Alias for backward compatibility
Tool = BaseTool





