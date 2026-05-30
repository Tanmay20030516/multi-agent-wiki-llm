// Trigger lint, show report, approve/reject per issue

import { useLint } from '../hooks/useLint'
import ProgressStream from './ProgressStream'

const stateStyles = {
  approved: 'bg-green-50 border-green-200',
  rejected: 'bg-slate-50 border-slate-200 opacity-60',
  pending: 'bg-white border-slate-200',
}

export default function LintPanel() {
  const { status, events, report, error, runLint, approve, reject } = useLint()

  const busy = status === 'running'

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-sm font-semibold text-slate-700 mb-1">Lint Wiki</h2>
        <p className="text-xs text-slate-400">
          The maintenance agent scans all wiki pages for issues and suggests
          fixes. Review each fix before applying.
        </p>
      </div>

      <button
        onClick={runLint}
        disabled={busy}
        className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700
                   text-white text-sm font-medium transition-colors
                   disabled:opacity-40 disabled:cursor-not-allowed"
      >
        {busy ? 'Running lint…' : 'Run lint'}
      </button>

      {error && (
        <p className="text-sm text-red-500">Error: {error}</p>
      )}

      <ProgressStream events={events.map((e) => ({ kind: 'progress', text: e }))} status={status} />

      {/* Report */}
      {report && (
        <div className="space-y-3">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">
            {report.issues.length} issue{report.issues.length !== 1 ? 's' : ''} found
          </p>

          {report.issues.length === 0 && (
            <p className="text-sm text-green-600">✓ Wiki looks clean</p>
          )}

          {report.issues.map((issue) => (
            <div
              key={issue.id}
              className={`rounded-xl border p-4 space-y-2 transition-colors
                          ${stateStyles[issue.state ?? 'pending']}`}
            >
              {/* Issue header */}
              <div className="flex items-start justify-between gap-4">
                <div className="space-y-0.5">
                  <p className="text-xs font-mono text-slate-500">{issue.page}</p>
                  <p className="text-sm text-slate-700">{issue.description}</p>
                </div>
                <span className={`shrink-0 text-xs px-2 py-0.5 rounded-full font-medium
                  ${issue.severity === 'error'
                    ? 'bg-red-100 text-red-600'
                    : 'bg-yellow-100 text-yellow-700'}`}>
                  {issue.severity ?? 'warn'}
                </span>
              </div>

              {/* Suggested fix */}
              {issue.fix && (
                <pre className="text-xs bg-slate-100 rounded-lg p-3 overflow-x-auto
                                text-slate-600 whitespace-pre-wrap">
                  {issue.fix}
                </pre>
              )}

              {/* Actions */}
              {!issue.state && (
                <div className="flex gap-2 pt-1">
                  <button
                    onClick={() => approve(issue.id)}
                    className="px-3 py-1 rounded-lg text-xs font-medium
                               bg-green-600 hover:bg-green-700 text-white transition-colors"
                  >
                    Apply fix
                  </button>
                  <button
                    onClick={() => reject(issue.id)}
                    className="px-3 py-1 rounded-lg text-xs font-medium
                               bg-slate-100 hover:bg-slate-200 text-slate-600 transition-colors"
                  >
                    Ignore
                  </button>
                </div>
              )}

              {issue.state === 'approved' && (
                <p className="text-xs text-green-600">✓ Fix applied</p>
              )}
              {issue.state === 'rejected' && (
                <p className="text-xs text-slate-400">Ignored</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}