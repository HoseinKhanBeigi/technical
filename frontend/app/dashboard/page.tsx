'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import apiClient from '@/lib/api'
import { clearAuthTokens, getRefreshToken } from '@/lib/auth'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface UserData {
  id: number
  username: string
  email: string
  subscription_status: 'active' | 'inactive'
  current_plan: 'basic' | 'pro' | 'none'
  total_amount_paid: number
  lifetime_value: number
}

export default function Dashboard() {
  const router = useRouter()
  const [userData, setUserData] = useState<UserData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [updating, setUpdating] = useState(false)

  useEffect(() => {
    fetchUserData()
  }, [])

  const fetchUserData = async () => {
    try {
      setLoading(true)
      setError(null)
      // Use JWT-authenticated API client
      const response = await apiClient.get('/api/user/status/')
      if (response.data) {
        setUserData(response.data)
      } else {
        setError('No user data received')
      }
    } catch (err: any) {
      console.error('Error fetching user data:', err)
      // Handle different error cases
      if (err.response?.status === 401 || err.response?.status === 403) {
        // Not authenticated - clear tokens and redirect to login
        clearAuthTokens()
        setError('Please log in to continue')
        setTimeout(() => {
          router.push('/login')
        }, 1500)
      } else if (err.response?.status === 500) {
        setError('Server error. Please try again later.')
      } else if (err.code === 'ECONNREFUSED' || err.message?.includes('Network Error')) {
        setError('Cannot connect to server. Please check if the backend is running.')
      } else {
        setError(err.response?.data?.detail || err.response?.data?.error || 'Failed to fetch user data. Please try logging in again.')
      }
    } finally {
      setLoading(false)
    }
  }

  const updateSubscription = async (plan: 'basic' | 'pro' | 'none') => {
    try {
      setUpdating(true)
      setError(null)
      setSuccess(null)
      
      // Use JWT-authenticated API client
      const response = await apiClient.post('/api/user/subscription/', { plan })
      
      setUserData(response.data)
      const planName = plan === 'none' ? 'cancelled' : plan === 'basic' ? 'Basic Plan' : 'Pro Plan'
      setSuccess(`Successfully ${plan === 'none' ? 'cancelled' : 'subscribed to'} ${planName}!`)
      
      // Refresh data after a short delay to ensure webhook has processed
      setTimeout(() => {
        fetchUserData()
      }, 2000)
    } catch (err: any) {
      setError(err.response?.data?.error || err.response?.data?.detail || 'Failed to update subscription')
    } finally {
      setUpdating(false)
    }
  }

  const formatCurrency = (cents: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(cents / 100)
  }

  // Show loading state
  if (loading) {
    return (
      <div className="container">
        <div className="card">
          <div className="loading">Loading...</div>
        </div>
      </div>
    )
  }

  // Show error state if there's an error and no user data
  if (error && !userData) {
    return (
      <div className="container">
        <div className="card">
          <h1>Error</h1>
          <p>{error}</p>
          <div style={{ marginTop: '1rem' }}>
            <a href="/login" style={{ color: '#667eea', textDecoration: 'underline' }}>
              Go to Login
            </a>
          </div>
        </div>
      </div>
    )
  }

  // Show error if no user data after loading (fallback)
  if (!userData) {
    return (
      <div className="container">
        <div className="card">
          <h1>Error</h1>
          <p>Unable to load user data. Please make sure you are logged in.</p>
          <div style={{ marginTop: '1rem' }}>
            <a href="/login" style={{ color: '#667eea', textDecoration: 'underline' }}>
              Go to Login
            </a>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="container">
      {/* Header */}
      <div style={{ marginBottom: '2rem', textAlign: 'center' }}>
        <h1 style={{ color: 'white', fontSize: '2.5rem', fontWeight: 700, marginBottom: '0.5rem' }}>
          Billing Dashboard
        </h1>
        <p style={{ color: 'rgba(255, 255, 255, 0.9)', fontSize: '1.1rem' }}>
          Welcome back, {userData.username}!
        </p>
      </div>

      {/* Status Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
        <div className="stat-card">
          <h3>Current Plan</h3>
          <div className="stat-value">
            {userData.current_plan === 'basic' ? 'Basic' : 
             userData.current_plan === 'pro' ? 'Pro' : 
             'None'}
          </div>
          <div style={{ marginTop: '0.5rem', fontSize: '0.875rem', opacity: 0.9 }}>
            Status: <span style={{ fontWeight: 600, textTransform: 'capitalize' }}>
              {userData.subscription_status}
            </span>
          </div>
        </div>

        <div className="stat-card" style={{ background: 'linear-gradient(135deg, #2ecc71 0%, #27ae60 100%)' }}>
          <h3>Lifetime Value</h3>
          <div className="stat-value">
            {formatCurrency(userData.total_amount_paid)}
          </div>
          <div style={{ marginTop: '0.5rem', fontSize: '0.875rem', opacity: 0.9 }}>
            Total amount paid
          </div>
        </div>
      </div>

      {/* Main Card */}
      <div className="card">
        {error && <div className="error">{error}</div>}
        {success && <div className="success">{success}</div>}

        {/* Subscription Management */}
        <div style={{ marginBottom: '2rem' }}>
          <h2 style={{ fontSize: '1.75rem', marginBottom: '1.5rem', color: '#333' }}>
            Manage Subscription
          </h2>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem' }}>
            {/* Basic Plan Card */}
            <div className={`plan-card ${userData.current_plan === 'basic' ? 'active' : ''}`}>
              <h3>Basic Plan</h3>
              <div className="price">$10<span style={{ fontSize: '1rem', color: '#999' }}>/month</span></div>
              <ul className="features">
                <li>Core features</li>
                <li>Standard support</li>
                <li>Basic analytics</li>
              </ul>
              <button
                className={`btn ${userData.current_plan === 'basic' ? 'btn-secondary' : 'btn-primary'}`}
                onClick={() => updateSubscription('basic')}
                disabled={updating || userData.current_plan === 'basic'}
                style={{ width: '100%', marginTop: '1rem' }}
              >
                {updating ? 'Updating...' : userData.current_plan === 'basic' ? 'Current Plan' : 'Upgrade to Basic'}
              </button>
            </div>

            {/* Pro Plan Card */}
            <div className={`plan-card ${userData.current_plan === 'pro' ? 'active' : ''}`}>
              <h3>Pro Plan</h3>
              <div className="price">$20<span style={{ fontSize: '1rem', color: '#999' }}>/month</span></div>
              <ul className="features">
                <li>All Basic features</li>
                <li>Premium support</li>
                <li>Advanced analytics</li>
                <li>Priority access</li>
              </ul>
              <button
                className={`btn ${userData.current_plan === 'pro' ? 'btn-secondary' : 'btn-secondary'}`}
                onClick={() => updateSubscription('pro')}
                disabled={updating || userData.current_plan === 'pro'}
                style={{ width: '100%', marginTop: '1rem' }}
              >
                {updating ? 'Updating...' : userData.current_plan === 'pro' ? 'Current Plan' : 'Upgrade to Pro'}
              </button>
            </div>
          </div>

          {/* Cancel Button */}
          {userData.current_plan !== 'none' && (
            <div style={{ marginTop: '2rem', textAlign: 'center' }}>
              <button
                className="btn btn-danger"
                onClick={() => updateSubscription('none')}
                disabled={updating}
                style={{ minWidth: '200px' }}
              >
                {updating ? 'Cancelling...' : 'Cancel Subscription'}
              </button>
            </div>
          )}
        </div>

        {/* Premium Access */}
        {userData.subscription_status === 'active' && (
          <div style={{ 
            marginTop: '2rem', 
            padding: '1.5rem', 
            background: 'linear-gradient(135deg, #f8f9ff 0%, #ffffff 100%)',
            borderRadius: '12px',
            border: '2px solid #667eea',
            textAlign: 'center'
          }}>
            <h3 style={{ marginBottom: '1rem', color: '#667eea' }}>🎉 Premium Access Active</h3>
            <p style={{ marginBottom: '1.5rem', color: '#666' }}>
              You have access to premium content and features!
            </p>
            <a 
              href="/premium" 
              style={{ 
                display: 'inline-block',
                padding: '0.75rem 2rem',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                borderRadius: '8px',
                fontWeight: 600,
                textDecoration: 'none',
                transition: 'all 0.3s ease',
                boxShadow: '0 4px 15px rgba(102, 126, 234, 0.3)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)'
                e.currentTarget.style.boxShadow = '0 6px 20px rgba(102, 126, 234, 0.4)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)'
                e.currentTarget.style.boxShadow = '0 4px 15px rgba(102, 126, 234, 0.3)'
              }}
            >
              → Access Premium Content
            </a>
          </div>
        )}

        {/* User Info & Logout */}
        <div style={{ 
          marginTop: '3rem', 
          paddingTop: '2rem', 
          borderTop: '2px solid #f0f0f0',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1rem'
        }}>
          <div>
            <p style={{ color: '#666', fontSize: '0.875rem', marginBottom: '0.25rem' }}>Logged in as</p>
            <p style={{ fontWeight: 600, color: '#333' }}>{userData.email}</p>
          </div>
          <button
            className="btn btn-danger"
            onClick={async () => {
              try {
                const refreshToken = getRefreshToken()
                if (refreshToken) {
                  await apiClient.post('/api/auth/jwt/logout/', { refresh: refreshToken })
                }
                clearAuthTokens()
                router.push('/login')
              } catch (err) {
                console.error('Logout error:', err)
                // Clear tokens anyway
                clearAuthTokens()
                router.push('/login')
              }
            }}
          >
            Logout
          </button>
        </div>
      </div>
    </div>
  )
}

