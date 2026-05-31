import { useState, use, Suspense, lazy } from 'react'
import ReactMarkdown from 'react-markdown'
import { fetchWikiTree, fetchWikiPage } from '../api/admin'

const WikiGraph = lazy(() => import('./WikiGraph'))

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

const TYPE_COLOR = {
  sources:  '#00f5ff',
  entities: '#ff00cc',
  concepts: '#7c3aff',
  analyses: '#ffaa00',
}

function TreeNode({ node, depth, selected, onSelect }) {
  const isDir = node.type === 'directory'
  const indent = depth * 14
  const color = TYPE_COLOR[node.name] ?? '#00f5ff'

  return (
    <div>
      <button
        onClick={() => !isDir && onSelect(node.path)}
        className={`w-full text-left py-1 pr-3 text-[0.72rem] rounded transition-all
          flex items-center gap-1.5
          ${isDir
            ? 'text-cyber-muted cursor-default font-bold tracking-widest uppercase'
            : selected === node.path
              ? 'text-cyber-cyan'
              : 'text-cyber-muted hover:text-cyber-text'}`}
        style={
          isDir
            ? { paddingLeft: `${indent + 8}px`, color, textShadow: `0 0 8px ${color}66`, paddingTop: '0.5rem' }
            : selected === node.path
              ? { paddingLeft: `${indent + 8}px`, color: '#00f5ff', textShadow: '0 0 6px #00f5ff', background: 'rgba(0,245,255,0.05)' }
              : { paddingLeft: `${indent + 8}px` }
        }
      >
        <span className="shrink-0" style={{ fontSize: '0.6rem', opacity: 0.7 }}>
          {isDir ? '◈' : '›'}
        </span>
        {node.name.replace('.md', '')}
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
    <div className="space-y-0">
      {tree.map((node) => (
        <TreeNode key={node.path} node={node} depth={0} selected={selected} onSelect={onSelect} />
      ))}
    </div>
  )
}

function PageView({ path }) {
  const data = use(getPagePromise(path))
  return (
    <div className="prose prose-sm max-w-none prose-cyber">
      <ReactMarkdown>{data.content ?? ''}</ReactMarkdown>
    </div>
  )
}

export default function WikiBrowser() {
  const [selected, setSelected] = useState(null)
  const [view, setView] = useState('tree')

  return (
    <div className="flex flex-col gap-4">
      {/* View toggle */}
      <div className="flex gap-2">
        {[
          { id: 'tree',  label: '◈ TREE' },
          { id: 'graph', label: '⬡ GRAPH' },
        ].map(({ id, label }) => (
          <button
            key={id}
            onClick={() => setView(id)}
            className={view === id ? 'btn-cyber' : 'btn-cyber-ghost'}
          >
            {label}
          </button>
        ))}
      </div>

      {view === 'tree' ? (
        <div className="flex gap-4 flex-1 overflow-hidden">
          {/* File tree */}
          <div className="w-52 shrink-0 overflow-y-auto cyber-card p-3"
            style={{ background: '#080818' }}>
            <p className="cyber-label mb-3">// PAGES</p>
            <Suspense fallback={<p className="text-cyber-muted text-xs">loading…</p>}>
              <WikiTree selected={selected} onSelect={setSelected} />
            </Suspense>
          </div>

          {/* Page content */}
          <div className="flex-1 overflow-y-auto cyber-card p-5">
            {!selected ? (
              <div className="h-full flex flex-col items-center justify-center gap-3 text-cyber-muted">
                <span className="text-4xl glow-cyan" style={{ opacity: 0.3 }}>◈</span>
                <p className="cyber-label">SELECT A PAGE TO VIEW</p>
              </div>
            ) : (
              <Suspense fallback={<p className="text-cyber-muted text-xs">// loading…</p>}>
                <PageView path={selected} />
              </Suspense>
            )}
          </div>
        </div>
      ) : (
        <div className="cyber-card" style={{
          height: 'calc(100vh - 240px)',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
        }}>
          <Suspense fallback={<p className="text-cyber-muted text-xs p-4">// loading graph…</p>}>
            <WikiGraph />
          </Suspense>
        </div>
      )}
    </div>
  )
}
