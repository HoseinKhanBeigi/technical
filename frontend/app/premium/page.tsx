'use client'

import { useEffect, useState } from 'react'
import axios from 'axios'
import { useRouter } from 'next/navigation'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function Premium() {
  const [userData, setUserData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    fetchUserData()
  }, [])

  const fetchUserData = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/user/status/`, {
        withCredentials: true,
      })
      
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
      <div className="card">
        <h1>🎉 Premium Content</h1>
        <p style={{ marginTop: '1rem', fontSize: '1.2rem' }}>
          Welcome to the premium section! This content is only accessible to users with an active subscription.
        </p>
        <div style={{ marginTop: '2rem' }}>
          <a href="/dashboard" style={{ color: '#667eea', textDecoration: 'underline' }}>
            ← Back to Dashboard
          </a>
        </div>
      </div>
    </div>
  )
}

