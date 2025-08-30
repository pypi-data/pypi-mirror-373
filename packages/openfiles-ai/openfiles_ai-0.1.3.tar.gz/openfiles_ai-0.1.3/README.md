# OpenFiles - Persistent File Storage for AI Agents (Python SDK)

OpenFiles gives your AI agents the ability to create, read, and manage files. Seamless OpenAI SDK integration with automatic file operations. Your AI agents can now save their work - reports, code, documents, data - with zero infrastructure setup.

## 🚀 Quick Start

```bash
pip install openfiles-ai
```

### OpenAI Integration
```python
# Before: from openai import OpenAI
# After:  from openfiles_ai import OpenAI

ai = OpenAI(
    api_key='sk_your_openai_key',           # Same as before
    openfiles_api_key='oa_your_key',    # Add this
    base_path='company/reports'             # Optional: organize files
)

# Everything else works exactly the same!
response = await ai.chat.completions.create(
    model='gpt-4',
    messages=[{'role': 'user', 'content': 'Generate quarterly business report'}],
)

# AI creates the file and responds with confirmation
print(response.choices[0].message.content)
# "I've generated a comprehensive Q1 2025 business report and saved it as company/reports/quarterly-report-q1-2025.md. The report includes financial metrics, growth analysis, and strategic recommendations."
```

## 📦 Package Structure

The SDK provides three distinct layers for different use cases:

| Layer | Import Path | Use Case | Best For |
|-------|-------------|----------|----------|
| **OpenAI** | `openfiles_ai.OpenAI` | OpenAI SDK integration | Existing OpenAI codebases |
| **Tools** | `openfiles_ai.tools.OpenFilesTools` | Framework-agnostic tools | Any AI framework (Anthropic, Cohere, etc.) |
| **Core** | `openfiles_ai.OpenFilesClient` | Direct API client | Custom integrations, frameworks |

## 📄 File Type Support

| File Category | Core Layer | Tools Layer | OpenAI Layer |
|---------------|------------|-------------|--------------|
| **Text Files** | ✅ | ✅ | ✅ |
| **Binary Files** | ✅ | 🚧 Coming Soon | 🚧 Coming Soon |

### Supported File Types

**✅ Text Files (All Layers)**
- Documents: `.md`, `.txt`, `.rtf`
- Code: `.js`, `.ts`, `.py`, `.java`, `.html`, `.css`
- Data: `.json`, `.csv`, `.yaml`, `.xml`, `.toml`
- Config: `.env`, `.ini`, `.conf`

**✅ Binary Files (Core Layer Only)**
- Images: `.png`, `.jpg`, `.gif`, `.webp`, `.bmp`, `.svg`
- Audio: `.mp3`, `.wav`, `.ogg`
- Documents: `.pdf`
- Archives: `.zip`

*Binary file support for Tools and OpenAI layers coming soon.*

---

## 🤖 OpenAI Layer (`openfiles_ai.OpenAI`)

Seamless OpenAI client integration with automatic file operations.

### Features
- ✅ **Zero code changes** - only change import path
- ✅ Automatic tool injection and execution
- ✅ Full OpenAI Python SDK compatibility
- ✅ Enhanced callbacks for monitoring
- ✅ Preserves all original OpenAI functionality

### Usage

**Before (using OpenAI directly):**
```python
from openai import OpenAI

ai = OpenAI(api_key='sk_your_openai_key')

response = await ai.chat.completions.create(
    model='gpt-4',
    messages=[{'role': 'user', 'content': 'Create a quarterly business report document'}],
    tools=[# manually define file tools #]
)

# Manually handle tool calls...
if response.choices[0].message.tool_calls:
    # Execute each tool call manually
    # Handle errors and retries
    # Make another API call with tool results
    # Complex multi-step workflow
```

**After (using OpenFiles):**
```python
from openfiles_ai import OpenAI  # Only this changes!

ai = OpenAI(
    api_key='sk_your_openai_key',           # Same
    openfiles_api_key='oa_your_key',    # Add this
    base_path='business/reports'            # Optional: organize files
)

response = await ai.chat.completions.create(
    model='gpt-4',
    messages=[{'role': 'user', 'content': 'Create a quarterly business report document'}],
    # tools auto-injected, sequential execution for reliability
)

# AI responds with confirmation of completed file operations
print(response.choices[0].message.content)
# Example: "I've created the quarterly business report document and saved it as business/reports/quarterly-report-q1-2025.md..."
```

