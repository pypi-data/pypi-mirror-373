"""Memory tool for storing user preferences and facts."""

import os
from pathlib import Path

from .base import BaseTool, ToolResult


class MemoryTool(BaseTool):
    """Tool for remembering user-specific facts and preferences."""

    def __init__(self, project_id: str = None):
        super().__init__(
            name="memory",
            display_name="Memory Tool",
            description="Write and read memory files in markdown format for storing user-related facts or preferences",
            parameter_schema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["write", "read", "list"],
                        "description": "Action to perform: write (create/update memory file), read (read specific file), or list (list all memory files)"
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Path to the memory file (relative to memory directory, e.g. 'preferences.md', 'projects/project1.md')"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the memory file (required for 'write' action)"
                    }
                },
                "required": ["action"]
            }
        )

        # Create memory directory structure similar to Kode
        # Base directory: ~/.pywen/memory/
        home_dir = Path.home()
        base_memory_dir = home_dir / ".pywen" / "memory"

        # Project-specific directory: ~/.pywen/memory/projects/{project_id}/
        # If no project_id provided, use current working directory name or 'default'
        if project_id is None:
            project_id = self._get_project_id()

        self.memory_dir = base_memory_dir / "projects" / project_id
        self.memory_dir.mkdir(parents=True, exist_ok=True)

    def _get_project_id(self) -> str:
        """Get project ID from current working directory or environment."""
        # Try to get from environment variable first
        project_id = os.environ.get('PYWEN_PROJECT_ID')
        if project_id:
            return project_id

        # Use current working directory name
        cwd = Path.cwd()
        project_name = cwd.name

        # Sanitize project name for use as directory name
        import re
        project_name = re.sub(r'[^\w\-_.]', '_', project_name)

        return project_name or 'default'

    def _get_full_path(self, file_path: str) -> Path:
        """Get full path for a memory file and ensure it's within memory directory."""
        full_path = (self.memory_dir / file_path).resolve()
        memory_dir_resolved = self.memory_dir.resolve()

        # Security check: ensure the path is within memory directory
        if not str(full_path).startswith(str(memory_dir_resolved)):
            raise ValueError(f"Invalid file path: {file_path}")

        return full_path

    def _read_memory_file(self, file_path: str) -> str:
        """Read content from a memory file."""
        full_path = self._get_full_path(file_path)

        if not full_path.exists():
            raise FileNotFoundError(f"Memory file does not exist: {file_path}")

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Failed to read memory file: {str(e)}")

    def _write_memory_file(self, file_path: str, content: str) -> None:
        """Write content to a memory file."""
        full_path = self._get_full_path(file_path)

        # Create parent directories if they don't exist
        full_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            raise Exception(f"Failed to write memory file: {str(e)}")

    def _list_memory_files(self) -> str:
        """List all memory files in the directory."""
        if not self.memory_dir.exists():
            return "No memory files found."

        files = []
        for file_path in self.memory_dir.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(self.memory_dir)
                files.append(str(relative_path))

        if not files:
            return "No memory files found."

        files.sort()
        return "Memory files:\n" + "\n".join(f"- {f}" for f in files)
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute memory operation."""
        action = kwargs.get("action")
        file_path = kwargs.get("file_path")
        content = kwargs.get("content")

        if not action:
            return ToolResult(call_id="", error="No action specified")

        try:
            if action == "write":
                if not file_path:
                    return ToolResult(call_id="", error="file_path is required for write action")
                if not content:
                    return ToolResult(call_id="", error="content is required for write action")

                # Ensure file has .md extension
                if not file_path.endswith('.md'):
                    file_path += '.md'

                self._write_memory_file(file_path, content)
                return ToolResult(call_id="", result=f"Successfully wrote memory file: {file_path}")

            elif action == "read":
                if not file_path:
                    return ToolResult(call_id="", error="file_path is required for read action")

                # Ensure file has .md extension
                if not file_path.endswith('.md'):
                    file_path += '.md'

                content = self._read_memory_file(file_path)
                return ToolResult(call_id="", result=f"Content of {file_path}:\n\n{content}")

            elif action == "list":
                file_list = self._list_memory_files()
                return ToolResult(call_id="", result=file_list)

            else:
                return ToolResult(call_id="", error=f"Unknown action: {action}. Supported actions: write, read, list")

        except FileNotFoundError as e:
            return ToolResult(call_id="", error=str(e))
        except ValueError as e:
            return ToolResult(call_id="", error=str(e))
        except Exception as e:
            return ToolResult(call_id="", error=f"Error executing memory operation: {str(e)}")
