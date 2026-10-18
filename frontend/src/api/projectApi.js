import { apiFetch } from './apiClient'

export async function getHealth() {
  return apiFetch('/api/health')
}

export async function getProjectInfo() {
  return apiFetch('/api/project')
}

export default {
  getHealth,
  getProjectInfo,
}
