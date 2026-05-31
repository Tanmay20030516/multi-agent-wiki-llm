import { useState } from 'react'
import { promoteToWiki } from '../api/query'

export default function SaveToWikiButton({ message, question }) {
  const [state, setState] = useState('idle')

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
      <span className="text-[0.65rem] font-mono glow-green flex items-center gap-1">
        ✓ COMMITTED TO WIKI
      </span>
    )
  }

  return (
    <button
      onClick={handleSave}
      disabled={state === 'saving'}
      className="text-[0.65rem] font-mono tracking-widest transition-all
                 flex items-center gap-1 disabled:opacity-40"
      style={{
        color: state === 'error' ? '#ff2d55' : '#6b7a9e',
        textShadow: state === 'error' ? '0 0 6px #ff2d55' : 'none',
      }}
      onMouseEnter={e => {
        if (state === 'idle') {
          e.currentTarget.style.color = '#00f5ff'
          e.currentTarget.style.textShadow = '0 0 6px #00f5ff88'
        }
      }}
      onMouseLeave={e => {
        if (state === 'idle') {
          e.currentTarget.style.color = '#6b7a9e'
          e.currentTarget.style.textShadow = 'none'
        }
      }}
    >
      {state === 'saving' ? '// WRITING TO WIKI…' :
       state === 'error'  ? '✗ WRITE FAILED' :
                            '↑ SAVE TO WIKI'}
    </button>
  )
}
