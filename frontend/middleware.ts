import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
  // Check if accessing /premium route
  if (request.nextUrl.pathname.startsWith('/premium')) {
    try {
      // Determine API URL - use internal Docker network URL for server-side requests
      const apiUrl = process.env.API_INTERNAL_URL || 
                    process.env.NEXT_PUBLIC_API_URL || 
                    'http://localhost:8000'
      
      // Fetch user status from backend
      const cookieHeader = request.headers.get('cookie') || ''
      const response = await fetch(`${apiUrl}/api/user/status/`, {
        headers: {
          'Cookie': cookieHeader,
        },
        credentials: 'include',
      })

      if (!response.ok) {
        // User not authenticated or error
        return NextResponse.redirect(new URL('/dashboard', request.url))
      }

      const userData = await response.json()
      
      // Check if user has active subscription
      if (userData.subscription_status !== 'active') {
        return NextResponse.redirect(new URL('/dashboard', request.url))
      }
    } catch (error) {
      // On error, redirect to dashboard
      return NextResponse.redirect(new URL('/dashboard', request.url))
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: '/premium/:path*',
}

