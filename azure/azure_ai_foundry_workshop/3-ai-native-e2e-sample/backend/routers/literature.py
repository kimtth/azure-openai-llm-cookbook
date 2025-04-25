from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import AzureAISearchTool, ConnectionType
from azure.identity import DefaultAzureCredential
from agents.literature import LiteratureChatHandler
import os
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/literature-chat")
async def chat_literature(request: Request):
    """
    Stream chat responses about literature using AI Search.
    
    Args:
        request: The request object containing the user's chat message
        
    Returns:
        StreamingResponse: Server-sent events stream of chat responses
        
    Raises:
        HTTPException: If there's an error processing the request
    """
    try:
        body = await request.json()
        message = body.get("message")
        if not message:
            raise HTTPException(status_code=400, detail="Message field is required")

        # Initialize AI Project client
        project_client = AIProjectClient.from_connection_string(
            credential=DefaultAzureCredential(),
            conn_str=os.environ["PROJECT_CONNECTION_STRING"]
        )
        
        # Get AI Search connection
        search_conn = project_client.connections.get_default(
            connection_type=ConnectionType.AZURE_AI_SEARCH,
            include_credentials=True
        )
        if not search_conn:
            raise ValueError("No default Azure AI Search connection found")
        
        # Configure AI Search tool
        ai_search_tool = AzureAISearchTool(
            index_connection_id=search_conn.id,
            index_name="literature-index"
        )
        
        # Create chat agent
        agent = project_client.agents.create_agent(
            model=os.environ["MODEL_DEPLOYMENT_NAME"],
            name="literature-chat",
            instructions="""You are a Literature Research Assistant. Help users find and understand scientific literature.
            Use the search tool to find relevant papers and provide evidence-based responses.
            Always cite your sources and provide context for your answers.""",
            tools=ai_search_tool.definitions,
            tool_resources=ai_search_tool.resources,
            headers={"x-ms-enable-preview": "true"}
        )
        logger.info(f"Created agent with ID: {agent.id}")
        
        # Create thread and message
        thread = project_client.agents.create_thread()
        logger.info(f"Created thread with ID: {thread.id}")
        
        message_obj = project_client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content=message
        )
        logger.info(f"Created message with ID: {message_obj.id}")
        
        # Create streaming response
        stream = project_client.agents.create_stream(
            thread_id=thread.id,
            assistant_id=agent.id,
            event_handler=LiteratureChatHandler()
        )
        
        async def generate_events():
            try:
                with stream as active_stream:
                    for event in active_stream:
                        if isinstance(event, tuple) and len(event) == 3:
                            _, _, response = event
                            if response:
                                yield f"data: {response}\n\n"
                                
                                # Check if this was an error response
                                try:
                                    resp_data = json.loads(response)
                                    if resp_data.get("type") == "error":
                                        logger.error(f"Stream error: {resp_data.get('content')}")
                                        break
                                except:
                                    pass
            except Exception as e:
                logger.error(f"Stream error: {str(e)}")
                error_msg = json.dumps({
                    "type": "error",
                    "content": str(e)
                })
                yield f"data: {error_msg}\n\n"
            finally:
                yield "data: {\"done\": true}\n\n"
        
        return StreamingResponse(
            generate_events(),
            media_type="text/event-stream"
        )
        
    except Exception as e:
        logger.error(f"Error in literature chat: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process literature chat: {str(e)}"
        )
