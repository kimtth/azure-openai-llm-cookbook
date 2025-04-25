"use client"

import { Card, CardContent, CardHeader, CardTitle } from "../ui/card"

export function AnalysisPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-4xl font-bold">Analysis</h1>
        <p className="text-lg text-muted-foreground mt-2">
          Analyze molecular structures and properties
        </p>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Molecular Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Upload or input molecular data for analysis.
          </p>
        </CardContent>
      </Card>
    </div>
  )
} 