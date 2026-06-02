// Thread management — persisted to SQLite via backend API
// A thread = { id, title, messages, created_at, updated_at }

import { useState, useCallback, useEffect } from 'react'

const API = '/api/chats'

// ── API helpers ─────────────────────────────────────────────────────────────

async function apiFetch(path, opts = {}) {
  const res = await fetch(`${API}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  })
  if (!res.ok && res.status !== 204) throw new Error(`${opts.method ?? 'GET'} ${path} → ${res.status}`)
  if (res.status === 204) return null
  return res.json()
}

// ── Hook ────────────────────────────────────────────────────────────────────

export function useThreads() {
  const [threads, setThreads]   = useState([])   // [{id, title, created_at, updated_at, message_count}]
  const [activeId, setActiveId] = useState(null)
  const [messages, setMessages] = useState([])   // messages for active thread
  const [loading, setLoading]   = useState(true)

  // Load thread list on mount
  useEffect(() => {
    apiFetch('')
      .then(data => {
        setThreads(data)
        setLoading(false)
        // Auto-select most recent, or create first thread
        if (data.length > 0) {
          setActiveId(data[0].id)
        }
      })
      .catch(() => setLoading(false))
  }, [])

  // Load messages when active thread changes
  useEffect(() => {
    if (!activeId) { setMessages([]); return }
    apiFetch(`/${activeId}`)
      .then(thread => {
        const msgs = (thread.messages ?? []).map(m => ({
          id: m.id,
          role: m.role,
          content: m.content,
          isError: !!m.is_error,
          progress: null,
        }))
        setMessages(msgs)
      })
      .catch(() => setMessages([]))
  }, [activeId])

  // Create a new thread
  const newThread = useCallback(async () => {
    const id = crypto.randomUUID()
    const thread = await apiFetch('', {
      method: 'POST',
      body: JSON.stringify({ id, title: 'New thread' }),
    })
    setThreads(prev => [thread, ...prev])
    setActiveId(id)
    setMessages([])
    return id
  }, [])

  // Persist messages to backend (called by useChat after each update)
  const updateMessages = useCallback(async (threadId, newMessages) => {
    setMessages(newMessages)

    // Auto-title from first user message
    const firstUser = newMessages.find(m => m.role === 'user')
    if (firstUser) {
      const title = firstUser.content.replace(/\[\[.+?\]\]/g, '').trim().slice(0, 50)
      setThreads(prev => prev.map(t =>
        t.id === threadId && t.title === 'New thread'
          ? { ...t, title, updated_at: Date.now() }
          : t.id === threadId ? { ...t, updated_at: Date.now() } : t
      ))
      // Persist title update only when it's still the default
      const thread = threads.find(t => t.id === threadId)
      if (thread?.title === 'New thread') {
        apiFetch(`/${threadId}`, { method: 'PATCH', body: JSON.stringify({ title }) }).catch(() => {})
      }
    }

    // Persist messages (fire-and-forget)
    apiFetch(`/${threadId}/messages`, {
      method: 'PUT',
      body: JSON.stringify({ messages: newMessages }),
    }).catch(() => {})
  }, [threads])

  // Switch to a thread
  const switchThread = useCallback((threadId) => {
    setActiveId(threadId)
  }, [])

  // Delete a thread
  const deleteThread = useCallback(async (threadId) => {
    await apiFetch(`/${threadId}`, { method: 'DELETE' })
    setThreads(prev => {
      const updated = prev.filter(t => t.id !== threadId)
      if (threadId === activeId) {
        const nextId = updated.length ? updated[0].id : null
        setActiveId(nextId)
        if (!nextId) setMessages([])
      }
      return updated
    })
  }, [activeId])

  const activeThread = threads.find(t => t.id === activeId) ?? null

  return {
    threads,
    activeId,
    activeThread,
    messages,        // messages for active thread (pre-loaded)
    loading,
    newThread,
    updateMessages,
    deleteThread,
    switchThread,
  }
}
