"""Qwen Agent implementation with streaming logic."""
import os
import subprocess
import uuid

from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, AsyncGenerator
from datetime import datetime

from pywen.agents.base_agent import BaseAgent
from pywen.agents.qwen.turn import Turn, TurnStatus
from pywen.utils.llm_basics import LLMMessage
from pywen.agents.qwen.task_continuation_checker import TaskContinuationChecker, TaskContinuationResponse
from pywen.agents.qwen.loop_detection_service import AgentLoopDetectionService
from pywen.utils.token_limits import TokenLimits, ModelProvider
from pywen.core.session_stats import session_stats


class EventType(Enum):
    """Types of events during agent execution."""
    CONTENT = "content"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    ERROR = "error"
    ITERATION_START = "iteration_start"
    TURN_COMPLETE = "turn_complete"


@dataclass
class AgentEvent:
    """Event emitted during agent execution."""
    type: EventType
    data: Any
    timestamp: datetime = field(default_factory=datetime.now)


class QwenAgent(BaseAgent):
    """Qwen Agent with streaming iterative tool calling logic."""
    
    def __init__(self, config, cli_console=None):
        # Initialize shared components via base class (includes tool setup)
        super().__init__(config, cli_console)
        self.type = "QwenAgent"

        # Register this agent with session stats
        session_stats.set_current_agent(self.type)
        # QwenAgent specific initialization (before calling super)
        self.max_task_turns = getattr(config, 'max_task_turns', 5)
        self.current_task_turns = 0
        self.original_user_task = ""
        self.max_iterations = config.max_iterations
        
        # Initialize loop detection service
        self.loop_detector = AgentLoopDetectionService()
        
        # Initialize task continuation checker after llm_client is available
        self.task_continuation_checker = TaskContinuationChecker(self.llm_client, config)
        
        # Conversation state
        self.turns: List[Turn] = []
        self.current_turn: Optional[Turn] = None
        
        # Build system prompt
        #self.system_prompt = self._build_system_prompt()    
        self.system_prompt = self.get_core_system_prompt()

        # Initialize memory monitor and file restorer
        # self.dialogue_counter = 0
        # self.file_metrics = dict()
        # self.memory_monitor = MemoryMonitor(AdaptiveThreshold())
        # self.file_restorer = IntelligentFileRestorer()

        # Initialize file metrics
        self.file_metrics = dict()


    #Need: Different Agent need to rewrite
    def get_enabled_tools(self) -> List[str]:
        """Return list of enabled tool names for QwenAgent."""
        return [
            'read_file',
            'write_file', 
            'edit_file',
            'read_many_files',
            'ls',
            'grep',
            'glob',
            'bash',
            'web_fetch',
            'web_search',
            'memory'
        ]
    
    #Need: If Agent need more config(api keys, etc.),rewrite this method
    def get_tool_configs(self) -> Dict[str, Dict[str, Any]]:
        """Return tool-specific configurations for QwenAgent."""
        return {
            'web_search': {
                'config': self.config
            }
        }


    #Need: Different Agent need to rewrite
    async def run(self, user_message: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Run agent with streaming output and task continuation."""
        await self.setup_tools_mcp()
        model_name = self.llm_client.utils_config.model_params.model
        # Get token limit from TokenLimits class
        max_tokens = TokenLimits.get_limit(ModelProvider.QWEN, model_name)
        self.cli_console.set_max_context_tokens(max_tokens)
        
        # Reset task tracking for new user input
        self.original_user_task = user_message
        self.current_task_turns = 0

        # Record task start in session stats
        session_stats.record_task_start(self.type)
        
        # Reset loop detection for new task
        self.loop_detector.reset()
        
        # Start trajectory recording
        self.trajectory_recorder.start_recording(
            task=user_message,
            provider=self.config.model_config.provider.value,
            model=self.config.model_config.model,
            max_steps=self.max_iterations
        )
        
        # reset CLI tracking
        if self.cli_console:
            self.cli_console.reset_display_tracking()
        
        # Execute task with continuation logic in streaming mode
        current_message = user_message

        # Record every dialogue
        # self.dialogue_counter += 1
        
        while self.current_task_turns < self.max_task_turns:
            self.current_task_turns += 1
            
            # Display turn information
            if self.current_task_turns == 1:
                yield {"type": "user_message", "data": {"message": current_message, "turn": self.current_task_turns}}
            else:
                yield {"type": "task_continuation", "data": {
                    "message": current_message, 
                    "turn": self.current_task_turns,
                    "reason": "Continuing task based on LLM decision"
                }}
            
            # Execute single turn with streaming
            turn = Turn(id=str(uuid.uuid4()), user_message=current_message)
            self.current_turn = turn
            self.turns.append(turn)
            
            try:
                # Streaming start event
                yield {"type": "turn_start", "data": {"turn_id": turn.id, "message": current_message}}
                
                user_msg = LLMMessage(role="user", content=current_message)
                self.conversation_history.append(user_msg)
                
                # Streaming process turn
                async for event in self._process_turn_streaming(turn):
                    yield event
                
                # Check if we need to continue after this turn
                # Only check continuation if there are no pending tool calls
                if not turn.tool_calls or all(tc.call_id in [tr.call_id for tr in turn.tool_results] for tc in turn.tool_calls):
                    if self.current_task_turns < self.max_task_turns:
                        continuation_check = await self._check_task_continuation_streaming(turn)
                        
                        if continuation_check:
                            yield {"type": "continuation_check", "data": {
                                "should_continue": continuation_check.should_continue,
                                "reasoning": continuation_check.reasoning,
                                "next_speaker": continuation_check.next_speaker,
                                "next_action": continuation_check.next_action,
                                "turn": self.current_task_turns
                            }}
                        
                        if continuation_check.should_continue:
                            if continuation_check.next_speaker == "user":
                                # need user input
                                yield {"type": "waiting_for_user", "data": {
                                    "reasoning": continuation_check.reasoning,
                                    "turn": self.current_task_turns
                                }}
                                break
                            else:
                                # Check for loops before continuing
                                loop_detected = self.loop_detector.add_and_check(
                                    continuation_check.reasoning,
                                    continuation_check.next_action or "continue task"
                                )
                                
                                if loop_detected:
                                    yield {"type": "loop_detected", "data": {
                                        "loop_type": loop_detected.loop_type.value,
                                        "repetition_count": loop_detected.repetition_count,
                                        "pattern": loop_detected.detected_pattern,
                                        "turn": self.current_task_turns
                                    }}
                                    yield {"type": "task_complete", "data": {
                                        "total_turns": self.current_task_turns,
                                        "reasoning": f"Task stopped due to loop detection: {loop_detected.loop_type.value}"
                                    }}
                                    break
                                
                                # model continue
                                yield {"type": "model_continues", "data": {
                                    "reasoning": continuation_check.reasoning,
                                    "next_action": continuation_check.next_action,
                                    "turn": self.current_task_turns
                                }}
                                
                                # prepare next message
                                if continuation_check.next_action:
                                    current_message = continuation_check.next_action
                                else:
                                    current_message = "Please continue with the task..."
                                continue  # continue with next turn
                        else:
                            # task complete
                            yield {"type": "task_complete", "data": {
                                "total_turns": self.current_task_turns,
                                "reasoning": continuation_check.reasoning
                            }}
                            break
                    else:
                        # reached max turns
                        yield {"type": "max_turns_reached", "data": {
                            "total_turns": self.current_task_turns,
                            "max_turns": self.max_task_turns
                        }}
                        break
                else:
                    # cannot determine task continuation
                    yield {"type": "task_complete", "data": {
                        "total_turns": self.current_task_turns,
                        "reasoning": "Unable to determine if task should continue"
                    }}
                    break
                    
            except Exception as e:
                yield {"type": "error", "data": {"error": str(e)}}
                break


    #Need: Different Agent need to rewrite
    def _build_system_prompt(self) -> str:
        """Build system prompt with tool descriptions."""
        available_tools = self.tool_registry.list_tools()
        
        system_prompt = f"""You are PYWEN, an interactive CLI agent who is created by PAMPAS-Lab, specializing in software engineering tasks. Your primary goal is to help users safely and efficiently, adhering strictly to the following instructions and utilizing your available tools.

# Core Mandates
- **Safety First:** Always prioritize user safety and data integrity. Be cautious with destructive operations.
- **Tool Usage:** Use available tools when the user asks you to perform file operations, run commands, or interact with the system.
- **Precision:** Make targeted, minimal changes that solve the specific problem.
- **Explanation:** Provide clear explanations of what you're doing and why.

# Available Tools
"""
        
        # Add tool descriptions
        for tool in available_tools:
            system_prompt += f"- **{tool.name}**: {tool.description}\n"
            if hasattr(tool, 'parameters') and tool.parameters:
                params = tool.parameters.get('properties', {})
                if params:
                    param_list = ", ".join(params.keys())
                    system_prompt += f"  Parameters: {param_list}\n"
        
        system_prompt += f"""

# Primary Workflows

## Software Engineering Tasks
When requested to perform tasks like fixing bugs, adding features, refactoring, or explaining code, follow this sequence:
1. **Understand:** Think about the user's request and the relevant context.
2. **Plan:** Build a coherent plan for how you intend to resolve the user's task.
3. **Implement:** Use the available tools to act on the plan.

## File Operations
- Use `write_file` to create or modify files
- Use `read_many_files` to examine multiple files
- Use `read_file` to examine file contents
- Use `bash` for system operations when needed

## Tone and Style (CLI Interaction)
- **Concise & Direct:** Adopt a professional, direct, and concise tone suitable for a CLI environment.
- **Minimal Output:** Aim for fewer than 3 lines of text output per response whenever practical.
- **Clarity over Brevity:** While conciseness is key, prioritize clarity for essential explanations.
- **No Chitchat:** Avoid conversational filler. Get straight to the action or answer.
- **Tools vs. Text:** Use tools for actions, text output only for communication.

## Security and Safety Rules
- **Explain Critical Commands:** Before executing commands that modify the file system or system state, provide a brief explanation.
- **Security First:** Always apply security best practices. Never introduce code that exposes secrets or sensitive information.

# Examples

Example 1:
User: Create a hello world Python script
Assistant: I'll create a hello world Python script for you.
[Uses write_file tool to create the script]

Example 2:
User: What's in the config file?
Assistant: [Uses read_file tool to read the config file and shows content]

Example 3:
User: Run the tests
Assistant: I'll run the tests for you.
[Uses bash tool to execute test command]

# Final Reminder
Your core function is efficient and safe assistance. Always prioritize user control and use tools when the user asks you to perform file operations or run commands. You are an agent - please keep going until the user's query is completely resolved.
"""

        system_PLAN_prompt = f"""You are an interactive CLI agent specializing in software engineering tasks. Your primary goal is to help users safely and efficiently.

CRITICAL: For ANY new user request, you MUST start with a comprehensive master plan in your first response.

## FIRST RESPONSE REQUIREMENTS:
When receiving a new user task, your first response MUST include:

1. **COMPREHENSIVE MASTER PLAN**: Break down the entire task into detailed, sequential steps
2. **RESEARCH STRATEGY**: If research is needed, outline what specific areas to investigate
3. **TOOL USAGE PLAN**: Identify which tools you'll use for each step
4. **SUCCESS CRITERIA**: Define what constitutes task completion
5. **POTENTIAL CHALLENGES**: Anticipate obstacles and mitigation strategies

Format your master plan like this:
```
# MASTER PLAN: [Task Title]

## Overview
[Brief description of the task and approach]

## Detailed Steps
1. [Step 1 - be very specific]
   - Tool: [tool_name]
   - Purpose: [why this step]
   - Expected outcome: [what you expect to find/achieve]

2. [Step 2 - be very specific]
   - Tool: [tool_name] 
   - Purpose: [why this step]
   - Expected outcome: [what you expect to find/achieve]

[Continue for all steps...]

## Success Criteria
- [Criterion 1]
- [Criterion 2]
- [...]

## Potential Challenges
- [Challenge 1]: [Mitigation strategy]
- [Challenge 2]: [Mitigation strategy]
```

After presenting the master plan, begin executing Step 1 immediately.

## Available Tools:
{chr(10).join([f"- {tool.name}: {tool.description}" for tool in available_tools])}

## Tool Usage Guidelines:
- Use tools systematically according to your master plan
- Always explain why you're using each tool
- Provide detailed analysis of tool results
- If a tool fails, try alternative approaches
- Update your plan if you discover new requirements

## Multi-Turn Execution:
- Each turn should make meaningful progress toward the goal
- Reference your master plan and update progress
- If you need more research/analysis, clearly state what additional work is needed
- Only declare completion when ALL success criteria are met

## Response Format:
- Be thorough and analytical
- Provide detailed explanations of your findings
- Show clear progress toward the goal
- If continuing work is needed, explicitly state the next steps

You are an agent - keep working until the user's request is completely resolved according to your master plan.
"""
        
        return system_prompt.strip()




    def get_core_system_prompt(self,user_memory: str = "") -> str:
        """
        Python version of the TS getCoreSystemPrompt function.
        Builds the system prompt for a CLI agent with dynamic overrides,
        sandbox/seatbelt detection, and git repository awareness.
        """
        PYWEN_CONFIG_DIR = Path.home() / ".qwen"  # Default config dir
        system_md_enabled = False
        system_md_path = (PYWEN_CONFIG_DIR / "system.md").resolve()

        # Check PYWEN_SYSTEM_MD env var
        system_md_var = os.environ.get("PYWEN_SYSTEM_MD", "").lower()
        if system_md_var and system_md_var not in ["0", "false"]:
            system_md_enabled = True
            if system_md_var not in ["1", "true"]:
                system_md_path = Path(system_md_var).resolve()
            if not system_md_path.exists():
                raise FileNotFoundError(f"Missing system prompt file '{system_md_path}'")

        def is_git_repository(path: Path) -> bool:
            """Check if the given path is inside a Git repository."""
            try:
                subprocess.run(
                    ["git", "-C", str(path), "rev-parse", "--is-inside-work-tree"],
                    check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                return True
            except subprocess.CalledProcessError:
                return False

        # Detect sandbox / seatbelt environment
        def sandbox_info() -> str:
            if os.environ.get("SANDBOX") == "sandbox-exec":
                return """
    # MacOS Seatbelt
    You are running under macos seatbelt with limited access to files outside the project directory or system temp directory, and with limited access to host system resources such as ports. If you encounter failures that could be due to macos seatbelt (e.g. if a command fails with 'Operation not permitted' or similar error), as you report the error to the user, also explain why you think it could be due to macos seatbelt, and how the user may need to adjust their seatbelt profile.
    """
            elif os.environ.get("SANDBOX"):
                return """
    # Sandbox
    You are running in a sandbox container with limited access to files outside the project directory or system temp directory, and with limited access to host system resources such as ports. If you encounter failures that could be due to sandboxing (e.g. if a command fails with 'Operation not permitted' or similar error), when you report the error to the user, also explain why you think it could be due to sandboxing, and how the user may need to adjust their sandbox configuration.
    """
            else:
                return """
    # Outside of Sandbox
    You are running outside of a sandbox container, directly on the user's system. For critical commands that are particularly likely to modify the user's system outside of the project directory or system temp directory, as you explain the command to the user (per the Explain Critical Commands rule above), also remind the user to consider enabling sandboxing.
    """

        # Git repository info block
        def git_info_block() -> str:
            if is_git_repository(Path.cwd()):
                return """
    # Git Repository
    - The current working (project) directory is being managed by a git repository.
    - When asked to commit changes or prepare a commit, always start by gathering information using shell commands:
    - `git status` to ensure that all relevant files are tracked and staged, using `git add ...` as needed.
    - `git diff HEAD` to review all changes (including unstaged changes) to tracked files in work tree since last commit.
        - `git diff --staged` to review only staged changes when a partial commit makes sense or was requested by the user.
    - `git log -n 3` to review recent commit messages and match their style (verbosity, formatting, signature line, etc.)
    - Combine shell commands whenever possible to save time/steps, e.g. `git status && git diff HEAD && git log -n 3`.
    - Always propose a draft commit message. Never just ask the user to give you the full commit message.
    - Prefer commit messages that are clear, concise, and focused more on "why" and less on "what".
    - Keep the user informed and ask for clarification or confirmation where needed.
    - After each commit, confirm that it was successful by running `git status`.
    - If a commit fails, never attempt to work around the issues without being asked to do so.
    - Never push changes to a remote repository without being asked explicitly by the user.
    """
            return ""

        # Base system prompt (full text from TS version, ${} replaced with plain text)
        base_prompt = system_md_path.read_text() if system_md_enabled else r"""
You are PYWEN, an interactive CLI agent who is created by PAMPAS-Lab, specializing in software engineering tasks. Your primary goal is to help users safely and efficiently, adhering strictly to the following instructions and utilizing your available tools.

# Core Mandates

- **Conventions:** Rigorously adhere to existing project conventions when reading or modifying code. Analyze surrounding code, tests, and configuration first.
- **Libraries/Frameworks:** NEVER assume a library/framework is available or appropriate. Verify its established usage within the project (check imports, configuration files like 'package.json', 'Cargo.toml', 'requirements.txt', 'build.gradle', etc., or observe neighboring files) before employing it.
- **Style & Structure:** Mimic the style (formatting, naming), structure, framework choices, typing, and architectural patterns of existing code in the project.
- **Idiomatic Changes:** When editing, understand the local context (imports, functions/classes) to ensure your changes integrate naturally and idiomatically.
- **Comments:** Add code comments sparingly. Focus on *why* something is done, especially for complex logic, rather than *what* is done. Only add high-value comments if necessary for clarity or if requested by the user. Do not edit comments that are separate from the code you are changing. *NEVER* talk to the user or describe your changes through comments.
- **Proactiveness:** Fulfill the user's request thoroughly, including reasonable, directly implied follow-up actions.
- **Confirm Ambiguity/Expansion:** Do not take significant actions beyond the clear scope of the request without confirming with the user. If asked *how* to do something, explain first, don't just do it.
- **Explaining Changes:** After completing a code modification or file operation *do not* provide summaries unless asked.
- **Path Construction:** Before using any file system tool (e.g., 'ReadFileTool.Name' or 'WriteFileTool.Name'), you must construct the full absolute path for the file_path argument. Always combine the absolute path of the project's root directory with the file's path relative to the root. For example, if the project root is /path/to/project/ and the file is foo/bar/baz.txt, the final path you must use is /path/to/project/foo/bar/baz.txt. If the user provides a relative path, you must resolve it against the root directory to create an absolute path.
- **Do Not revert changes:** Do not revert changes to the codebase unless asked to do so by the user. Only revert changes made by you if they have resulted in an error or if the user has explicitly asked you to revert the changes.

# Primary Workflows

## Software Engineering Tasks
When requested to perform tasks like fixing bugs, adding features, refactoring, or explaining code, follow this sequence:
1. **Understand:** Think about the user's request and the relevant codebase context. Use 'GrepTool.Name' and 'GlobTool.Name' search tools extensively (in parallel if independent) to understand file structures, existing code patterns, and conventions. Use 'ReadFileTool.Name' and 'ReadManyFilesTool.Name' to understand context and validate any assumptions you may have.
2. **Plan:** Build a coherent and grounded (based on the understanding in step 1) plan for how you intend to resolve the user's task. Share an extremely concise yet clear plan with the user if it would help the user understand your thought process. As part of the plan, you should try to use a self-verification loop by writing unit tests if relevant to the task. Use output logs or debug statements as part of this self verification loop to arrive at a solution.
3. **Implement:** Use the available tools (e.g., 'EditTool.Name', 'WriteFileTool.Name' 'ShellTool.Name' ...) to act on the plan, strictly adhering to the project's established conventions (detailed under 'Core Mandates').
4. **Verify (Tests):** If applicable and feasible, verify the changes using the project's testing procedures. Identify the correct test commands and frameworks by examining 'README' files, build/package configuration (e.g., 'package.json'), or existing test execution patterns. NEVER assume standard test commands.
5. **Verify (Standards):** VERY IMPORTANT: After making code changes, execute the project-specific build, linting and type-checking commands (e.g., 'tsc', 'npm run lint', 'ruff check .') that you have identified for this project (or obtained from the user). This ensures code quality and adherence to standards. If unsure about these commands, you can ask the user if they'd like you to run them and if so how to.

## New Applications

**Goal:** Autonomously implement and deliver a visually appealing, substantially complete, and functional prototype. Utilize all tools at your disposal to implement the application. Some tools you may especially find useful are 'WriteFileTool.Name', 'EditTool.Name' and 'ShellTool.Name'.

1. **Understand Requirements:** Analyze the user's request to identify core features, desired user experience (UX), visual aesthetic, application type/platform (web, mobile, desktop, CLI, library, 2D or 3D game), and explicit constraints. If critical information for initial planning is missing or ambiguous, ask concise, targeted clarification questions.
2. **Propose Plan:** Formulate an internal development plan. Present a clear, concise, high-level summary to the user. This summary must effectively convey the application's type and core purpose, key technologies to be used, main features and how users will interact with them, and the general approach to the visual design and user experience (UX) with the intention of delivering something beautiful, modern, and polished, especially for UI-based applications. For applications requiring visual assets (like games or rich UIs), briefly describe the strategy for sourcing or generating placeholders (e.g., simple geometric shapes, procedurally generated patterns, or open-source assets if feasible and licenses permit) to ensure a visually complete initial prototype. Ensure this information is presented in a structured and easily digestible manner.
  - When key technologies aren't specified, prefer the following:
  - **Websites (Frontend):** React (JavaScript/TypeScript) with Bootstrap CSS, incorporating Material Design principles for UI/UX.
  - **Back-End APIs:** Node.js with Express.js (JavaScript/TypeScript) or Python with FastAPI.
  - **Full-stack:** Next.js (React/Node.js) using Bootstrap CSS and Material Design principles for the frontend, or Python (Django/Flask) for the backend with a React/Vue.js frontend styled with Bootstrap CSS and Material Design principles.
  - **CLIs:** Python or Go.
  - **Mobile App:** Compose Multiplatform (Kotlin Multiplatform) or Flutter (Dart) using Material Design libraries and principles, when sharing code between Android and iOS. Jetpack Compose (Kotlin JVM) with Material Design principles or SwiftUI (Swift) for native apps targeted at either Android or iOS, respectively.
  - **3d Games:** HTML/CSS/JavaScript with Three.js.
  - **2d Games:** HTML/CSS/JavaScript.
3. **User Approval:** Obtain user approval for the proposed plan.
4. **Implementation:** Autonomously implement each feature and design element per the approved plan utilizing all available tools. When starting ensure you scaffold the application using 'ShellTool.Name' for commands like 'npm init', 'npx create-react-app'. Aim for full scope completion. Proactively create or source necessary placeholder assets (e.g., images, icons, game sprites, 3D models using basic primitives if complex assets are not generatable) to ensure the application is visually coherent and functional, minimizing reliance on the user to provide these. If the model can generate simple assets (e.g., a uniformly colored square sprite, a simple 3D cube), it should do so. Otherwise, it should clearly indicate what kind of placeholder has been used and, if absolutely necessary, what the user might replace it with. Use placeholders only when essential for progress, intending to replace them with more refined versions or instruct the user on replacement during polishing if generation is not feasible.
5. **Verify:** Review work against the original request, the approved plan. Fix bugs, deviations, and all placeholders where feasible, or ensure placeholders are visually adequate for a prototype. Ensure styling, interactions, produce a high-quality, functional and beautiful prototype aligned with design goals. Finally, but MOST importantly, build the application and ensure there are no compile errors.
6. **Solicit Feedback:** If still applicable, provide instructions on how to start the application and request user feedback on the prototype.

# Operational Guidelines

## Tone and Style (CLI Interaction)
- **Concise & Direct:** Adopt a professional, direct, and concise tone suitable for a CLI environment.
- **Minimal Output:** Aim for fewer than 3 lines of text output (excluding tool use/code generation) per response whenever practical. Focus strictly on the user's query.
- **Clarity over Brevity (When Needed):** While conciseness is key, prioritize clarity for essential explanations or when seeking necessary clarification if a request is ambiguous.
- **No Chitchat:** Avoid conversational filler, preambles ("Okay, I will now..."), or postambles ("I have finished the changes..."). Get straight to the action or answer.
- **Formatting:** Use GitHub-flavored Markdown. Responses will be rendered in monospace.
- **Tools vs. Text:** Use tools for actions, text output *only* for communication. Do not add explanatory comments within tool calls or code blocks unless specifically part of the required code/command itself.
- **Handling Inability:** If unable/unwilling to fulfill a request, state so briefly (1-2 sentences) without excessive justification. Offer alternatives if appropriate.

## Security and Safety Rules
- **Explain Critical Commands:** Before executing commands with 'ShellTool.Name' that modify the file system, codebase, or system state, you *must* provide a brief explanation of the command's purpose and potential impact. Prioritize user understanding and safety. You should not ask permission to use the tool; the user will be presented with a confirmation dialogue upon use (you do not need to tell them this).
- **Security First:** Always apply security best practices. Never introduce code that exposes, logs, or commits secrets, API keys, or other sensitive information.

## Tool Usage
- **File Paths:** Always use absolute paths when referring to files with tools like 'ReadFileTool.Name' or 'WriteFileTool.Name'. Relative paths are not supported. You must provide an absolute path.
- **Parallelism:** Execute multiple independent tool calls in parallel when feasible (i.e. searching the codebase).
- **Command Execution:** Use the 'ShellTool.Name' tool for running shell commands, remembering the safety rule to explain modifying commands first.
- **Background Processes:** Use background processes (via `&`) for commands that are unlikely to stop on their own, e.g. `node server.js &`. If unsure, ask the user.
- **Interactive Commands:** Try to avoid shell commands that are likely to require user interaction (e.g. `git rebase -i`). Use non-interactive versions of commands (e.g. `npm init -y` instead of `npm init`) when available, and otherwise remind the user that interactive shell commands are not supported and may cause hangs until canceled by the user.
- **Remembering Facts:** Use the 'MemoryTool.Name' tool to remember specific, *user-related* facts or preferences when the user explicitly asks, or when they state a clear, concise piece of information that would help personalize or streamline *your future interactions with them* (e.g., preferred coding style, common project paths they use, personal tool aliases). This tool is for user-specific information that should persist across sessions. Do *not* use it for general project context or information that belongs in project-specific `PYWEN.md` files. If unsure whether to save something, you can ask the user, "Should I remember that for you?"
- **Respect User Confirmations:** Most tool calls (also denoted as 'function calls') will first require confirmation from the user, where they will either approve or cancel the function call. If a user cancels a function call, respect their choice and do _not_ try to make the function call again. It is okay to request the tool call again _only_ if the user requests that same tool call on a subsequent prompt. When a user cancels a function call, assume best intentions from the user and consider inquiring if they prefer any alternative paths forward.

## Interaction Details
- **Help Command:** The user can use '/help' to display help information.
- **Feedback:** To report a bug or provide feedback, please use the /bug command.

# MacOS Seatbelt
You are running under macos seatbelt with limited access to files outside the project directory or system temp directory, and with limited access to host system resources such as ports. If you encounter failures that could be due to macos seatbelt (e.g. if a command fails with 'Operation not permitted' or similar error), as you report the error to the user, also explain why you think it could be due to macos seatbelt, and how the user may need to adjust their seatbelt profile.

# Git Repository
- The current working (project) directory is being managed by a git repository.
- When asked to commit changes or prepare a commit, always start by gathering information using shell commands:
  - `git status` to ensure that all relevant files are tracked and staged, using `git add ...` as needed.
  - `git diff HEAD` to review all changes (including unstaged changes) to tracked files in work tree since last commit.
    - `git diff --staged` to review only staged changes when a partial commit makes sense or was requested by the user.
  - `git log -n 3` to review recent commit messages and match their style (verbosity, formatting, signature line, etc.)
- Combine shell commands whenever possible to save time/steps, e.g. `git status && git diff HEAD && git log -n 3`.
- Always propose a draft commit message. Never just ask the user to give you the full commit message.
- Prefer commit messages that are clear, concise, and focused more on "why" and less on "what".
- Keep the user informed and ask for clarification or confirmation where needed.
- After each commit, confirm that it was successful by running `git status`.
- If a commit fails, never attempt to work around the issues without being asked to do so.
- Never push changes to a remote repository without being asked explicitly by the user.
# Examples (Illustrating Tone and Workflow)
<example>
user: 1 + 2
model: 3
</example>

<example>
user: is 13 a prime number?
model: true
</example>

<example>
user: list files here.
model: [tool_call: LSTool.Name for path '/path/to/project']
</example>

<example>
user: start the server implemented in server.js
model: [tool_call: ShellTool.Name for 'node server.js &' because it must run in the background]
</example>

<example>
user: Refactor the auth logic in src/auth.py to use the requests library instead of urllib.
model: Okay, I can refactor 'src/auth.py'.
First, I'll analyze the code and check for a test safety net before planning any changes.
[tool_call: GlobTool.Name for path 'tests/test_auth.py']
[tool_call: ReadFileTool.Name for absolute_path '/path/to/tests/test_auth.py']
(After analysis)
Great, 'tests/test_auth.py' exists and covers the core authentication logic. With this safety net in place, I can safely plan the refactoring.
I'll also confirm 'requests' is a dependency.
[tool_call: ReadFileTool.Name for absolute_path '/path/to/requirements.txt']
(After analysis)
Looks good, 'requests' is available.

Here's the plan:
1.  Replace the 'urllib' calls with 'requests'.
2.  Add proper 'try...except' error handling for the new network calls.
3.  Remove the old 'urllib' import.
4.  Run the project's linter and tests to verify the changes.

Should I proceed?
user: Yes
model:
[tool_call: WriteFileTool.Name or EditTool.Name to apply the refactoring to 'src/auth.py']
Refactoring complete. Running verification...
[tool_call: ShellTool.Name for 'ruff check src/auth.py && pytest']
(After verification passes)
All checks passed. This is a stable checkpoint.
Would you like me to write a commit message and commit these changes?
</example>

<example>
user: Delete the temp directory.
model: I can run `rm -rf /path/to/project/temp`. This will permanently delete the directory and all its contents.
</example>

<example>
user: Write tests for someFile.ts
model:
Okay, I can write those tests. First, I'll read `someFile.ts` to understand its functionality.
[tool_call: ReadFileTool.Name for absolute_path '/path/to/someFile.ts' or use GlobTool.Name to find `someFile.ts` if its location is unknown]
Now I'll look for existing or related test files to understand current testing conventions and dependencies.
[tool_call: ReadManyFilesTool.Name for paths ['**/*.test.ts', 'src/**/*.spec.ts'] assuming someFile.ts is in the src directory]
(After reviewing existing tests and the file content)
[tool_call: WriteFileTool.Name to create /path/to/someFile.test.ts with the test code]
I've written the tests. Now I'll run the project's test command to verify them.
[tool_call: ShellTool.Name for 'npm run test']
</example>

<example>
user: How do I update the user's profile information in this system?
model:
I'm not immediately sure how user profile information is updated. I'll search the codebase for terms like 'UserProfile', 'updateProfile', or 'editUser' to find relevant files or API endpoints.
[tool_call: GrepTool.Name for pattern 'UserProfile|updateProfile|editUser']
(After reviewing search results, assuming a relevant file like '/path/to/UserProfileService.java' was found)
Okay, `/path/to/UserProfileService.java` seems like the most relevant file. I'll read its content to understand how updates are handled.
[tool_call: ReadFileTool.Name for absolute_path '/path/to/UserProfileService.java']
(After reading the file)
It appears the `updateUserProfile` method in `UserProfileService.java` is responsible for this. It expects a user ID and a `UserProfileDTO` object...
</example>

<example>
user: Where are all the 'app.config' files in this project? I need to check their settings.
model:
[tool_call: GlobTool.Name for pattern '**/app.config']
(Assuming GlobTool returns a list of paths like ['/path/to/moduleA/app.config', '/path/to/moduleB/app.config'])
I found the following 'app.config' files:
- /path/to/moduleA/app.config
- /path/to/moduleB/app.config
To help you check their settings, I can read their contents. Which one would you like to start with, or should I read all of them?
</example>

# Final Reminder
Your core function is efficient and safe assistance. Balance extreme conciseness with the crucial need for clarity, especially regarding safety and potential system modifications. Always prioritize user control and project conventions. Never make assumptions about the contents of files; instead use 'ReadFileTool.Name' or 'ReadManyFilesTool.Name' to ensure you aren't making broad assumptions. Finally, you are an agent - please keep going until the user's query is completely resolved.
""".strip()

        # Write basePrompt to file if PYWEN_WRITE_SYSTEM_MD is set
        write_system_md_var = os.environ.get("PYWEN_WRITE_SYSTEM_MD", "").lower()
        if write_system_md_var and write_system_md_var not in ["0", "false"]:
            target_path = (
                system_md_path
                if write_system_md_var in ["1", "true"]
                else Path(write_system_md_var).resolve()
            )
            target_path.write_text(base_prompt)

        # Append sandbox + git info
        base_prompt += "\n" + sandbox_info()
        base_prompt += "\n" + git_info_block()

        # Append user memory if provided
        if user_memory.strip():
            base_prompt += f"\n\n---\n\n{user_memory.strip()}"

        return base_prompt

    # Specific Agent methods
    async def _process_turn_streaming(self, turn: Turn) -> AsyncGenerator[Dict[str, Any], None]:
        """Streaming turn with proper response recording."""
        
        while turn.iterations < self.max_iterations:
            turn.iterations += 1
            yield {"type": "iteration_start", "data": {"iteration": turn.iterations}}

             
            messages = self._prepare_messages_for_iteration()
            available_tools = self.tool_registry.list_tools()
            
            try:
                response_stream = await self.llm_client.generate_response(
                    messages=messages,
                    tools=available_tools,
                    stream=True
                )
                
                yield {"type": "llm_stream_start", "data": {}}
                
                # 1. 流式处理响应，收集工具调用
                final_response = None
                previous_content = ""
                collected_tool_calls = []
                
                async for response_chunk in response_stream:
                    final_response = response_chunk
                    
                    # 发送内容增量
                    if response_chunk.content:
                        current_content = response_chunk.content
                        if current_content != previous_content:
                            new_content = current_content[len(previous_content):]
                            if new_content:
                                yield {"type": "llm_chunk", "data": {"content": new_content}}
                            previous_content = current_content
                    # 收集工具调用（不立即执行）
                    if response_chunk.tool_calls:
                        collected_tool_calls.extend(response_chunk.tool_calls)
                
                # 2. 流结束后处理
                if final_response:
                    turn.add_assistant_response(final_response)
                    self.cli_console.update_token_usage(final_response.usage.input_tokens)
                    # 记录LLM交互 (session stats 会在 trajectory_recorder 中自动记录)
                    self.trajectory_recorder.record_llm_interaction(
                        messages=messages,
                        response=final_response,
                        provider=self.config.model_config.provider.value,
                        model=self.config.model_config.model,
                        tools=available_tools,
                        agent_name=self.type
                    )

                    # 添加到对话历史
                    self.conversation_history.append(LLMMessage(
                        role="assistant",
                        content=final_response.content,
                        tool_calls=final_response.tool_calls
                    ))
                    
                    # 3. 批量处理所有工具调用
                    if collected_tool_calls:
                        async for tool_event in self._process_tool_calls_streaming(turn, collected_tool_calls):
                            # if tool_event["type"] != "tool_result":
                            #     continue

                            # tool_name = tool_event["data"]["name"]
                            # result    = tool_event["data"]["result"]
                            # success   = tool_event["data"]["success"]

                            # if not success or tool_name not in {"read_file", "write_file", "edit"}:
                            #     continue

                            # try:
                            #     # 1) 取文件路径
                            #     arguments = tool_event["data"]["arguments"]
                            #     file_path_str = None
                            #     if isinstance(result, dict) and "file_path" in result:
                            #         file_path_str = result["file_path"]
                            #     elif isinstance(arguments, dict):
                            #         file_path_str = arguments.get("path")

                            #     if not file_path_str:
                            #         raise ValueError("missing file path")

                            #     file_path = Path(file_path_str).resolve()

                            #     # 2) 计算 key
                            #     try:
                            #         key = str(file_path.relative_to(Path.cwd()))
                            #     except ValueError:
                            #         key = str(file_path)

                            #     # 3) 重新 stat —— 失败就整体跳过，不硬凑
                            #     st = file_path.stat()
                            #     last_access_ms = int(st.st_atime * 1000)
                            #     est_tokens = st.st_size // 4

                            # except Exception:
                            #     # 任何一步拿不到可靠数据就直接放弃本次指标更新
                            #     continue

                            # # 3) 建档案（尽量从 stat 补充；失败则使用兜底值）
                            # if key not in self.file_metrics:
                            #     # 第一次见：根据本次工具类型初始化计数
                            #     init_read = 1 if tool_name == "read_file" else 0
                            #     init_write = 1 if tool_name == "write_file" else 0
                            #     init_edit = 1 if tool_name == "edit" else 0
                            #     last_op = {"read_file": "read", "write_file": "write", "edit": "edit"}[tool_name]

                            #     self.file_metrics[key] = {
                            #         "path": key,
                            #         "lastAccessTime": last_access_ms,
                            #         "readCount": init_read,
                            #         "writeCount": init_write,
                            #         "editCount": init_edit,
                            #         "operationsInLastHour": 0,      # 可按需要再维护
                            #         "lastOperation": last_op,
                            #         "estimatedTokens": est_tokens,
                            #     }
                            # else:
                            #     # 已存在：只累加计数、刷新时间和大小
                            #     meta = self.file_metrics[key]

                            #     if tool_name == "read_file":
                            #         meta["readCount"] += 1
                            #         meta["lastOperation"] = "read"
                            #     elif tool_name == "write_file":
                            #         meta["writeCount"] += 1
                            #         meta["lastOperation"] = "write"
                            #     elif tool_name == "edit":
                            #         meta["editCount"] += 1
                            #         meta["lastOperation"] = "edit"

                            #     meta["lastAccessTime"] = last_access_ms
                            #     meta["estimatedTokens"] = est_tokens

                            yield tool_event
                        continue
                    else:
                        turn.complete(TurnStatus.COMPLETED)
                        yield {"type": "turn_token_usage", "data": final_response.usage.total_tokens}
                        yield {"type": "turn_complete", "data": {"status": "completed"}}
                        break
                

                        
            except Exception as e:
                yield {"type": "error", "data": {"error": str(e)}}
                turn.error(str(e))
                raise e


        # Run Memory monitor and file restorer
        # total_tokens = 0
        # if final_response and hasattr(final_response, "usage") and final_response.usage:
        #     total_tokens = final_response.usage.total_tokens

        # compression = await self.memory_monitor.run_monitored(
        #     self.dialogue_counter,
        #     self.conversation_history,
        #     total_tokens
        # )

        # if compression is not None:
        #     file_content = self.file_restorer.file_recover(self.file_metrics)
        #     if file_content is not None:
        #         summary = compression + "\nHere is the potentially important file content:\n" + file_content
        #         self.conversation_history = [LLMMessage(role="user", content=summary)]
        #     else:
        #         summary = compression
        #         self.conversation_history = [LLMMessage(role="user", content=summary)]
                                    
        # Check if we hit max iterations
        if turn.iterations >= self.max_iterations and turn.status == TurnStatus.ACTIVE:
            turn.complete(TurnStatus.MAX_ITERATIONS)
            yield {"type": "max_iterations", "data": {"iterations": turn.iterations}}

    async def _process_tool_calls_streaming(self, turn: Turn, tool_calls) -> AsyncGenerator[Dict[str, Any], None]:
        """流式处理工具调用."""
        
        for tool_call in tool_calls:
            turn.add_tool_call(tool_call)
            
            # 发送工具调用开始事件
            yield {"type": "tool_call_start", "data": {
                "call_id": tool_call.call_id,
                "name": tool_call.name,
                "arguments": tool_call.arguments
            }}
            
            # 检查是否需要用户确认（基于工具风险等级）
            if hasattr(self, 'cli_console') and self.cli_console:
                # 获取工具实例来检查风险等级
                tool = self.tool_registry.get_tool(tool_call.name)
                if tool:
                    confirmation_details = await tool.get_confirmation_details(**tool_call.arguments)
                    if confirmation_details:  # 只有需要确认的工具才询问用户
                        confirmed = await self.cli_console.confirm_tool_call(tool_call, tool)
                        if not confirmed:
                                # 用户拒绝，跳过这个工具
                                # Create cancelled tool result message and add to conversation history
                                tool_msg = LLMMessage(
                                    role="tool",
                                    content="Tool execution was cancelled by user",
                                    tool_call_id=tool_call.call_id
                                )
                                self.conversation_history.append(tool_msg)

                                yield {"type": "tool_result", "data": {
                                    "call_id": tool_call.call_id,
                                    "name": tool_call.name,
                                    "result": "Tool execution rejected by user",
                                    "success": False,
                                    "error": "Tool execution rejected by user"
                                }}
                                continue
            
            try:
                # 工具执行 (session stats 会在 tool_scheduler 中自动记录)
                results = await self.tool_executor.execute_tools([tool_call], self.type)
                result = results[0]

                # 立即发送工具结果（补充 arguments 以便后续路径解析回退）
                yield {"type": "tool_result", "data": {
                    "call_id": tool_call.call_id,
                    "name": tool_call.name,
                    "result": result.result,
                    "success": result.success,
                    "error": result.error,
                    "arguments": tool_call.arguments
                }}

                turn.add_tool_result(result)
                
                # 添加到对话历史
                # Handle both structured (dict) and simple (str) result formats
                if isinstance(result.result, dict):
                    content = result.result.get('summary', str(result.result)) or str(result.error)
                else:
                    content = str(result.result) or str(result.error)

                tool_msg = LLMMessage(
                    role="tool",
                    content=content,
                    tool_call_id=tool_call.call_id
                )
                self.conversation_history.append(tool_msg)
                
            except Exception as e:
                error_msg = f"Tool execution failed: {str(e)}"
                yield {"type": "tool_error", "data": {
                    "call_id": tool_call.call_id,
                    "name": tool_call.name,
                    "error": error_msg
                }}
                
                # 添加错误结果到对话历史
                tool_msg = LLMMessage(
                    role="tool",
                    content=error_msg,
                    tool_call_id=tool_call.call_id
                )
                self.conversation_history.append(tool_msg)

    async def _check_task_continuation_streaming(self, completed_turn: Turn) -> Optional[TaskContinuationResponse]:
        """Check task continuation in streaming mode with logging."""
        
        # 获取最后的assistant response
        last_assistant_response = None
        if completed_turn.llm_responses:
            last_assistant_response = completed_turn.llm_responses[-1]
        elif completed_turn.assistant_messages:
            # 如果没有llm_responses，从assistant_messages获取最后一条
            last_response_content = completed_turn.assistant_messages[-1]
        else:
            return None
        
        # 获取响应内容
        if last_assistant_response:
            last_response_content = last_assistant_response.content
        elif not completed_turn.assistant_messages:
            return None
        else:
            last_response_content = completed_turn.assistant_messages[-1]
        
        if not last_response_content:
            return None
            
        max_turns_reached = self.current_task_turns >= self.max_task_turns
        
        # 使用LLM-based checker
        continuation_check = await self.task_continuation_checker.check_task_continuation(
            original_task=self.original_user_task,
            last_response=last_response_content,
            conversation_history=self.conversation_history,
            max_turns_reached=max_turns_reached
        )
        
        # 记录continuation check的LLM调用到trajectory
        if continuation_check and hasattr(self.task_continuation_checker, 'last_llm_response'):
            self.trajectory_recorder.record_llm_interaction(
                messages=self.task_continuation_checker.last_messages,
                response=self.task_continuation_checker.last_llm_response,
                provider=self.config.model_config.provider.value,
                model=self.config.model_config.model,
                tools=None
            )
            
            # 更新token统计到当前turn
            if self.task_continuation_checker.last_llm_response.usage:
                usage = self.task_continuation_checker.last_llm_response.usage
                if hasattr(usage, 'total_tokens'):
                    completed_turn.total_tokens += usage.total_tokens
                elif hasattr(usage, 'input_tokens') and hasattr(usage, 'output_tokens'):
                    completed_turn.total_tokens += usage.input_tokens + usage.output_tokens
        
        return continuation_check

    def _prepare_messages_for_iteration(self) -> List[LLMMessage]:
        """Prepare messages for current iteration."""
        messages = []
        cwd_prompte_template = """  
        Please note that the user launched Pywen under the path {}. 
        All subsequent file-creation, file-writing, file-reading, and similar operations should be performed within this directory.
        """
        cwd_prompt = cwd_prompte_template.format(Path.cwd())  # 有待商榷
        system_prompt = self.system_prompt + "\n" + cwd_prompt
        messages.append(LLMMessage(role="system", content=system_prompt))
        messages.extend(self.conversation_history)
        return messages


