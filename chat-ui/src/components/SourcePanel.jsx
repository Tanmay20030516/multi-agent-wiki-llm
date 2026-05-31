import { use, Suspense } from 'react'
import ReactMarkdown from 'react-markdown'
import { fetchWikiPage } from '../api/query'

const pageCache = new Map()
function getPagePromise(pageName) {
  if (!pageCache.has(pageName)) pageCache.set(pageName, fetchWikiPage(pageName))
  return pageCache.get(pageName)
}

function PageContent({ pageName }) {
  const data = use(getPagePromise(pageName))
  return (
    <div className="prose prose-sm max-w-none prose-cyber">
      <ReactMarkdown>{data.content ?? ''}</ReactMarkdown>
    </div>
  )
}

export default function SourcePanel({ pageName, onClose }) {
  if (!pageName) return null

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-10"
        style={{ background: 'rgba(7,7,20,0.7)', backdropFilter: 'blur(2px)' }}
        onClick={onClose}
      />

      {/* Slide-in panel */}
      <div className="fixed right-0 top-0 h-full w-[420px] z-20 flex flex-col slide-in-right"
        style={{
          background: '#0b0b1e',
          borderLeft: '1px solid rgba(0,245,255,0.2)',
          boxShadow: '-4px 0 40px rgba(0,245,255,0.08), -1px 0 0 rgba(0,245,255,0.15)',
        }}>

        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-[#00f5ff15]"
          style={{ background: '#080818' }}>
          <div className="flex items-center gap-2">
            <span className="glow-cyan text-xs">◈</span>
            <span className="font-mono text-xs glow-cyan">[[{pageName}]]</span>
          </div>
          <button
            onClick={onClose}
            className="text-cyber-muted hover:text-cyber-cyan transition-colors text-sm font-mono"
            style={{ lineHeight: 1 }}
          >
            ✕
          </button>
        </div>

        {/* Neon top-bar line */}
        <div style={{
          height: '1px',
          background: 'linear-gradient(90deg, transparent, #00f5ff88, transparent)',
          boxShadow: '0 0 8px #00f5ff66',
        }} />

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-5 py-5">
          <Suspense fallback={
            <p className="text-cyber-muted text-xs font-mono blink">// loading page</p>
          }>
            <PageContent pageName={pageName} />
          </Suspense>
        </div>
      </div>
    </>
  )
}
