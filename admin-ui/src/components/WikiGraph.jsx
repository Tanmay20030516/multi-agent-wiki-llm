import { useEffect, useRef, useState } from 'react'
import ForceGraph2D from 'react-force-graph-2d'
import { fetchWikiGraph } from '../api/admin'

const TYPE_COLORS = {
  source:   '#6366f1', // indigo
  entity:   '#f59e0b', // amber
  concept:  '#10b981', // emerald
  analysis: '#ec4899', // pink
}

export default function WikiGraph() {
  const [graphData, setGraphData] = useState(null)
  const [error, setError] = useState(null)
  const [selected, setSelected] = useState(null)
  const fgRef = useRef()

  useEffect(() => {
    fetchWikiGraph()
      .then(data => setGraphData({ nodes: data.nodes, links: data.edges }))
      .catch(e => setError(e.message))
  }, [])

  if (error) return <p className="text-sm text-red-500">Error: {error}</p>
  if (!graphData) return <p className="text-xs text-slate-400">Loading graph…</p>
  if (graphData.nodes.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-slate-400 space-y-2">
        <span className="text-4xl">🗺️</span>
        <p className="text-sm">No wiki pages yet — ingest some sources first.</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-3 h-full">
      {/* Legend */}
      <div className="flex flex-wrap gap-4 text-xs text-slate-500">
        {Object.entries(TYPE_COLORS).map(([type, color]) => (
          <span key={type} className="flex items-center gap-1.5">
            <span className="inline-block w-3 h-3 rounded-full" style={{ background: color }} />
            {type}
          </span>
        ))}
        <span className="text-slate-400 ml-auto">{graphData.nodes.length} nodes · {graphData.links.length} edges</span>
      </div>

      {/* Selected node info */}
      {selected && (
        <div className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-600 flex items-center gap-2">
          <span className="inline-block w-2 h-2 rounded-full" style={{ background: TYPE_COLORS[selected.type] ?? '#94a3b8' }} />
          <span className="font-medium">{selected.label}</span>
          <span className="text-slate-400">({selected.type})</span>
          <button onClick={() => setSelected(null)} className="ml-auto text-slate-400 hover:text-slate-600">✕</button>
        </div>
      )}

      {/* Graph canvas */}
      <div className="flex-1 rounded-xl border border-slate-200 overflow-hidden bg-white">
        <ForceGraph2D
          ref={fgRef}
          graphData={graphData}
          nodeLabel="label"
          nodeColor={node => TYPE_COLORS[node.type] ?? '#94a3b8'}
          nodeRelSize={5}
          linkColor={() => '#cbd5e1'}
          linkWidth={1}
          onNodeClick={node => setSelected(node)}
          nodeCanvasObject={(node, ctx, globalScale) => {
            const label = node.label
            const fontSize = Math.max(10 / globalScale, 4)
            const r = 5
            ctx.beginPath()
            ctx.arc(node.x, node.y, r, 0, 2 * Math.PI)
            ctx.fillStyle = TYPE_COLORS[node.type] ?? '#94a3b8'
            ctx.fill()
            if (globalScale > 1.5) {
              ctx.font = `${fontSize}px Sans-Serif`
              ctx.fillStyle = '#334155'
              ctx.textAlign = 'center'
              ctx.textBaseline = 'top'
              ctx.fillText(label, node.x, node.y + r + 2)
            }
          }}
          cooldownTicks={100}
          width={undefined}
          height={undefined}
        />
      </div>
    </div>
  )
}