### Enhanced Configuration

```python
ai = OpenAI(
    # All standard OpenAI options work
    api_key='sk_your_openai_key',
    
    # OpenFiles additions
    openfiles_api_key='oa_your_key',
    
    # Optional monitoring callbacks
    on_file_operation=lambda op: print(f"📁 {op.action}: {op.path}"),
    on_tool_execution=lambda exec: print(f"🔧 {exec.function} ({exec.duration}ms)"),
    on_error=lambda error: print(f"❌ Error: {error.message}")
)
```

### Organized File Operations with BasePath

Create structured file organization for your AI operations:

```python
from openfiles_ai import OpenAI

# Option 1: Constructor BasePath (all operations scoped)
project_ai = OpenAI(
    api_key='sk_your_openai_key',
    openfiles_api_key='oa_your_key',
    base_path='projects/ecommerce-site',
    on_file_operation=lambda op: print(f"📁 {op.action}: {op.path}")
)

# Option 2: Create scoped clients for different areas
main_ai = OpenAI(
    api_key='sk_your_openai_key',
    openfiles_api_key='oa_your_key'
)

frontend_ai = main_ai.with_base_path('frontend')
backend_ai = main_ai.with_base_path('backend')
docs_ai = main_ai.with_base_path('documentation')

# Each AI client operates in its own file namespace
response1 = await frontend_ai.chat.completions.create(
    model='gpt-4',
    messages=[{'role': 'user', 'content': 'Create React components for the header'}]
)
# Creates files under 'frontend/' automatically

response2 = await backend_ai.chat.completions.create(
    model='gpt-4',
    messages=[{'role': 'user', 'content': 'Generate Python API models'}]
)
# Creates files under 'backend/' automatically

response3 = await docs_ai.chat.completions.create(
    model='gpt-4',
    messages=[{'role': 'user', 'content': 'Write API documentation'}]
)
# Creates files under 'documentation/' automatically
```

---

## 🛠️ Tools Layer (`openfiles_ai.tools.OpenFilesTools`)

Framework-agnostic tool definitions compatible with any AI platform that supports tool calling.

### Features
- ✅ OpenAI-compatible tool definitions
- ✅ Works with any AI framework (Anthropic Claude, Cohere, etc.)
- ✅ Automatic tool execution
- ✅ Selective processing (only handles OpenFiles tools)
- ✅ Rich error handling and callbacks

### Usage
```python
from openfiles_ai import OpenFilesClient
from openfiles_ai.tools import OpenFilesTools

client = OpenFilesClient(api_key='oa_your_key')
tools = OpenFilesTools(client)

# Use with any AI framework
response = await your_ai_client.chat(
    messages=[{'role': 'user', 'content': 'Create a company policy document'}],
    tools=[
        *[tool.to_dict() for tool in tools.definitions],  # OpenFiles file tools
        *my_custom_tools       # Your other tools
    ]
)

# Process only OpenFiles tools
processed = await tools.process_tool_calls(response)
if processed.handled:
    print(f"Processed {len(processed.results)} file operations")
    for result in processed.results:
        if result.status == 'success':
            print(f"✅ {result.function}: {result.data.path if result.data else 'completed'}")
```

### Tool Definitions

| Tool | Description | Use Case |
|------|-------------|----------|
| `write_file` | Create new file | AI generates reports, documentation, configurations from scratch |
| `read_file` | Read and display file | AI reviews existing content before making changes or answering questions |
| `edit_file` | Modify specific text | AI fixes typos, updates values, refactors specific sections |
| `list_files` | Browse directory | AI explores document structure to understand available files |
| `append_to_file` | Add content to end | AI adds new entries to logs, lists, or ongoing documents |
| `overwrite_file` | Replace entire content | AI completely rewrites outdated files with new content |
| `get_file_metadata` | Get file info only | AI checks file size, version, modification dates for decisions |
| `get_file_versions` | Access file history | AI reviews changes over time or reverts to previous versions |

---

## 🔧 Core Layer (`openfiles_ai.OpenFilesClient`)

Direct API client for OpenFiles platform with complete file operations.

### Features
- ✅ **8 file operations** (write, read, edit, list, append, overwrite, get_metadata, get_versions)
- ✅ Version control with automatic versioning
- ✅ Simple path conventions (no leading slashes)
- ✅ Python-first with full type safety (Pydantic models)
- ✅ Comprehensive error handling with logging

### Usage

