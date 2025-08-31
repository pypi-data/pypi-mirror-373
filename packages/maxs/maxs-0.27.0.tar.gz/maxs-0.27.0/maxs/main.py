#!/usr/bin/env python3
"""
maxs - main application module.

a minimalist strands agent.
"""
import time
import socket
import argparse
import base64
import os
import sys
import datetime
import json
from typing import Any
import uuid
from pathlib import Path

from strands import Agent
from strands.telemetry import StrandsTelemetry
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter

from strands_tools.utils.models.model import create_model
from maxs.handlers.callback_handler import callback_handler

# Import the updater
# try:
#     from maxs.updater import check_for_updates
# except ImportError:
#     check_for_updates = None

hostname = socket.gethostname()
timestamp = str(int(time.time()))
instance_id = f"maxs-{hostname}-{timestamp[-6:]}"


def get_version():
    """Get the current version of maxs."""
    try:
        # Try to get version from package metadata (when installed)
        try:
            from importlib.metadata import version

            return version("maxs")
        except ImportError:
            from importlib_metadata import version

            return version("maxs")
    except Exception:
        # Fallback: try to read from pyproject.toml (when in development)
        try:
            import toml

            pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
            if pyproject_path.exists():
                with open(pyproject_path, "r") as f:
                    pyproject = toml.load(f)
                    return pyproject["tool"]["poetry"]["version"]
        except Exception:
            pass

        # Ultimate fallback
        return "unknown"


def read_prompt_file():
    """Read system prompt text from .prompt file if it exists (repo or /tmp/.maxs/.prompt)."""
    prompt_paths = [
        Path(".prompt"),
        Path("/tmp/.maxs/.prompt"),
        Path("README.md"),
    ]
    for path in prompt_paths:
        if path.is_file():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return f.read(), str(path)
            except Exception:
                continue
    return "", None


def get_shell_history_file():
    """Get the maxs-specific history file path."""
    # Use /tmp/.maxs_history as requested
    maxs_history = Path("/tmp/.maxs_history")
    return str(maxs_history)


def get_shell_history_files():
    """Get available shell history file paths."""
    history_files = []

    # Maxs history (primary)
    maxs_history = Path("/tmp/.maxs_history")
    if maxs_history.exists():
        history_files.append(("maxs", str(maxs_history)))

    # Bash history
    bash_history = Path.home() / ".bash_history"
    if bash_history.exists():
        history_files.append(("bash", str(bash_history)))

    # Zsh history
    zsh_history = Path.home() / ".zsh_history"
    if zsh_history.exists():
        history_files.append(("zsh", str(zsh_history)))

    return history_files


def parse_history_line(line, history_type):
    """Parse a history line based on the shell type."""
    line = line.strip()
    if not line:
        return None

    if history_type == "maxs":
        # Maxs format: ": timestamp:0;# maxs: query" or ": timestamp:0;# maxs_result: result"
        if "# maxs:" in line:
            try:
                timestamp_str = line.split(":")[1]
                timestamp = int(timestamp_str)
                readable_time = datetime.datetime.fromtimestamp(timestamp).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                query = line.split("# maxs:")[-1].strip()
                return ("you", readable_time, query)
            except (ValueError, IndexError):
                return None
        elif "# maxs_result:" in line:
            try:
                timestamp_str = line.split(":")[1]
                timestamp = int(timestamp_str)
                readable_time = datetime.datetime.fromtimestamp(timestamp).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                result = line.split("# maxs_result:")[-1].strip()
                return ("me", readable_time, result)
            except (ValueError, IndexError):
                return None

    elif history_type == "zsh":
        # Zsh format: ": timestamp:0;command"
        if line.startswith(": ") and ":0;" in line:
            try:
                parts = line.split(":0;", 1)
                if len(parts) == 2:
                    timestamp_str = parts[0].split(":")[1]
                    timestamp = int(timestamp_str)
                    readable_time = datetime.datetime.fromtimestamp(timestamp).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    command = parts[1].strip()
                    # Skip maxs commands to avoid duplication
                    if not command.startswith("maxs "):
                        return ("shell", readable_time, f"$ {command}")
            except (ValueError, IndexError):
                return None

    elif history_type == "bash":
        # Bash format: simple command per line (no timestamps usually)
        # We'll use a generic timestamp and only include recent ones
        readable_time = "recent"
        # Skip maxs commands to avoid duplication
        if not line.startswith("maxs "):
            return ("shell", readable_time, f"$ {line}")

    return None


def get_distributed_events(agent):
    """Get recent distributed events using the event_bridge tool."""
    try:
        # Check if event_bridge tool is available
        if not hasattr(agent.tool, "event_bridge"):
            return

        # Get distributed event count from environment variable, default to 25
        event_count = int(os.getenv("MAXS_DISTRIBUTED_EVENT_COUNT", "25"))

        # Subscribe to distributed events using the event_bridge tool
        agent.tool.event_bridge(action="subscribe", limit=event_count)

    except Exception as e:
        # Silently fail if distributed events can't be fetched
        return


