"""
OpenFiles Tools - Framework-agnostic AI tool definitions

Provides OpenAI-compatible tool definitions and automatic execution
for file operations. Only handles OpenFiles tools, ignoring others.
"""

import json
from typing import Any, Dict, List, Optional

from ..core import OpenFilesClient


class ToolDefinition:
    """OpenAI-compatible tool definition"""

    def __init__(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        strict: bool = True,
    ):
        self.type = "function"
        self.function = {
            "name": name,
            "description": description,
            "strict": strict,
            "parameters": parameters,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for OpenAI API"""
        return {"type": self.type, "function": self.function}


class ToolResult:
    """Result of tool execution"""

    def __init__(
        self,
        tool_call_id: str,
        function: str,
        status: str = "success",
        data: Any = None,
        error: Optional[str] = None,
        args: Optional[Dict[str, Any]] = None,
    ):
        self.tool_call_id = tool_call_id
        self.function = function
        self.status = status  # 'success' or 'error'
        self.data = data
        self.error = error
        self.args = args or {}


class ProcessedToolCalls:
    """Result of processing tool calls"""

    def __init__(self, handled: bool = False, results: Optional[List[ToolResult]] = None):
        self.handled = handled
        self.results = results or []
        self.tool_messages = []

        # Generate tool messages for OpenAI API
        for result in self.results:
            if result.status == "success":
                # Convert Pydantic models to dict for JSON serialization
                data = result.data
                if hasattr(data, "model_dump"):
                    data = data.model_dump(mode="json")
                elif hasattr(data, "dict"):
                    data = data.dict()

                content = json.dumps({"success": True, "data": data, "operation": result.function})
            else:
                content = json.dumps(
                    {
                        "success": False,
                        "error": {"code": "EXECUTION_ERROR", "message": result.error},
                        "operation": result.function,
                    }
                )

            self.tool_messages.append(
                {"role": "tool", "tool_call_id": result.tool_call_id, "content": content}
            )


class ToolCall:
    """Represents a tool call from OpenAI API"""

    def __init__(self, id: str, function_name: str, arguments: str):
        self.id = id
        self.function = {"name": function_name, "arguments": arguments}


class OpenFilesTools:
    """
    OpenFiles Tools for AI Agents

    Provides OpenAI-compatible tool definitions and automatic execution
    for file operations. Only handles OpenFiles tools, ignoring others.

    Example:
        ```python
        from openfiles import OpenFilesClient
        from openfiles.tools import OpenFilesTools

        client = OpenFilesClient(api_key='oa_...')
        tools = OpenFilesTools(client)

        # With base_path for organized file structure
        project_tools = OpenFilesTools(client, 'projects/website')

        # Use with existing OpenAI client
        import openai
        response = openai.chat.completions.create(
            model='gpt-4',
            messages=[...],
            tools=[tool.to_dict() for tool in project_tools.definitions] + my_other_tools
        )

        # Process OpenFiles tools only
        processed = await project_tools.process_tool_calls(response)
        if processed.handled:
            print('Files created:', processed.results)
        ```
    """

    def __init__(self, client: OpenFilesClient, base_path: Optional[str] = None):
        """
        Initialize OpenFiles tools

        Args:
            client: OpenFiles client instance
            base_path: Base path prefix for all file operations
        """
        self.client = client
        self.base_path = base_path

    def with_base_path(self, base_path: str) -> "OpenFilesTools":
        """
        Create a new OpenFilesTools instance with a base path prefix
        All file operations will automatically prefix paths with the base path

        Args:
            base_path: The base path to prefix to all operations

        Returns:
            New OpenFilesTools instance with the specified base path

        Example:
            ```python
            tools = OpenFilesTools(client)
            project_tools = tools.with_base_path('projects/website')

            # AI operations will create files under 'projects/website/'
            ```
        """
        return OpenFilesTools(self.client, base_path)

    @property
    def definitions(self) -> List[ToolDefinition]:
        """
        OpenAI-compatible tool definitions
        Use these in your OpenAI chat completions request
        """
        return [
            ToolDefinition(
                name="write_file",
                description="CREATE a NEW file (fails if file exists). Use when user wants to: create, generate, make, or write a new file. For existing files, use edit_file, append_to_file, or overwrite_file instead.",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path (S3-style, no leading slash)",
                            "example": "reports/quarterly-report.md",
                        },
                        "content": {"type": "string", "description": "File content to write"},
                        "contentType": {
                            "type": "string",
                            "description": "MIME type of file content. Provide specific type (e.g., text/plain, text/markdown, application/json) or use application/octet-stream as default",
                            "default": "application/octet-stream",
                            "example": "text/markdown",
                        },
                    },
                    "required": ["path", "content", "contentType"],
                    "additionalProperties": False,
                },
            ),
            ToolDefinition(
                name="read_file",
                description="READ and DISPLAY existing file content. Use when user asks to: see, show, read, view, display, or retrieve file content. Returns the actual content to show the user.",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path (S3-style, no leading slash)",
                            "example": "reports/quarterly-report.md",
                        },
                        "version": {
                            "type": "number",
                            "description": "Specific version to read (use 0 or omit for latest version)",
                            "default": 0,
                        },
                    },
                    "required": ["path", "version"],
                    "additionalProperties": False,
                },
            ),
            ToolDefinition(
                name="edit_file",
                description="MODIFY parts of an existing file by replacing specific text. Use when user wants to: update, change, fix, or edit specific portions while keeping the rest.",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path (S3-style, no leading slash)",
                            "example": "reports/quarterly-report.md",
                        },
                        "oldString": {
                            "type": "string",
                            "description": "Exact string to find and replace",
                        },
                        "newString": {
                            "type": "string",
                            "description": "Replacement string",
                        },
                    },
                    "required": ["path", "oldString", "newString"],
                    "additionalProperties": False,
                },
            ),
            ToolDefinition(
                name="list_files",
                description="LIST files in a directory. Use when user wants to: browse files, see what exists, explore directory contents, or find available files.",
                parameters={
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": "Directory path to list files from",
                            "example": "reports/",
                            "default": "/",
                        },
                        "recursive": {
                            "type": "boolean",
                            "description": "If true, lists all files across all directories. If false (default), only lists files in the specified directory",
                            "default": False,
                        },
                        "limit": {
                            "type": "number",
                            "description": "Maximum number of files to return",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 100,
                        },
                    },
                    "required": ["directory", "recursive", "limit"],
                    "additionalProperties": False,
                },
            ),
            ToolDefinition(
                name="append_to_file",
                description="ADD content to the END of existing file. Use for: adding to logs, extending lists, continuing documents, or accumulating data without losing existing content.",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path (S3-style, no leading slash)",
                            "example": "logs/daily-operations.log",
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to append to the file",
                        },
                    },
                    "required": ["path", "content"],
                    "additionalProperties": False,
                },
            ),
            ToolDefinition(
                name="overwrite_file",
                description="REPLACE ALL content in existing file. Use when user wants to: completely rewrite, reset, or replace entire file content. Keeps the file but changes everything inside.",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path (S3-style, no leading slash)",
                            "example": "policies/employee-handbook.md",
                        },
                        "content": {
                            "type": "string",
                            "description": "New content to replace existing content",
                        },
                        "isBase64": {
                            "type": "boolean",
                            "description": "Whether the content is base64 encoded",
                            "default": False,
                        },
                    },
                    "required": ["path", "content", "isBase64"],
                    "additionalProperties": False,
                },
            ),
            ToolDefinition(
                name="get_file_metadata",
                description="GET file information (size, version, dates) WITHOUT content. Use for: checking file stats, properties, or metadata when content is not needed.",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path (S3-style, no leading slash)",
                            "example": "reports/quarterly-report.md",
                        },
                        "version": {
                            "type": "number",
                            "description": "Specific version to get metadata for (use 0 for latest version)",
                            "default": 0,
                        },
                    },
                    "required": ["path", "version"],
                    "additionalProperties": False,
                },
            ),
            ToolDefinition(
                name="get_file_versions",
                description="GET file version history and information. Use when user wants to: see versions, check history, or explore file changes over time.",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path (S3-style, no leading slash)",
                            "example": "reports/quarterly-report.md",
                        },
                        "limit": {
                            "type": "number",
                            "description": "Maximum number of versions to return",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 50,
                        },
                        "offset": {
                            "type": "number",
                            "description": "Number of versions to skip (for pagination)",
                            "default": 0,
                            "minimum": 0,
                        },
                    },
                    "required": ["path", "limit", "offset"],
                    "additionalProperties": False,
                },
            ),
        ]

    async def process_tool_calls(self, response: Any) -> ProcessedToolCalls:
        """
        Process OpenAI response and execute OpenFiles tool calls

        Args:
            response: OpenAI chat completion response or similar structure

        Returns:
            ProcessedToolCalls with execution results
        """
        results = []
        handled = False

        # Handle different response formats (Pydantic models and dicts)
        if hasattr(response, "choices"):
            choices = response.choices
        elif isinstance(response, dict) and "choices" in response:
            choices = response["choices"]
        else:
            choices = []

        for choice in choices:
            if hasattr(choice, "message"):
                message = choice.message
            elif isinstance(choice, dict) and "message" in choice:
                message = choice["message"]
            else:
                continue
                
            if hasattr(message, "tool_calls"):
                tool_calls = message.tool_calls or []
            elif isinstance(message, dict) and "tool_calls" in message:
                tool_calls = message["tool_calls"] or []
            else:
                continue

            for tool_call in tool_calls:
                if hasattr(tool_call, "id"):
                    tool_call_id = tool_call.id
                elif isinstance(tool_call, dict):
                    tool_call_id = tool_call.get("id")
                else:
                    continue
                    
                if hasattr(tool_call, "function"):
                    function = tool_call.function
                elif isinstance(tool_call, dict):
                    function = tool_call.get("function", {})
                else:
                    continue
                    
                if hasattr(function, "name"):
                    function_name = function.name
                elif isinstance(function, dict):
                    function_name = function.get("name")
                else:
                    continue
                    
                if hasattr(function, "arguments"):
                    arguments = function.arguments
                elif isinstance(function, dict):
                    arguments = function.get("arguments", "{}")
                else:
                    arguments = "{}"

                if self._is_openfiles_tool(function_name):
                    handled = True

                    try:
                        args = json.loads(arguments)
                        tool_call_obj = ToolCall(tool_call_id, function_name, arguments)
                        result_data = await self._execute_tool(tool_call_obj)

                        results.append(
                            ToolResult(
                                tool_call_id=tool_call_id,
                                function=function_name,
                                status="success",
                                data=result_data,
                                args=args,
                            )
                        )

                    except Exception as e:
                        args = json.loads(arguments) if arguments else {}
                        error_message = str(e)

                        results.append(
                            ToolResult(
                                tool_call_id=tool_call_id,
                                function=function_name,
                                status="error",
                                error=error_message,
                                args=args,
                            )
                        )

        return ProcessedToolCalls(handled=handled, results=results)

    def _is_openfiles_tool(self, name: str) -> bool:
        """Check if a tool name is an OpenFiles tool (internal method)"""
        return name in [
            "write_file",
            "read_file",
            "edit_file",
            "list_files",
            "append_to_file",
            "overwrite_file",
            "get_file_metadata",
            "get_file_versions",
        ]

    async def _execute_tool(self, tool_call: ToolCall) -> Any:
        """Execute a single tool call (private - for internal use only)"""
        args = json.loads(tool_call.function["arguments"])

        if tool_call.function["name"] == "write_file":
            return await self.client.write_file(
                path=args["path"],
                content=args["content"],
                content_type=args["contentType"],
                base_path=self.base_path,
            )

        elif tool_call.function["name"] == "read_file":
            version = args["version"] if args["version"] != 0 else None
            content_response = await self.client.read_file(
                path=args["path"], version=version, base_path=self.base_path
            )
            return {
                "path": args["path"],
                "content": content_response.data.content,
                "version": args["version"],
            }

        elif tool_call.function["name"] == "edit_file":
            return await self.client.edit_file(
                path=args["path"],
                old_string=args["oldString"],
                new_string=args["newString"],
                base_path=self.base_path,
            )

        elif tool_call.function["name"] == "list_files":
            kwargs = {
                "directory": args["directory"],
                "limit": args["limit"],
                "base_path": self.base_path
            }
            if "recursive" in args:
                kwargs["recursive"] = args["recursive"]
            return await self.client.list_files(**kwargs)

        elif tool_call.function["name"] == "append_to_file":
            return await self.client.append_file(
                path=args["path"], content=args["content"], base_path=self.base_path
            )

        elif tool_call.function["name"] == "overwrite_file":
            return await self.client.overwrite_file(
                path=args["path"],
                content=args["content"],
                is_base64=args.get("isBase64", False),
                base_path=self.base_path,
            )

        elif tool_call.function["name"] == "get_file_metadata":
            version = args["version"] if args["version"] != 0 else None
            return await self.client.get_metadata(
                path=args["path"], version=version, base_path=self.base_path
            )

        elif tool_call.function["name"] == "get_file_versions":
            return await self.client.get_versions(
                path=args["path"],
                limit=args["limit"],
                offset=args["offset"],
                base_path=self.base_path,
            )

        else:
            raise ValueError(f"Unknown tool: {tool_call.function['name']}")
