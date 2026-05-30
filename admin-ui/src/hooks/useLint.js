// Lint state: trigger, report, per-issue approve/reject

import { useState, useEffect } from 'react'
import { useWebSocket } from './useWebSocket'
import { triggerLint, approveFix, rejectFix } from '../api/admin'

const WS_URL = `ws://${window.location.host}/ws/maintenance`

export function useLint() {
  const [status, setStatus] = useState('idle')  // idle | running | done | error
  const [events, setEvents] = useState([])
  const [report, setReport] = useState(null)    // { issues: [...] }
  const [error, setError] = useState(null)
  const { lastEvent, connected } = useWebSocket(WS_URL)

  useEffect(() => {
    if (!lastEvent) return
    const { type, payload } = lastEvent

    if (type === 'progress') {
      setEvents((prev) => [...prev, payload])
    } else if (type === 'done') {
      setStatus('done')
      // payload may carry the report JSON
      if (payload?.issues) setReport(payload)
    } else if (type === 'error') {
      setStatus('error')
      setError(payload)
    }
  }, [lastEvent])

  async function runLint() {
    setStatus('running')
    setEvents([])
    setReport(null)
    setError(null)
    try {
      const result = await triggerLint()
      // Backend may return report synchronously or via WS
      if (result?.issues) {
        setReport(result)
        setStatus('done')
      }
    } catch (e) {
      setStatus('error')
      setError(e.message)
    }
  }

  async function approve(issueId) {
    await approveFix(issueId)
    setReport((prev) => ({
      ...prev,
      issues: prev.issues.map((i) =>
        i.id === issueId ? { ...i, state: 'approved' } : i
      ),
    }))
  }

  async function reject(issueId) {
    await rejectFix(issueId)
    setReport((prev) => ({
      ...prev,
      issues: prev.issues.map((i) =>
        i.id === issueId ? { ...i, state: 'rejected' } : i
      ),
    }))
  }

  return { status, events, report, error, connected, runLint, approve, reject }
}