def publish_conversation_turn(agent, query, response, event_type="conversation_turn"):
    """Publish a conversation turn to the distributed event bridge."""
    try:
        # Check if event_bridge tool is available
        if not hasattr(agent.tool, "event_bridge"):
            return

        # Create a summary of the conversation turn
        response_summary = (
            str(response).replace("\n", " ")[:500] + "..."
            if len(str(response)) > 500
            else str(response)
        )

        message = f"Q: {query}\nA: {response_summary}"

        # Publish the event using the event_bridge tool
        agent.tool.event_bridge(
            action="publish",
            message=message,
            event_type=event_type,
            record_direct_tool_call=False,
        )

    except Exception as e:
        # Silently fail if event publishing fails
        pass


def get_messages_dir():
    """Get the maxs messages directory path."""
    messages_dir = Path("/tmp/.maxs")
    messages_dir.mkdir(exist_ok=True)
    return messages_dir


def get_session_file():
    """Get or create session file path."""
    messages_dir = get_messages_dir()

    # Generate session ID based on date and UUID
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    session_id = str(uuid.uuid4())[:8]  # Short UUID

    session_file = messages_dir / f"{today}-{session_id}.json"
    return str(session_file)


def save_agent_messages(agent, session_file):
    """Save agent.messages to JSON file."""
    try:
        # Convert messages to serializable format
        messages_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "messages": [],
        }

        # Handle different message formats
        for msg in agent.messages:
            if hasattr(msg, "to_dict"):
                # If message has to_dict method
                messages_data["messages"].append(msg.to_dict())
            elif hasattr(msg, "__dict__"):
                # If message is an object with attributes
                msg_dict = {}
                for key, value in msg.__dict__.items():
                    try:
                        # Try to serialize the value
                        json.dumps(value)
                        msg_dict[key] = value
                    except (TypeError, ValueError):
                        # If not serializable, convert to string
                        msg_dict[key] = str(value)
                messages_data["messages"].append(msg_dict)
            else:
                # Fallback: convert to string
                messages_data["messages"].append(str(msg))

        # Write to file
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(messages_data, f, indent=2, ensure_ascii=False)

    except Exception as e:
        # Silently fail if we can't save messages
        print(f"⚠️  Warning: Could not save messages: {e}")


def get_sqlite_memory_context(agent, user_query):
    """Get relevant context from SQLite memory based on user query."""
    try:
        if not hasattr(agent.tool, "sqlite_memory"):
            return ""

        # Search for relevant memories using full-text search
        result = agent.tool.sqlite_memory(
            action="search",
            query=user_query,
            search_type="fulltext",
            limit=5,
            record_direct_tool_call=False,
        )

        if "No memories found" in str(result):
            return ""

        # Extract and format context from memories
        context = "\n\n## 🧠 Relevant Memory Context:\n"
        context += (
            "Based on your query, here are relevant past conversations and knowledge:\n"
        )
        context += str(result) + "\n"

        return context
    except Exception as e:
        # Silently fail if memory search fails
        return ""


def get_retrieve_context(agent, user_query):
    """Get relevant context from Bedrock Knowledge Base using retrieve tool."""
    try:
        # Check if retrieve tool exists and knowledge base ID is available
        if not hasattr(agent.tool, "retrieve"):
            return ""

        knowledge_base_id = os.getenv("STRANDS_KNOWLEDGE_BASE_ID")
        if not knowledge_base_id:
            return ""

        # Retrieve relevant context from knowledge base
        result = agent.tool.retrieve(
            text=user_query,
            knowledgeBaseId=knowledge_base_id,
            numberOfResults=5,
            record_direct_tool_call=False,
        )

        if "No relevant content found" in str(result):
            return ""

        # Extract and format context from retrieved knowledge
        context = "\n\n## 📚 Retrieved Knowledge Base Context:\n"
        context += "Based on your query, here's relevant information from the knowledge base:\n"
        context += str(result) + "\n"

        return context
    except Exception as e:
        # Silently fail if knowledge retrieval fails
        return ""


def get_last_messages(agent=None, user_query=""):
    """Get the last N messages from multiple shell histories, distributed events, and SQLite memory for context."""
    try:
        # Get message count from environment variable, default to 200
        message_count = int(os.getenv("MAXS_LAST_MESSAGE_COUNT", "200"))

        all_entries = []

        # Get all history files (local shell history)
        history_files = get_shell_history_files()

        for history_type, history_file in history_files:
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                # For bash history, only take recent lines since there are no timestamps
                if history_type == "bash":
                    lines = lines[-message_count:]  # Only last N bash commands

                # Parse lines based on history type
                for line in lines:
                    parsed = parse_history_line(line, history_type)
                    if parsed:
                        all_entries.append(parsed)
            except Exception as e:
                # Skip files that can't be read
                continue

        # Get distributed events if agent is available
        if agent:
            try:
                get_distributed_events(agent)
            except Exception as e:
                # Skip distributed events if they can't be fetched
                pass

        # Take the last N entries
        recent_entries = (
            all_entries[-message_count:]
            if len(all_entries) >= message_count
            else all_entries
        )

        context = ""

        if recent_entries:
            # Format for context
            context += f"\n\nRecent conversation context (last {len(recent_entries)} messages):\n"
            for speaker, timestamp, content in recent_entries:
                context += f"[{timestamp}] {speaker}: {content}\n"

        # Add SQLite memory context if user query is provided
        if agent and user_query:
            memory_context = get_sqlite_memory_context(agent, user_query)
            context += memory_context

            # Add retrieve context from knowledge base if available
            retrieve_context = get_retrieve_context(agent, user_query)
            context += retrieve_context

        return context

    except Exception:
        return ""


