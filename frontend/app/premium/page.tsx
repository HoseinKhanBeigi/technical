'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import apiClient from '@/lib/api'

export default function Premium() {
  const [userData, setUserData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    fetchUserData()
  }, [])

  const fetchUserData = async () => {
    try {
      // Use JWT-authenticated API client
      const response = await apiClient.get('/api/user/status/')
      
      if (response.data.subscription_status !== 'active') {
        router.push('/dashboard')
        return
      }
      
      setUserData(response.data)
    } catch (err) {
      router.push('/dashboard')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="container">
        <div className="loading">Loading...</div>
      </div>
    )
  }

  return (
    <div className="container">
      {/* Header */}
      <div style={{ marginBottom: '2rem', textAlign: 'center' }}>
        <h1 style={{ color: 'white', fontSize: '2.5rem', fontWeight: 700, marginBottom: '0.5rem' }}>
          Premium Content
        </h1>
        <p style={{ color: 'rgba(255, 255, 255, 0.9)', fontSize: '1.1rem' }}>
          Exclusive content for premium subscribers
        </p>
      </div>

      {/* Premium Content Card */}
      <div className="card">
        <div style={{ textAlign: 'center', padding: '2rem 0' }}>
          <div style={{ 
            fontSize: '4rem', 
            marginBottom: '1.5rem',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text'
          }}>
            🎉
          </div>
          <h1 style={{ fontSize: '2.5rem', marginBottom: '1rem', color: '#333' }}>
            Welcome to Premium!
          </h1>
          <p style={{ fontSize: '1.25rem', color: '#666', marginBottom: '2rem', lineHeight: '1.6' }}>
            You have access to exclusive premium content and features. 
            This section is only available to users with an active subscription.
          </p>

          {/* Feature Grid */}
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
            gap: '1.5rem',
            marginTop: '3rem',
            marginBottom: '3rem'
          }}>
            <div style={{ padding: '1.5rem', background: '#f8f9fa', borderRadius: '12px' }}>
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>⚡</div>
              <h3 style={{ marginBottom: '0.5rem', color: '#333' }}>Fast Access</h3>
              <p style={{ color: '#666', fontSize: '0.875rem' }}>Priority support and faster response times</p>
            </div>
            <div style={{ padding: '1.5rem', background: '#f8f9fa', borderRadius: '12px' }}>
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>📊</div>
              <h3 style={{ marginBottom: '0.5rem', color: '#333' }}>Analytics</h3>
              <p style={{ color: '#666', fontSize: '0.875rem' }}>Advanced analytics and insights</p>
            </div>
            <div style={{ padding: '1.5rem', background: '#f8f9fa', borderRadius: '12px' }}>
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🔒</div>
              <h3 style={{ marginBottom: '0.5rem', color: '#333' }}>Secure</h3>
              <p style={{ color: '#666', fontSize: '0.875rem' }}>Enterprise-grade security</p>
            </div>
          </div>

          {/* Back Button */}
          <div style={{ marginTop: '3rem', paddingTop: '2rem', borderTop: '2px solid #f0f0f0' }}>
            <a 
              href="/dashboard" 
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
              ← Back to Dashboard
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}

