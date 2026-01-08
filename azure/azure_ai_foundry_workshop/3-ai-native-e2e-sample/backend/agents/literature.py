from azure.ai.projects.models import AgentEventHandler, MessageDeltaChunk, ThreadMessage, ThreadRun, RunStep, RunStatus, RunStepType, RunStepStatus
from typing import Any, Generator, Dict, Union
import logging
import json

logger = logging.getLogger(__name__)

class LiteratureChatHandler(AgentEventHandler):
    """Event handler for streaming literature chat responses."""
    
    def __init__(self):
        super().__init__()
        self.current_run_status = None
        
    def on_message_delta(self, delta: MessageDeltaChunk) -> Generator[Union[str, Dict[str, Any]], None, None]:
        """Handle streaming message chunks."""
        if delta.text:
            logger.debug(f"Received message delta: {delta.text[:100]}...")
            return json.dumps({
                "type": "delta",
                "content": delta.text
            })
        return None

    def on_thread_message(self, message: ThreadMessage) -> Generator[Dict[str, Any], None, None]:
        """Handle complete thread messages."""
        if message.content and len(message.content) > 0:
            logger.info(f"Received thread message: {message.id}")
            try:
                # Handle MessageTextDetails object properly
                if hasattr(message.content, 'value'):
                    content = message.content.value
                else:
                    content = str(message.content)

                if content.strip():  # Only send if there's actual content
                    return json.dumps({
                        "type": "message",
                        "content": content
                    })
            except Exception as e:
                logger.error(f"Error processing message content: {str(e)}")
                return json.dumps({"error": str(e)})
        return None

    def on_thread_run(self, run: ThreadRun) -> None:
        """Handle thread run status updates."""
        logger.info(f"Thread run status: {run.status}")

    def on_run_step(self, step: RunStep) -> None:
        """Handle individual run steps."""
        logger.info(f"Run step type: {step.type}, Status: {step.status}")

    def on_run_status_changed(self, event_data):
        """Handle run status changed events"""
        status = event_data.get("status")
        self.current_run_status = status
        logger.info(f"Thread run status: {status}")
        
        if status == RunStatus.FAILED:
            return json.dumps({
                "type": "error",
                "content": "The assistant encountered an error processing your request."
            })
        return None

    def on_error(self, data: str) -> Generator[Dict[str, Any], None, None]:
        """Handle error events."""
        error_msg = f"Error in literature chat: {data}"
        logger.error(error_msg)
        return json.dumps({
            "type": "error",
            "content": error_msg
        })

    def on_done(self) -> Generator[Dict[str, Any], None, None]:
        """Handle stream completion."""
        logger.info("Literature chat stream completed")
        if self.current_run_status == RunStatus.FAILED:
            return json.dumps({
                "type": "error",
                "content": "The conversation ended with an error."
            })
        return json.dumps({"done": True})

    def on_unhandled_event(self, event_type: str, event_data: Any) -> None:
        """Handle any unrecognized events."""
        logger.warning(f"Unhandled event type: {event_type}, Data: {event_data}")

    def on_run_step_started(self, event_data):
        """Handle run step started events"""
        step_type = event_data.get("step_type")
        logger.info(f"Run step type: {step_type}, Status: RunStepStatus.IN_PROGRESS")
        return None

    def on_run_step_completed(self, event_data):
        """Handle run step completed events"""
        step_type = event_data.get("step_type")
        logger.info(f"Run step type: {step_type}, Status: RunStepStatus.COMPLETED")
        return None

    def __call__(self, run_status=None, run_step=None, message=None):
        try:
            if run_status:
                logger.info(f"Thread run status: {run_status}")
                
            if run_step:
                logger.info(f"Run step type: {run_step.type}, Status: {run_step.status}")
                
            if message:
                logger.info(f"Received thread message: {message.id}")
                if message.content:
                    try:
                        # Handle MessageTextDetails object properly
                        if hasattr(message.content, 'value'):
                            content = message.content.value
                        else:
                            content = str(message.content)
                            
                        # Return properly formatted JSON response
                        return None, None, json.dumps({
                            "type": "message",
                            "content": content
                        })
                    except Exception as e:
                        logger.error(f"Error processing message content: {str(e)}")
                        return None, None, json.dumps({
                            "type": "error",
                            "content": f"Failed to process message: {str(e)}"
                        })

            if run_status == RunStatus.COMPLETED:
                logger.info("Literature chat stream completed")
                
        except Exception as e:
            logger.error(f"Error in literature chat handler: {str(e)}")
            return None, None, json.dumps({
                "type": "error",
                "content": f"Handler error: {str(e)}"
            })
        
        return None, None, None
