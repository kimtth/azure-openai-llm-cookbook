import { useState, useEffect } from "react"
import { Button } from "../components/ui/button"
import { Card, CardContent } from "../components/ui/card"
import { RefreshCw } from "lucide-react"
import { api } from "../lib/api"
import type { TrialEvent } from "../types/api"
import { TrialVisualization } from "../components/trial-visualization"

export function TrialsPage() {
  const [events, setEvents] = useState<TrialEvent[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [simulationActive, setSimulationActive] = useState(false)

  const simulateTrialData = async () => {
    setLoading(true)
    setError(null)
    try {
      console.log('Calling simulateTrialData API...')
      const { data, error: apiError } = await api.simulateTrialData()
      
      console.log('API Response:', { data, error: apiError })
      
      if (apiError) {
        throw new Error(apiError)
      }

      if (!data || typeof data !== 'object') {
        console.error('No data received from API')
        throw new Error("No data received from API")
      }

      setEvents(data.events)
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Failed to simulate trial data"
      console.error('Trial simulation error:', error)
      setError(errorMessage)
      setEvents([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    let interval: NodeJS.Timeout
    if (simulationActive) {
      interval = setInterval(simulateTrialData, 5000)
    }
    return () => clearInterval(interval)
  }, [simulationActive])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center space-y-4">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
          <p className="text-muted-foreground">Loading clinical trials data...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-bold">Clinical Trials Monitor</h1>
          <p className="text-lg text-muted-foreground mt-2">
            Monitor and analyze ongoing clinical trials.
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-4">
            <Button
              onClick={() => setSimulationActive(!simulationActive)}
              variant="outline"
              className="border-2"
              disabled={loading}
            >
              <div className="flex items-center space-x-2">
                <RefreshCw className={`h-4 w-4 ${simulationActive ? 'animate-spin' : ''}`} />
                <span>{simulationActive ? "Stop Simulation" : "Start Continuous Simulation"}</span>
              </div>
            </Button>
            <Button
              onClick={simulateTrialData}
              disabled={loading || simulationActive}
              variant="outline"
              className="border-2"
            >
              {loading ? (
                <div className="flex items-center space-x-2">
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"></div>
                  <span>Simulating...</span>
                </div>
              ) : (
                <div className="flex items-center space-x-2">
                  <RefreshCw className="h-4 w-4" />
                  <span>Single Event</span>
                </div>
              )}
            </Button>
          </div>
        </div>
      </div>

      {error && (
        <Card className="border-destructive">
          <CardContent className="p-6">
            <p className="text-center text-destructive">{error}</p>
          </CardContent>
        </Card>
      )}

      <TrialVisualization
        events={events}
        data={events.map(event => ({
          timestamp: event.timestamp,
          efficacy: Math.random() * 100,
          safety: Math.random() * 100,
          adherence: Math.random() * 100
        }))}
      />
    </div>
  )
}