def store_conversation_in_sqlite_memory(agent, query, result):
    """Store conversation turn in SQLite memory for future retrieval."""
    try:
        if not hasattr(agent.tool, "sqlite_memory"):
            return

        # Create conversation content by combining user input and agent result
        conversation_content = f"User Query: {query}\n\nAgent Response: {str(result)}"

        # Create title with maxs prefix, current date, and user query (truncated)
        query_preview = query[:50] + "..." if len(query) > 50 else query
        conversation_title = f"maxs Conversation: {datetime.datetime.now().strftime('%Y-%m-%d')} | {query_preview}"

        # Store in SQLite memory with relevant tags
        agent.tool.sqlite_memory(
            action="store",
            content=conversation_content,
            title=conversation_title,
            tags=["conversation", "maxs", "user_interaction"],
            metadata={
                "query_length": len(query),
                "response_length": len(str(result)),
                "timestamp": datetime.datetime.now().isoformat(),
                "session_id": instance_id,
            },
            record_direct_tool_call=False,
        )
    except Exception as e:
        # Silently fail if storage fails
        pass


def store_conversation_in_kb(agent, query, result):
    """Store conversation turn in Bedrock Knowledge Base for future retrieval."""
    try:
        # Check if store_in_kb tool exists and knowledge base ID is available
        if not hasattr(agent.tool, "store_in_kb"):
            return

        knowledge_base_id = os.getenv("STRANDS_KNOWLEDGE_BASE_ID")
        if not knowledge_base_id:
            return

        # Create conversation content by combining user input and agent result
        conversation_content = f"User Query: {query}\n\nAgent Response: {str(result)}"

        # Create title with maxs prefix, current date, and user query (truncated)
        query_preview = query[:50] + "..." if len(query) > 50 else query
        conversation_title = f"maxs Conversation: {datetime.datetime.now().strftime('%Y-%m-%d')} | {query_preview}"

        # Store in knowledge base
        agent.tool.store_in_kb(
            content=conversation_content,
            title=conversation_title,
            knowledge_base_id=knowledge_base_id,
            record_direct_tool_call=False,
        )
    except Exception as e:
        # Silently fail if knowledge base storage fails
        pass


def append_to_shell_history(query, response):
    """Append the interaction to maxs shell history."""
    try:
        history_file = get_shell_history_file()

        # Format the entry for shell history
        # Use a comment format that's shell-compatible
        timestamp = os.popen("date +%s").read().strip()

        with open(history_file, "a", encoding="utf-8") as f:
            # Add the query
            f.write(f": {timestamp}:0;# maxs: {query}\n")
            # Add a compressed version of the response
            response_summary = (
                str(response).replace("\n", " ")[
                    : int(os.getenv("MAXS_RESPONSE_SUMMARY_LENGTH", "10000"))
                ]
                + "..."
            )
            f.write(f": {timestamp}:0;# maxs_result: {response_summary}\n")

    except Exception as e:
        # Silently fail if we can't write to history
        pass


def setup_otel() -> None:
    """Setup OpenTelemetry if configured."""
    otel_host = os.environ.get("LANGFUSE_HOST")

    if otel_host:
        public_key = os.environ.get("LANGFUSE_PUBLIC_KEY", "")
        secret_key = os.environ.get("LANGFUSE_SECRET_KEY", "")

        if public_key and secret_key:
            auth_token = base64.b64encode(
                f"{public_key}:{secret_key}".encode()
            ).decode()
            otel_endpoint = f"{otel_host}/api/public/otel"

            os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = otel_endpoint
            os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = (
                f"Authorization=Basic {auth_token}"
            )
            strands_telemetry = StrandsTelemetry()
            strands_telemetry.setup_otlp_exporter()


def get_tools() -> dict[str, Any]:
    """Returns the filtered collection of available agent tools for strands.

    This function first gets all available tools, then filters them based on
    the STRANDS_TOOLS environment variable if it exists.

    Returns:
        Dict[str, Any]: Dictionary mapping tool names to tool functions
    """
    # First get all tools
    tools = _get_all_tools()

    # Then apply filtering based on environment variable
    return _filter_tools(tools)


