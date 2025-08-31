interface ApiResponse<T> {
  data: T;
  message?: string;
}

interface Thought {
  id: string;
  path: string;
  title: string;
  content: string;
  thought_metadata: Record<string, any>;
  team_id: string;
  created_at: string;
  updated_at: string;
}

interface ThoughtPreview {
  id: string;
  title: string;
  excerpt: string;
  path: string;
  team: string;
  lastModified: string;
  tags: string[];
}

interface Team {
  id: string;
  name: string;
  description?: string;
  settings: Record<string, any>;
  created_at: string;
  updated_at: string;
}

interface TeamStats {
  name: string;
  status: 'active' | 'syncing' | 'error';
  memberCount: number;
  thoughtCount: number;
}

interface SearchResult {
  thoughts: ThoughtPreview[];
  total: number;
}

interface SystemStats {
  totalThoughts: number;
  activeTeams: number;
  syncStatus: number;
  memoryUsage: string;
}

import { authManager } from './auth';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const DEFAULT_SEARCH_LIMIT = process.env.NEXT_PUBLIC_DEFAULT_SEARCH_LIMIT
  ? Number(process.env.NEXT_PUBLIC_DEFAULT_SEARCH_LIMIT)
  : undefined;
const USE_MOCK_DATA = false; // Toggle for development

// Warn when relying on development defaults
if (!process.env.NEXT_PUBLIC_API_URL && typeof window !== 'undefined') {
  // Point to the config env var explicitly
  // eslint-disable-next-line no-console
  console.warn(
    'API base URL missing. Set NEXT_PUBLIC_API_URL to your backend URL.'
  );
}

