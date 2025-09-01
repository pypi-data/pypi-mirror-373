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
      
      // Check for local mode first
      const isLocalMode = localStorage.getItem('ai-mem-local-mode') === 'true';
      if (isLocalMode) {
        setAuthState({
          user: {
            id: 'local-user',
            username: 'local',
            email: 'local@ai-mem.com',
            avatar_url: null
          },
          isAuthenticated: true,
          isLoading: false,
        });
        return;
      }
      
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
      // Check if we're in local mode
      const isLocalMode = localStorage.getItem('ai-mem-local-mode') === 'true';
      if (isLocalMode) {
        localStorage.removeItem('ai-mem-local-mode');
      } else {
        await authManager.logout();
        authManager.clearAuth();
      }
      
      setAuthState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
      });
    } catch (error) {
      console.error('Logout failed:', error);
      // Clear auth state even if API call fails
      localStorage.removeItem('ai-mem-local-mode');
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
    window.addEventListener('mem8-auth-change', handleAuthChange);
    
    // Listen for storage changes (cross-tab sync)
    window.addEventListener('storage', (e) => {
      if (e.key === 'ai_mem_token' || e.key === 'ai_mem_user') {
        handleAuthChange();
      }
    });

    return () => {
      window.removeEventListener('mem8-auth-change', handleAuthChange);
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