import { useState, useEffect, useRef, useCallback } from 'react';

export function useWebSocket(url) {
  const [data, setData] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);
  
  const wsRef = useRef(null);
  const retryRef = useRef(0);
  const reconnectTimeoutRef = useRef(null);
  const isMountedRef = useRef(true); // Tracks if component is still on screen

  const connect = useCallback(() => {
    // Clear any pending reconnects before starting a new one
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        // If component unmounted while connection was opening, close immediately
        if (!isMountedRef.current) return ws.close();
        
        setIsConnected(true);
        setError(null);
        retryRef.current = 0; // Reset the backoff timer on success
      };

      ws.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);
          setData(parsed);
        } catch (e) {
          console.error('WebSocket parse error:', e);
        }
      };

      ws.onclose = (event) => {
        setIsConnected(false);
        
        // ONLY reconnect if the component is still mounted AND it wasn't 
        // a deliberate closure (code 1000 = Normal Closure)
        if (isMountedRef.current && event.code !== 1000) {
          const delay = Math.min(1000 * Math.pow(2, retryRef.current), 10000);
          retryRef.current += 1;
          
          reconnectTimeoutRef.current = setTimeout(connect, delay);
        }
      };

      ws.onerror = (err) => {
        // Note: browser security prevents reading specific WS error details
        setError('Connection to server lost.');
        ws.close(); // Force a close event to trigger the reconnect logic
      };
    } catch (e) {
      console.error('WebSocket setup error:', e);
      setError(e.message);
    }
  }, [url]);

  useEffect(() => {
    isMountedRef.current = true;
    connect();

    // Cleanup function runs when the component unmounts
    return () => {
      isMountedRef.current = false; // Flag to prevent future reconnects
      
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        // Close with code 1000 (Normal Closure) so onclose doesn't try to reconnect
        wsRef.current.close(1000, "Component unmounted"); 
      }
    };
  }, [connect]);

  // Utility: Send messages back to the FastAPI server
  const sendMessage = useCallback((message) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('Cannot send message: WebSocket is disconnected.');
    }
  }, []);

  // Utility: Manually force a reconnect (useful for a "Retry Connection" UI button)
  const forceReconnect = useCallback(() => {
    retryRef.current = 0;
    if (wsRef.current) {
      wsRef.current.close(); // Closing it triggers the auto-reconnect flow
    } else {
      connect();
    }
  }, [connect]);

  return { 
    data, 
    isConnected, 
    error, 
    sendMessage, 
    forceReconnect 
  };
}