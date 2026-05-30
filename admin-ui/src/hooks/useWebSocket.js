// Shared WebSocket connection hook
// Returns: { lastEvent, connected, send }
// lastEvent shape: { type: 'token'|'progress'|'done'|'error', payload: string }

import { useState, useEffect, useRef, useCallback } from 'react'

export function useWebSocket(url) {
  const [lastEvent, setLastEvent] = useState(null)
  const [connected, setConnected] = useState(false)
  const wsRef = useRef(null)

  useEffect(() => {
    const ws = new WebSocket(url)
    wsRef.current = ws

    ws.onopen = () => setConnected(true)
    ws.onclose = () => setConnected(false)
    ws.onerror = () => setConnected(false)

    ws.onmessage = (e) => {
      try {
        const event = JSON.parse(e.data)
        setLastEvent(event)
      } catch {
        setLastEvent({ type: 'token', payload: e.data })
      }
    }

    return () => ws.close()
  }, [url])

  const send = useCallback((data) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data))
    }
  }, [])

  return { lastEvent, connected, send }
}