'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import axios from 'axios'

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
      const response = await axios.get(`${API_URL}/api/user/status/`, {
        withCredentials: true,
        headers: {
          'Content-Type': 'application/json',
        },
      })
      if (response.data) {
        setUserData(response.data)
      } else {
        setError('No user data received')
      }
    } catch (err: any) {
      console.error('Error fetching user data:', err)
      // Handle different error cases
      if (err.response?.status === 401 || err.response?.status === 403) {
        // Not authenticated - redirect to login
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
      
      const response = await axios.post(
        `${API_URL}/api/user/subscription/`,
        { plan },
        { 
          withCredentials: true,
          headers: {
            'Content-Type': 'application/json',
          },
        }
      )
      
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
      <div className="card">
        <h1>Dashboard</h1>
        
        {error && <div className="error">{error}</div>}
        {success && <div className="success">{success}</div>}

        <div style={{ marginTop: '2rem' }}>
          <h2>
            Current Plan:
            <span className={`plan-badge plan-${userData.current_plan}`}>
              {userData.current_plan === 'basic' ? 'Basic Plan' : 
               userData.current_plan === 'pro' ? 'Pro Plan' : 
               'No Plan'}
            </span>
            <span className={`status-badge status-${userData.subscription_status}`}>
              {userData.subscription_status}
            </span>
          </h2>

          <h2 style={{ marginTop: '1.5rem' }}>
            Lifetime Spend: <span style={{ color: '#2ecc71', fontSize: '1.5rem' }}>
              {formatCurrency(userData.total_amount_paid)}
            </span>
          </h2>

          <div style={{ marginTop: '2rem' }}>
            <h3>Manage Subscription</h3>
            <div style={{ marginTop: '1rem' }}>
              <button
                className="btn btn-primary"
                onClick={() => updateSubscription('basic')}
                disabled={updating || userData.current_plan === 'basic'}
              >
                {updating ? 'Updating...' : 'Upgrade to Basic ($10)'}
              </button>
              <button
                className="btn btn-secondary"
                onClick={() => updateSubscription('pro')}
                disabled={updating || userData.current_plan === 'pro'}
              >
                {updating ? 'Updating...' : 'Upgrade to Pro ($20)'}
              </button>
              {userData.current_plan !== 'none' && (
                <button
                  className="btn btn-danger"
                  onClick={() => updateSubscription('none')}
                  disabled={updating}
                >
                  {updating ? 'Cancelling...' : 'Cancel Subscription'}
                </button>
              )}
            </div>
          </div>

          {userData.subscription_status === 'active' && (
            <div style={{ marginTop: '2rem' }}>
              <a href="/premium" style={{ color: '#667eea', textDecoration: 'underline' }}>
                → Access Premium Content
              </a>
            </div>
          )}

          <div style={{ marginTop: '2rem', paddingTop: '2rem', borderTop: '1px solid #eee' }}>
            <button
              className="btn btn-danger"
              onClick={async () => {
                try {
                  await axios.post(`${API_URL}/api/logout/`, {}, { withCredentials: true })
                  router.push('/login')
                } catch (err) {
                  console.error('Logout error:', err)
                }
              }}
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

