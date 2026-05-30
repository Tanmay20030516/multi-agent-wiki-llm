// Textarea for editing schema.md with a save button

import { useState, use, Suspense } from 'react'
import { fetchSchema, saveSchema } from '../api/admin'

let schemaPromise = null
function getSchemaPromise() {
  if (!schemaPromise) schemaPromise = fetchSchema()
  return schemaPromise
}

function Editor() {
  const data = use(getSchemaPromise())
  const [content, setContent] = useState(data.content ?? '')
  const [saveState, setSaveState] = useState('idle') // idle | saving | saved | error

  async function handleSave() {
    setSaveState('saving')
    try {
      await saveSchema(content)
      // Bust cache so next open re-fetches
      schemaPromise = null
      setSaveState('saved')
      setTimeout(() => setSaveState('idle'), 2000)
    } catch {
      setSaveState('error')
    }
  }

  return (
    <div className="space-y-3">
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        rows={28}
        className="w-full rounded-xl border border-slate-200 px-4 py-3
                   text-xs font-mono text-slate-700 leading-relaxed
                   focus:outline-none focus:ring-2 focus:ring-indigo-300
                   resize-none"
        spellCheck={false}
      />

      <div className="flex items-center gap-3">
        <button
          onClick={handleSave}
          disabled={saveState === 'saving'}
          className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700
                     text-white text-sm font-medium transition-colors
                     disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {saveState === 'saving' ? 'Saving…' : 'Save schema'}
        </button>

        {saveState === 'saved' && (
          <span className="text-xs text-green-600">✓ Saved</span>
        )}
        {saveState === 'error' && (
          <span className="text-xs text-red-500">Save failed</span>
        )}
      </div>
    </div>
  )
}

export default function SchemaEditor() {
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-sm font-semibold text-slate-700 mb-1">Schema</h2>
        <p className="text-xs text-slate-400">
          Edit schema.md — this tells the maintenance agent how to structure
          every wiki page.
        </p>
      </div>

      <Suspense fallback={<p className="text-xs text-slate-400">Loading schema…</p>}>
        <Editor />
      </Suspense>
    </div>
  )
}