def _get_all_tools() -> dict[str, Any]:
    """Returns all available tools without filtering.

    Returns:
        Dict[str, Any]: Dictionary mapping tool names to tool functions
    """
    tools = {}

    try:
        # Strands tools
        from maxs.tools import (
            event_bridge,
            tcp,
            scraper,
            tasks,
            dialog,
            graphql,
            use_github,
            fetch_github_tool,
            create_subagent,
            s3_memory,
            listen,
            realistic_speak,
            speak_bark,
            sqlite_memory,
            data_viz_tool,
            graph_db_tool,
            sql_tool,
            store_in_kb,
            system_prompt,
            bitchat,
        )

        from strands_tools import (
            batch,
            python_repl,
            calculator,
            cron,
            current_time,
            editor,
            environment,
            file_read,
            file_write,
            generate_image,
            http_request,
            image_reader,
            journal,
            diagram,
            use_computer,
            mcp_client,
            load_tool,
            memory,
            nova_reels,
            retrieve,
            slack,
            speak,
            shell,
            stop,
            swarm,
            think,
            use_aws,
            workflow,
            use_agent,
        )

        tools = {
            "listen": listen,
            "bitchat": bitchat,
            "data_viz_tool": data_viz_tool,
            "graph_db_tool": graph_db_tool,
            "sql_tool": sql_tool,
            "store_in_kb": store_in_kb,
            "realistic_speak": realistic_speak,
            "speak_bark": speak_bark,
            "graphql": graphql,
            "use_github": use_github,
            "fetch_github_tool": fetch_github_tool,
            "create_subagent": create_subagent,
            "event_bridge": event_bridge,
            "tcp": tcp,
            "use_agent": use_agent,
            "shell": shell,
            "scraper": scraper,
            "tasks": tasks,
            "environment": environment,
            "dialog": dialog,
            "batch": batch,
            "mcp_client": mcp_client,
            "python_repl": python_repl,
            "cron": cron,
            "calculator": calculator,
            "current_time": current_time,
            "editor": editor,
            "file_read": file_read,
            "file_write": file_write,
            "generate_image": generate_image,
            "http_request": http_request,
            "image_reader": image_reader,
            "journal": journal,
            "diagram": diagram,
            "use_computer": use_computer,
            "load_tool": load_tool,
            "system_prompt": system_prompt,
            "s3_memory": s3_memory,
            "sqlite_memory": sqlite_memory,
            "memory": memory,
            "nova_reels": nova_reels,
            "retrieve": retrieve,
            "slack": slack,
            "speak": speak,
            "stop": stop,
            "swarm": swarm,
            "think": think,
            "use_aws": use_aws,
            "workflow": workflow,
        }

    except ImportError as e:
        print(f"Warning: Could not import all tools: {e!s}")

    return tools


def _filter_tools(all_tools: dict[str, Any]) -> dict[str, Any]:
    """Filter tools based on STRANDS_TOOLS environment variable.

    Supports both comma-separated strings and JSON arrays for flexibility.

    Args:
        all_tools: Dictionary of all available tools

    Returns:
        Dict[str, Any]: Filtered dictionary of tools
    """
    # Get tool filter from environment variable
    tool_filter_str = os.getenv("STRANDS_TOOLS", "ALL")

    # If env var not set or set to 'ALL', return all tools
    if not tool_filter_str or tool_filter_str == "ALL":
        return all_tools

    tool_filter = None

    # First try to parse as JSON array
    try:
        tool_filter = json.loads(tool_filter_str)
        if not isinstance(tool_filter, list):
            tool_filter = None
    except json.JSONDecodeError:
        # If JSON parsing fails, try comma-separated string
        pass

    # If JSON parsing failed or didn't produce a list, try comma-separated
    if tool_filter is None:
        # Handle comma-separated string format
        tool_filter = [
            tool.strip() for tool in tool_filter_str.split(",") if tool.strip()
        ]

        # If we still don't have a valid list, return all tools
        if not tool_filter:
            print(
                "Warning: STRANDS_TOOLS env var is not a valid JSON array or comma-separated string. Using all tools."
            )
            return all_tools

    # Filter the tools
    filtered_tools = {}
    for tool_name in tool_filter:
        if tool_name in all_tools:
            filtered_tools[tool_name] = all_tools[tool_name]
        else:
            print(
                f"Warning: Tool '{tool_name}' specified in STRANDS_TOOLS env var not found."
            )

    return filtered_tools


