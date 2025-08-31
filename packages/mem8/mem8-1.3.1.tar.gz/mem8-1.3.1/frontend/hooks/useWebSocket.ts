import { useEffect, useRef, useState, useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { authManager } from '@/lib/auth';

const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';

interface WebSocketMessage {
  type: 'thought_updated' | 'thought_created' | 'thought_deleted' | 'connection_established' | 'error' | 'pong';
  thought?: any;
  team_id?: string;
  error?: string;
  timestamp: string;
}

interface UseWebSocketProps {
  teamId?: string;
  enabled?: boolean;
}

export function useWebSocket({ teamId, enabled = true }: UseWebSocketProps) {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const queryClient = useQueryClient();
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const cleanup = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
    }
    setIsConnected(false);
  }, []);

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);

  const startPing = useCallback(() => {
    pingIntervalRef.current = setInterval(() => {
      sendMessage({
        type: 'ping',
        timestamp: new Date().toISOString()
      });
    }, 30000); // Ping every 30 seconds
  }, [sendMessage]);

  const connect = useCallback(() => {
    if (!enabled || !teamId || !authManager.isAuthenticated()) {
      return;
    }

    // Clean up existing connection
    cleanup();

    const user = authManager.getUser();
    const wsUrl = `${WS_BASE_URL}/api/v1/sync/${teamId}?user_id=${user?.id}`;
    
    console.log('Connecting to WebSocket:', wsUrl);
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
      setConnectionError(null);
      setReconnectAttempts(0);
      startPing();
    };

    ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        console.log('WebSocket message received:', message);

        switch (message.type) {
          case 'thought_created':
          case 'thought_updated':
          case 'thought_deleted':
            // Invalidate and refetch thoughts data
            queryClient.invalidateQueries({ queryKey: ['thoughts'] });
            queryClient.invalidateQueries({ queryKey: ['thoughts', teamId] });
            break;
          
          case 'connection_established':
            console.log('Connection confirmed for team:', message.team_id);
            break;
          
          case 'error':
            console.error('WebSocket error message:', message.error);
            setConnectionError(message.error || 'Unknown WebSocket error');
            break;
          
          case 'pong':
            // Pong received, connection is alive
            break;
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.onclose = (event) => {
      console.log('WebSocket closed:', event.code, event.reason);
      setIsConnected(false);
      
      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current);
      }

      // Attempt to reconnect if not intentionally closed
      if (event.code !== 1000 && enabled && teamId && reconnectAttempts < 5) {
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
        console.log(`Reconnecting in ${delay}ms... (attempt ${reconnectAttempts + 1})`);
        
        reconnectTimeoutRef.current = setTimeout(() => {
          setReconnectAttempts(prev => prev + 1);
          connect();
        }, delay);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnectionError('WebSocket connection error');
    };
  }, [enabled, teamId, cleanup, queryClient, reconnectAttempts, startPing]);

  const disconnect = useCallback(() => {
    cleanup();
    setReconnectAttempts(0);
  }, [cleanup]);

  // Connect on mount and when dependencies change
  useEffect(() => {
    if (enabled && teamId && authManager.isAuthenticated()) {
      connect();
    } else {
      disconnect();
    }

    return disconnect;
  }, [enabled, teamId, connect, disconnect]);

  // Listen for auth changes
  useEffect(() => {
    const handleAuthChange = () => {
      if (authManager.isAuthenticated()) {
        connect();
      } else {
        disconnect();
      }
    };

    window.addEventListener('mem8-auth-change', handleAuthChange);
    return () => window.removeEventListener('mem8-auth-change', handleAuthChange);
  }, [connect, disconnect]);

  return {
    isConnected,
    connectionError,
    sendMessage,
    connect,
    disconnect,
    reconnectAttempts,
  };
}