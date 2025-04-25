// This file defines the API types used by the frontend to interact with backend endpoints
// such as trial event simulation, multi-agent responses, and clinical trial data.
export interface ChatMessage {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: string
}

export interface ChatResponse {
  messages: ChatMessage[]
  error?: string
}

export interface PatientData {
  age: string
  gender: string
  conditions: string
  medications: string
}

export interface MoleculeData {
  smiles: string
  name?: string
  properties?: {
    molecularWeight?: number
    logP?: number
    hBondDonors?: number
    hBondAcceptors?: number
  }
}

export interface LiteratureSearchResult {
  title: string
  authors: string[]
  abstract: string
  publicationDate: string
  doi?: string
}

export interface ClinicalTrialData {
  id: string
  phase: number
  status: string
  startDate: string
  completionDate?: string
  participants: number
  conditions: string[]
  interventions: string[]
}

export interface PredictionResult {
  efficacy: number
  sideEffects: string[]
  confidence: number
  recommendations: string[]
}

export interface AnalysisResult {
  properties: MoleculeData['properties']
  predictions: {
    toxicity: number
    drugLikeness: number
    synthesizability: number
  }
  similarCompounds: string[]
}

export interface Document {
  title: string;
  abstract?: string;
  content?: string;
  authors: string[];
  relevance: number;
  journal?: string;
  year?: number;
}

export interface SearchResponse {
  query: string;
  summary: string;
  agent_id: string;
  data?: {
    category?: string;
    risk_rating?: string;
    side_effects?: string[];
    interactions?: string[];
  };
}

export interface TrialResponse {
  trials: ClinicalTrialData[]
  totalTrials: number
  page: number
  pageSize: number
}

export interface DigitalTwinResponse {
  population_size: number
  toxicity_scores: {
    mean: number
    std: number
  }
  efficacy_metrics: {
    response_rate: number
    survival_gain: string
  }
  adverse_events: {
    mild: number
    moderate: number
    severe: number
  }
  agent_id: string
}

export interface MedicationInfo {
  name: string;
  notes?: string;
}

export interface MedicationAnalysis {
  structured_info: {
    category: string;
    common_side_effects: string[];
    risk_rating: string;
    interactions: string[];
  };
  ai_explanation: string;
  disclaimer: string;
}

export interface EligibilityRequest {
  age: string;
  gender: string;
  conditions: string;
  medications: string;
}

export interface EligibilityResponse {
  classification: {
    status: 'Likely Eligible' | 'Ineligible';
    confidence: number;
    matched_trials: string[];
  };
  ai_explanation: string;
  disclaimer: string;
}

export interface TrialEvent {
  trialId: string;
  patientId: string;
  studyArm: string;
  timestamp: string;
  vitals: {
    heartRate: number;
    bloodPressure: string;
    temperature: number;
    respiratoryRate: number;
    oxygenSaturation: number;
  };
  adverseEvents: Array<{
    type: string;
    description: string | null;
  }>;
}

export interface TrialEventAnalysis {
  vitals_analysis?: string;
  adverse_events_analysis?: string;
  summary: string;
}

export interface TrialEventResponse {
  status: string;
  message: string;
  events: TrialEvent[];
}
