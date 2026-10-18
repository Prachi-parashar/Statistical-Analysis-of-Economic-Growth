import { apiFetch } from './apiClient'

export async function getSimpleRegression() {
  return apiFetch('/api/regression/simple')
}

export async function getMultipleRegression() {
  return apiFetch('/api/regression/multiple')
}

export async function getRobustRegression() {
  return apiFetch('/api/regression/robust')
}

export async function getModelComparison() {
  return apiFetch('/api/regression/model-comparison')
}

export async function getRegressionAnalysis() {
  return apiFetch('/api/statistics/regression')
}

export default {
  getSimpleRegression,
  getMultipleRegression,
  getRobustRegression,
  getModelComparison,
  getRegressionAnalysis,
}
