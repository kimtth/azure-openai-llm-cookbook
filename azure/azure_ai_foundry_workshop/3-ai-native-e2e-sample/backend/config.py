import os
from typing import Dict
import logging
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Get the absolute path to the .env file
env_path = Path(__file__).parent / '.env'
logger.info(f"Looking for .env file at: {env_path}")
logger.info(f"Current working directory: {os.getcwd()}")

# Load environment variables with explicit path and override
load_dotenv(dotenv_path=env_path, override=True)

# Debug print to verify environment variables
logger.info("Environment variables loaded:")
logger.info(f"EVENTHUB_NAME: {os.getenv('EVENTHUB_NAME')}")
# Don't log the full connection string for security, just check if it exists
logger.info(f"EVENTHUB_CONNECTION_STRING exists: {bool(os.getenv('EVENTHUB_CONNECTION_STRING'))}")
logger.info(f"CONSUMER_GROUP: {os.getenv('CONSUMER_GROUP')}")

# After loading env vars
logger.info("Debug: All environment variables:")
for key in ["EVENTHUB_CONNECTION_STRING", "EVENTHUB_NAME", "CONSUMER_GROUP"]:
    value = os.getenv(key)
    if key == "EVENTHUB_CONNECTION_STRING" and value:
        logger.info(f"{key}: [present, length={len(value)}]")
    else:
        logger.info(f"{key}: {value}")

def validate_event_hubs_config() -> Dict[str, str]:
    """Validate and return Event Hubs configuration.
    
    Raises:
        ValueError: If any required configuration is missing
    """
    connection_string = os.getenv("EVENTHUB_CONNECTION_STRING")
    eventhub_name = os.getenv("EVENTHUB_NAME")
    consumer_group = os.getenv("CONSUMER_GROUP", "$Default")
    
    if not connection_string:
        raise ValueError(
            "EVENTHUB_CONNECTION_STRING environment variable is not set. "
            "Please check your .env file and environment configuration."
        )
    if not eventhub_name:
        raise ValueError(
            "EVENTHUB_NAME environment variable is not set. "
            "Please check your .env file and environment configuration."
        )
    
    # Log configuration status (without sensitive info)
    logger.info(f"✅ Event Hubs configuration validated for hub: {eventhub_name}")
        
    return {
        "connection_string": connection_string,
        "eventhub_name": eventhub_name,
        "consumer_group": consumer_group
    }

try:
    EVENT_HUBS_CONFIG = validate_event_hubs_config()
except ValueError as e:
    logger.error(f"❌ Configuration error: {str(e)}")
    raise
