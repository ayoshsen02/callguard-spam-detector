import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('cg_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export const analyzeCall  = (text) => api.post('/analyze', { text })
export const verifyOTP    = (id_token) => api.post('/auth/verify-otp', { id_token })
export default api
