import { useState, useEffect, useCallback } from 'react';
import { authManager, User } from '@/lib/auth';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export function useAuth() {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true,
  });

  // Initialize auth state
  const initializeAuth = useCallback(async () => {
    try {
      setAuthState(prev => ({ ...prev, isLoading: true }));
      
      if (!authManager.isAuthenticated()) {
        setAuthState({
          user: null,
          isAuthenticated: false,
          isLoading: false,
        });
        return;
      }

      // Try to get current user from API to validate token
      try {
        const user = await authManager.getCurrentUser();
        setAuthState({
          user,
          isAuthenticated: true,
          isLoading: false,
        });
      } catch (error) {
        // Token might be expired or invalid
        console.warn('Auth token validation failed:', error);
        authManager.clearAuth();
        setAuthState({
          user: null,
          isAuthenticated: false,
          isLoading: false,
        });
      }
    } catch (error) {
      console.error('Auth initialization error:', error);
      setAuthState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
      });
    }
  }, []);

  // Handle login
  const login = useCallback(async (code: string, state?: string) => {
    try {
      const authResponse = await authManager.handleGitHubCallback(code, state);
      setAuthState({
        user: authResponse.user,
        isAuthenticated: true,
        isLoading: false,
      });
      return authResponse;
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  }, []);

  // Handle logout
  const logout = useCallback(async () => {
    try {
      await authManager.logout();
      setAuthState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
      });
    } catch (error) {
      console.error('Logout failed:', error);
      // Clear auth state even if API call fails
      authManager.clearAuth();
      setAuthState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
      });
    }
  }, []);

  // Get GitHub auth URL
  const getGitHubAuthUrl = useCallback(async () => {
    return authManager.getGitHubAuthUrl();
  }, []);

  // Initialize auth on mount
  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  // Listen for auth changes (from other tabs, etc.)
  useEffect(() => {
    const handleAuthChange = () => {
      initializeAuth();
    };

    // Listen for custom auth change events
    window.addEventListener('ai-mem-auth-change', handleAuthChange);
    
    // Listen for storage changes (cross-tab sync)
    window.addEventListener('storage', (e) => {
      if (e.key === 'ai_mem_token' || e.key === 'ai_mem_user') {
        handleAuthChange();
      }
    });

    return () => {
      window.removeEventListener('ai-mem-auth-change', handleAuthChange);
      window.removeEventListener('storage', handleAuthChange);
    };
  }, [initializeAuth]);

  return {
    ...authState,
    login,
    logout,
    getGitHubAuthUrl,
    refreshAuth: initializeAuth,
  };
}