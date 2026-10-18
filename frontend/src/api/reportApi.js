import { apiFetch, getApiResourceUrl } from './apiClient'

export async function getReportInfo() {
  return apiFetch('/api/report')
}

export async function getFigures() {
  return apiFetch('/api/figures')
}

export function getFigureUrl(path) {
  return getApiResourceUrl(`/api/figures/${path}`)
}

export function getReportPdfUrl(bustCache = true) {
  const base = getApiResourceUrl('/api/report/pdf')
  return bustCache ? `${base}?t=${Date.now()}` : base
}

export function getReportMdUrl(bustCache = true) {
  const base = getApiResourceUrl('/api/report/md')
  return bustCache ? `${base}?t=${Date.now()}` : base
}

export function getTableUrl(filename) {
  return getApiResourceUrl(`/api/tables/${filename}`)
}

export async function getTableJson(filename) {
  return apiFetch(`/api/tables/json/${filename}`)
}

export async function runAnalysis() {
  return apiFetch('/api/analysis/run', { method: 'POST' })
}

export async function getCurrentAnalysis() {
  return apiFetch('/api/analysis/current')
}

export default {
  getReportInfo,
  getFigures,
  getFigureUrl,
  getReportPdfUrl,
  getReportMdUrl,
  getTableUrl,
  getTableJson,
  runAnalysis,
  getCurrentAnalysis,
}
