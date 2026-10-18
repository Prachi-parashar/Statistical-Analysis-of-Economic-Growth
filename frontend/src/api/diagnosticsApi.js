import { apiFetch } from './apiClient'

export async function getDiagnostics() {
  return apiFetch('/api/diagnostics')
}

export async function getVifResults() {
  return apiFetch('/api/diagnostics/vif')
}

export async function getRegressionDiagnostics() {
  return apiFetch('/api/statistics/diagnostics')
}

export default {
  getDiagnostics,
  getVifResults,
  getRegressionDiagnostics,
}
