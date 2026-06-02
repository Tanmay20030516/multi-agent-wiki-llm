// Chat state: message history, send(), streaming, loading flag

import { useState, useEffect, useRef } from 'react'
import { useWebSocket } from './useWebSocket'

const WS_URL = `ws://${window.location.host}/ws/query`

export function useChat({ initialMessages = [], onMessagesChange } = {}) {
  // initialMessages is the thread's saved history — only used on mount.
  // Thread switching is handled by key={activeId} on ChatWindow (remounts fresh).
  const [messages, setMessages] = useState(initialMessages)
  const [loading, setLoading] = useState(false)
  const streamingRef = useRef(null)
  const { lastEvent, connected, send } = useWebSocket(WS_URL)

  // Persist messages to parent (useThreads → localStorage) after each update
  const onMessagesChangeRef = useRef(onMessagesChange)
  onMessagesChangeRef.current = onMessagesChange
  useEffect(() => {
    onMessagesChangeRef.current?.(messages)
  }, [messages])

  // Handle incoming WebSocket events
  useEffect(() => {
    if (!lastEvent) return

    const { type, content, tool_name } = lastEvent

    if (type === 'llm_response') {
      // Simulate typewriter by revealing the full content word-by-word
      const msgId = streamingRef.current
      const words = content.split(/(\s+)/) // split keeping whitespace
      let i = 0
      const tick = () => {
        if (i >= words.length) return
        const chunk = words[i++]
        setMessages((prev) =>
          prev.map((m) =>
            m.id === msgId ? { ...m, content: m.content + chunk } : m
          )
        )
        setTimeout(tick, 18) // ~18ms per word ≈ natural reading pace
      }
      tick()
    } else if (type === 'tool_call') {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === streamingRef.current
            ? { ...m, progress: `Reading ${tool_name}…` }
            : m
        )
      )
    } else if (type === 'tool_result') {
      // no-op
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

    const userMsg = { id: crypto.randomUUID(), role: 'user', content: question }
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
