"""Tool for reading multiple files at once."""

import os

from .base import BaseTool, ToolResult


class ReadManyFilesTool(BaseTool):
    """Read multiple files at once."""
    
    def __init__(self):
        super().__init__(
            name="read_many_files",
            display_name="Read Multiple Files",
            description="Read content from multiple files",
            parameter_schema={
                "type": "object",
                "properties": {
                    "paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of file paths to read"
                    },
                    "max_file_size": {
                        "type": "integer",
                        "description": "Maximum file size in bytes (default: 100KB)",
                        "default": 102400
                    },
                    "encoding": {
                        "type": "string",
                        "description": "Text encoding (default: utf-8)",
                        "default": "utf-8"
                    }
                },
                "required": ["paths"]
            }
        )
    
    async def execute(self, **kwargs) -> ToolResult:
        """Read multiple files."""
        paths = kwargs.get("paths", [])
        max_file_size = kwargs.get("max_file_size", 102400)
        encoding = kwargs.get("encoding", "utf-8")
        
        if not paths:
            return ToolResult(call_id="", error="No paths provided")
        
        if not isinstance(paths, list):
            return ToolResult(call_id="", error="Paths must be a list")
        
        results = []
        
        for path in paths:
            try:
                if not os.path.exists(path):
                    results.append(f"=== {path} ===\nError: File not found")
                    continue
                
                # Check file size
                file_size = os.path.getsize(path)
                if file_size > max_file_size:
                    results.append(f"=== {path} ===\nError: File too large ({file_size} bytes > {max_file_size} bytes)")
                    continue
                
                # Read file content
                with open(path, "r", encoding=encoding, errors="ignore") as f:
                    content = f.read()
                
                results.append(f"=== {path} ===\n{content}")
                
            except Exception as e:
                results.append(f"=== {path} ===\nError: {str(e)}")
        
        if not results:
            return ToolResult(call_id="", result="No files could be read")
        
        return ToolResult(call_id="", result="\n\n".join(results))
