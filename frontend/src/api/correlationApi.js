import { apiFetch } from './apiClient'

export async function getPearsonCorrelation() {
  return apiFetch('/api/correlation/pearson')
}

export async function getSpearmanCorrelation() {
  return apiFetch('/api/correlation/spearman')
}

export async function getPredictorCorrelationCheck() {
  return apiFetch('/api/correlation/predictor-check')
}

export async function getCorrelationAnalysis() {
  return apiFetch('/api/statistics/correlation')
}

export default {
  getPearsonCorrelation,
  getSpearmanCorrelation,
  getPredictorCorrelationCheck,
  getCorrelationAnalysis,
}
