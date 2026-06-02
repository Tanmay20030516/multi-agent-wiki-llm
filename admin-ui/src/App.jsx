import { useState } from 'react'
import IngestPanel from './components/IngestPanel'
import LintPanel from './components/LintPanel'
import WikiBrowser from './components/WikiBrowser'
import LogViewer from './components/LogViewer'
import SchemaEditor from './components/SchemaEditor'

const TABS = [
  { id: 'ingest', label: 'INGEST',  glyph: '⬇️', component: IngestPanel },
  { id: 'lint',   label: 'LINT',    glyph: '🛠️', component: LintPanel },
  { id: 'wiki',   label: 'WIKI',    glyph: '🧠', component: WikiBrowser },
  { id: 'log',    label: 'LOG',     glyph: '🖥️', component: LogViewer },
  { id: 'schema', label: 'SCHEMA',  glyph: '🗂️', component: SchemaEditor },
]

export default function App() {
  const [activeTab, setActiveTab] = useState('ingest')
  const ActiveComponent = TABS.find((t) => t.id === activeTab).component

  return (
    <div className="h-screen bg-cyber-bg flex flex-col overflow-hidden">

      {/* ── Header ── */}
      <header className="shrink-0 border-b border-[#00f5ff22] bg-cyber-surface px-6 py-3
                         flex items-center gap-4"
        style={{ boxShadow: '0 1px 20px rgba(0,245,255,0.08)' }}>

        {/* Logo */}
        <div className="flex items-center gap-2">
          <span className="text-lg">⬡</span>
          <span
            className="cyber-title text-sm font-bold tracking-widest select-none"
            data-text="WIKI//SYS"
          >
            WIKI//SYS
          </span>
        </div>

        {/* Separator */}
        <div className="h-4 w-px bg-[#00f5ff22]" />

        {/* Status dot */}
        <div className="flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-cyber-green neon-pulse"
            style={{ boxShadow: '0 0 6px #00ff88, 0 0 12px #00ff8866' }} />
          <span className="cyber-label text-cyber-green" style={{ fontSize: '0.55rem' }}>
            SYSTEMS NOMINAL
          </span>
        </div>

        <div className="ml-auto flex items-center gap-3">
          <span className="cyber-label">ADMIN CONSOLE</span>
          <span className="border border-[#00f5ff33] px-2 py-0.5 rounded text-[0.55rem]
                           text-cyber-cyan tracking-widest font-mono">
            v0.1.0
          </span>
        </div>
      </header>

      {/* ── Tab bar ── */}
      <nav className="shrink-0 bg-cyber-surface border-b border-[#00f5ff15] px-6 flex gap-0.5">
        {TABS.map((tab) => {
          const active = activeTab === tab.id
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-3 text-[0.65rem] tracking-[0.15em] font-mono font-medium
                         transition-all relative group
                         ${active
                           ? 'text-cyber-cyan'
                           : 'text-cyber-muted hover:text-cyber-text'}`}
            >
              {/* Active underline glow */}
              {active && (
                <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-cyber-cyan"
                  style={{ boxShadow: '0 0 8px #00f5ff, 0 0 16px #00f5ff88' }} />
              )}
              <span className="mr-1.5 opacity-60">{tab.glyph}</span>
              {tab.label}
            </button>
          )
        })}
      </nav>

      {/* ── Panel ── */}
      <main className="flex-1 overflow-y-auto cyber-grid" style={{ minHeight: 0 }}>
        <div className={`${activeTab === 'wiki' ? '' : 'max-w-4xl mx-auto'} px-6 py-8 fade-in-up`}>
          {/* Panel header */}
          <div className="flex items-center gap-3 mb-6">
            <span className="cyber-label text-cyber-muted">
              {'>>'} {TABS.find(t => t.id === activeTab)?.label}
            </span>
            <div className="flex-1 cyber-divider" />
          </div>
          <ActiveComponent />
        </div>
      </main>
    </div>
  )
}
