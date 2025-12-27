/**
 * JWT Authentication utilities.
 * 
 * Handles JWT token storage, retrieval, and API request authentication.
 */

const TOKEN_KEY = 'jwt_access_token'
const REFRESH_TOKEN_KEY = 'jwt_refresh_token'

/**
 * Store JWT tokens in localStorage.
 */
export function setAuthTokens(accessToken: string, refreshToken: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(TOKEN_KEY, accessToken)
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken)
  }
}

/**
 * Get the current access token.
 */
export function getAccessToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem(TOKEN_KEY)
  }
  return null
}

/**
 * Get the current refresh token.
 */
export function getRefreshToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem(REFRESH_TOKEN_KEY)
  }
  return null
}

/**
 * Clear all stored tokens.
 */
export function clearAuthTokens(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
  }
}

/**
 * Check if user is authenticated (has a token).
 */
export function isAuthenticated(): boolean {
  return getAccessToken() !== null
}

/**
 * Get authorization header for API requests.
 */
export function getAuthHeader(): { Authorization: string } | {} {
  const token = getAccessToken()
  if (token) {
    return { Authorization: `Bearer ${token}` }
  }
  return {}
}

