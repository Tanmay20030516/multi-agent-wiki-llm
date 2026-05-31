import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { useIngest } from '../hooks/useIngest'
import ProgressStream from './ProgressStream'

export default function IngestPanel() {
  const { status, events, error, ingestFile, ingestPastedText, confirm, reject, reset } = useIngest()
  const [pasteMode, setPasteMode] = useState(false)
  const [pastedText, setPastedText] = useState('')
  const [filename, setFilename] = useState('')

  const onDrop = useCallback((accepted) => {
    if (accepted[0]) ingestFile(accepted[0])
  }, [ingestFile])

  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    onDrop,
    accept: { 'text/*': ['.md', '.txt'], 'application/pdf': ['.pdf'] },
    multiple: false,
    disabled: status === 'uploading' || status === 'ingesting',
    noClick: true,
  })

  function handlePasteSubmit() {
    if (!pastedText.trim()) return
    ingestPastedText(pastedText, filename || 'pasted-note.md')
  }

  const busy = status === 'uploading' || status === 'ingesting' || status === 'executing'

  return (
    <div className="space-y-6">
      {/* Description */}
      <p className="text-cyber-muted text-xs leading-relaxed">
        // upload a source file or paste raw text — the maintenance agent will
        parse and integrate it into the wiki knowledge base.
      </p>

      {/* Mode toggle */}
      <div className="flex gap-2">
        {[
          { id: false, label: '↓ UPLOAD FILE' },
          { id: true,  label: '⌨ PASTE TEXT'  },
        ].map(({ id, label }) => (
          <button
            key={String(id)}
            onClick={() => { setPasteMode(id); reset() }}
            className={pasteMode === id ? 'btn-cyber' : 'btn-cyber-ghost'}
          >
            {label}
          </button>
        ))}
      </div>

      {!pasteMode ? (
        /* ── Dropzone ── */
        <div
          {...getRootProps()}
          className={`rounded border-2 border-dashed p-10 text-center transition-all
            ${isDragActive
              ? 'border-cyber-cyan bg-[#00f5ff08]'
              : 'border-[#00f5ff22] hover:border-[#00f5ff55] bg-cyber-surface'}
            ${busy ? 'opacity-30 pointer-events-none' : ''}`}
          style={isDragActive
            ? { boxShadow: '0 0 20px #00f5ff33, inset 0 0 20px #00f5ff0a' }
            : {}}
        >
          <input {...getInputProps()} />
          <div className="text-3xl mb-3 glow-cyan">⬡</div>
          <p className="text-cyber-text text-sm mb-1">
            {isDragActive ? '// DROP TO INJECT //' : 'drag & drop to upload'}
          </p>
          <p className="cyber-label mb-4">.md · .txt · .pdf</p>
          <button
            type="button"
            onClick={open}
            disabled={busy}
            className="btn-cyber"
          >
            BROWSE FILES
          </button>
        </div>
      ) : (
        /* ── Paste area ── */
        <div className="space-y-3">
          <input
            type="text"
            placeholder="// filename  (e.g. my-note.md)"
            value={filename}
            onChange={(e) => setFilename(e.target.value)}
            className="input-cyber"
          />
          <textarea
            rows={8}
            placeholder="// paste source text here..."
            value={pastedText}
            onChange={(e) => setPastedText(e.target.value)}
            className="input-cyber font-mono"
            style={{ resize: 'none' }}
          />
          <button
            onClick={handlePasteSubmit}
            disabled={!pastedText.trim() || busy}
            className="btn-cyber w-full"
          >
            {busy ? '// INGESTING…' : '⬆ INGEST TEXT'}
          </button>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="cyber-card-red p-3 text-xs glow-red font-mono">
          ✗ ERROR :: {error}
        </div>
      )}

      {/* Live stream */}
      <ProgressStream events={events} status={status} />

      {/* Confirmation gate */}
      {status === 'awaiting' && (
        <div className="cyber-card-magenta p-4 space-y-3 fade-in-up">
          <p className="cyber-label glow-magenta">// AGENT AWAITING AUTHORIZATION</p>
          <p className="text-cyber-text text-xs leading-relaxed mt-1">
            The agent has presented its write plan above. Approve to execute all writes to the wiki.
          </p>
          <div className="flex gap-2 pt-1">
            <button onClick={() => confirm('yes')} className="btn-cyber">
              ✓ AUTHORIZE &amp; WRITE
            </button>
            <button onClick={reject} className="btn-cyber-ghost">
              ✗ ABORT
            </button>
          </div>
        </div>
      )}

      {status === 'executing' && (
        <p className="text-cyber-cyan text-xs font-mono animate-pulse">
          // writing pages to wiki…
        </p>
      )}

      {status === 'done' && (
        <div className="flex items-center gap-3 pt-2">
          <span className="glow-green text-xs">✓ INGEST COMPLETE</span>
          <button onClick={reset} className="btn-cyber-ghost text-[0.6rem]">
            ← NEW INGEST
          </button>
        </div>
      )}
    </div>
  )
}
