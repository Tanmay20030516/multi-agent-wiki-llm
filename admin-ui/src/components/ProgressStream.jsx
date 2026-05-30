// Live event feed shown during ingest and lint operations

import { useRef, useEffect } from 'react'

const kindStyles = {
  progress: 'text-slate-400',
  token: 'text-indigo-400',
  error: 'text-red-400',
}

export default function ProgressStream({ events, status }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [events])

  if (!events.length && status === 'idle') return null

  return (
    <div className="mt-4 rounded-xl border border-slate-200 bg-slate-950
                    font-mono text-xs p-4 h-52 overflow-y-auto">
      {events.length === 0 && (
        <span className="text-slate-500">Waiting for agent…</span>
      )}

      {events.map((ev, i) => (
        <div key={i} className={kindStyles[ev.kind] ?? 'text-slate-300'}>
          <span className="text-slate-600 mr-2 select-none">›</span>
          {ev.text}
        </div>
      ))}

      {status === 'done' && (
        <div className="text-green-400 mt-2">✓ Done</div>
      )}
      {status === 'error' && (
        <div className="text-red-400 mt-2">✗ Error</div>
      )}

      <div ref={bottomRef} />
    </div>
  )
}