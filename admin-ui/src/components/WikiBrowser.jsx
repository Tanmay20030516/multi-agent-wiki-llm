// File tree and graph view of wiki/ — click a page to read its content

import { useState, use, Suspense, lazy } from 'react'
import ReactMarkdown from 'react-markdown'
import { fetchWikiTree, fetchWikiPage } from '../api/admin'

const WikiGraph = lazy(() => import('./WikiGraph'))

// Promise cache — avoids refetch on re-render
let treePromise = null
function getTreePromise() {
  if (!treePromise) treePromise = fetchWikiTree()
  return treePromise
}
export function invalidateTreeCache() {
  treePromise = null
  pageCache.clear()
}

const pageCache = new Map()
function getPagePromise(path) {
  if (!pageCache.has(path)) pageCache.set(path, fetchWikiPage(path))
  return pageCache.get(path)
}

function TreeNode({ node, depth, selected, onSelect }) {
  const isDir = node.type === 'directory'
  const indent = depth * 16

  return (
    <div>
      <button
        onClick={() => !isDir && onSelect(node.path)}
        style={{ paddingLeft: `${indent + 8}px` }}
        className={`w-full text-left py-1 pr-3 text-xs rounded transition-colors
          flex items-center gap-1.5
          ${isDir
            ? 'text-slate-500 font-semibold cursor-default'
            : selected === node.path
              ? 'bg-indigo-50 text-indigo-700'
              : 'text-slate-600 hover:bg-slate-100'}`}
      >
        <span>{isDir ? '📁' : '📄'}</span>
        {node.name}
      </button>

      {isDir && node.children?.map((child) => (
        <TreeNode
          key={child.path}
          node={child}
          depth={depth + 1}
          selected={selected}
          onSelect={onSelect}
        />
      ))}
    </div>
  )
}

function WikiTree({ selected, onSelect }) {
  const tree = use(getTreePromise())
  return (
    <div className="space-y-0.5">
      {tree.map((node) => (
        <TreeNode
          key={node.path}
          node={node}
          depth={0}
          selected={selected}
          onSelect={onSelect}
        />
      ))}
    </div>
  )
}

function PageView({ path }) {
  const data = use(getPagePromise(path))
  return (
    <div className="prose prose-sm max-w-none text-slate-700">
      <ReactMarkdown>{data.content ?? ''}</ReactMarkdown>
    </div>
  )
}

export default function WikiBrowser() {
  const [selected, setSelected] = useState(null)
  const [view, setView] = useState('tree') // 'tree' | 'graph'

  return (
    <div className="flex flex-col gap-4 h-full">
      {/* View toggle */}
      <div className="flex gap-2">
        {['tree', 'graph'].map(v => (
          <button
            key={v}
            onClick={() => setView(v)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors capitalize
              ${view === v
                ? 'bg-indigo-600 text-white'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}
          >
            {v === 'tree' ? '📁 Tree' : '🕸️ Graph'}
          </button>
        ))}
      </div>

      {view === 'tree' ? (
        <div className="flex gap-6 flex-1 overflow-hidden">
          {/* Tree */}
          <div className="w-56 shrink-0 overflow-y-auto border-r border-slate-100 pr-2">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-3">
              Pages
            </p>
            <Suspense fallback={<p className="text-xs text-slate-400">Loading tree…</p>}>
              <WikiTree selected={selected} onSelect={setSelected} />
            </Suspense>
          </div>

          {/* Page content */}
          <div className="flex-1 overflow-y-auto">
            {!selected && (
              <p className="text-sm text-slate-400">Select a page to read it</p>
            )}
            {selected && (
              <Suspense fallback={<p className="text-xs text-slate-400">Loading…</p>}>
                <PageView path={selected} />
              </Suspense>
            )}
          </div>
        </div>
      ) : (
        <div className="flex-1 overflow-hidden">
          <Suspense fallback={<p className="text-xs text-slate-400">Loading graph…</p>}>
            <WikiGraph />
          </Suspense>
        </div>
      )}
    </div>
  )
}