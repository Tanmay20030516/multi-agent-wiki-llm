import { useState, useCallback, useEffect, useRef } from 'react'
import ChatWindow from './components/ChatWindow'
import SourcePanel from './components/SourcePanel'
import ThreadSidebar from './components/ThreadSidebar'
import { useThreads } from './hooks/useThreads'

export default function App() {
  const [openPage, setOpenPage] = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const {
    threads,
    activeId,
    messages,        // pre-loaded messages for active thread
    loading,
    newThread,
    updateMessages,
    deleteThread,
    switchThread,
  } = useThreads()

  // Auto-create first thread when DB is empty (guard against strict-mode double-invoke)
  const didInit = useRef(false)
  useEffect(() => {
    if (!loading && !didInit.current && threads.length === 0) {
      didInit.current = true
      newThread()
    }
  }, [loading, threads.length, newThread])

  const handleMessagesChange = useCallback((msgs) => {
    if (activeId) updateMessages(activeId, msgs)
  }, [activeId, updateMessages])

  return (
    <div className="h-screen bg-cyber-bg flex flex-col overflow-hidden">

      {/* ── Header ── */}
      <header className="shrink-0 bg-cyber-surface border-b border-[#00f5ff22] px-4 py-3
                         flex items-center gap-4"
        style={{ boxShadow: '0 1px 20px rgba(0,245,255,0.08)' }}>

        <button
          onClick={() => setSidebarOpen(v => !v)}
          className="text-cyber-muted hover:text-cyber-cyan transition-colors text-sm font-mono"
          title={sidebarOpen ? 'Hide threads' : 'Show threads'}
        >
          ☰
        </button>

        <div className="h-4 w-px bg-[#00f5ff22]" />

        <div className="flex items-center gap-2">
          <span className="text-lg glow-cyan">⬡</span>
          <span className="cyber-title text-sm font-bold tracking-widest select-none"
                data-text="WIKI//NEURAL">
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

        <div className="ml-auto flex items-center gap-3">
          <span className="cyber-label">NEURAL INTERFACE</span>
          <button onClick={newThread} className="btn-cyber-ghost text-xs px-3 py-1">
            ＋ NEW
          </button>
        </div>
      </header>

      {/* ── Body ── */}
      <div className="flex-1 overflow-hidden flex">

        {sidebarOpen && (
          <ThreadSidebar
            threads={threads}
            activeId={activeId}
            onNew={newThread}
            onSwitch={switchThread}
            onDelete={deleteThread}
          />
        )}

        <main className="flex-1 overflow-hidden flex flex-col border-x border-[#00f5ff0f]"
          style={{ background: 'linear-gradient(180deg, #070714 0%, #090920 100%)' }}>
          {loading ? (
            <div className="flex-1 flex items-center justify-center">
              <p className="cyber-label text-cyber-muted blink">// connecting…</p>
            </div>
          ) : activeId ? (
            <ChatWindow
              key={activeId}
              onOpenSource={setOpenPage}
              initialMessages={messages}
              onMessagesChange={handleMessagesChange}
            />
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center space-y-3">
                <div style={{ fontSize: '3rem', color: '#00f5ff', opacity: 0.3 }}>⬡</div>
                <p className="cyber-label">NO THREAD SELECTED</p>
                <button onClick={newThread} className="btn-cyber text-xs px-4 py-2">
                  ＋ NEW THREAD
                </button>
              </div>
            </div>
          )}
        </main>
      </div>

      <SourcePanel pageName={openPage} onClose={() => setOpenPage(null)} />
    </div>
  )
}