```python
from openfiles_ai import OpenFilesClient
import os

client = OpenFilesClient(
    api_key=os.getenv('OPENFILES_API_KEY'),
    base_path='company/reports'  # Organize all reports under this path
)

# Write a file (creates 'company/reports/quarterly-report.md')
result = await client.write_file(
    path='quarterly-report.md',
    content='# Q1 2025 Report\n\nRevenue increased 15%...',
    content_type='text/markdown'
)

# Read the file back
content_response = await client.read_file(path='quarterly-report.md')
content = content_response.data.content

# Edit the file
await client.edit_file(
    path='quarterly-report.md',
    old_string='Revenue increased 15%',
    new_string='Revenue increased 18%'
)

# Get file metadata
metadata_response = await client.get_metadata(path='quarterly-report.md')
metadata = metadata_response.data
print(f"File version: {metadata.version}, Size: {metadata.size} bytes")
```

---

## 🔄 Which Layer Should I Use?

| | OpenAI Layer | Tools Layer | Core Layer |
|--|-------------|-------------|-----------|
| **👥 Best For** | **Existing OpenAI apps** | Multi-framework developers | Custom integrations |
| **⭐ Difficulty** | **⭐ Easiest** | ⭐⭐ Medium | ⭐⭐⭐ Advanced |
| **🔧 Setup** | **Change import only** | Add tools + handle calls | Direct API integration |
| **🤖 AI Framework** | **OpenAI (Others coming soon)** | Any framework | Direct API |
| **⚙️ Tool Management** | **Fully automatic** | Manual processing | No tools (direct API) |
| **🎛️ Control Level** | **Plug & play** | Moderate control | Full control |

---

## 🔑 Authentication

Get your API key from [OpenFiles Console](https://console.openfiles.ai):

1. Sign up with GitHub OAuth
2. Generate API key in Settings
3. Use format: `oa_xxxxxxxxxxxxxxxxxxxxxxxxxxxx`

```python
import os
from openfiles_ai import OpenFilesClient

# Environment variables (recommended)
client = OpenFilesClient(
    api_key=os.getenv('OPENFILES_API_KEY'),
    base_path='my-project'  # Optional: organize files by project
)
```

---

## 🎯 Best Practices

### File Paths
- Use simple paths: `reports/quarterly-report-q1.md` ✅
- No leading slashes: `/reports/quarterly-report.md` ❌
- Use forward slashes on all platforms
- Keep paths descriptive and organized

### Error Handling
```python
from openfiles_ai import OpenFilesClient
from openfiles_ai.core.exceptions import FileOperationError

client = OpenFilesClient(api_key='oa_your_key')

try:
    await client.write_file(
        path='employee-handbook.md', 
        content='Employee handbook content...',
        content_type='text/markdown'
    )
except FileOperationError as error:
    if error.status_code == 409:
        # File already exists - use edit_file or overwrite_file instead
        await client.overwrite_file(
            path='employee-handbook.md',
            content='Updated employee handbook content...'
        )
    print(f'Operation failed: {error.message}')
```

---

## 🗺️ Roadmap

### **🚧 Coming Soon**
- **Delete Operation** - Remove files and folders
- **Anthropic Claude Support** - Native drop-in replacement for Claude
- **Google Gemini Support** - Native drop-in replacement for Gemini
- **Semantic Search** - AI-powered file discovery
- **Binary File Support for Tools & OpenAI Layers** - Currently only Core layer supports binary files

### **🔮 Future Features**
- **More AI Providers** - Cohere, Mistral, and local models
- **Real-time Sync** - WebSocket support for live file updates
- **File Sharing** - Share files between projects and teams
- **Multi-agent Workflows** - Advanced agent coordination
- **Plugin Ecosystem** - Community-built integrations

---

## 📖 Complete Examples

The examples in this README demonstrate:
- **Core API Integration** - Direct file operations with organized structure
- **Tools Integration** - Framework-agnostic AI tool usage  
- **OpenAI Integration** - Drop-in replacement with automatic file operations

Each example demonstrates session isolation, business-focused use cases, and covers all SDK features.

---

## 🤝 Support

- [GitHub Issues](https://github.com/openfiles-ai/openfiles/issues)
- [Documentation](https://github.com/openfiles-ai/openfiles/tree/main/sdks/python)
- [Email Support](mailto:contact@openfiles.ai)

---

**Built for AI agents, by AI enthusiasts** 🤖✨
