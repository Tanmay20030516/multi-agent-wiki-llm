import { useState } from 'react'
import ChatWindow from './components/ChatWindow'
import SourcePanel from './components/SourcePanel'

export default function App() {
  const [openPage, setOpenPage] = useState(null)

  return (
    <div className="h-screen bg-cyber-bg flex flex-col overflow-hidden">

      {/* ── Header ── */}
      <header className="shrink-0 bg-cyber-surface border-b border-[#00f5ff22] px-6 py-3
                         flex items-center gap-4"
        style={{ boxShadow: '0 1px 20px rgba(0,245,255,0.08)' }}>

        <div className="flex items-center gap-2">
          <span className="text-lg glow-cyan">⬡</span>
          <span
            className="cyber-title text-sm font-bold tracking-widest select-none"
            data-text="WIKI//NEURAL"
          >
            WIKI//NEURAL
          </span>
        </div>

        <div className="h-4 w-px bg-[#00f5ff22]" />

        <div className="flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-cyber-green neon-pulse"
            style={{ boxShadow: '0 0 6px #00ff88' }} />
          <span className="cyber-label text-cyber-green" style={{ fontSize: '0.55rem' }}>
            QUERY INTERFACE ONLINE
          </span>
        </div>

        <div className="ml-auto">
          <span className="cyber-label">NEURAL INTERFACE</span>
        </div>
      </header>

      {/* ── Chat ── */}
      <main className="flex-1 overflow-hidden max-w-3xl w-full mx-auto flex flex-col
                       border-x border-[#00f5ff0f]"
        style={{ background: 'linear-gradient(180deg, #070714 0%, #090920 100%)' }}>
        <ChatWindow onOpenSource={setOpenPage} />
      </main>

      {/* ── Source panel ── */}
      <SourcePanel pageName={openPage} onClose={() => setOpenPage(null)} />
    </div>
  )
}