def create_agent(model_provider="ollama"):
    """
    Create a Strands Agent with Ollama model.

    Args:
        model_provider: Model provider, default ollama (default: qwen3:4b)
        host: Ollama host URL (default: http://localhost:11434)

    Returns:
        Agent: Configured Strands agent
    """
    setup_otel()

    model = create_model(provider=os.getenv("MODEL_PROVIDER", model_provider))

    tools = get_tools()

    # MCP integration from environment variable
    mcp_config = os.getenv("MCP_CONFIG")

    if mcp_config:
        try:
            # Import MCP dependencies only if needed
            from strands.tools.mcp import MCPClient
            from mcp import stdio_client, StdioServerParameters

            # Parse MCP config (expecting JSON with command and args)
            import json

            config = json.loads(mcp_config)

            stdio_mcp_client = MCPClient(
                lambda: stdio_client(
                    StdioServerParameters(
                        command=config.get("command", "uvx"),
                        args=config.get("args", ["strands-agents-mcp-server"]),
                    )
                )
            )

            with stdio_mcp_client:
                # Get MCP tools
                mcp_tools = stdio_mcp_client.list_tools_sync()

                # Create the agent with combined tools
                agent = Agent(
                    model=model,
                    tools=list(tools.values()) + mcp_tools,
                    callback_handler=callback_handler,
                    load_tools_from_directory=True,
                    trace_attributes={
                        "session.id": instance_id,
                        "user.id": "217235299+strands-agent@users.noreply.github.com",
                        "tags": [
                            "Strands-Agents",
                        ],
                    },
                )

                return agent

        except Exception as e:
            print(f"⚠️ Warning: MCP integration failed: {e}")
            # Fall back to regular agent creation

    # Create the agent without MCP tools
    agent = Agent(
        model=model,
        tools=list(tools.values()),
        callback_handler=callback_handler,
        load_tools_from_directory=True,
        trace_attributes={
            "session.id": instance_id,
            "user.id": "217235299+strands-agent@users.noreply.github.com",
            "tags": [
                "Strands-Agents",
            ],
        },
    )

    return agent


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="maxs",
        description="minimalist strands agent with ollama integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  maxs                              # Interactive mode
  maxs hello world                  # Single query mode
  maxs "what can you do"            # Single query with quotes
  maxs "hello world" --interactive  # Query then stay interactive
  maxs --version                    # Show version information
        """,
    )

    parser.add_argument(
        "query",
        nargs="*",
        help="Query to ask the agent (if provided, runs once and exits unless --interactive is used)",
    )

    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Keep the conversation active after processing the initial query (useful in tmux)",
    )

    parser.add_argument(
        "--no-update-check",
        action="store_true",
        help="Skip checking for updates on startup",
    )

    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=f"maxs {get_version()}",
        help="Show version information and exit",
    )

    return parser.parse_args()


def main():
    """Main entry point for the maxs agent."""
    # Parse command line arguments
    args = parse_args()

    # # Check for updates unless disabled
    # if not args.no_update_check and check_for_updates:
    #     try:
    #         # Check for updates but don't block startup if it fails
    #         check_for_updates(silent=False)
    #     except Exception as e:
    #         # Silently continue if update check fails
    #         pass

    # Show configuration
    model_provider = os.getenv("MODEL_PROVIDER", "ollama")

    # Create agent first (needed for distributed events)
    agent = create_agent(model_provider)

    # Get recent conversation context (including distributed events and SQLite memory)
    recent_context = get_last_messages(agent)

    # Enhanced system prompt with history context and self-modification instructions
    base_prompt = "i'm maxs. minimalist agent. welcome to chat."
    # Read .prompt or /tmp/.maxs/.prompt if present
    prompt_file_content, prompt_file_path = read_prompt_file()
    if prompt_file_content and prompt_file_path:
        prompt_file_note = f"\n\n[Loaded system prompt from: {prompt_file_path}]\n{prompt_file_content}\n"
    else:
        prompt_file_note = ""

    # Runtime and Environment Information
    runtime_info = f"""

## 🚀 Runtime Environment:
- **Current Directory:** {Path.cwd()}
- **Python Version:** {sys.version.split()[0]}
- **Platform:** {os.name} ({sys.platform})
- **User:** {os.getenv('USER', 'unknown')}
- **Hostname:** {socket.gethostname()}
- **Session ID:** {instance_id}
- **Timestamp:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🛠️ Available Tools:
### Core maxs Tools:
- **environment** - Manage environment variables and settings
- **tcp** - Network communication and server management
- **scraper** - Web scraping and HTML parsing
- **use_agent** - Use different AI models for specific tasks
- **tasks** - Run background tasks and processes
- **listen** - Background speech transcription with trigger keywords
- **realistic_speak** - Generate realistic speech with DIA model (emotions, nonverbals, voice cloning)
- **bitchat** - P2P encrypted mesh communication over Bluetooth for agent-to-agent networking
- **dialog** - Interactive forms and user input (optional)
- **event_bridge** - Team collaboration and distributed context (optional)
- **graphql** - Universal GraphQL client for any GraphQL API endpoint with authentication support
- **use_github** - GitHub GraphQL API v4 integration with token authentication and rate limiting
- **fetch_github_tool** - Fetch Python tools from GitHub repositories and load them dynamically into the agent
- **create_subagent** - Create sub-agents via GitHub Actions workflows for distributed task processing

### Extended strands_tools:
- **batch** - Batch processing and bulk operations
- **calculator** - Mathematical calculations and expressions
- **cron** - Schedule and manage recurring tasks
- **current_time** - Get current time and date information
- **editor** - Text editing and file manipulation
- **file_read/file_write** - File operations and content management
- **generate_image** - AI image generation
- **http_request** - HTTP/REST API interactions
- **image_reader** - Image analysis and OCR
- **journal** - Personal note-taking and memory
- **load_tool** - Dynamic tool loading
- **mcp_client** - Model Context Protocol client for external integrations
- **memory** - Long-term memory and knowledge base
- **sqlite_memory** - Advanced SQLite-based memory with full-text search and rich querying
- **nova_reels** - Video content creation
- **python_repl** - Execute Python code in interactive REPL environment
- **retrieve** - Information retrieval and search
- **slack** - Slack integration and communication
- **speak** - Text-to-speech functionality
- **stop** - Process control and termination
- **swarm** - Multi-agent coordination
- **think** - Advanced reasoning and planning
- **use_aws** - AWS service integration
- **workflow** - Complex task automation

