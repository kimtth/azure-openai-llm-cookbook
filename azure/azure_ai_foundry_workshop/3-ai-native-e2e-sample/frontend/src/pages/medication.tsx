import { useState } from "react"
import { Card, CardContent } from "../components/ui/card"
import { Input } from "../components/ui/input"
import { Textarea } from "../components/ui/textarea"
import { Button } from "../components/ui/button"
import { api } from "../lib/api"
import type { MedicationAnalysis } from "../types/api"

import { motion, AnimatePresence } from "framer-motion"
import { FlaskConical } from "lucide-react"

export function MedicationPage() {
  const [name, setName] = useState("")
  const [notes, setNotes] = useState("")
  const [loading, setLoading] = useState(false)
  const [finalResult, setFinalResult] = useState<MedicationAnalysis | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [statusMessages, setStatusMessages] = useState<string[]>([])

  const analyzeMedication = async () => {
    setLoading(true)
    setError(null)
    setFinalResult(null)
    setStatusMessages([])
    try {
      const res = await api.analyzeMedication({ name, notes }, (event) => {
        if (event.type === "message") {
          setStatusMessages((prev) => [...prev, event.content])
        } else if (event.type === "final") {
          setFinalResult(event.content)
        }
      })
      if (res.error) {
        throw new Error(res.error)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to analyze medication")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-1">
        <h1 className="text-4xl font-bold">Medication Analysis</h1>
        <p className="text-lg text-muted-foreground">
          Analyze medication properties and potential interactions
        </p>
      </div>

      {/* Input Card */}
      <Card>
        <CardContent className="p-6 space-y-4">
          <Input
            placeholder="Enter medication name (e.g. 'Aspirin')"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <Textarea
            placeholder="Additional notes or context (optional)"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />

          <Button
            variant="outline"
            className="flex items-center justify-center gap-2 transition-colors duration-200"
            onClick={analyzeMedication}
            disabled={loading || !name}
          >
            <FlaskConical className="h-4 w-4" />
            {loading ? "Analyzing..." : "Analyze Medication"}
          </Button>
        </CardContent>
      </Card>

      {/* Error Display */}
      {error && (
        <Card className="border-destructive">
          <CardContent className="p-6">
            <p className="text-center text-destructive">{error}</p>
          </CardContent>
        </Card>
      )}

      {/* Show a spinner if loading but no messages yet */}
      <AnimatePresence>
        {loading && statusMessages.length === 0 && (
          <motion.div
            key="loadingSpinner"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="flex items-center justify-center"
          >
            <div className="flex flex-col items-center gap-2 py-4">
              {/* Tailwind spinner style */}
              <div className="animate-spin h-8 w-8 border-4 border-current border-t-transparent rounded-full" />
              <p className="text-muted-foreground">Starting analysis...</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Progress Messages */}
      <AnimatePresence>
        {loading && statusMessages.length > 0 && (
          <motion.div
            key="progressCard"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            <Card>
              <CardContent className="p-6">
                <h2 className="text-xl font-medium mb-2">Progress</h2>
                <ul className="list-disc pl-6 space-y-1">
                  {statusMessages.map((msg, idx) => (
                    <motion.li
                      key={idx}
                      className="text-muted-foreground"
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.05 }}
                    >
                      {msg}
                    </motion.li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Final Result */}
      <AnimatePresence>
        {finalResult && (
          <motion.div
            key="analysisCard"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.4 }}
          >
            <Card>
              <CardContent className="p-6 space-y-4">
                <h2 className="text-2xl font-bold">Analysis Results</h2>

                <div>
                  <h3 className="font-medium mb-1">Analysis:</h3>
                  <p className="text-muted-foreground">
                    {finalResult.analysis || "N/A"}
                  </p>
                </div>

                <div>
                  <h3 className="font-medium mb-1">Interactions:</h3>
                  {finalResult.interactions?.length ? (
                    <ul className="list-disc pl-5">
                      {finalResult.interactions.map((item, i) => (
                        <li key={i}>{item}</li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-muted-foreground">N/A</p>
                  )}
                </div>

                <div>
                  <h3 className="font-medium mb-1">Warnings:</h3>
                  {finalResult.warnings?.length ? (
                    <ul className="list-disc pl-5">
                      {finalResult.warnings.map((item, i) => (
                        <li key={i}>{item}</li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-muted-foreground">N/A</p>
                  )}
                </div>

                <div>
                  <h3 className="font-medium mb-1">Recommendations:</h3>
                  {finalResult.recommendations?.length ? (
                    <ul className="list-disc pl-5">
                      {finalResult.recommendations.map((item, i) => (
                        <li key={i}>{item}</li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-muted-foreground">N/A</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
