"""
This module implements the specialized agents for clinical trial event analysis.
Each agent is responsible for a specific task in the workflow:
  - VitalsAgent: Processes patient vital signs.
  - AdverseEventAgent: Assesses adverse events.
  - DataSummaryAgent: Summarizes overall trial data.
These agents are coordinated by the TrialAgentCoordinator.
"""

from typing import Dict, Any
from opentelemetry import trace
from azure.ai.projects import AIProjectClient

tracer = trace.get_tracer(__name__)

class SpecializedAgent:
    """Base class for specialized trial analysis agents."""
    
    def __init__(self, project_client: AIProjectClient, model: str, instructions: str):
        self.project_client = project_client
        self.model = model
        self.instructions = instructions
        self._agent = None
    
    async def initialize(self) -> None:
        """Initialize the agent with Azure AI Foundry."""
        self._agent = await self.project_client.agents.create_agent(
            model=self.model,
            instructions=self.instructions
        )
    
    async def process_message(self, message: str) -> Dict[str, Any]:
        """Process a message using the agent.
        
        Args:
            message: The message to process
            
        Returns:
            The agent's response.
        """
        with tracer.start_as_current_span("process_agent_message") as span:
            try:
                if not self._agent:
                    await self.initialize()
                    
                if not self._agent:
                    raise RuntimeError("Failed to initialize agent")
                    
                response = await self._agent.process_message(message)
                return {"response": response, "agent_type": self.__class__.__name__}
                
            except Exception as e:
                span.set_status(trace.Status(trace.StatusCode.ERROR))
                span.record_exception(e)
                raise

class VitalsAgent(SpecializedAgent):
    """Agent specialized in analyzing patient vital signs."""
    
    def __init__(self, project_client: AIProjectClient, model: str):
        super().__init__(
            project_client=project_client,
            model=model,
            instructions="""You are a medical expert specialized in analyzing patient vital signs.
            Assess vital sign measurements and identify any concerning patterns or anomalies."""
        )

class AdverseEventAgent(SpecializedAgent):
    """Agent specialized in assessing adverse events."""
    
    def __init__(self, project_client: AIProjectClient, model: str):
        super().__init__(
            project_client=project_client,
            model=model,
            instructions="""You are a medical expert specialized in analyzing adverse events in clinical trials.
            Assess the severity and potential implications of reported adverse events."""
        )

class DataSummaryAgent(SpecializedAgent):
    """Agent specialized in summarizing trial data."""
    
    def __init__(self, project_client: AIProjectClient, model: str):
        super().__init__(
            project_client=project_client,
            model=model,
            instructions="""You are a clinical trial data analyst specialized in summarizing trial events.
            Generate concise summaries of trial data and identify key patterns or trends."""
        )
