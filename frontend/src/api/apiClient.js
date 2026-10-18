const BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/+$/, '')

/**
 * Generic fetch wrapper for backend API calls
 * @param {string} endpoint - Path relative to base URL (e.g. '/api/project')
 * @param {RequestInit} [options] - Fetch options
 * @returns {Promise<any>} Parsed JSON response
 */
export async function apiFetch(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`
  
  const headers = {
    'Accept': 'application/json',
    ...options.headers,
  }

  try {
    const res = await fetch(url, { ...options, headers })
    if (!res.ok) {
      const errorText = await res.text().catch(() => '')
      let errorJson
      try { errorJson = JSON.parse(errorText) } catch (e) { /* ignore */ }
      const message = errorJson?.detail || errorJson?.reason || `HTTP ${res.status}: ${res.statusText}`
      throw new Error(message)
    }
    return await res.json()
  } catch (err) {
    if (err.name === 'TypeError' && err.message.includes('fetch')) {
      throw new Error('Failed to connect to backend server. Please check if FastAPI is running.')
    }
    throw err
  }
}

/**
 * Get full URL for absolute resources like figures, pdfs, tables
 * @param {string} path - Relative endpoint path
 * @returns {string} Full URL string
 */
export function getApiResourceUrl(path) {
  return `${BASE_URL}${path.startsWith('/') ? '' : '/'}${path}`
}

export default {
  fetch: apiFetch,
  getResourceUrl: getApiResourceUrl,
  BASE_URL,
}
