"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card"
import { api } from "../../lib/api"

export function TrialsPage() {
  const [trials, setTrials] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadTrials() {
      try {
        const data = await api.getTrials()
        setTrials(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load trials')
      } finally {
        setLoading(false)
      }
    }

    loadTrials()
  }, [])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-4xl font-bold">Clinical Trials</h1>
        <p className="text-lg text-muted-foreground mt-2">
          Monitor and analyze clinical trial data
        </p>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Active Trials</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p className="text-muted-foreground">Loading trials...</p>
          ) : error ? (
            <p className="text-red-500">{error}</p>
          ) : trials.length === 0 ? (
            <p className="text-muted-foreground">No active trials found.</p>
          ) : (
            <div className="space-y-4">
              {trials.map(trial => (
                <div key={trial.id} className="p-4 border rounded-lg">
                  <h3 className="font-medium">{trial.name}</h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    {trial.description}
                  </p>
                  <div className="flex gap-2 mt-2 text-sm">
                    <span className="px-2 py-1 bg-primary/10 rounded-full">
                      Phase {trial.phase}
                    </span>
                    <span className="px-2 py-1 bg-secondary/10 rounded-full">
                      {trial.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}