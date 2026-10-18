import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { ThemeProvider } from './context/ThemeContext.jsx'
import Sidebar from './components/Sidebar.jsx'
import Header from './components/Header.jsx'
import ErrorBoundary from './components/ErrorBoundary.jsx'
import Dashboard             from './pages/Dashboard.jsx'
import Dataset               from './pages/Dataset.jsx'
import DescriptiveStatistics from './pages/DescriptiveStatistics.jsx'
import ProbabilityDistribution from './pages/ProbabilityDistribution.jsx'
import Correlation           from './pages/Correlation.jsx'
import Regression            from './pages/Regression.jsx'
import Diagnostics           from './pages/Diagnostics.jsx'
import Reports               from './pages/Reports.jsx'
import About                 from './pages/About.jsx'

export default function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <div className="flex h-screen overflow-hidden bg-slate-50 dark:bg-slate-900 text-slate-800 dark:text-slate-100 transition-colors duration-150">
          <Sidebar />
          <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
            <Header />
            <main className="flex-1 overflow-y-auto bg-slate-50 dark:bg-slate-900">
              <ErrorBoundary title="Application Route Error">
                <Routes>
                  <Route path="/"                       element={<Dashboard />} />
                  <Route path="/dataset"                element={<Dataset />} />
                  <Route path="/descriptive-statistics" element={<DescriptiveStatistics />} />
                  <Route path="/probability"            element={<ProbabilityDistribution />} />
                  <Route path="/correlation"            element={<Correlation />} />
                  <Route path="/regression"             element={<Regression />} />
                  <Route path="/diagnostics"            element={<Diagnostics />} />
                  <Route path="/reports"                element={<Reports />} />
                  <Route path="/about"                  element={<About />} />
                </Routes>
              </ErrorBoundary>
            </main>
          </div>
        </div>
      </BrowserRouter>
    </ThemeProvider>
  )
}
