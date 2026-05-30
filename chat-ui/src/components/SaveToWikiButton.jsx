// Appears below each assistant message — lets user promote the answer to wiki

import { useState } from 'react'
import { promoteToWiki } from '../api/query'

export default function SaveToWikiButton({ message, question }) {
  const [state, setState] = useState('idle') // idle | saving | saved | error

  async function handleSave() {
    setState('saving')
    try {
      await promoteToWiki({
        title: question.slice(0, 60),
        content: message.content,
        source_question: question,
      })
      setState('saved')
    } catch {
      setState('error')
    }
  }

  if (state === 'saved') {
    return (
      <span className="text-xs text-green-600 flex items-center gap-1">
        ✓ Saved to wiki
      </span>
    )
  }

  return (
    <button
      onClick={handleSave}
      disabled={state === 'saving'}
      className="text-xs text-slate-400 hover:text-indigo-600 transition-colors
                 disabled:opacity-50 flex items-center gap-1"
    >
      {state === 'saving' ? 'Saving…' : '↑ Save to wiki'}
      {state === 'error' && <span className="text-red-500 ml-1">Failed</span>}
    </button>
  )
}