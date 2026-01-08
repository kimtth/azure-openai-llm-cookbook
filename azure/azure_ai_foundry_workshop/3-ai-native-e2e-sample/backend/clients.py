# This module initializes and validates the Azure AI clients.
# These clients are critical for communication with the AI agents used in the trial event analysis flow.
import os
import logging
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

logger = logging.getLogger(__name__)

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

project_client = None
chat_client = None

def validate_project_client(client) -> bool:
    """Validate project client is properly initialized."""
    if not client:
        logger.error("Project client is None")
        return False
        
    if not hasattr(client, 'agents'):
        logger.error("Project client missing 'agents' attribute")
        logger.error("Client type: %s", type(client))
        logger.error("Available attributes: %s", dir(client))
        return False
        
    return True

def ensure_clients():
    """Ensure clients are initialized for multi-agent communication."""
    global project_client, chat_client
    
    logger.info("🔌 Initializing Azure AI clients")
    
    try:
        conn_str = os.getenv("PROJECT_CONNECTION_STRING")
        if not conn_str:
            raise ValueError("PROJECT_CONNECTION_STRING environment variable not set")
        logger.debug("Connection string: %s", conn_str)
        
        if not project_client or not validate_project_client(project_client):
            logger.info("Creating new project client")
            try:
                project_client = AIProjectClient.from_connection_string(
                    credential=DefaultAzureCredential(),
                    conn_str=conn_str
                )
                logger.debug("Project client created: %s", project_client)
                logger.debug("Project client type: %s", type(project_client))
                logger.debug("Project client attributes: %s", dir(project_client))
                
                if not validate_project_client(project_client):
                    raise ValueError("Project client validation failed after creation")
                    
                logger.info("✅ AIProjectClient initialized successfully")
                
                logger.debug("Getting chat client from project client")
                chat_client = project_client.inference.get_chat_completions_client()
                logger.info("✅ Chat client initialized successfully")
            except Exception as e:
                logger.error("Failed to create project client: %s", str(e), exc_info=True)
                project_client = None
                chat_client = None
                raise
        else:
            logger.debug("Using existing project client: %s", project_client)
            
        if not validate_project_client(project_client):
            raise ValueError("Project client validation failed in final check")
            
        return project_client, chat_client
        
    except Exception as e:
        logger.error("❌ Failed to initialize clients: %s", str(e), exc_info=True)
        logger.error("Project client state: %s", project_client)
        logger.error("Connection string used: %s", os.getenv("PROJECT_CONNECTION_STRING", "Not set"))
        raise

__all__ = ['project_client', 'chat_client', 'tracer', 'ensure_clients']
