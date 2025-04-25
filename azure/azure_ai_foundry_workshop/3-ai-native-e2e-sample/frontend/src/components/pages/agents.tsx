"use client"

import { Card, CardContent, CardHeader, CardTitle } from "../ui/card"

export function AgentsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-4xl font-bold">AI Agents</h1>
        <p className="text-lg text-muted-foreground mt-2">
          Manage and monitor AI agents for drug discovery
        </p>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Active Agents</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            No active agents found.
          </p>
        </CardContent>
      </Card>
    </div>
  )
} 