import { apiFetch } from './apiClient'

export async function getDataset() {
  return apiFetch('/api/dataset')
}

export async function getMetadata() {
  return apiFetch('/api/dataset/metadata')
}

export async function getLiveData() {
  return apiFetch('/api/data/live')
}

export async function refreshLiveData() {
  return apiFetch('/api/data/refresh', { method: 'POST' })
}

export default {
  getDataset,
  getMetadata,
  getLiveData,
  refreshLiveData,
}
