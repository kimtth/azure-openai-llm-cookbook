import { useEffect, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { Card, CardContent } from "./ui/card"
import { cn } from "../lib/utils"
import { motion, AnimatePresence } from "framer-motion"
import { AgentWorkflow } from "./agents/agent-workflow"
import type { TrialEvent, TrialEventAnalysis } from "../types/api"

interface TrialVisualizationProps {
  data: Array<{
    timestamp: string
    efficacy: number
    safety: number
    adherence: number
  }>
  events?: TrialEvent[]
  className?: string
}

export function TrialVisualization({ data, events = [], className }: TrialVisualizationProps) {
  const [eventLog, setEventLog] = useState<TrialEvent[]>([])
  const [currentAnalysis, setCurrentAnalysis] = useState<TrialEventAnalysis>()
  const [processing, setProcessing] = useState(false)

  useEffect(() => {
    if (events.length > 0) {
      setEventLog(prev => [...prev, ...events].slice(-10))
      setProcessing(true)
      // Simulate agent processing time
      setTimeout(() => {
        setProcessing(false)
        const latestEvent = events[events.length - 1]
        setCurrentAnalysis({
          vitals_analysis: `Analysis of vital signs: HR=${latestEvent.vitals.heartRate}, BP=${latestEvent.vitals.bloodPressure}, Temp=${latestEvent.vitals.temperature}°C`,
          adverse_events_analysis: latestEvent.adverseEvents.length > 0 
            ? `Found ${latestEvent.adverseEvents.length} adverse events: ${latestEvent.adverseEvents.map(ae => ae.type).join(', ')}` 
            : undefined,
          summary: `Trial ${latestEvent.trialId} proceeding as expected. Patient ${latestEvent.patientId} in ${latestEvent.studyArm} arm shows stable indicators.`
        })
      }, 2000)
    }
  }, [events])

  return (
    <div className="space-y-6">
      <Card className={cn("w-full", className)}>
        <CardContent className="p-6">
          <h3 className="text-lg font-semibold mb-4">Trial Metrics Over Time</h3>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data}>
                <XAxis 
                  dataKey="timestamp" 
                  tickFormatter={(value) => new Date(value).toLocaleDateString()}
                />
                <YAxis />
                <Tooltip
                  labelFormatter={(value) => new Date(value).toLocaleString()}
                  contentStyle={{
                    backgroundColor: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))"
                  }}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="efficacy" 
                  stroke="hsl(217.2 91.2% 59.8%)"
                  strokeWidth={2}
                  dot={{ r: 4 }}
                  name="Efficacy"
                  animationDuration={1000}
                />
                <Line 
                  type="monotone" 
                  dataKey="safety" 
                  stroke="hsl(142.1 76.2% 36.3%)"
                  strokeWidth={2}
                  dot={{ r: 4 }}
                  name="Safety"
                  animationDuration={1000}
                />
                <Line 
                  type="monotone" 
                  dataKey="adherence" 
                  stroke="hsl(346.8 77.2% 49.8%)"
                  strokeWidth={2}
                  dot={{ r: 4 }}
                  name="Adherence"
                  animationDuration={1000}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <AgentWorkflow
        analysis={currentAnalysis}
        processing={processing}
      />

      <Card>
        <CardContent className="p-6">
          <h3 className="text-lg font-semibold mb-4">Event Log</h3>
          <div className="space-y-2">
            <AnimatePresence>
              {eventLog.map((event, index) => (
                <motion.div
                  key={`${event.timestamp}-${index}`}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className="p-3 bg-muted rounded-md"
                >
                  <div className="flex justify-between text-sm">
                    <span className="font-medium">Trial {event.trialId}</span>
                    <span className="text-muted-foreground">
                      {new Date(event.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <div className="mt-2 space-y-2 text-sm">
                    <p>Patient: {event.patientId} ({event.studyArm})</p>
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <span className="text-muted-foreground">Heart Rate:</span> {event.vitals.heartRate} bpm
                      </div>
                      <div>
                        <span className="text-muted-foreground">BP:</span> {event.vitals.bloodPressure}
                      </div>
                    </div>
                    {event.adverseEvents.length > 0 && (
                      <div className="mt-1">
                        <span className="text-muted-foreground">Adverse Events:</span>{' '}
                        {event.adverseEvents.map(ae => ae.type).join(', ')}
                      </div>
                    )}
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
