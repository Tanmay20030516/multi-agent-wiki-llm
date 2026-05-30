// Renders log.md as a chronological activity feed

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
    <div className="prose prose-sm max-w-none text-slate-700 font-mono">
      <ReactMarkdown>{data.content ?? 'No log entries yet.'}</ReactMarkdown>
    </div>
  )
}

export default function LogViewer() {
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-sm font-semibold text-slate-700 mb-1">Activity Log</h2>
        <p className="text-xs text-slate-400">
          Append-only record of every ingest, lint pass, and query promotion.
        </p>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-5
                      overflow-y-auto max-h-[calc(100vh-220px)]">
        <Suspense fallback={<p className="text-xs text-slate-400">Loading log…</p>}>
          <LogContent />
        </Suspense>
      </div>
    </div>
  )
}