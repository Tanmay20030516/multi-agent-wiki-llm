// Chat state: message history, send(), streaming, loading flag

import { useState, useEffect, useRef } from 'react'
import { useWebSocket } from './useWebSocket'

const WS_URL = `ws://${window.location.host}/ws/query`

export function useChat() {
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const streamingRef = useRef(null) // id of the message currently being streamed
  const { lastEvent, connected, send } = useWebSocket(WS_URL)

  // Handle incoming WebSocket events
  useEffect(() => {
    if (!lastEvent) return

    const { type, content, tool_name } = lastEvent

    if (type === 'llm_response') {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === streamingRef.current
            ? { ...m, content: m.content + content }
            : m
        )
      )
    } else if (type === 'tool_call') {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === streamingRef.current
            ? { ...m, progress: `Reading ${tool_name}…` }
            : m
        )
      )
    } else if (type === 'tool_result') {
      // tool result received, agent will continue
    } else if (type === 'done') {
      setLoading(false)
      streamingRef.current = null
    } else if (type === 'error') {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === streamingRef.current
            ? { ...m, content: `Error: ${content}`, isError: true }
            : m
        )
      )
      setLoading(false)
      streamingRef.current = null
    }
  }, [lastEvent])

  function sendMessage(question) {
    if (!question.trim() || loading) return

    // Add user message
    const userMsg = { id: crypto.randomUUID(), role: 'user', content: question }
    // Add empty assistant message that will be streamed into
    const assistantMsg = {
      id: crypto.randomUUID(),
      role: 'assistant',
      content: '',
      progress: null,
      isError: false,
    }

    setMessages((prev) => [...prev, userMsg, assistantMsg])
    streamingRef.current = assistantMsg.id
    setLoading(true)

    send({ type: 'query', question })
  }

  return { messages, loading, connected, sendMessage }
}