import logging
import os
from datetime import datetime

def setup_logging():
    """Configure logging for the application."""
    log_level = getattr(logging, os.getenv("LOG_LEVEL", "INFO"))
    
    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")
        
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        handlers=[
            # Console handler
            logging.StreamHandler(),
            # File handler - new file each day
            logging.FileHandler(
                filename=f'logs/app_{datetime.now().strftime("%Y%m%d")}.log',
                encoding='utf-8'
            )
        ]
    )
    
    # Log startup information
    logger = logging.getLogger(__name__)
    logger.info("🚀 Logging initialized at level: %s", log_level)
    logger.info("📂 Environment variables loaded: %s", ", ".join(f"{k}={'*' * 8 if 'SECRET' in k or 'KEY' in k else 'set' if v else 'not set'}" for k, v in os.environ.items())) 