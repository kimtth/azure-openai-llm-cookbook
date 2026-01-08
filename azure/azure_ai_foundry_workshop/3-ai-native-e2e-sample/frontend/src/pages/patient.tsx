import { useState } from "react"
import { Button } from "../components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import { Input } from "../components/ui/input"
import { Label } from "../components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select"
import { Textarea } from "../components/ui/textarea"
import { api } from "../lib/api"
import type { PatientData, EligibilityResponse } from "../types/api"

export function PatientPage() {
  const [patientData, setPatientData] = useState<PatientData>({
    age: '',
    gender: '',
    conditions: '',
    medications: ''
  })
  const [eligibility, setEligibility] = useState<EligibilityResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleCheckEligibility = async () => {
    if (!patientData.age || !patientData.gender) {
      setError('Please fill in at least age and gender')
      return
    }

    setLoading(true)
    setError(null)
    try {
      const { data, error: apiError } = await api.checkEligibility(patientData)
      if (apiError) {
        throw new Error(apiError)
      }
      setEligibility(data ?? null)
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to check eligibility')
      setEligibility(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">Clinical Trial Eligibility Explorer</h1>
        <p className="text-base sm:text-lg text-muted-foreground mt-2">
          Explore potential clinical trial matches based on patient information. This is a demonstration tool and not intended for medical decisions.
        </p>
      </div>

      {error && (
        <Card className="border-destructive">
          <CardContent className="p-6">
            <p className="text-center text-destructive">{error}</p>
          </CardContent>
        </Card>
      )}

      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Patient Information</CardTitle>
          </CardHeader>
          <CardContent>
            <form className="space-y-4" onSubmit={(e) => e.preventDefault()}>
              <div className="space-y-2">
                <Label htmlFor="age">Age</Label>
                <Input
                  id="age"
                  type="number"
                  value={patientData.age}
                  onChange={(e) => setPatientData({ ...patientData, age: e.target.value })}
                  placeholder="Enter age"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="gender">Gender</Label>
                <Select 
                  value={patientData.gender} 
                  onValueChange={(value) => setPatientData({ ...patientData, gender: value })}
                >
                  <SelectTrigger id="gender">
                    <SelectValue placeholder="Select gender" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="male">Male</SelectItem>
                    <SelectItem value="female">Female</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="conditions">Pre-existing Conditions</Label>
                <Textarea
                  id="conditions"
                  value={patientData.conditions}
                  onChange={(e) => setPatientData({ ...patientData, conditions: e.target.value })}
                  placeholder="Enter pre-existing conditions (e.g., Type 2 Diabetes, Hypertension)"
                  className="resize-none"
                  rows={3}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="medications">Current Medications</Label>
                <Textarea
                  id="medications"
                  value={patientData.medications}
                  onChange={(e) => setPatientData({ ...patientData, medications: e.target.value })}
                  placeholder="Enter current medications (e.g., Metformin, Lisinopril)"
                  className="resize-none"
                  rows={3}
                />
              </div>

              <Button 
                onClick={handleCheckEligibility} 
                disabled={loading || !patientData.age || !patientData.gender}
                variant="outline"
                className="w-full border-2 hover:bg-primary hover:text-primary-foreground transition-colors"
              >
                {loading ? (
                  <div className="flex items-center justify-center space-x-2">
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"></div>
                    <span>Checking Eligibility...</span>
                  </div>
                ) : (
                  'Check Eligibility'
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Eligibility Results</h2>
          {eligibility ? (
            <Card>
              <CardContent className="p-6 space-y-6">
                <div>
                  <h3 className="font-medium mb-2">Initial Assessment</h3>
                  <p className="text-muted-foreground">{eligibility.classification.status}</p>
                </div>

                <div>
                  <h3 className="font-medium mb-2">Confidence Score</h3>
                  <p className="text-muted-foreground">{(eligibility.classification.confidence * 100).toFixed(1)}%</p>
                </div>

                {eligibility.classification.matched_trials.length > 0 && (
                  <div>
                    <h3 className="font-medium mb-2">Potential Trial Matches</h3>
                    <div className="flex flex-wrap gap-2">
                      {eligibility.classification.matched_trials.map((trial, index) => (
                        <span key={index} className="px-2 py-1 bg-secondary rounded-md text-sm">
                          {trial}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <div>
                  <h3 className="font-medium mb-2">AI Summary</h3>
                  <p className="text-muted-foreground whitespace-pre-wrap">{eligibility.ai_explanation}</p>
                </div>

                <div className="mt-4 p-4 bg-muted rounded-lg">
                  <p className="text-sm text-muted-foreground italic">
                    {eligibility.disclaimer || "This is a demonstration tool only. Please consult healthcare professionals for actual clinical trial eligibility assessment."}
                  </p>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="p-6">
                <p className="text-muted-foreground">
                  Enter patient information and click "Check Eligibility" to see potential clinical trial matches. This tool provides general guidance only.
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
