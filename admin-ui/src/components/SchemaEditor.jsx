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
      schemaPromise = null
      setSaveState('saved')
      setTimeout(() => setSaveState('idle'), 2500)
    } catch {
      setSaveState('error')
    }
  }

  return (
    <div className="space-y-3">
      {/* Editor */}
      <div className="cyber-card overflow-hidden">
        {/* Editor titlebar */}
        <div className="flex items-center gap-2 px-4 py-2 border-b border-[#00f5ff15]"
          style={{ background: '#080818' }}>
          <span className="w-2 h-2 rounded-full bg-cyber-red" style={{ boxShadow: '0 0 4px #ff2d55' }} />
          <span className="w-2 h-2 rounded-full bg-cyber-amber" style={{ boxShadow: '0 0 4px #ffaa00' }} />
          <span className="w-2 h-2 rounded-full bg-cyber-green" style={{ boxShadow: '0 0 4px #00ff88' }} />
          <span className="cyber-label ml-2">schema.md</span>
          <span className="ml-auto cyber-label text-cyber-cyan" style={{ fontSize: '0.55rem' }}>
            {content.length.toLocaleString()} chars
          </span>
        </div>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          rows={28}
          spellCheck={false}
          className="w-full px-4 py-4 text-[0.75rem] font-mono leading-relaxed
                     outline-none resize-none bg-transparent
                     text-cyber-text caret-cyber-cyan"
          style={{ minHeight: '420px' }}
          placeholder="// schema.md content…"
        />
      </div>

      {/* Save controls */}
      <div className="flex items-center gap-3">
        <button
          onClick={handleSave}
          disabled={saveState === 'saving'}
          className="btn-cyber"
        >
          {saveState === 'saving' ? '// WRITING…' : '⬆ SAVE SCHEMA'}
        </button>

        {saveState === 'saved' && (
          <span className="glow-green text-xs font-mono fade-in-up">
            ✓ SCHEMA UPDATED
          </span>
        )}
        {saveState === 'error' && (
          <span className="glow-red text-xs font-mono">
            ✗ WRITE FAILED
          </span>
        )}
      </div>
    </div>
  )
}

export default function SchemaEditor() {
  return (
    <div className="space-y-4">
      <p className="text-cyber-muted text-xs leading-relaxed">
        // edit schema.md — defines page structure, frontmatter templates,
        and maintenance agent instructions. changes take effect immediately.
      </p>

      <Suspense fallback={
        <p className="text-cyber-muted text-xs font-mono">// loading schema…</p>
      }>
        <Editor />
      </Suspense>
    </div>
  )
}
