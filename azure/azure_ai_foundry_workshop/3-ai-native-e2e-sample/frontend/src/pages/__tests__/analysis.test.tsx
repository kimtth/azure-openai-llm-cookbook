import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { AnalysisPage } from '../analysis'
import { api } from '../../lib/api'
import { vi } from 'vitest'

// Mock the API
vi.mock('../../lib/api', () => ({
  api: {
    analyzeMedication: vi.fn()
  }
}))

describe('AnalysisPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders medication input form', () => {
    render(<AnalysisPage />)
    
    expect(screen.getByText('Medication Info Summaries')).toBeInTheDocument()
    expect(screen.getByLabelText('Medication Name')).toBeInTheDocument()
    expect(screen.getByLabelText('Additional Notes (Optional)')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /analyze medication/i })).toBeInTheDocument()
  })

  it('handles medication input', () => {
    render(<AnalysisPage />)
    
    const nameInput = screen.getByLabelText('Medication Name')
    const notesInput = screen.getByLabelText('Additional Notes (Optional)')
    
    fireEvent.change(nameInput, { target: { value: 'Aspirin' } })
    fireEvent.change(notesInput, { target: { value: 'Daily low-dose' } })
    
    expect(nameInput).toHaveValue('Aspirin')
    expect(notesInput).toHaveValue('Daily low-dose')
  })

  it('disables submit button without medication name', () => {
    render(<AnalysisPage />)
    
    const nameInput = screen.getByLabelText('Medication Name')
    fireEvent.change(nameInput, { target: { value: '' } })
    
    const submitButton = screen.getByRole('button', { name: /analyze medication/i })
    expect(submitButton).toBeDisabled()
  })

  it('handles successful API response', async () => {
    const mockResponse = {
      structured_info: {
        category: 'Over-the-counter analgesic',
        common_side_effects: ['Stomach upset', 'Headache'],
        risk_rating: 'Low',
        interactions: ['Blood thinners', 'NSAIDs']
      },
      ai_explanation: 'Test explanation',
      disclaimer: 'This information is for educational purposes only.'
    }
    
    vi.mocked(api.analyzeMedication).mockResolvedValueOnce({ data: mockResponse })
    
    render(<AnalysisPage />)
    
    const nameInput = screen.getByLabelText('Medication Name')
    fireEvent.change(nameInput, { target: { value: 'Aspirin' } })
    
    const submitButton = screen.getByRole('button', { name: /analyze medication/i })
    fireEvent.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByText('Over-the-counter analgesic')).toBeInTheDocument()
      expect(screen.getByText('Stomach upset')).toBeInTheDocument()
      expect(screen.getByText('Low')).toBeInTheDocument()
      expect(screen.getByText('Test explanation')).toBeInTheDocument()
      expect(screen.getByText(/educational purposes only/i)).toBeInTheDocument()
    })
  })

  it('handles API error', async () => {
    vi.mocked(api.analyzeMedication).mockRejectedValueOnce(new Error('Test error'))
    
    render(<AnalysisPage />)
    
    const nameInput = screen.getByLabelText('Medication Name')
    fireEvent.change(nameInput, { target: { value: 'Aspirin' } })
    
    const submitButton = screen.getByRole('button', { name: /analyze medication/i })
    fireEvent.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByText('Test error')).toBeInTheDocument()
    })
  })

  it('shows loading state during API call', async () => {
    vi.mocked(api.analyzeMedication).mockImplementationOnce(() => new Promise(resolve => setTimeout(resolve, 100)))
    
    render(<AnalysisPage />)
    
    const nameInput = screen.getByLabelText('Medication Name')
    fireEvent.change(nameInput, { target: { value: 'Aspirin' } })
    
    const submitButton = screen.getByRole('button', { name: /analyze medication/i })
    fireEvent.click(submitButton)
    
    expect(screen.getByText('Analyzing...')).toBeInTheDocument()
    
    await waitFor(() => {
      expect(screen.queryByText('Analyzing...')).not.toBeInTheDocument()
    })
  })
})
