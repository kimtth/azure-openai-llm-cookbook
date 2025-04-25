from azure.ai.projects.telemetry import trace_function
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
import json
from typing import Any, Callable, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

def analyze_medication_info(name: str, notes: Optional[str] = None) -> str:
    """
    Analyzes medication information and provides structured analysis.
    
    Args:
        name (str): Name of the medication
        notes (Optional[str]): Additional notes or context about the medication
        
    Returns:
        str: JSON string containing structured medication analysis
    """
    try:
        # In a production environment, this would use more sophisticated analysis
        structured = {
            "analysis": f"Analysis of {name}",
            "interactions": [
                "May interact with other medications",
                "Consult your healthcare provider about potential interactions"
            ],
            "warnings": [
                "Use with caution",
                "Follow prescribed dosage",
                "Store in a cool, dry place"
            ],
            "recommendations": [
                "Take as prescribed",
                "Do not stop taking without consulting your doctor",
                "Report any unusual side effects"
            ]
        }
        
        # Add span attributes for telemetry
        span = trace.get_current_span()
        span.set_attribute("medication.name", name)
        span.set_status(Status(StatusCode.OK))
        
        return json.dumps(structured)
    except Exception as e:
        logger.error(f"Error analyzing medication info: {str(e)}")
        return json.dumps({
            "error": "Failed to analyze medication information",
            "details": str(e)
        })

analyze_medication_info.__name__ = "analyze_medication_info"

# Statically defined user functions for fast reference
medication_functions = {analyze_medication_info}
