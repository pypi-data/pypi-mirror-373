/**
 * Authentication utilities for GitHub OAuth integration
 */

export interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
  avatar_url?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

const TOKEN_KEY = 'ai_mem_token';
const USER_KEY = 'ai_mem_user';
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class AuthManager {
  private static instance: AuthManager;
  
  static getInstance(): AuthManager {
    if (!AuthManager.instance) {
      AuthManager.instance = new AuthManager();
    }
    return AuthManager.instance;
  }
  
  /**
   * Store authentication data
   */
  setAuthData(authResponse: AuthResponse): void {
    localStorage.setItem(TOKEN_KEY, authResponse.access_token);
    localStorage.setItem(USER_KEY, JSON.stringify(authResponse.user));
    this.emitAuthChange();
  }
  
  /**
   * Get stored access token
   */
  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  }
  
  /**
   * Get stored user data
   */
  getUser(): User | null {
    const userData = localStorage.getItem(USER_KEY);
    return userData ? JSON.parse(userData) : null;
  }
  
  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!this.getToken();
  }
  
  /**
   * Clear authentication data (logout)
   */
  clearAuth(): void {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    this.emitAuthChange();
  }
  
  /**
   * Emit authentication change event
   */
  private emitAuthChange(): void {
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('mem8-auth-change'));
    }
  }
  
  /**
   * Get authorization headers for API requests
   */
  getAuthHeaders(): Record<string, string> {
    // Check for local mode first
    const isLocalMode = typeof window !== 'undefined' && localStorage.getItem('mem8-local-mode') === 'true';
    if (isLocalMode) {
      return { 'X-Local-Mode': 'true' };
    }
    
    const token = this.getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  }
  
  /**
   * Get GitHub OAuth URL
   */
  async getGitHubAuthUrl(): Promise<string> {
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/github/url`);
    const data = await response.json();
    return data.auth_url;
  }
  
  /**
   * Handle GitHub OAuth callback
   */
  async handleGitHubCallback(code: string, state?: string): Promise<AuthResponse> {
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/github/callback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ code, state }),
    });
    
    if (!response.ok) {
      throw new Error(`Authentication failed: ${response.statusText}`);
    }
    
    const authResponse: AuthResponse = await response.json();
    this.setAuthData(authResponse);
    return authResponse;
  }
  
  /**
   * Get current user from API
   */
  async getCurrentUser(): Promise<User> {
    const token = this.getToken();
    if (!token) {
      throw new Error('Not authenticated');
    }
    
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    
    if (!response.ok) {
      throw new Error(`Failed to get user info: ${response.statusText}`);
    }
    
    return response.json();
  }
  
  /**
   * Logout
   */
  async logout(): Promise<void> {
    const token = this.getToken();
    if (token) {
      try {
        await fetch(`${API_BASE_URL}/api/v1/auth/logout`, {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
      } catch (error) {
        console.error('Logout request failed:', error);
      }
    }
    
    this.clearAuth();
  }
}

export const authManager = AuthManager.getInstance();