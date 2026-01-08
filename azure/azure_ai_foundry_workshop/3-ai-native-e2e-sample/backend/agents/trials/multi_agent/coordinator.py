from typing import Dict, Any, List
from azure.ai.projects import AIProjectClient
from azure.ai.inference import InferenceClient
from opentelemetry import trace
from utils.telemetry import tracer

class TrialAgentCoordinator:
    """
    Coordinator for managing trial event analysis using a multi-agent system.
    
    This class is responsible for:
    - Initializing a team of agents:
      • A 'team_leader' that orchestrates overall analysis and delegates tasks.
      • Specialized agents for processing vitals, assessing adverse events, and summarizing trial data.
    - Processing incoming trial events by delegating to agents and aggregating their responses.
    - Incorporating telemetry for tracing, error capturing, and performance insights.
    """
    
    def __init__(self, project_client: AIProjectClient, inference_client: InferenceClient):
        self.project_client = project_client
        self.inference_client = inference_client
        self.agents = {}

    async def initialize_agents(self):
        """
        Initializes all agents required for processing trial events.
        
        Process:
        1. Creates a 'team_leader' agent responsible for coordinating task delegation.
        2. Instantiates specialized agents:
           - 'vitals' for analyzing patient vital signs.
           - 'adverse_events' for assessing potential adverse effects.
           - 'data_summary' for aggregating and summarizing overall event data.
        
        Telemetry:
        - Uses telemetry spans to record the process duration and any initialization errors.
        """
        with tracer.start_as_current_span("initialize_trial_agents") as span:
            try:
                # Create Team Leader agent
                self.agents["team_leader"] = await self.project_client.agents.create_agent(
                    model="gpt-4o",
                    instructions="""You are the Team Leader agent coordinating trial analysis.
                    Analyze incoming trial events and delegate tasks to specialized agents."""
                )
                # Create specialized agents with specific roles
                agent_specs = {
                    "vitals": "Analyze patient vital signs and identify anomalies",
                    "adverse_events": "Monitor and assess adverse events",
                    "data_summary": "Aggregate and summarize trial data trends"
                }
                for agent_id, instructions in agent_specs.items():
                    self.agents[agent_id] = await self.project_client.agents.create_agent(
                        model="gpt-4o",
                        instructions=instructions
                    )
                span.set_attribute("agents.initialized", len(self.agents))
                return True
            except Exception as e:
                span.set_status(trace.Status(trace.StatusCode.ERROR))
                span.record_exception(e)
                raise

    async def process_trial_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes an incoming trial event through the multi-agent system.
        
        Workflow:
        1. Delegates the event to the team leader agent via _delegate_tasks.
        2. Aggregates responses (including agent outputs and event metadata) into a structured analysis result.
        3. Telemetry is used to track process completion and capture any errors.
        
        Returns:
            A dictionary containing the event id, timestamp, aggregated agent analysis, and additional recommendations.
        """
        with tracer.start_as_current_span("process_trial_event") as span:
            try:
                # Get analysis from team leader after delegating tasks
                leader_response = await self._delegate_tasks(event)
                analysis = {
                    "event_id": event.get("id"),
                    "timestamp": event.get("timestamp"),
                    "analysis": leader_response,
                    "recommendations": []
                }
                span.set_attribute("event.processed", True)
                return analysis
            except Exception as e:
                span.set_status(trace.Status(trace.StatusCode.ERROR))
                span.record_exception(e)
                raise

    async def _delegate_tasks(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delegates specific analysis tasks to the appropriate specialized agents.
        
        For a given trial event:
        - If available, the 'vitals' agent processes vital sign data.
        - If there are adverse events, the 'adverse_events' agent assesses their details.
        - Independently, the 'data_summary' agent generates an overall event summary.
        
        Each agent's response is collected and the total number of processed tasks is logged via telemetry.
        
        Returns:
            A dictionary mapping analysis types to responses returned by each agent.
        """
        with tracer.start_as_current_span("delegate_trial_tasks") as span:
            try:
                responses = {}
                # Process vital signs using the 'vitals' agent
                if "vitals" in event:
                    vitals_response = await self.agents["vitals"].process_message(
                        f"Analyze these vital signs: {event['vitals']}"
                    )
                    responses["vitals_analysis"] = vitals_response
                # Process adverse events if present
                if "adverseEvents" in event and event["adverseEvents"]:
                    adverse_response = await self.agents["adverse_events"].process_message(
                        f"Assess these adverse events: {event['adverseEvents']}"
                    )
                    responses["adverse_events_analysis"] = adverse_response
                # Always generate a summary of the trial event data
                summary_response = await self.agents["data_summary"].process_message(
                    f"Summarize this trial event data: {event}"
                )
                responses["summary"] = summary_response
                span.set_attribute("tasks.completed", len(responses))
                return responses
            except Exception as e:
                span.set_status(trace.Status(trace.StatusCode.ERROR))
                span.record_exception(e)
                raise