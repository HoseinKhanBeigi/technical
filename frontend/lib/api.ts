/**
 * API client with JWT authentication.
 * 
 * Centralized axios instance with automatic token injection and refresh.
 */
import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosError } from 'axios'
import { getAccessToken, getRefreshToken, setAuthTokens, clearAuthTokens } from './auth'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false,  // JWT doesn't need cookies
})

// Request interceptor: Add JWT token to all requests
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getAccessToken()
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor: Handle token refresh on 401
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    // If 401 and not already retrying, try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = getRefreshToken()
        if (!refreshToken) {
          throw new Error('No refresh token available')
        }

        // Attempt to refresh the token
        const response = await axios.post(`${API_URL}/api/auth/jwt/refresh/`, {
          refresh: refreshToken,
        })

        const { access } = response.data
        const currentRefresh = getRefreshToken()

        // Update tokens
        if (currentRefresh) {
          setAuthTokens(access, currentRefresh)
        }

        // Retry original request with new token
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${access}`
        }

        return apiClient(originalRequest)
      } catch (refreshError) {
        // Refresh failed, clear tokens and redirect to login
        clearAuthTokens()
        if (typeof window !== 'undefined') {
          window.location.href = '/login'
        }
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

export default apiClient

