import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, type Thought, type ThoughtPreview, type Team, type TeamStats, type SearchResult, type SystemStats } from '@/lib/api';

// Health check
export function useHealth() {
  return useQuery({
    queryKey: ['health'],
    queryFn: () => apiClient.getHealth(),
    refetchInterval: 30000, // Check every 30 seconds
  });
}

// Filesystem Thoughts (no auth required)
export function useFilesystemThoughts(params?: { search?: string; tags?: string[]; repository?: string; limit?: number }) {
  return useQuery({
    queryKey: ['filesystem-thoughts', params],
    queryFn: () => apiClient.getFilesystemThoughts(params),
    enabled: true,
  });
}

// Thoughts
export function useThoughts(params?: { team_id?: string; skip?: number; limit?: number }) {
  return useQuery({
    queryKey: ['thoughts', params],
    queryFn: () => apiClient.getThoughts(params),
    enabled: true,
  });
}

export function useThought(id: string) {
  return useQuery({
    queryKey: ['thoughts', id],
    queryFn: () => apiClient.getThought(id),
    enabled: !!id,
  });
}

export function useCreateThought() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (thought: Partial<Thought>) => apiClient.createThought(thought),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['thoughts'] });
      queryClient.invalidateQueries({ queryKey: ['system-stats'] });
    },
  });
}

export function useUpdateThought() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, thought }: { id: string; thought: Partial<Thought> }) => 
      apiClient.updateThought(id, thought),
    onSuccess: (updatedThought) => {
      queryClient.invalidateQueries({ queryKey: ['thoughts'] });
      queryClient.setQueryData(['thoughts', updatedThought.id], updatedThought);
    },
  });
}

export function useDeleteThought() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => apiClient.deleteThought(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['thoughts'] });
      queryClient.invalidateQueries({ queryKey: ['system-stats'] });
    },
  });
}

// Search
export function useSearchThoughts(params: {
  query: string;
  search_type?: 'fulltext' | 'semantic';
  team_id?: string;
  limit?: number;
}) {
  return useQuery({
    queryKey: ['search', params],
    queryFn: () => apiClient.searchThoughts(params),
    enabled: params.query.length > 2,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Teams
export function useTeams() {
  return useQuery({
    queryKey: ['teams'],
    queryFn: () => apiClient.getTeams(),
  });
}

export function useTeam(id: string) {
  return useQuery({
    queryKey: ['teams', id],
    queryFn: () => apiClient.getTeam(id),
    enabled: !!id,
  });
}

export function useTeamStats(id: string) {
  return useQuery({
    queryKey: ['teams', id, 'stats'],
    queryFn: () => apiClient.getTeamStats(id),
    enabled: !!id,
    refetchInterval: 60000, // Refresh every minute
  });
}

// System stats
export function useSystemStats() {
  return useQuery({
    queryKey: ['system-stats'],
    queryFn: () => apiClient.getSystemStats(),
    refetchInterval: 30000, // Refresh every 30 seconds
  });
}

// Sync
export function useSyncTeam() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (teamId: string) => apiClient.syncTeam(teamId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['thoughts'] });
      queryClient.invalidateQueries({ queryKey: ['teams'] });
      queryClient.invalidateQueries({ queryKey: ['system-stats'] });
    },
  });
}

export function useSyncStatus(teamId: string) {
  return useQuery({
    queryKey: ['sync-status', teamId],
    queryFn: () => apiClient.getSyncStatus(teamId),
    enabled: !!teamId,
    refetchInterval: 10000, // Check every 10 seconds
  });
}