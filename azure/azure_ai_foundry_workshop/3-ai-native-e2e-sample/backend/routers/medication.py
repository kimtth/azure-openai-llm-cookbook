from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import BingGroundingTool, FunctionTool, SubmitToolOutputsAction, RequiredFunctionToolCall, ToolOutput
from azure.identity import DefaultAzureCredential
from agents.medication_functions import medication_functions
import os
import logging
import json
import time
import asyncio
from pydantic import BaseModel
from typing import Optional

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/agents", tags=["medication"])

class MedicationInfo(BaseModel):
    name: str
    notes: Optional[str] = None

class MedicationAnalysis(BaseModel):
    analysis: str
    interactions: list[str]
    warnings: list[str]
    recommendations: list[str]

@router.post("/medication/analyze_stream")
async def analyze_medication_stream(info: MedicationInfo):
    async def event_generator():
        try:
            # Initialize client
            project_client = AIProjectClient.from_connection_string(
                credential=DefaultAzureCredential(),
                conn_str=os.environ["PROJECT_CONNECTION_STRING"]
            )
            logger.info(f"Starting streaming medication analysis for: {info.name}")
            
            # Get Bing connection and set up the tool
            bing_conn = project_client.connections.get(connection_name=os.environ["BING_CONNECTION_NAME"])
            if not bing_conn:
                yield f"data: {json.dumps({'type': 'error', 'content': 'No Bing connection found.'})}\n\n"
                return
            bing_tool = BingGroundingTool(connection_id=bing_conn.id)
            
            # Update system prompt with the new instructions:
            # The assistant must use Bing to search for medication data,
            # then call the analyze_medication_info function to format the response.
            system_prompt = (
                "You are a medication analysis assistant. Use Bing to retrieve accurate, up-to-date "
                "information about the medication specified by the user. Once you obtain Bing's results, "
                "call the analyze_medication_info function to structure your response as a JSON string. "
                "Return only a valid JSON string without any markdown or additional text."
            )
            
            # Configure function tools
            functions = FunctionTool(functions=medication_functions)
            
            # Create agent with both Bing and function tools
            agent = project_client.agents.create_agent(
                model=os.environ["MODEL_DEPLOYMENT_NAME"],
                name="medication-analysis-stream",
                instructions=system_prompt,
                tools=[*bing_tool.definitions, *functions.definitions],
                headers={"x-ms-enable-preview": "true"}
            )
            logger.info(f"Created agent with ID: {agent.id}")
            yield f"data: {json.dumps({'type': 'message', 'content': 'Agent created. Starting thread...'})}\n\n"
            
            # Create thread and initial message
            thread = project_client.agents.create_thread()
            message_content = f"Analyze the medication: {info.name}. {info.notes if info.notes else ''}"
            project_client.agents.create_message(
                thread_id=thread.id,
                role="user",
                content=message_content
            )
            yield f"data: {json.dumps({'type': 'message', 'content': 'Thread created and message sent.'})}\n\n"
            
            # Create and start the run
            run = project_client.agents.create_run(thread_id=thread.id, assistant_id=agent.id)
            logger.info(f"Created run with ID: {run.id}")
            yield f"data: {json.dumps({'type': 'message', 'content': 'Run initiated. Processing...'})}\n\n"
            
            # Poll for run completion
            max_retries = 60
            retry_count = 0
            while run.status in ["queued", "in_progress", "requires_action"]:
                await asyncio.sleep(1)
                run = project_client.agents.get_run(thread_id=thread.id, run_id=run.id)
                logger.info(f"Current run status: {run.status}")
                yield f"data: {json.dumps({'type': 'message', 'content': f'Run status: {run.status}'})}\n\n"
                retry_count += 1
                if retry_count >= max_retries:
                    yield f"data: {json.dumps({'type': 'error', 'content': 'Run timed out.'})}\n\n"
                    return
                # Handle required function calls if any
                if run.status == "requires_action" and hasattr(run, "required_action") and isinstance(run.required_action, SubmitToolOutputsAction):
                    tool_calls = run.required_action.submit_tool_outputs.tool_calls
                    if not tool_calls:
                        logger.error("No tool calls provided")
                        break
                    tool_outputs = []
                    for tool_call in tool_calls:
                        if isinstance(tool_call, RequiredFunctionToolCall):
                            try:
                                output = functions.execute(tool_call)
                                tool_outputs.append(
                                    ToolOutput(
                                        tool_call_id=tool_call.id,
                                        output=output
                                    )
                                )
                                yield f"data: {json.dumps({'type': 'message', 'content': f'Executed function call: {tool_call.function.name}'})}\n\n"
                            except Exception as e:
                                logger.error(f"Error executing tool call: {e}")
                    if tool_outputs:
                        run = project_client.agents.submit_tool_outputs_to_run(
                            thread_id=thread.id,
                            run_id=run.id,
                            tool_outputs=tool_outputs
                        )
                        continue
            
            # Once the run is complete, look for the assistant message
            if run.status == "failed":
                logger.error(f"Run failed: {run.last_error}")
                yield f"data: {json.dumps({'type': 'error', 'content': f'Run failed: {run.last_error}'})}\n\n"
                return

            messages = project_client.agents.list_messages(thread_id=thread.id)
            final_result = None
            for msg in reversed(messages.data):
                if msg.role == "assistant":
                    # Loop through message content parts
                    for content in msg.content:
                        if hasattr(content, 'text') and content.text:
                            text = content.text.value
                            # If the response is formatted with markdown, extract JSON
                            if text.startswith('```json'):
                                text = text.split('```json')[1].split('```')[0].strip()
                            try:
                                final_result = json.loads(text)
                                break
                            except json.JSONDecodeError as e:
                                logger.error(f"JSON decode error: {e}")
                    if final_result:
                        break

            if final_result is None:
                yield f"data: {json.dumps({'type': 'error', 'content': 'No valid response received from AI'})}\n\n"
                return

            # Yield final result as a completed message
            yield f"data: {json.dumps({'done': True, 'type': 'final', 'content': final_result})}\n\n"
            
        except Exception as ex:
            logger.error(f"Exception in streaming analysis: {ex}")
            yield f"data: {json.dumps({'type': 'error', 'content': str(ex)})}\n\n"
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")
