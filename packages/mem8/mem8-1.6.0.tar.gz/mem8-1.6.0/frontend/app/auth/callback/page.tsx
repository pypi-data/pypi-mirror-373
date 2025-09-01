'use client'

import { useEffect, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { authManager } from '@/lib/auth'

export default function AuthCallbackPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [status, setStatus] = useState<'loading' | 'processing' | 'success' | 'error'>('loading')
  const [error, setError] = useState<string>('')

  useEffect(() => {
    let hasHandled = false // Prevent double execution
    
    const handleCallback = async () => {
      if (hasHandled) return
      hasHandled = true
      
      // Check if already authenticated first
      if (authManager.isAuthenticated()) {
        console.log('Already authenticated, redirecting to main page')
        setStatus('success')
        router.push('/')
        return
      }
      
      const code = searchParams.get('code')
      const state = searchParams.get('state')
      const oauthError = searchParams.get('error')

      if (oauthError) {
        setError(`GitHub OAuth error: ${oauthError}`)
        setStatus('error')
        return
      }

      if (!code) {
        setError('No authorization code received from GitHub')
        setStatus('error')
        return
      }

      try {
        setStatus('processing') // Show processing state during API call
        
        // Use the auth manager to handle the callback
        const authResponse = await authManager.handleGitHubCallback(code, state || undefined)
        
        setStatus('success')
        
        // Small delay to show success state before redirect
        setTimeout(() => {
          router.push('/')
        }, 500)
        
      } catch (err) {
        console.error('Authentication error:', err)
        const errorMessage = err instanceof Error ? err.message : 'Authentication failed'
        
        // If the error suggests code was already used and we're somehow already authenticated
        if (errorMessage.includes('expired') || errorMessage.includes('incorrect')) {
          if (authManager.isAuthenticated()) {
            console.log('Code expired but user is authenticated, redirecting')
            setStatus('success')
            setTimeout(() => {
              router.push('/')
            }, 500)
            return
          }
        }
        
        // Only show error after a brief delay to avoid flashing errors during successful auth
        setTimeout(() => {
          if (!authManager.isAuthenticated()) {
            setError(errorMessage)
            setStatus('error')
          }
        }, 1000)
      }
    }

    handleCallback()
  }, [searchParams, router])

  return (
    <div className="min-h-screen bg-black text-green-400 font-mono flex items-center justify-center">
      <div className="max-w-md w-full text-center space-y-4">
        <div className="text-2xl font-bold">
          &gt; AI-MEM TERMINAL
        </div>
        
        {(status === 'loading' || status === 'processing') && (
          <div className="space-y-2">
            <div className="text-lg">&gt; AUTHENTICATING...</div>
            <div className="text-gray-400">
              &gt; {status === 'loading' ? 'Validating OAuth response' : 'Exchanging tokens with server'}
            </div>
            <div className="inline-flex items-center space-x-1">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse delay-75"></div>
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse delay-150"></div>
            </div>
          </div>
        )}
        
        {status === 'success' && (
          <div className="space-y-2">
            <div className="text-lg text-green-400">✅ AUTHENTICATION SUCCESSFUL</div>
            <div className="text-gray-400">&gt; Redirecting to terminal...</div>
          </div>
        )}
        
        {status === 'error' && (
          <div className="space-y-4">
            <div className="text-lg text-red-400">❌ AUTHENTICATION FAILED</div>
            <div className="text-red-400 text-sm">{error}</div>
            <button
              onClick={() => router.push('/')}
              className="px-4 py-2 border border-green-400 text-green-400 hover:bg-green-400 hover:text-black transition-colors"
            >
              &gt; Return to Login
            </button>
          </div>
        )}
      </div>
    </div>
  )
}