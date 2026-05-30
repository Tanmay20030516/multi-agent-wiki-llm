// Ingest state: upload, trigger, live progress events from WebSocket

import { useState, useEffect } from 'react'
import { useWebSocket } from './useWebSocket'
import { uploadSource, ingestText } from '../api/admin'

const WS_URL = `ws://${window.location.host}/ws/maintenance`

export function useIngest() {
  const [status, setStatus] = useState('idle') // idle | uploading | ingesting | awaiting | executing | done | error
  const [events, setEvents] = useState([])
  const [error, setError] = useState(null)
  const [sessionId, setSessionId] = useState(null)  // stored when agent pauses for confirmation
  const { lastEvent, connected, send } = useWebSocket(WS_URL)

  useEffect(() => {
    if (!lastEvent) return
    const { type, content, tool_name, tool_args, session_id } = lastEvent

    if (type === 'tool_call') {
      const desc = tool_args?.path || tool_args?.query || tool_args?.slug || ''
      setEvents((prev) => [...prev, { kind: 'progress', text: `${tool_name}(${desc})` }])
    } else if (type === 'tool_result') {
      setEvents((prev) => [...prev, { kind: 'progress', text: content }])
    } else if (type === 'llm_response') {
      setEvents((prev) => [...prev, { kind: 'token', text: content }])
    } else if (type === 'awaiting_input') {
      // Agent finished planning — waiting for user to confirm before writing
      setEvents((prev) => [...prev, { kind: 'token', text: content }])
      setSessionId(session_id)
      setStatus('awaiting')
    } else if (type === 'done') {
      setSessionId(null)
      setStatus('done')
    } else if (type === 'error') {
      setStatus('error')
      setError(content)
    }
  }, [lastEvent])

  async function ingestFile(file) {
    setStatus('uploading')
    setEvents([])
    setError(null)
    setSessionId(null)
    try {
      const { path } = await uploadSource(file)
      setStatus('ingesting')
      send({ type: 'ingest', source_path: path })
    } catch (e) {
      setStatus('error')
      setError(e.message)
    }
  }

  async function ingestPastedText(text, filename) {
    setStatus('uploading')
    setEvents([])
    setError(null)
    setSessionId(null)
    try {
      const { path } = await ingestText(text, filename)
      setStatus('ingesting')
      send({ type: 'ingest', source_path: path })
    } catch (e) {
      setStatus('error')
      setError(e.message)
    }
  }

  function confirm(message = 'yes') {
    if (!sessionId) return
    setStatus('executing')
    send({ type: 'continue', session_id: sessionId, message })
    setSessionId(null)
  }

  function reject() {
    setSessionId(null)
    setStatus('idle')
    setEvents([])
  }

  function reset() {
    setStatus('idle')
    setEvents([])
    setError(null)
    setSessionId(null)
  }

  return { status, events, error, connected, sessionId, ingestFile, ingestPastedText, confirm, reject, reset }
}
