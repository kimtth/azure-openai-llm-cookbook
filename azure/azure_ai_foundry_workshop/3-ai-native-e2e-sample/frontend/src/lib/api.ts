import type { MedicationAnalysis, MedicationInfo, TrialEvent } from "../types/api";
import { API_URL, API_VERSION } from '../config'

interface ApiResponse<T> {
  data: T | null;
  error: string | null;
}

export interface ApiEvent {
  type: string;
  content: any;
}

export const api = {
   analyzeMedication: async (
    { name, notes }: MedicationInfo,
    onEvent: (event: ApiEvent) => void
  ): Promise<ApiResponse<MedicationAnalysis>> => {
    try {
      const response = await fetch(`${API_URL}/agents/medication/analyze_stream`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'x-api-version': API_VERSION,
        },
        body: JSON.stringify({ name, notes })
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || 'Failed to analyze medication');
      }
      
      if (!response.body) {
        throw new Error('No response body received');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let finalResult: MedicationAnalysis | null = null;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.slice(6).trim();
            if (!dataStr) continue;
            try {
              const parsed = JSON.parse(dataStr);
              if (parsed.type === 'error') {
                throw new Error(parsed.content);
              }
              if (parsed.type === 'message') {
                // Pass run status messages to UI
                onEvent({ type: 'message', content: parsed.content });
              }
              if (parsed.done === true) {
                // Final result received
                finalResult = parsed.content;
                onEvent({ type: 'final', content: parsed.content });
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e);
            }
          }
        }
      }
      
      if (!finalResult) {
        throw new Error('Stream ended without valid final response');
      }
      
      return { data: finalResult, error: null };
    } catch (error) {
      return { 
        data: null, 
        error: error instanceof Error ? error.message : 'Failed to analyze medication'
      };
    }
  },

  simulateTrialData: async (): Promise<ApiResponse<{ events: TrialEvent[] }>> => {
    try {
      const response = await fetch(`${API_URL}/api/trials/simulate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-version': API_VERSION,
        }
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(error || 'Failed to simulate trial data');
      }

      const data = await response.json();
      return { data, error: null };
    } catch (error) {
      return {
        data: null,
        error: error instanceof Error ? error.message : 'Failed to simulate trial data'
      };
    }
  }
};

export interface LiteratureSearchResponse {
  results: string[]
  summary?: string
  error?: string
}

export interface LiteratureChatResponse {
  response: string
  error?: string
}

export interface LiteratureChatRequest {
  message: string
  history?: Array<{ role: 'user' | 'assistant', content: string }>
}

export const literatureApi = {
  chat: async (message: string) => {
    const response = await fetch(`${API_URL}/api/agents/literature-chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-version': API_VERSION,
      },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      throw new Error('Failed to chat with literature agent');
    }

    return response.body;
  }
};
