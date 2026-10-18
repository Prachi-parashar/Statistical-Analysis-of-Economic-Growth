import { apiFetch } from './apiClient'

export async function getDescriptiveStatistics() {
  return apiFetch('/api/statistics/descriptive')
}

export async function getSummaryStatistics() {
  return apiFetch('/api/descriptive-statistics/summary')
}

export async function getProbability() {
  return apiFetch('/api/probability')
}

export async function getNormalityTests() {
  return apiFetch('/api/probability/normality-tests')
}

export async function getDistributionAnalysis() {
  return apiFetch('/api/statistics/distribution')
}

export async function getStatisticalInterpretations() {
  return apiFetch('/api/statistics/interpretations')
}

export default {
  getDescriptiveStatistics,
  getSummaryStatistics,
  getProbability,
  getNormalityTests,
  getDistributionAnalysis,
  getStatisticalInterpretations,
}
