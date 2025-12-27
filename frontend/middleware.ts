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
      
      // Get JWT token from cookie (if available) or let client-side handle it
      // For middleware, we'll check if user is authenticated via session or JWT
      const cookieHeader = request.headers.get('cookie') || ''
      
      // Try to get JWT token from cookie (if stored there) or use session
      // For now, let the client-side component handle JWT authentication
      // Middleware will just check session as fallback
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

