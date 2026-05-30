// Drag-and-drop file upload + text paste area for ingesting raw sources

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

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'text/*': ['.md', '.txt'], 'application/pdf': ['.pdf'] },
    multiple: false,
    disabled: status === 'uploading' || status === 'ingesting',
  })

  function handlePasteSubmit() {
    if (!pastedText.trim()) return
    ingestPastedText(pastedText, filename || 'pasted-note.md')
  }

  const busy = status === 'uploading' || status === 'ingesting' || status === 'executing'

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-sm font-semibold text-slate-700 mb-1">Ingest Source</h2>
        <p className="text-xs text-slate-400">
          Upload a file or paste text. The maintenance agent will process it
          into the wiki.
        </p>
      </div>

      {/* Mode toggle */}
      <div className="flex gap-2">
        <button
          onClick={() => { setPasteMode(false); reset() }}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors
            ${!pasteMode
              ? 'bg-indigo-600 text-white'
              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}
        >
          Upload file
        </button>
        <button
          onClick={() => { setPasteMode(true); reset() }}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors
            ${pasteMode
              ? 'bg-indigo-600 text-white'
              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}
        >
          Paste text
        </button>
      </div>

      {!pasteMode ? (
        // Dropzone
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-10 text-center
                      cursor-pointer transition-colors
                      ${isDragActive
                        ? 'border-indigo-400 bg-indigo-50'
                        : 'border-slate-200 hover:border-slate-300 bg-slate-50'}
                      ${busy ? 'opacity-50 pointer-events-none' : ''}`}
        >
          <input {...getInputProps()} />
          <p className="text-2xl mb-2">📄</p>
          <p className="text-sm text-slate-600">
            {isDragActive ? 'Drop it here…' : 'Drag & drop a file, or click to browse'}
          </p>
          <p className="text-xs text-slate-400 mt-1">.md · .txt · .pdf</p>
        </div>
      ) : (
        // Paste area
        <div className="space-y-3">
          <input
            type="text"
            placeholder="Filename (e.g. my-note.md)"
            value={filename}
            onChange={(e) => setFilename(e.target.value)}
            className="w-full rounded-lg border border-slate-200 px-3 py-2
                       text-sm text-slate-700 placeholder:text-slate-400
                       focus:outline-none focus:ring-2 focus:ring-indigo-300"
          />
          <textarea
            rows={8}
            placeholder="Paste your text here…"
            value={pastedText}
            onChange={(e) => setPastedText(e.target.value)}
            className="w-full rounded-lg border border-slate-200 px-3 py-2
                       text-sm text-slate-700 placeholder:text-slate-400
                       focus:outline-none focus:ring-2 focus:ring-indigo-300
                       resize-none font-mono"
          />
          <button
            onClick={handlePasteSubmit}
            disabled={!pastedText.trim() || busy}
            className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700
                       text-white text-sm font-medium transition-colors
                       disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {busy ? 'Ingesting…' : 'Ingest text'}
          </button>
        </div>
      )}

      {/* Status + live stream */}
      {error && (
        <p className="text-sm text-red-500">Error: {error}</p>
      )}
      <ProgressStream events={events} status={status} />

      {/* Confirmation prompt — agent has presented its plan and is waiting */}
      {status === 'awaiting' && (
        <div className="rounded-xl border border-indigo-200 bg-indigo-50 p-4 space-y-3">
          <p className="text-sm font-medium text-indigo-800">
            Agent is waiting for your approval to write the pages above.
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => confirm('yes')}
              className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700
                         text-white text-sm font-medium transition-colors"
            >
              ✓ Approve &amp; write
            </button>
            <button
              onClick={reject}
              className="px-4 py-2 rounded-lg bg-slate-100 hover:bg-slate-200
                         text-slate-600 text-sm font-medium transition-colors"
            >
              ✗ Cancel
            </button>
          </div>
        </div>
      )}

      {status === 'executing' && (
        <p className="text-sm text-indigo-600 animate-pulse">Writing pages to wiki…</p>
      )}

      {status === 'done' && (
        <button
          onClick={reset}
          className="text-xs text-slate-400 hover:text-slate-600 transition-colors"
        >
          ← Ingest another
        </button>
      )}
    </div>
  )
}