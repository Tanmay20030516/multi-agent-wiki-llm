// Ingest state: upload, trigger, live progress events from WebSocket

import { useState, useEffect } from 'react'
import { useWebSocket } from './useWebSocket'
import { uploadSource, ingestText } from '../api/admin'

const WS_URL = `ws://${window.location.host}/ws/maintenance`

export function useIngest() {
  const [status, setStatus] = useState('idle') // idle | uploading | ingesting | done | error
  const [events, setEvents] = useState([])     // progress log lines
  const [error, setError] = useState(null)
  const { lastEvent, connected, send } = useWebSocket(WS_URL)

  useEffect(() => {
    if (!lastEvent) return
    const { type, payload } = lastEvent

    if (type === 'progress') {
      setEvents((prev) => [...prev, { kind: 'progress', text: payload }])
    } else if (type === 'token') {
      setEvents((prev) => [...prev, { kind: 'token', text: payload }])
    } else if (type === 'done') {
      setStatus('done')
    } else if (type === 'error') {
      setStatus('error')
      setError(payload)
    }
  }, [lastEvent])

  async function ingestFile(file) {
    setStatus('uploading')
    setEvents([])
    setError(null)
    try {
      const { path } = await uploadSource(file)
      setStatus('ingesting')
      send({ action: 'ingest', source_path: path })
    } catch (e) {
      setStatus('error')
      setError(e.message)
    }
  }

  async function ingestPastedText(text, filename) {
    setStatus('uploading')
    setEvents([])
    setError(null)
    try {
      const { path } = await ingestText(text, filename)
      setStatus('ingesting')
      send({ action: 'ingest', source_path: path })
    } catch (e) {
      setStatus('error')
      setError(e.message)
    }
  }

  function reset() {
    setStatus('idle')
    setEvents([])
    setError(null)
  }

  return { status, events, error, connected, ingestFile, ingestPastedText, reset }
}