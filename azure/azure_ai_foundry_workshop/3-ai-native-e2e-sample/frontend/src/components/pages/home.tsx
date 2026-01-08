"use client"

// Remove unused import
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card"

export function HomePage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-4xl font-bold">Drug Discovery Platform</h1>
        <p className="text-lg text-muted-foreground mt-2">
          Welcome to the AI-powered drug discovery platform
        </p>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Overview</CardTitle>
        </CardHeader>
        <CardContent>
          <p>
            This platform provides tools for:
          </p>
          <ul className="list-disc list-inside mt-2 space-y-1">
            <li>Molecular analysis and design</li>
            <li>Clinical trial data analysis</li>
            <li>Literature research</li>
            <li>Patient response prediction</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}  