import ReactMarkdown from 'react-markdown'
import { useLint } from '../hooks/useLint'

export default function LintPanel() {
  const { status, report, result, error, runLint, confirmFixes, dismiss } = useLint()
  const busy = status === 'running' || status === 'confirming'

  return (
    <div className="space-y-6">
      <p className="text-cyber-muted text-xs leading-relaxed">
        // the maintenance agent will scan all wiki pages, detect broken links,
        orphaned nodes, schema violations and contradictions.
      </p>

      <button
        onClick={runLint}
        disabled={busy}
        className="btn-cyber"
        style={busy ? {} : { animationName: 'neon-pulse', animationDuration: '2.5s', animationIterationCount: 'infinite' }}
      >
        {status === 'running' ? '// SCANNING…' : '⟳ EXECUTE LINT'}
      </button>

      {/* Error */}
      {error && (
        <div className="cyber-card-red p-3 text-xs glow-red font-mono fade-in-up">
          ✗ FAULT :: {error}
        </div>
      )}

      {/* Lint report */}
      {(status === 'done' || status === 'confirming') && report && (() => {
        const hasErrors   = report.includes('🔴')
        const hasWarnings = report.includes('🟡')
        const hasIssues   = hasErrors || hasWarnings
        return (
          <div className="space-y-4 fade-in-up">
            {/* Health status banner */}
            {!hasIssues ? (
              <div className="cyber-card-green p-4 flex items-center gap-3">
                <span className="text-2xl glow-green">✓</span>
                <div>
                  <p className="text-cyber-green text-xs font-bold tracking-widest uppercase"
                    style={{ textShadow: '0 0 6px #00ff88' }}>
                    ALL SYSTEMS NOMINAL
                  </p>
                  <p className="text-xs text-cyber-muted mt-0.5">
                    zero errors · zero warnings · wiki integrity verified
                  </p>
                </div>
              </div>
            ) : (
              <div className="cyber-card p-3 flex items-center gap-3"
                style={{ borderColor: 'rgba(255,170,0,0.3)' }}>
                <span className="text-xl">⚠</span>
                <p className="text-cyber-amber text-xs tracking-wide"
                  style={{ textShadow: '0 0 6px #ffaa00' }}>
                  {hasErrors ? 'CRITICAL ISSUES DETECTED' : 'WARNINGS DETECTED'}
                </p>
              </div>
            )}

            {/* Report content */}
            <div className="cyber-card p-5">
              <p className="cyber-label mb-3">// LINT REPORT</p>
              <div className="prose prose-sm max-w-none prose-cyber">
                <ReactMarkdown>{report}</ReactMarkdown>
              </div>
            </div>

            {/* Action buttons */}
            {hasIssues ? (
              <div className="cyber-card-magenta p-4 space-y-3">
                <p className="cyber-label glow-magenta">// SELECT REPAIR MODE</p>
                <div className="flex flex-wrap gap-2 pt-1">
                  <button
                    onClick={() => confirmFixes('fix all issues')}
                    disabled={busy}
                    className="btn-cyber-magenta"
                  >
                    {status === 'confirming' ? '// APPLYING…' : '⟳ FIX ALL'}
                  </button>
                  {hasErrors && (
                    <button
                      onClick={() => confirmFixes('fix errors only, ignore warnings')}
                      disabled={busy}
                      className="btn-cyber-amber"
                    >
                      FIX ERRORS ONLY
                    </button>
                  )}
                  <button onClick={dismiss} disabled={busy} className="btn-cyber-ghost">
                    DISMISS
                  </button>
                </div>
              </div>
            ) : (
              <button onClick={dismiss} className="btn-cyber-ghost">
                CLOSE REPORT
              </button>
            )}
          </div>
        )
      })()}

      {/* Fix results */}
      {status === 'confirmed' && result && (
        <div className="cyber-card-green p-4 space-y-3 fade-in-up">
          <p className="cyber-label glow-green">// REPAIR COMPLETE</p>
          <div className="prose prose-sm max-w-none prose-cyber mt-2">
            <ReactMarkdown>{result}</ReactMarkdown>
          </div>
          <button onClick={dismiss} className="btn-cyber-ghost mt-2">
            CLOSE
          </button>
        </div>
      )}
    </div>
  )
}
