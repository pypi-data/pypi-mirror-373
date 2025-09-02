"""
OpenAI client with OpenFiles tool integration

Drop-in replacement for OpenAI client with automatic file operations.
Follows OpenAI 2025 best practices for tool calling.
"""

import asyncio
import time
from typing import Any, Callable, Dict, List, Optional

from openai import OpenAI as OriginalOpenAI

from ..core import OpenFilesClient
from ..tools import OpenFilesTools
from ..utils.logger import get_logger

logger = get_logger(__name__)


class FileOperation:
    """Represents a file operation for monitoring"""

    def __init__(
        self,
        action: str,
        path: Optional[str] = None,
        version: Optional[int] = None,
        success: bool = True,
        error: Optional[str] = None,
        data: Any = None,
    ):
        self.action = action
        self.path = path
        self.version = version
        self.success = success
        self.error = error
        self.data = data


class ToolExecution:
    """Represents a tool execution for monitoring"""

    def __init__(
        self,
        tool_call_id: str,
        function: str,
        success: bool,
        result: Any = None,
        error: Optional[str] = None,
        duration: Optional[float] = None,
    ):
        self.tool_call_id = tool_call_id
        self.function = function
        self.success = success
        self.result = result
        self.error = error
        self.duration = duration


class ClientOptions:
    """Enhanced OpenAI configuration with OpenFiles functionality"""

    def __init__(
        self,
        openfiles_api_key: str,
        api_key: Optional[str] = None,
        openfiles_base_url: Optional[str] = None,
        base_path: Optional[str] = None,
        on_file_operation: Optional[Callable[[FileOperation], None]] = None,
        on_tool_execution: Optional[Callable[[ToolExecution], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        **openai_kwargs,
    ):
        self.openfiles_api_key = openfiles_api_key
        self.api_key = api_key
        self.openfiles_base_url = openfiles_base_url
        self.base_path = base_path
        self.on_file_operation = on_file_operation
        self.on_tool_execution = on_tool_execution
        self.on_error = on_error
        self.openai_kwargs = openai_kwargs


class OpenAI(OriginalOpenAI):
    """
    Drop-in replacement for OpenAI client with automatic file operations

    Simply replace your OpenAI import and add openfiles_api_key to get
    automatic file operation capabilities with zero code changes.

    Example:
        ```python
        # Before: from openai import OpenAI
        # After:  from openfiles.openai import OpenAI

        ai = OpenAI(
            api_key='sk_your_openai_key',           # Same as before
            openfiles_api_key='oa_your_key',       # Add this
            base_path='projects/website',           # Optional: organize files
            on_file_operation=lambda op: print(f"{op.action}: {op.path}")  # Optional
        )

        # Create scoped clients for different areas
        config_ai = ai.with_base_path('config')
        docs_ai = ai.with_base_path('documentation')

        # Everything else works exactly the same!
        response = await config_ai.chat.completions.create(
            model='gpt-4',
            messages=[{'role': 'user', 'content': 'Generate app configuration file'}],
            tools=[...my_custom_tools]  # Your tools + OpenFiles tools (auto-injected)
        )

        # File operations happen automatically, response ready to use!
        print(response.choices[0].message.content)
        ```
    """

    def __init__(
        self,
        openfiles_api_key: str,
        api_key: Optional[str] = None,
        openfiles_base_url: Optional[str] = None,
        base_path: Optional[str] = None,
        on_file_operation: Optional[Callable[[FileOperation], None]] = None,
        on_tool_execution: Optional[Callable[[ToolExecution], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        **openai_kwargs,
    ):
        """
        Initialize OpenAI client with OpenFiles integration

        Args:
            openfiles_api_key: OpenFiles API key (required)
            api_key: OpenAI API key (optional, can use environment variable)
            openfiles_base_url: OpenFiles API base URL (optional)
            base_path: Base path prefix for file operations (optional)
            on_file_operation: Callback for file operation monitoring (optional)
            on_tool_execution: Callback for tool execution monitoring (optional)
            on_error: Callback for error handling (optional)
            **openai_kwargs: Additional OpenAI client configuration
        """
        # Initialize the original OpenAI client
        super().__init__(api_key=api_key, **openai_kwargs)

        # Store configuration
        self.config = ClientOptions(
            openfiles_api_key=openfiles_api_key,
            api_key=api_key,
            openfiles_base_url=openfiles_base_url,
            base_path=base_path,
            on_file_operation=on_file_operation,
            on_tool_execution=on_tool_execution,
            on_error=on_error,
            **openai_kwargs,
        )

        # Initialize OpenFiles components
        self.artifacts = OpenFilesClient(
            api_key=openfiles_api_key,
            base_url=openfiles_base_url,
            base_path=base_path,
        )
        self.tools_instance = OpenFilesTools(self.artifacts)

        logger.info(
            f"OpenAI client initialized with file operations{f' (base_path: {base_path})' if base_path else ''}"
        )

        # Override chat.completions.create to auto-handle OpenFiles tools
        original_create = self.chat.completions.create
        self.chat.completions.create = self._create_enhanced_method(original_create)

    def with_base_path(self, base_path: str) -> "OpenAI":
        """
        Create a new OpenAI client instance with a base path prefix
        All file operations will automatically prefix paths with the base path

        Args:
            base_path: The base path to prefix to all operations

        Returns:
            New OpenAI client instance with the specified base path

        Example:
            ```python
            ai = OpenAI(api_key='sk_...', openfiles_api_key='oa_...')
            project_ai = ai.with_base_path('projects/website')

            # AI operations will create files under 'projects/website/'
            response = await project_ai.chat.completions.create(
                model='gpt-4',
                messages=[{'role': 'user', 'content': 'Create config.json'}]
            )
            ```
        """
        # Combine base paths
        enhanced_base_path = base_path
        if self.config.base_path:
            enhanced_base_path = f"{self.config.base_path}/{base_path}".replace("//", "/").rstrip("/")

        return OpenAI(
            openfiles_api_key=self.config.openfiles_api_key,
            api_key=self.config.api_key,
            openfiles_base_url=self.config.openfiles_base_url,
            base_path=enhanced_base_path,
            on_file_operation=self.config.on_file_operation,
            on_tool_execution=self.config.on_tool_execution,
            on_error=self.config.on_error,
            **self.config.openai_kwargs,
        )

    def _create_enhanced_method(self, original_create):
        """Create enhanced method with proper typing for OpenAI API"""
        
        async def enhanced_create(
            messages,
            model,
            tools=None,
            parallel_tool_calls=None,
            **kwargs
        ):
            return await self._enhanced_create(
                original_create,
                messages=messages,
                model=model,
                tools=tools,
                parallel_tool_calls=parallel_tool_calls,
                **kwargs
            )
        
        return enhanced_create

    async def _enhanced_create(
        self, 
        original_create, 
        messages, 
        model, 
        tools=None, 
        parallel_tool_calls=None,
        **kwargs
    ):
        """
        Enhanced create method that auto-handles OpenFiles tools
        True drop-in replacement - user doesn't need to manage tool flow
        """
        try:
            # Auto-inject OpenFiles tools alongside user's tools
            openfiles_tools = [tool.to_dict() for tool in self.tools_instance.definitions]
            enhanced_tools = openfiles_tools + (tools or [])

            enhanced_params = {
                "messages": messages,
                "model": model,
                "tools": enhanced_tools,
                "parallel_tool_calls": False,  # Force sequential execution for reliable file operations
                **kwargs
            }

            # Call OpenAI API
            response = original_create(**enhanced_params)

            # Auto-execute OpenFiles tools if present
            tool_messages = await self._execute_tools(response)

            if tool_messages:
                # Continue conversation with tool results automatically
                final_response = original_create(
                    messages=[
                        *messages,
                        response.choices[0].message,
                        *tool_messages,
                    ],
                    model=model,
                    tools=tools,  # Only user tools in follow-up
                    **kwargs
                )
                return final_response

            return response

        except Exception as e:
            if self.config.on_error:
                self.config.on_error(e)
            raise

    async def _execute_tools(self, response) -> List[Dict[str, Any]]:
        """
        Execute OpenFiles tools from a completion response
        Returns tool messages that should be added to the conversation

        Args:
            response: OpenAI completion response containing tool calls

        Returns:
            List of tool messages to add to conversation
        """
        start_time = time.time()

        # Use the tools layer to process the response
        processed = await self.tools_instance.process_tool_calls(response)

        total_duration = time.time() - start_time

        # Return the tool messages for conversation
        tool_messages = []
        for result in processed.results:
            if result.status == "success":
                tool_messages.append({
                    "role": "tool",
                    "tool_call_id": result.tool_call_id,
                    "content": self._create_tool_message_content(result),
                })

                # Trigger callbacks for successful operations
                operation_path = self._extract_operation_path(result)

                if self.config.on_file_operation:
                    self.config.on_file_operation(
                        FileOperation(
                            action=result.function.replace("_", " "),
                            path=operation_path,
                            version=getattr(result.data, "version", None) if hasattr(result.data, "version") else None,
                            success=True,
                            data=result.data,
                        )
                    )

                if self.config.on_tool_execution:
                    self.config.on_tool_execution(
                        ToolExecution(
                            tool_call_id=result.tool_call_id,
                            function=result.function,
                            success=True,
                            result=result.data,
                            duration=total_duration,
                        )
                    )

            else:
                tool_messages.append({
                    "role": "tool",
                    "tool_call_id": result.tool_call_id,
                    "content": self._create_error_message_content(result),
                })

                if self.config.on_file_operation:
                    self.config.on_file_operation(
                        FileOperation(
                            action=result.function.replace("_", " "),
                            path=result.args.get("path"),
                            success=False,
                            error=result.error,
                        )
                    )

                if self.config.on_tool_execution:
                    self.config.on_tool_execution(
                        ToolExecution(
                            tool_call_id=result.tool_call_id,
                            function=result.function,
                            success=False,
                            error=result.error,
                            duration=total_duration,
                        )
                    )

        return tool_messages

    def _create_tool_message_content(self, result) -> str:
        """Create content for successful tool execution"""
        import json

        # Convert data to JSON-serializable format
        data = result.data
        if hasattr(data, "model_dump"):
            data = data.model_dump(mode="json")
        elif hasattr(data, "dict"):
            data = data.dict()

        return json.dumps({
            "success": True,
            "data": data,
            "operation": result.function,
            "message": self._get_operation_message(result.function, result.args, result.data),
        })

    def _create_error_message_content(self, result) -> str:
        """Create content for failed tool execution"""
        import json

        return json.dumps({
            "success": False,
            "error": {"code": "EXECUTION_ERROR", "message": result.error},
            "operation": result.function,
        })

    def _extract_operation_path(self, result) -> Optional[str]:
        """Extract path from result for monitoring"""
        if hasattr(result.data, "path"):
            return result.data.path
        elif result.args and "path" in result.args:
            return result.args["path"]
        elif result.function == "list_files":
            directory = result.args.get("directory", "/") if result.args else "/"
            file_count = 0
            if hasattr(result.data, "data") and hasattr(result.data.data, "files"):
                file_count = len(result.data.data.files)
            return f"{directory} ({file_count} files)"
        return None

    def _get_operation_message(self, function: str, args: Dict[str, Any], data: Any) -> str:
        """Generate human-readable operation message"""
        if function == "write_file":
            return f"Created file: {args.get('path', 'unknown')}"
        elif function == "read_file":
            return f"Read file: {args.get('path', 'unknown')}"
        elif function == "edit_file":
            return f"Edited file: {args.get('path', 'unknown')}"
        elif function == "list_files":
            directory = args.get("directory", "/")
            file_count = 0
            if hasattr(data, "data") and hasattr(data.data, "files"):
                file_count = len(data.data.files)
            return f"Listed {file_count} files in: {directory}"
        elif function == "append_to_file":
            return f"Appended to file: {args.get('path', 'unknown')}"
        elif function == "overwrite_file":
            return f"Overwrote file: {args.get('path', 'unknown')}"
        elif function == "get_file_metadata":
            return f"Got metadata for: {args.get('path', 'unknown')}"
        elif function == "get_file_versions":
            return f"Got versions for: {args.get('path', 'unknown')}"
        else:
            return f"Executed {function}"