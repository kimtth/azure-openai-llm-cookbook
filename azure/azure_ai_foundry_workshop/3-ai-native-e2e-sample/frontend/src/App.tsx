import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider } from './components/theme-provider'
import { MainLayout } from './components/layout/main-layout'
import { HomePage } from './pages/home'
import { MedicationPage } from './pages/medication'
import { TrialsPage } from './pages/trials'
import { LiteraturePage } from './pages/literature'
import { Toaster } from './components/ui/toaster'
import { PatientPage } from './pages/patient'

function App() {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="app-theme">
      <Router>
        <MainLayout>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/medication" element={<MedicationPage />} />
            <Route path="/trials" element={<TrialsPage />} />
            <Route path="/literature" element={<LiteraturePage />} />
            <Route path="/patient" element={<PatientPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </MainLayout>
      </Router>
      <Toaster />
    </ThemeProvider>
  )
}

export default App
