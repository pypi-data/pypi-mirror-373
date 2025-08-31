'use client';

import React, { useEffect, useState } from 'react';
import { authManager, type User } from '@/lib/auth';
import { Button } from '@/components/ui/button';

export function GitHubAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Check if user is already authenticated
    const currentUser = authManager.getUser();
    if (currentUser) {
      setUser(currentUser);
    }

    // Handle OAuth callback
    const handleCallback = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const code = urlParams.get('code');
      const state = urlParams.get('state');
      
      if (code) {
        setLoading(true);
        try {
          const authResponse = await authManager.handleGitHubCallback(code, state || undefined);
          setUser(authResponse.user);
          // Clean up URL parameters
          window.history.replaceState({}, document.title, window.location.pathname);
        } catch (err) {
          setError(err instanceof Error ? err.message : 'Authentication failed');
        } finally {
          setLoading(false);
        }
      }
    };

    handleCallback();
  }, []);

  const handleLogin = async () => {
    setLoading(true);
    setError(null);
    try {
      const authUrl = await authManager.getGitHubAuthUrl();
      window.location.href = authUrl;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get auth URL');
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    setLoading(true);
    try {
      await authManager.logout();
      setUser(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Logout failed');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-green-400 font-mono">
          &gt; Authenticating...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center p-8 space-y-4">
        <div className="text-red-400 font-mono">
          ERROR: {error}
        </div>
        <Button 
          onClick={() => setError(null)}
          className="bg-gray-800 border border-gray-600 text-green-400 hover:bg-gray-700"
        >
          &gt; Retry
        </Button>
      </div>
    );
  }

  if (user) {
    return (
      <div className="flex items-center justify-between p-4 bg-gray-900 border border-gray-700 rounded">
        <div className="flex items-center space-x-3">
          {user.avatar_url && (
            <img 
              src={user.avatar_url} 
              alt={user.username}
              className="w-8 h-8 rounded-full border border-green-400"
            />
          )}
          <div>
            <div className="text-green-400 font-mono text-sm">
              &gt; {user.username}
            </div>
            <div className="text-gray-400 font-mono text-xs">
              {user.email}
            </div>
          </div>
        </div>
        <Button
          onClick={handleLogout}
          size="sm"
          variant="ghost"
          className="text-gray-400 hover:text-red-400 font-mono"
        >
          logout
        </Button>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center p-8 space-y-4">
      <div className="text-gray-400 font-mono text-center">
        <div>&gt; AI-MEM TERMINAL</div>
        <div>&gt; AUTHENTICATION REQUIRED</div>
      </div>
      
      <Button
        onClick={handleLogin}
        className="bg-gray-800 border border-green-400 text-green-400 hover:bg-green-400 hover:text-black font-mono"
      >
        &gt; Connect GitHub
      </Button>
      
      <div className="text-xs text-gray-500 font-mono text-center">
        &gt; Secure OAuth2 authentication
        <br />
        &gt; No passwords stored locally
      </div>
    </div>
  );
}