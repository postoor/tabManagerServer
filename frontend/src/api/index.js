import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

// Attach token from localStorage
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle 401 -> redirect to login
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api

// ─── Auth ─────────────────────────────────────────────────────────────────────
export const authApi = {
  register: (email, password) =>
    api.post('/auth/register', { email, password }),
  login: (email, password) =>
    api.post('/auth/login', { email, password }),
  me: () => api.get('/auth/me'),
}

// ─── Bookmarks ────────────────────────────────────────────────────────────────
export const bookmarksApi = {
  getCollections: () => api.get('/bookmarks/'),
  createCollection: (data) => api.post('/bookmarks/collections', data),
  updateCollection: (id, data) => api.put(`/bookmarks/collections/${id}`, data),
  deleteCollection: (id) => api.delete(`/bookmarks/collections/${id}`),
  addBookmark: (collectionId, data) =>
    api.post(`/bookmarks/collections/${collectionId}/bookmarks`, data),
  updateBookmark: (id, data) => api.put(`/bookmarks/bookmarks/${id}`, data),
  deleteBookmark: (id) => api.delete(`/bookmarks/bookmarks/${id}`),
  reorder: (type, items) => api.post('/bookmarks/reorder', { type, items }),
}

// ─── Sync ─────────────────────────────────────────────────────────────────────
export const syncApi = {
  push: (data) => api.post('/sync/push', data),
  pull: () => api.get('/sync/pull'),
  status: () => api.get('/sync/status'),
}
