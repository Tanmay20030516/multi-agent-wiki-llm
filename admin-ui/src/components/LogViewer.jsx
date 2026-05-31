import { use, Suspense } from 'react'
import ReactMarkdown from 'react-markdown'
import { fetchLog } from '../api/admin'

let logPromise = null
function getLogPromise() {
  if (!logPromise) logPromise = fetchLog()
  return logPromise
}

function LogContent() {
  const data = use(getLogPromise())
  return (
    <div className="prose prose-sm max-w-none prose-cyber font-mono">
      <ReactMarkdown>{data.content ?? '// no log entries yet.'}</ReactMarkdown>
    </div>
  )
}

export default function LogViewer() {
  return (
    <div className="space-y-4">
      <p className="text-cyber-muted text-xs leading-relaxed">
        // append-only record of every ingest, lint pass, and query promotion.
        most recent entries appear first.
      </p>

      <div className="cyber-card p-5 overflow-y-auto max-h-[calc(100vh-280px)]"
        style={{ background: '#050510' }}>
        {/* Terminal header */}
        <div className="flex items-center gap-2 mb-4 pb-3 border-b border-[#00f5ff15]">
          <span className="w-2 h-2 rounded-full bg-cyber-red" style={{ boxShadow: '0 0 4px #ff2d55' }} />
          <span className="w-2 h-2 rounded-full bg-cyber-amber" style={{ boxShadow: '0 0 4px #ffaa00' }} />
          <span className="w-2 h-2 rounded-full bg-cyber-green" style={{ boxShadow: '0 0 4px #00ff88' }} />
          <span className="cyber-label ml-2">ACTIVITY_LOG.md</span>
          <span className="ml-auto blink cyber-label" style={{ color: '#00f5ff44' }}>REC</span>
        </div>
        <Suspense fallback={
          <p className="text-cyber-muted text-xs font-mono">// loading log…</p>
        }>
          <LogContent />
        </Suspense>
      </div>
    </div>
  )
}
