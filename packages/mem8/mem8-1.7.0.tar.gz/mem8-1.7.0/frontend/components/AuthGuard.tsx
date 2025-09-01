'use client';

import React, { useState, useEffect } from 'react';
import { authManager } from '@/lib/auth';
import { GitHubAuth } from './GitHubAuth';

interface AuthGuardProps {
  children: React.ReactNode;
}

export function AuthGuard({ children }: AuthGuardProps) {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    // Check authentication status
    const checkAuth = () => {
      // Check for local mode first
      const isLocalMode = localStorage.getItem('mem8-local-mode') === 'true';
      const authenticated = isLocalMode || authManager.isAuthenticated();
      setIsAuthenticated(authenticated);
    };

    checkAuth();

    // Listen for auth state changes
    const handleAuthChange = () => {
      checkAuth();
    };

    // Custom event listener for auth changes
    window.addEventListener('mem8-auth-change', handleAuthChange);

    // Check periodically in case token expires
    const interval = setInterval(checkAuth, 30000); // Check every 30 seconds

    return () => {
      window.removeEventListener('mem8-auth-change', handleAuthChange);
      clearInterval(interval);
    };
  }, []);

  // Show loading state while checking authentication
  if (isAuthenticated === null) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-green-400 font-mono">
          &gt; Initializing mem8...
        </div>
      </div>
    );
  }

  // Show login if not authenticated
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <GitHubAuth />
      </div>
    );
  }

  // Show protected content
  return <>{children}</>;
}

// Utility function to trigger auth change events
export const triggerAuthChange = () => {
  window.dispatchEvent(new CustomEvent('mem8-auth-change'));
};