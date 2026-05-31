import { useRef, useEffect } from 'react'

const kindColor = {
  progress: '#6b7a9e',
  token:    '#00f5ff',
  error:    '#ff2d55',
}

export default function ProgressStream({ events, status }) {
  const bottomRef = useRef(null)
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [events])

  if (!events.length && status === 'idle') return null

  return (
    <div className="mt-4 rounded cyber-card font-mono text-xs p-4 h-52 overflow-y-auto"
      style={{ background: '#050510', borderColor: 'rgba(0,245,255,0.15)' }}>

      {/* Terminal header bar */}
      <div className="flex items-center gap-2 mb-3 pb-2 border-b border-[#00f5ff15]">
        <span className="w-2 h-2 rounded-full bg-cyber-red"
          style={{ boxShadow: '0 0 4px #ff2d55' }} />
        <span className="w-2 h-2 rounded-full bg-cyber-amber"
          style={{ boxShadow: '0 0 4px #ffaa00' }} />
        <span className="w-2 h-2 rounded-full bg-cyber-green"
          style={{ boxShadow: '0 0 4px #00ff88' }} />
        <span className="cyber-label ml-2">AGENT STREAM</span>
      </div>

      {events.length === 0 && (
        <span className="text-[#2a2a4a]">// waiting for agent response…</span>
      )}

      {events.map((ev, i) => (
        <div key={i} className="flex gap-2 leading-5">
          <span style={{ color: '#00f5ff55' }} className="select-none shrink-0">›</span>
          <span style={{ color: kindColor[ev.kind] ?? '#a8b8d8' }}>{ev.text}</span>
        </div>
      ))}

      {status === 'done' && (
        <div className="mt-2 glow-green flex items-center gap-2">
          <span>✓</span>
          <span>PROCESS COMPLETE</span>
        </div>
      )}
      {status === 'error' && (
        <div className="mt-2 glow-red flex items-center gap-2">
          <span>✗</span>
          <span>PROCESS TERMINATED — CHECK LOGS</span>
        </div>
      )}
      <div ref={bottomRef} />
    </div>
  )
}
