import { useEffect, useRef, useState, Component } from 'react'
import ForceGraph2D from 'react-force-graph-2d'
import { fetchWikiGraph } from '../api/admin'

const TYPE_COLORS = {
  source: '#00f5ff',
  entity: '#ff00cc',
  concept: '#7c3aff',
  analysis: '#ffaa00',
}
const TYPE_GLOW = {
  source: '0 0 8px #00f5ff, 0 0 16px #00f5ff66',
  entity: '0 0 8px #ff00cc, 0 0 16px #ff00cc66',
  concept: '0 0 8px #7c3aff, 0 0 16px #7c3aff66',
  analysis: '0 0 8px #ffaa00, 0 0 16px #ffaa0066',
}

// Error boundary to catch ForceGraph2D crashes
class GraphErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { error: null }
  }
  static getDerivedStateFromError(error) {
    return { error: error.message || String(error) }
  }
  render() {
    if (this.state.error) {
      return (
        <div className="p-6 text-center">
          <p className="glow-red text-xs font-mono mb-2">✗ GRAPH RENDER ERROR</p>
          <p className="text-cyber-muted text-xs font-mono">{this.state.error}</p>
        </div>
      )
    }
    return this.props.children
  }
}

export default function WikiGraph() {
  const [graphData, setGraphData] = useState(null)
  const [error, setError] = useState(null)
  const [selected, setSelected] = useState(null)
  const fgRef = useRef()

  useEffect(() => {
    fetchWikiGraph()
      .then(data => {
        // Deep-clone nodes/links to avoid mutation issues
        const nodes = data.nodes.map(n => ({ ...n }))
        const edges = (data.edges || []).map(e => ({ ...e }))
        setGraphData({ nodes, links: edges })
      })
      .catch(e => setError(e.message))
  }, [])

  if (error) return (
    <div className="p-4 glow-red text-xs font-mono">✗ GRAPH ERROR :: {error}</div>
  )
  if (!graphData) return (
    <div className="p-4 text-cyber-muted text-xs font-mono blink">// loading graph data</div>
  )
  if (graphData.nodes.length === 0) return (
    <div className="h-full flex flex-col items-center justify-center gap-3 text-cyber-muted">
      <span className="text-5xl glow-cyan" style={{ opacity: 0.2 }}>⬡</span>
      <p className="cyber-label">NO NODES — INGEST SOURCES FIRST</p>
    </div>
  )

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Legend */}
      <div className="flex items-center gap-5 px-4 py-2 border-b border-[#00f5ff15]"
        style={{ background: '#080818', flexShrink: 0 }}>
        {Object.entries(TYPE_COLORS).map(([type, color]) => (
          <span key={type} className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full"
              style={{ background: color, boxShadow: `0 0 4px ${color}` }} />
            <span className="cyber-label" style={{ color }}>{type}</span>
          </span>
        ))}
        <span className="ml-auto cyber-label">
          {graphData.nodes.length} nodes · {graphData.links.length} edges
        </span>
      </div>

      {/* Selected node */}
      {selected && (
        <div className="px-4 py-2 flex items-center gap-2 border-b border-[#00f5ff15]"
          style={{ background: '#0a0a20', flexShrink: 0 }}>
          <span className="w-2 h-2 rounded-full"
            style={{
              background: TYPE_COLORS[selected.type] ?? '#00f5ff',
              boxShadow: TYPE_GLOW[selected.type] ?? 'none',
            }} />
          <span className="text-xs font-mono glow-cyan">{selected.label}</span>
          <span className="cyber-label ml-1">({selected.type})</span>
          <button onClick={() => setSelected(null)}
            className="ml-auto text-cyber-muted hover:text-cyber-text text-sm transition-colors">
            ✕
          </button>
        </div>
      )}

      {/* Graph canvas */}
      <div style={{ flex: 1, minHeight: '400px', overflow: 'hidden' }}>
        <GraphErrorBoundary>
          <ForceGraph2D
            ref={fgRef}
            graphData={graphData}
            backgroundColor="#080818"
            nodeLabel="label"
            nodeColor={n => TYPE_COLORS[n.type] ?? '#6b7a9e'}
            nodeRelSize={5}
            linkColor={() => 'rgba(0,245,255,0.15)'}
            linkWidth={1.2}
            onNodeClick={n => setSelected(n)}
            nodeCanvasObjectMode={() => 'replace'}
            nodeCanvasObject={(node, ctx, globalScale) => {
              if (node.x == null || node.y == null) return
              const color = TYPE_COLORS[node.type] ?? '#6b7a9e'
              const r = 5

              // Outer glow halo
              const grad = ctx.createRadialGradient(node.x, node.y, 0, node.x, node.y, r * 2.5)
              grad.addColorStop(0, color + '66')
              grad.addColorStop(0.5, color + '22')
              grad.addColorStop(1, color + '00')
              ctx.beginPath()
              ctx.arc(node.x, node.y, r * 2, 0, 2 * Math.PI)
              ctx.fillStyle = grad
              ctx.fill()

              // Solid core
              ctx.beginPath()
              ctx.arc(node.x, node.y, r, 0, 2 * Math.PI)
              ctx.fillStyle = color
              ctx.shadowColor = color
              ctx.shadowBlur = 5
              ctx.fill()
              ctx.shadowBlur = 0

              // Label
              const fs = Math.max(10 / globalScale, 4)
              ctx.font = `${fs}px 'JetBrains Mono', monospace`
              ctx.fillStyle = color + 'dd'
              ctx.textAlign = 'center'
              ctx.textBaseline = 'top'
              ctx.fillText(node.label, node.x, node.y + r + 2)
            }}
            cooldownTicks={150}
            onEngineStop={() => fgRef.current?.zoomToFit?.(400, 40)}
          />
        </GraphErrorBoundary>
      </div>
    </div>
  )
}
