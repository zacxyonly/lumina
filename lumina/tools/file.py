"""File operation tools."""

import os
import json
from pathlib import Path
from typing import Dict, Any, List
from lumina.tools.base import Tool, ToolParameter


class ReadFileTool(Tool):
    """Tool for reading file contents."""
    
    name = "read_file"
    description = "Read contents of a file"
    parameters = [
        ToolParameter(
            name="path",
            type="string",
            description="Path to the file to read",
            required=True
        )
    ]
    
    async def execute(self, path: str, **kwargs) -> Dict[str, Any]:
        """Read file contents."""
        try:
            file_path = Path(path).resolve()
            
            if not file_path.exists():
                return {"status": "error", "error": f"File not found: {path}"}
            
            if not file_path.is_file():
                return {"status": "error", "error": f"Not a file: {path}"}
            
            content = file_path.read_text(encoding='utf-8')
            
            return {
                "status": "success",
                "result": {
                    "path": str(file_path),
                    "content": content,
                    "size": file_path.stat().st_size,
                }
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}


class WriteFileTool(Tool):
    """Tool for writing content to a file."""
    
    name = "write_file"
    description = "Write content to a file"
    parameters = [
        ToolParameter(
            name="path",
            type="string",
            description="Path to the file to write",
            required=True
        ),
        ToolParameter(
            name="content",
            type="string",
            description="Content to write to the file",
            required=True
        ),
        ToolParameter(
            name="mode",
            type="string",
            description="Write mode: 'write' (overwrite) or 'append'",
            required=False,
            enum=["write", "append"],
            default="write"
        )
    ]
    
    async def execute(self, path: str, content: str, mode: str = "write", **kwargs) -> Dict[str, Any]:
        """Write content to file."""
        try:
            file_path = Path(path).resolve()
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            if mode == "append":
                file_path.write_text(
                    file_path.read_text(encoding='utf-8') + content if file_path.exists() else content,
                    encoding='utf-8'
                )
            else:
                file_path.write_text(content, encoding='utf-8')
            
            return {
                "status": "success",
                "result": {
                    "path": str(file_path),
                    "bytes_written": len(content.encode('utf-8')),
                    "mode": mode
                }
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}


class ListDirectoryTool(Tool):
    """Tool for listing directory contents."""
    
    name = "list_directory"
    description = "List contents of a directory"
    parameters = [
        ToolParameter(
            name="path",
            type="string",
            description="Path to the directory to list",
            required=True
        ),
        ToolParameter(
            name="recursive",
            type="boolean",
            description="Whether to list recursively",
            required=False,
            default=False
        )
    ]
    
    async def execute(self, path: str, recursive: bool = False, **kwargs) -> Dict[str, Any]:
        """List directory contents."""
        try:
            dir_path = Path(path).resolve()
            
            if not dir_path.exists():
                return {"status": "error", "error": f"Directory not found: {path}"}
            
            if not dir_path.is_dir():
                return {"status": "error", "error": f"Not a directory: {path}"}
            
            files = []
            directories = []
            
            if recursive:
                for item in dir_path.rglob("*"):
                    rel_path = str(item.relative_to(dir_path))
                    if item.is_file():
                        files.append(rel_path)
                    elif item.is_dir():
                        directories.append(rel_path)
            else:
                for item in dir_path.iterdir():
                    if item.is_file():
                        files.append(item.name)
                    elif item.is_dir():
                        directories.append(item.name)
            
            return {
                "status": "success",
                "result": {
                    "path": str(dir_path),
                    "files": sorted(files),
                    "directories": sorted(directories),
                    "total_items": len(files) + len(directories)
                }
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}


class SearchFilesTool(Tool):
    """Tool for searching files by pattern."""
    
    name = "search_files"
    description = "Search for files matching a pattern"
    parameters = [
        ToolParameter(
            name="path",
            type="string",
            description="Directory path to search in",
            required=True
        ),
        ToolParameter(
            name="pattern",
            type="string",
            description="Glob pattern to match (e.g., '*.py', '**/*.txt')",
            required=True
        )
    ]
    
    async def execute(self, path: str, pattern: str, **kwargs) -> Dict[str, Any]:
        """Search for files matching pattern."""
        try:
            dir_path = Path(path).resolve()
            
            if not dir_path.exists():
                return {"status": "error", "error": f"Directory not found: {path}"}
            
            matches = []
            for file_path in dir_path.glob(pattern):
                if file_path.is_file():
                    matches.append(str(file_path.relative_to(dir_path)))
            
            return {
                "status": "success",
                "result": {
                    "path": str(dir_path),
                    "pattern": pattern,
                    "matches": sorted(matches),
                    "count": len(matches)
                }
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}


# Export all file tools
def get_file_tools() -> List[Tool]:
    """Get all file operation tools."""
    return [
        ReadFileTool(),
        WriteFileTool(),
        ListDirectoryTool(),
        SearchFilesTool(),
    ]
