import { useState } from 'react'
import { promoteToWiki } from '../api/query'

export default function SaveToWikiButton({ message, question }) {
  const [state, setState] = useState('idle') // idle | saving | saved | error

  async function handleSave() {
    if (state !== 'idle') return
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
      setTimeout(() => setState('idle'), 2000)
    }
  }

  const label = { idle: '↑ wiki', saving: '…', saved: '✓ saved', error: '✗' }[state]
  const color = { idle: '#6b7a9e', saving: '#6b7a9e', saved: '#00ff88', error: '#ff2d55' }[state]
  const glow  = { idle: 'none', saving: 'none', saved: '0 0 6px #00ff8888', error: '0 0 6px #ff2d5588' }[state]

  return (
    <button
      onClick={handleSave}
      disabled={state === 'saving' || state === 'saved'}
      title={state === 'saved' ? 'Saved to wiki' : 'Save to wiki'}
      style={{ color, textShadow: glow, borderColor: color + '44' }}
      className="text-[0.6rem] font-mono tracking-widest px-2 py-0.5 rounded border
                 transition-all disabled:opacity-60 hover:brightness-150"
    >
      {label}
    </button>
  )
}