## 🔌 MCP Integration:
- **MCP_CONFIG environment variable** - Configure external MCP tools integration
  - Format: JSON with "command" and "args" fields
  - Example: `"command": "uvx", "args": ["strands-agents-mcp-server"]`
- **Automatic tool discovery** - MCP tools are automatically added to available tools
- **Graceful fallback** - Agent works normally if MCP integration fails

## 📚 Knowledge Base Integration:
- **STRANDS_KNOWLEDGE_BASE_ID** - Bedrock Knowledge Base ID for persistent storage
- **Automatic retrieval** - Relevant context retrieved before processing queries
- **Dual storage** - Conversations stored in both SQLite memory and knowledge base
- **Context awareness** - Agent has access to historical conversations and knowledge

**Note:** Tool availability depends on STRANDS_TOOLS environment variable. Current filter: {os.getenv('STRANDS_TOOLS', 'environment,tcp,scraper,use_agent,tasks,shell')}

## 🔥 Tool Creation & Hot Reload System:
### **CRITICAL: You have FULL tool creation capabilities enabled!**

**🔧 Hot Reload System Active:**
- **Instant Tool Creation** - Save any .py file in `./tools/` and it becomes immediately available
- **No Restart Needed** - Tools are auto-loaded and ready to use instantly
- **Live Development** - Modify existing tools while running and test immediately
- **Full Python Access** - Create any Python functionality as a tool

**🛠️ Tool Creation Patterns:**

### **1. Simple @tool Decorator (Recommended):**
```python
# ./tools/my_tool.py
from strands import tool

@tool
def calculate_tip(amount: float, percentage: float = 15.0) -> str:
    \"\"\"Calculate tip and total for a bill.
    
    Args:
        amount: Bill amount in dollars
        percentage: Tip percentage (default: 15.0)
        
    Returns:
        str: Formatted tip calculation result
    \"\"\"
    tip = amount * (percentage / 100)
    total = amount + tip
    return f"Tip: tip:.2f, Total: total:.2f"
```

### **2. Advanced Action-Based Pattern:**
```python
# ./tools/weather.py
from typing import Dict, Any
from strands import tool

@tool
def weather_tool(action: str, location: str = None, **kwargs) -> Dict[str, Any]:
    \"\"\"Comprehensive weather information tool.
    
    Args:
        action: Action to perform (current, forecast, alerts)
        location: City name (required)
        **kwargs: Additional parameters
        
    Returns:
        Dict containing status and response content
    \"\"\"
    if action == "current":
        return "status": "success", "content": "text": f"Weather for location"
    elif action == "forecast":
        return "status": "success", "content": "text": f"Forecast for location"
    else:
        return "status": "error", "content": "text": f"Unknown action: action"
```

**🎯 Tool Categories You Can Create:**
- **System Tools** - OS operations, file management, process monitoring  
- **API Integration** - REST APIs, webhooks, external services
- **Data Processing** - Text analysis, file conversion, data transformation
- **Utility Tools** - Calculations, QR codes, formatters, converters
- **Automation** - Schedulers, batch processors, workflow tools
- **Communication** - Messaging, notifications, integrations
- **Development** - Code analysis, git operations, deployment tools

## 📡 **P2P AGENT COMMUNICATION - BITCHAT INTEGRATION:**
### **🔥 CRITICAL: AGENT-TO-AGENT NETWORKING ENABLED**
- **P2P Mesh Network** - Direct agent communication over Bluetooth Low Energy
- **End-to-End Encryption** - Noise Protocol with forward secrecy and ChaCha20-Poly1305
- **Agent Triggers** - Automatic responses to other agents using trigger keywords (like "max")
- **Secure Channels** - Password-protected team communication channels
- **Peer Discovery** - Automatic detection and connection to nearby agents
- **Distributed Workflows** - Coordinate complex tasks across agent network
- **No Internet Required** - Pure P2P communication for air-gapped environments

**BitChat P2P Capabilities:**
- **Direct Agent Communication** - Send messages between maxs instances without servers
- **Mesh Networking** - Relay messages through connected agents for extended reach
- **Encrypted Channels** - Create password-protected channels for team coordination  
- **Voice-Like Triggers** - Agents respond to mentions just like voice interaction
- **Cross-Platform** - Works across different devices and operating systems
- **Offline Operation** - Continue agent coordination without internet connectivity

