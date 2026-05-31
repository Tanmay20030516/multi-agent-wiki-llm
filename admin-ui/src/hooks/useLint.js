// Lint state: trigger HTTP lint, show report, confirm fixes

import { useState } from 'react'
import { triggerLint, confirmLintFixes } from '../api/admin'

export function useLint() {
  const [status, setStatus] = useState('idle')  // idle | running | done | confirming | confirmed | error
  const [report, setReport] = useState(null)    // markdown string from agent
  const [sessionId, setSessionId] = useState(null)
  const [result, setResult] = useState(null)    // markdown string after confirm
  const [error, setError] = useState(null)

  async function runLint() {
    setStatus('running')
    setReport(null)
    setSessionId(null)
    setResult(null)
    setError(null)
    try {
      const data = await triggerLint()
      setReport(data.report)
      setSessionId(data.session_id)
      setStatus('done')
    } catch (e) {
      setStatus('error')
      setError(e.message)
    }
  }

  async function confirmFixes(message) {
    if (!sessionId) return
    setStatus('confirming')
    setError(null)
    try {
      const data = await confirmLintFixes(sessionId, message)
      setResult(data.result)
      setStatus('confirmed')
    } catch (e) {
      setStatus('error')
      setError(e.message)
    }
  }

  function dismiss() {
    setStatus('idle')
    setReport(null)
    setSessionId(null)
    setResult(null)
    setError(null)
  }

  return { status, report, result, error, runLint, confirmFixes, dismiss }
}
