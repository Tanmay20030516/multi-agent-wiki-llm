// Trigger lint, show markdown report, confirm fix batch

import ReactMarkdown from 'react-markdown'
import { useLint } from '../hooks/useLint'

export default function LintPanel() {
  const { status, report, result, error, runLint, confirmFixes, dismiss } = useLint()

  const busy = status === 'running' || status === 'confirming'

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-sm font-semibold text-slate-700 mb-1">Lint Wiki</h2>
        <p className="text-xs text-slate-400">
          The maintenance agent scans all wiki pages for issues and suggests
          fixes. Review the report, then choose which fixes to apply.
        </p>
      </div>

      <button
        onClick={runLint}
        disabled={busy}
        className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700
                   text-white text-sm font-medium transition-colors
                   disabled:opacity-40 disabled:cursor-not-allowed"
      >
        {status === 'running' ? 'Running lint…' : 'Run lint'}
      </button>

      {error && (
        <p className="text-sm text-red-500">Error: {error}</p>
      )}

      {/* Lint report — shown after run completes */}
      {(status === 'done' || status === 'confirming') && report && (() => {
        const hasErrors = report.includes('🔴')
        const hasWarnings = report.includes('🟡')
        const hasIssues = hasErrors || hasWarnings
        return (
          <div className="space-y-4">
            {/* Clean-wiki success banner */}
            {!hasIssues && (
              <div className="rounded-xl border border-green-200 bg-green-50 p-4 flex items-center gap-3">
                <span className="text-2xl">✅</span>
                <div>
                  <p className="text-sm font-semibold text-green-800">Wiki is healthy — no issues found</p>
                  <p className="text-xs text-green-600 mt-0.5">All pages passed the lint check.</p>
                </div>
              </div>
            )}

            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">
                Lint Report
              </p>
              <div className="prose prose-sm max-w-none text-slate-700">
                <ReactMarkdown>{report}</ReactMarkdown>
              </div>
            </div>

            {hasIssues ? (
              <div className="rounded-xl border border-indigo-200 bg-indigo-50 p-4 space-y-3">
                <p className="text-sm font-medium text-indigo-800">
                  Apply fixes? The agent will write the corrections to the wiki.
                </p>
                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={() => confirmFixes('fix all issues')}
                    disabled={busy}
                    className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700
                               text-white text-sm font-medium transition-colors
                               disabled:opacity-40 disabled:cursor-not-allowed"
                  >
                    {status === 'confirming' ? 'Applying…' : 'Fix all'}
                  </button>
                  {hasErrors && (
                    <button
                      onClick={() => confirmFixes('fix errors only, ignore warnings')}
                      disabled={busy}
                      className="px-4 py-2 rounded-lg bg-amber-500 hover:bg-amber-600
                                 text-white text-sm font-medium transition-colors
                                 disabled:opacity-40 disabled:cursor-not-allowed"
                    >
                      Fix errors only
                    </button>
                  )}
                  <button
                    onClick={dismiss}
                    disabled={busy}
                    className="px-4 py-2 rounded-lg bg-slate-100 hover:bg-slate-200
                               text-slate-600 text-sm font-medium transition-colors
                               disabled:opacity-40 disabled:cursor-not-allowed"
                  >
                    Dismiss
                  </button>
                </div>
              </div>
            ) : (
              <button
                onClick={dismiss}
                className="px-4 py-2 rounded-lg bg-slate-100 hover:bg-slate-200
                           text-slate-600 text-sm font-medium transition-colors"
              >
                Done
              </button>
            )}
          </div>
        )
      })()}

      {/* Result after fixes applied */}
      {status === 'confirmed' && result && (
        <div className="space-y-3">
          <div className="rounded-xl border border-green-200 bg-green-50 p-4">
            <p className="text-xs font-semibold text-green-700 uppercase tracking-wide mb-3">
              ✓ Fixes applied
            </p>
            <div className="prose prose-sm max-w-none text-slate-700">
              <ReactMarkdown>{result}</ReactMarkdown>
            </div>
          </div>
          <button
            onClick={dismiss}
            className="px-4 py-2 rounded-lg bg-slate-100 hover:bg-slate-200
                       text-slate-600 text-sm font-medium transition-colors"
          >
            Done
          </button>
        </div>
      )}
    </div>
  )
}