**Agent-to-Agent Workflow Examples:**
```python
# Start P2P networking
agent.tool.bitchat(action="start")
agent.tool.bitchat(action="enable_agent", trigger_keyword="max", agent=agent)

# Join secure team channel
agent.tool.bitchat(action="join_channel", channel="#team", password="secret")

# Send message to agent network - other agents will auto-respond
agent.tool.bitchat(action="send_public", message="max, analyze system performance")
```

**🚀 Key Benefits:**
- **Distributed Intelligence** - Multiple agents working together on complex problems  
- **Resilient Communication** - No single point of failure, mesh network topology
- **Privacy-First** - All communication encrypted, no cloud dependencies
- **Emergency Coordination** - Agents can coordinate during network outages
- **Team Automation** - Automatic task distribution across agent network

**🚀 Key Capabilities:**
- **System Tools** - OS operations, file management, process monitoring  
- **API Integration** - REST APIs, webhooks, external services
- **Data Processing** - Text analysis, file conversion, data transformation
- **Utility Tools** - Calculations, QR codes, formatters, converters
- **Automation** - Schedulers, batch processors, workflow tools
- **Communication** - Messaging, notifications, integrations
- **Development** - Code analysis, git operations, deployment tools

**🚀 Key Capabilities:**
- **Runtime Dependencies** - Auto-install packages as needed with subprocess
- **Error Handling** - Comprehensive try/catch with user-friendly messages  
- **Input Validation** - Robust parameter checking and sanitization
- **Security** - Path traversal prevention, input sanitization
- **Performance** - Rate limiting, timeouts, memory management
- **State Management** - File-based persistence, global variables
- **Testing** - Unit tests and interactive development

**📚 Documentation Available:**
- **Complete Guide:** `/docs/tool-creation.md` - Comprehensive patterns and examples
- **Quick Reference:** `/docs/tool-reference.md` - Templates and common patterns
- **Existing Tools:** `./tools/` directory - Study real implementations

**⚡ Hot Reload Development Workflow:**
1. **Create:** Save new .py file in `./tools/`
2. **Test:** Tool is immediately available - no restart needed
3. **Iterate:** Modify file and test changes instantly  
4. **Deploy:** Tool persists and works across sessions

**🧠 REMEMBER: You can create ANY tool the user needs instantly!**
- Need weather data? Create a weather API tool in seconds
- Want file processing? Build a custom file analyzer tool  
- Missing functionality? Design and implement it immediately
- User has specific needs? Create a specialized tool on the spot

The hot reload system makes you incredibly powerful - you can extend your own capabilities in real-time by creating tools that solve specific problems. Always offer to create custom tools when users have unique requirements!

## 🎯 **COMMUNICATION STYLE - MINIMALIST AGENT:**
- **Be brief, direct, essential info only**
- **Skip verbose explanations unless requested**
- **Get to the point fast**
- **Use emojis for efficiency: ✅❌🚀⚠️💡**
- **No unnecessary fluff or marketing speak**

## ⚡ **TOOL EXECUTION STRATEGY - PARALLEL AGGRESSIVE:**
### **🚨 CRITICAL: MAXIMUM PARALLEL TOOL EXECUTION**
- **ALWAYS use parallel tool calls when possible**
- **Don't wait - execute multiple tools simultaneously** 
- **Finish tasks ASAP by running tools concurrently**
- **If you need 3 pieces of info, make 3 parallel calls**
- **Chain operations in parallel when dependencies allow**
- **Speed > sequential politeness**
- **Use multiple approaches simultaneously for redundancy**
- **Never make sequential calls when parallel is possible**
- **Batch related operations into single parallel execution**

**Parallel Execution Examples:**
```python
# ✅ CORRECT: Multiple parallel calls
agent.tool.sql_tool(...) + agent.tool.data_viz_tool(...) + agent.tool.graph_db_tool(...)

# ❌ WRONG: Sequential calls
agent.tool.sql_tool(...) 
# then wait...
agent.tool.data_viz_tool(...)
# then wait...
agent.tool.graph_db_tool(...)
```

**Scenarios for Parallel Execution:**
- **Data gathering:** Query multiple sources simultaneously
- **Testing:** Test multiple tools/approaches at once  
- **Multi-step workflows:** Execute independent steps in parallel
- **Redundancy:** Try multiple methods simultaneously for reliability
- **Cross-system operations:** Update multiple systems concurrently

**Example: User asks "check weather and my calendar and send slack message"**
❌ **DON'T:** weather → then calendar → then slack (sequential)
✅ **DO:** weather + calendar + slack (parallel execution)