class ApiClient {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...authManager.getAuthHeaders(),
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`API request failed: ${response.status} ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`API request to ${endpoint} failed:`, error);
      throw error;
    }
  }

  // Health check
  async getHealth(): Promise<{ status: string }> {
    if (USE_MOCK_DATA) {
      return { status: 'ok' };
    }
    return this.request('/api/v1/health');
  }

  // Filesystem Thoughts API (local files, no auth needed for display)
  async getFilesystemThoughts(params?: {
    search?: string;
    tags?: string[];
    repository?: string;
    limit?: number;
  }): Promise<any> {
    const searchParams = new URLSearchParams();
    if (params?.search) searchParams.append('search', params.search);
    if (params?.tags) params.tags.forEach(tag => searchParams.append('tags', tag));
    if (params?.repository) searchParams.append('repository', params.repository);
    if (params?.limit) searchParams.append('limit', params.limit.toString());
    
    const query = searchParams.toString();
    // Use public endpoint that doesn't require auth
    return this.request(`/api/v1/public/thoughts/local${query ? `?${query}` : ''}`);
  }

  // Thoughts API
  async getThoughts(params?: {
    team_id?: string;
    skip?: number;
    limit?: number;
  }): Promise<Thought[]> {
    if (USE_MOCK_DATA) {
      return [
        {
          id: 'thought-1',
          path: '/thoughts/shared/projects/mem8-phase3.md',
          title: 'Phase 3 Frontend Implementation',
          content: '# Phase 3 Frontend Implementation\n\nCompleted Next.js frontend with terminal aesthetic and full API integration...',
          thought_metadata: { tags: ['frontend', 'nextjs', 'implementation'], created_by: 'claude' },
          team_id: 'team-1',
          created_at: new Date(Date.now() - 1000 * 60 * 60).toISOString(), // 1 hour ago
          updated_at: new Date(Date.now() - 1000 * 60 * 30).toISOString(), // 30 mins ago
        },
        {
          id: 'thought-2',
          path: '/thoughts/shared/research/terminal-design.md',
          title: 'Terminal Design System Research',
          content: '# Terminal Design System Research\n\nAnalyzed AgenticInsights design patterns for terminal IDE aesthetic...',
          thought_metadata: { tags: ['design', 'terminal', 'ui'], created_by: 'designer' },
          team_id: 'team-2',
          created_at: new Date(Date.now() - 1000 * 60 * 60 * 4).toISOString(), // 4 hours ago
          updated_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(), // 2 hours ago
        },
        {
          id: 'thought-3',
          path: '/thoughts/shared/backend/api-integration.md',
          title: 'Backend API Integration Guide',
          content: '# Backend API Integration\n\nDocumentation for connecting frontend to FastAPI backend with async SQLAlchemy...',
          thought_metadata: { tags: ['backend', 'api', 'integration'], created_by: 'developer' },
          team_id: 'team-1',
          created_at: new Date(Date.now() - 1000 * 60 * 60 * 6).toISOString(),
          updated_at: new Date(Date.now() - 1000 * 60 * 60 * 1).toISOString(),
        },
      ];
    }
    
    const searchParams = new URLSearchParams();
    if (params?.team_id) searchParams.append('team_id', params.team_id);
    if (params?.skip) searchParams.append('skip', params.skip.toString());
    if (params?.limit) searchParams.append('limit', params.limit.toString());
    
    const query = searchParams.toString();
    return this.request(`/api/v1/thoughts${query ? `?${query}` : ''}`);
  }

  async getThought(id: string): Promise<Thought> {
    return this.request(`/api/v1/thoughts/${id}`);
  }

  async createThought(thought: Partial<Thought>): Promise<Thought> {
    return this.request('/api/v1/thoughts/', {
      method: 'POST',
      body: JSON.stringify(thought),
    });
  }

  async updateThought(id: string, thought: Partial<Thought>): Promise<Thought> {
    return this.request(`/api/v1/thoughts/${id}`, {
      method: 'PUT',
      body: JSON.stringify(thought),
    });
  }

  async deleteThought(id: string): Promise<void> {
    return this.request(`/api/v1/thoughts/${id}`, {
      method: 'DELETE',
    });
  }

  // Search API
  async searchThoughts(params: {
    query: string;
    search_type?: 'fulltext' | 'semantic';
    team_id?: string;
    limit?: number;
  }): Promise<SearchResult> {
    const searchParams = new URLSearchParams({
      q: params.query,
      search_type: params.search_type || 'fulltext',
    });

    // Limit handling: prefer explicit param, else env default, else warn and omit
    if (params.limit != null) {
      searchParams.set('limit', String(params.limit));
    } else if (DEFAULT_SEARCH_LIMIT != null && Number.isFinite(DEFAULT_SEARCH_LIMIT)) {
      searchParams.set('limit', String(DEFAULT_SEARCH_LIMIT));
    } else if (typeof window !== 'undefined') {
      // eslint-disable-next-line no-console
      console.warn(
        'Search limit not provided. Set NEXT_PUBLIC_DEFAULT_SEARCH_LIMIT or pass a limit parameter.'
      );
    }
    
    if (params.team_id) {
      searchParams.append('team_id', params.team_id);
    }
    
    return this.request(`/api/v1/search?${searchParams.toString()}`);
  }

  // Teams API
  async getTeams(): Promise<Team[]> {
    if (USE_MOCK_DATA) {
      return [
        {
          id: 'team-1',
          name: 'Development',
          description: 'Backend and frontend development team',
          settings: { memberCount: 3 },
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        {
          id: 'team-2',
          name: 'Design',
          description: 'UI/UX design team',
          settings: { memberCount: 2 },
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      ];
    }
    return this.request('/api/v1/teams/');
  }

  async getTeam(id: string): Promise<Team> {
    return this.request(`/api/v1/teams/${id}`);
  }

  async getTeamStats(id: string): Promise<TeamStats> {
    return this.request(`/api/v1/teams/${id}/stats`);
  }

  // System stats
  async getSystemStats(): Promise<SystemStats> {
    if (USE_MOCK_DATA) {
      return {
        totalThoughts: 127,
        activeTeams: 2,
        syncStatus: 98,
        memoryUsage: '42MB',
      };
    }
    return this.request('/api/v1/system/stats');
  }

  // Sync API
  async syncTeam(teamId: string): Promise<{ message: string }> {
    return this.request(`/api/v1/sync/teams/${teamId}`, {
      method: 'POST',
    });
  }

  async getSyncStatus(teamId: string): Promise<{ status: string; lastSync: string }> {
    return this.request(`/api/v1/sync/teams/${teamId}/status`);
  }
}

export const apiClient = new ApiClient();

export type {
  Thought,
  ThoughtPreview,
  Team,
  TeamStats,
  SearchResult,
  SystemStats,
};
