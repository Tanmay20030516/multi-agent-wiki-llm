// Root layout: ChatWindow left, SourcePanel slide-in right

import { useState } from 'react'
import ChatWindow from './components/ChatWindow'
import SourcePanel from './components/SourcePanel'

export default function App() {
  const [openPage, setOpenPage] = useState(null)

  return (
    <div className="h-screen bg-slate-50 flex flex-col">
      {/* Top bar */}
      <header className="bg-white border-b border-slate-200 px-6 py-3
                         flex items-center gap-3 shrink-0">
        <span className="text-lg">🧠</span>
        <h1 className="font-semibold text-slate-800 text-sm tracking-wide">
          LLM Wiki
        </h1>
        <span className="text-slate-300 text-xs ml-auto">chat</span>
      </header>

      {/* Main */}
      <main className="flex-1 overflow-hidden max-w-3xl w-full mx-auto
                       flex flex-col bg-white border-x border-slate-200">
        <ChatWindow onOpenSource={setOpenPage} />
      </main>

      {/* Source panel (slide-in) */}
      <SourcePanel
        pageName={openPage}
        onClose={() => setOpenPage(null)}
      />
    </div>
  )
}