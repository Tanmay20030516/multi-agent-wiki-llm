// Root layout: tabbed interface — Ingest | Lint | Wiki | Log | Schema

import { useState } from 'react'
import IngestPanel from './components/IngestPanel'
import LintPanel from './components/LintPanel'
import WikiBrowser from './components/WikiBrowser'
import LogViewer from './components/LogViewer'
import SchemaEditor from './components/SchemaEditor'

const TABS = [
  { id: 'ingest', label: '↓ Ingest',  component: IngestPanel },
  { id: 'lint',   label: '✦ Lint',    component: LintPanel },
  { id: 'wiki',   label: '📖 Wiki',   component: WikiBrowser },
  { id: 'log',    label: '📋 Log',    component: LogViewer },
  { id: 'schema', label: '⚙ Schema', component: SchemaEditor },
]

export default function App() {
  const [activeTab, setActiveTab] = useState('ingest')
  const ActiveComponent = TABS.find((t) => t.id === activeTab).component

  return (
    <div className="h-screen bg-slate-50 flex flex-col">
      {/* Top bar */}
      <header className="bg-white border-b border-slate-200 px-6 py-3
                         flex items-center gap-3 shrink-0">
        <span className="text-lg">🛠</span>
        <h1 className="font-semibold text-slate-800 text-sm tracking-wide">
          LLM Wiki
        </h1>
        <span className="text-slate-300 text-xs ml-auto">admin</span>
      </header>

      {/* Tab bar */}
      <nav className="bg-white border-b border-slate-200 px-6 flex gap-1 shrink-0">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-3 py-2.5 text-xs font-medium transition-colors border-b-2
              ${activeTab === tab.id
                ? 'border-indigo-600 text-indigo-700'
                : 'border-transparent text-slate-500 hover:text-slate-700'}`}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      {/* Panel */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-6 py-6">
          <ActiveComponent />
        </div>
      </main>
    </div>
  )
}