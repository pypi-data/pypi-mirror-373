import sys
import uuid
from typing import Dict, List

from codemie_sdk import CodeMieClient
from codemie_sdk.models.assistant import (
    AssistantChatRequest,
    ChatMessage,
    ChatRole,
)
from .model import AssistantInfo, AssistantNotFoundError, Settings

from mcp.server.fastmcp import FastMCP

# Initialize settings at module level
try:
    settings = Settings()
except Exception as e:
    print(f"Error initializing settings: {str(e)}", file=sys.stderr)
    sys.exit(1)


def get_client() -> CodeMieClient:
    """Gets authenticated CodeMie client instance."""
    try:
        client = CodeMieClient(
            username=settings.auth.username,
            password=settings.auth.password,
            auth_client_id=settings.auth.client_id,
            auth_client_secret=settings.auth.client_secret,
            verify_ssl=settings.verify_ssl,
            auth_realm_name=settings.auth_realm_name,
            auth_server_url=settings.auth_server_url,
            codemie_api_domain=settings.api_domain,
        )

        if not client.token:
            print("Failed to obtain authentication token", file=sys.stderr)
            raise ValueError("Failed to obtain authentication token")

        print("Successfully initialized CodeMie client", file=sys.stdout)
        return client
    except Exception as e:
        print(f"Error initializing client: {str(e)}", file=sys.stderr)
        raise


def get_assistant_info(assistant_id: str) -> AssistantInfo:
    """
    Retrieve and validate assistant information.

    Args:
        assistant_id: The ID of the assistant to retrieve

    Returns:
        AssistantInfo: Validated assistant information

    Raises:
        AssistantNotFoundError: If the assistant doesn't exist
        ValueError: If there are validation errors
    """
    try:
        assistant = get_client().assistants.get(assistant_id)
        if not assistant:
            raise AssistantNotFoundError(assistant_id)

        return AssistantInfo(
            id=assistant.id,
            name=assistant.name,
            description=assistant.description,
            project=assistant.project,
            slug=assistant.slug,
        )
    except AssistantNotFoundError:
        print(f"Assistant not found: {assistant_id}", file=sys.stderr)
        raise
    except Exception as e:
        print(f"Error retrieving assistant {assistant_id}: {str(e)}", file=sys.stderr)
        raise


# Initialize FastMCP server
mcp = FastMCP("codemie-assistants")
# Get and validate assistant by identifier.
codemie_assistant = get_assistant_info(settings.assistant_id)

chat_tool_name = "ask_" + codemie_assistant.name.lower().replace(" ", "_")
chat_assistant_tool_description = (
    f"""
This tool allows to ask and communicate with '{codemie_assistant.name}'.
Call this tool when '{codemie_assistant.slug}' or '{codemie_assistant.name} is present in message'
Purpose of '{codemie_assistant.name}' is: {codemie_assistant.description}.
You MUST always call this tool when '{codemie_assistant.name}' is tagged or referenced.
"""
    + """
Tool accepts the following parameters:
 - message - required. User message to send to assistant
 - conversation_id - string. Identifier of current conversation. if context or history contains Conversation_Id, this ID must be passed as parameter
 must not be passed with the first call, only if returned previously
 - history. List[Dict[str, str]]. MUST always be passed to assistant
    Example of the given param [{"role": "User", "message": "show my tools"}, {"role": "Assistant", "message": "Here are the tools available for use: **functions.generic_jira_tool**}]
    This parameter must always be filled when conversation is in progress

Returns assistant response. IMPORTANT: response must never be formatter or summarized. 
"""
)


@mcp.tool(
    name=chat_tool_name,
    description=chat_assistant_tool_description,
)
async def chat_with_assistant(
    message: str,
    history: List[Dict[str, str]] = None,
    conversation_id: str = None,
) -> str:
    """
    Chat with a specific assistant.
    :param str message: required. User request to send to assistant
    :param List[Dict[str, str]] history: Must be passed to assistant if user proceeds current conversation
    :param str conversation_id: Identifier of current conversation
    Example of the given param [{'role': 'User', 'message': 'show my tools'}, {'role': 'Assistant', 'message': 'Here are the tools available for use: **functions.generic_jira_tool**'}]
    This parameter must always be filled when conversation is in progress

    :return response from assistant.
    """
    try:
        client = get_client()
        if not message or not message.strip():
            print("Empty message provided", file=sys.stderr)
            raise ValueError("Empty message provided")

        # Convert history to ChatMessage objects if provided
        chat_history = []
        if history:
            try:
                for msg in history:
                    if (
                        not isinstance(msg, dict)
                        or "role" not in msg
                        or "message" not in msg
                    ):
                        print(f"Invalid history format: {msg}", file=sys.stderr)
                        raise ValueError(f"Invalid history format: {msg}")
                    chat_history.append(
                        ChatMessage(role=ChatRole(msg["role"]), message=msg["message"])
                    )
            except Exception as e:
                print(f"Error processing chat history: {str(e)}", file=sys.stderr)
                raise

        # Create chat request
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        print(f"Starting chat with assistant {settings.assistant_id} ", file=sys.stdout)

        request = AssistantChatRequest(
            text=message,
            conversation_id=conversation_id,
            history=chat_history,
            stream=False,
        )

        # Send chat request
        response = client.assistants.chat(
            assistant_id=settings.assistant_id, request=request
        )

        if not response or not response.generated:
            print(
                f"Received empty response from {codemie_assistant.name}",
                file=sys.stderr,
            )
            raise ValueError("Received empty response from assistant")

        print(
            f"Successfully received response from {codemie_assistant.name} for conversation {conversation_id}",
            file=sys.stdout,
        )
        return f"Response: {response.generated}. Conversation_Id: {conversation_id}"

    except Exception as e:
        print(f"Error in chat_with_assistant: {str(e)}", file=sys.stderr)
        raise


def main():
    try:
        print("Starting CodeMie Assistants MCP server", file=sys.stdout)
        # Initialize and run the server
        mcp.run(transport="stdio")
    except Exception as e:
        print(f"Error starting MCP server: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
