// Slide-in panel that shows a wiki page when a [[citation]] is clicked

import { use, Suspense } from 'react'
import ReactMarkdown from 'react-markdown'
import { fetchWikiPage } from '../api/query'

// Cache promises so we don't refetch the same page
const pageCache = new Map()

function getPagePromise(pageName) {
  if (!pageCache.has(pageName)) {
    pageCache.set(pageName, fetchWikiPage(pageName))
  }
  return pageCache.get(pageName)
}

function PageContent({ pageName }) {
  const data = use(getPagePromise(pageName))
  return (
    <div className="prose prose-sm max-w-none text-slate-700">
      <ReactMarkdown>{data.content ?? ''}</ReactMarkdown>
    </div>
  )
}

// function PageError({ pageName }) {
//   return (
//     <p className="text-sm text-red-500">
//       Could not load <span className="font-mono">[[{pageName}]]</span>
//     </p>
//   )
// }

export default function SourcePanel({ pageName, onClose }) {
  if (!pageName) return null

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/20 z-10"
        onClick={onClose}
      />

      {/* Panel */}
      <div className="fixed right-0 top-0 h-full w-105 bg-white z-20
                      shadow-2xl flex flex-col border-l border-slate-200">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4
                        border-b border-slate-100">
          <span className="font-mono text-sm text-indigo-700">[[{pageName}]]</span>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-700 transition-colors text-lg"
          >
            ✕
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-5 py-4">
          <Suspense fallback={<p className="text-sm text-slate-400">Loading…</p>}>
            <PageContent pageName={pageName} />
          </Suspense>
        </div>
      </div>
    </>
  )
}