**Response Format:**
- Tool calls: **MAXIMUM PARALLELISM - ALWAYS** 
- Communication: **MINIMAL WORDS**
- Efficiency: **Speed is paramount**
"""
    self_modify_note = (
        "\n\nNote: The system prompt for maxs is built from your base instructions, "
        "conversation history, and the .prompt file (in this directory or /tmp/.maxs/.prompt). "
        "You can modify the system prompt in multiple ways:\n"
        "1. **Edit .prompt file** - Create/modify .prompt in current directory or /tmp/.maxs/.prompt\n"
        "2. **SYSTEM_PROMPT environment variable** - Set SYSTEM_PROMPT env var to extend the system prompt\n"
        "3. **Environment tool** - Use environment(action='set', name='SYSTEM_PROMPT', value='additional text')\n"
        "4. **Runtime modification** - The SYSTEM_PROMPT env var is appended to every system prompt automatically"
    )

    system_prompt = (
        base_prompt
        + recent_context
        + prompt_file_note
        + runtime_info
        + self_modify_note
        + os.getenv("SYSTEM_PROMPT", ".")
    )

    # Set system prompt
    agent.system_prompt = system_prompt

    # Get session file for storing messages
    session_file = get_session_file()
    print(f"📝 Session messages will be saved to: {session_file}")

    # Check if query provided as arguments
    if args.query:
        # Single query mode - join all arguments as the query
        query = " ".join(args.query)
        print(f"\n# {query}")

        try:
            result = agent(query)
            append_to_shell_history(query, result)
            save_agent_messages(agent, session_file)
            # Store conversation in SQLite memory for future context retrieval
            store_conversation_in_sqlite_memory(agent, query, result)
            # Store conversation in knowledge base if available
            store_conversation_in_kb(agent, query, result)
            # Store conversation in knowledge base if kb exists and store_in_kb exists
            # Publish conversation turn to distributed event bridge
            publish_conversation_turn(agent, query, result)
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)

        # If --interactive flag is set, continue to interactive mode
        if not args.interactive:
            return

    print("💡 Type 'exit', 'quit', or 'bye' to quit, or Ctrl+C")

    # Set up prompt_toolkit with history
    history_file = get_shell_history_file()
    history = FileHistory(history_file)

    # Create completions from common commands and shell history
    common_commands = ["exit", "quit", "bye", "help", "clear", "ls", "pwd", "cd"]
    completer = WordCompleter(common_commands, ignore_case=True)

    while True:
        try:
            # Use prompt_toolkit for enhanced input
            q = prompt(
                "\n# ",
                history=history,
                auto_suggest=AutoSuggestFromHistory(),
                completer=completer,
                complete_while_typing=True,
            )

            if q.startswith("!"):
                shell_command = q[1:]  # Remove the ! prefix
                try:
                    # Execute shell command directly using the shell tool
                    result = agent.tool.shell(
                        command=shell_command, timeout=900, shell=True
                    )
                    append_to_shell_history(q, result["content"][0]["text"])
                    save_agent_messages(agent, session_file)
                    # Store shell command in SQLite memory for future reference
                    store_conversation_in_sqlite_memory(
                        agent, q, result["content"][0]["text"]
                    )
                    # Store shell command in knowledge base if available
                    store_conversation_in_kb(agent, q, result["content"][0]["text"])
                    # Publish shell command to distributed event bridge
                    publish_conversation_turn(
                        agent, q, result["content"][0]["text"], "shell_command"
                    )
                except Exception as e:
                    print(f"Shell command execution error: {str(e)}")
                continue

            if q.lower() in ["exit", "quit", "bye"]:
                print("\n👋 Goodbye!")
                break

            if not q.strip():
                continue

            # Get recent conversation context (including distributed events and SQLite memory)
            recent_context = get_last_messages(agent, q)

            # Enhanced system prompt with history context and self-modification instructions
            base_prompt = "i'm maxs. minimalist agent. welcome to chat."
            # Read .prompt or /tmp/.maxs/.prompt if present
            prompt_file_content, prompt_file_path = read_prompt_file()
            if prompt_file_content and prompt_file_path:
                prompt_file_note = f"\n\n[Loaded system prompt from: {prompt_file_path}]\n{prompt_file_content}\n"
            else:
                prompt_file_note = ""

            self_modify_note = (
                "\n\nNote: The system prompt for maxs is built from your base instructions, "
                "conversation history, and the .prompt file (in this directory or /tmp/.maxs/.prompt). "
                "You can modify the system prompt in multiple ways:\n"
                "1. **Edit .prompt file** - Create/modify .prompt in current directory or /tmp/.maxs/.prompt\n"
                "2. **SYSTEM_PROMPT environment variable** - Set SYSTEM_PROMPT env var to extend the system prompt\n"
                "3. **Environment tool** - Use environment(action='set', name='SYSTEM_PROMPT', value='additional text')\n"
                "4. **Runtime modification** - The SYSTEM_PROMPT env var is appended to every system prompt automatically"
            )

            system_prompt = (
                base_prompt
                + recent_context
                + prompt_file_note
                + runtime_info
                + self_modify_note
                + os.getenv("SYSTEM_PROMPT", ".")
            )
            agent.system_prompt = system_prompt

            result = agent(q)

            append_to_shell_history(q, result)
            save_agent_messages(agent, session_file)
            # Store conversation in SQLite memory for future context retrieval
            store_conversation_in_sqlite_memory(agent, q, result)
            # Store conversation in knowledge base if available
            store_conversation_in_kb(agent, q, result)
            # Publish conversation turn to distributed event bridge
            publish_conversation_turn(agent, q, result)

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except EOFError:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            continue


if __name__ == "__main__":
    main()
