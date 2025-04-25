import { AgentCard } from "./agent-card"
import type { TrialEventAnalysis } from "../../types/api"

export interface AgentWorkflowProps {
  analysis?: TrialEventAnalysis
  processing: boolean
}

export function AgentWorkflow({ analysis, processing }: AgentWorkflowProps) {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Agent Workflow</h3>
      <div className="grid gap-4 md:grid-cols-2">
        <AgentCard
          name="Team Leader"
          role="Orchestrates analysis and delegates tasks"
          status={processing ? "processing" : analysis ? "complete" : "idle"}
        />
        <AgentCard
          name="Vitals Agent"
          role="Analyzes patient vital signs"
          status={processing ? "processing" : analysis?.vitals_analysis ? "complete" : "idle"}
          result={analysis?.vitals_analysis}
        />
        <AgentCard
          name="Adverse Events Agent"
          role="Assesses adverse events"
          status={processing ? "processing" : analysis?.adverse_events_analysis ? "complete" : "idle"}
          result={analysis?.adverse_events_analysis}
        />
        <AgentCard
          name="Data Summary Agent"
          role="Summarizes trial data"
          status={processing ? "processing" : analysis?.summary ? "complete" : "idle"}
          result={analysis?.summary}
        />
      </div>
    </div>
  )
}
