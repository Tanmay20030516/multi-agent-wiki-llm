export default function CitationLink({ pageName, onOpen }) {
  return (
    <button
      onClick={() => onOpen(pageName)}
      className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[0.68rem]
                 font-mono transition-all mx-0.5"
      style={{
        color: '#00f5ff',
        border: '1px solid rgba(0,245,255,0.4)',
        background: 'rgba(0,245,255,0.06)',
        textShadow: '0 0 6px #00f5ff88',
        boxShadow: '0 0 4px rgba(0,245,255,0.2)',
      }}
      onMouseEnter={e => {
        e.currentTarget.style.background = 'rgba(0,245,255,0.12)'
        e.currentTarget.style.boxShadow = '0 0 8px rgba(0,245,255,0.5), 0 0 16px rgba(0,245,255,0.2)'
        e.currentTarget.style.textShadow = '0 0 8px #00f5ff'
      }}
      onMouseLeave={e => {
        e.currentTarget.style.background = 'rgba(0,245,255,0.06)'
        e.currentTarget.style.boxShadow = '0 0 4px rgba(0,245,255,0.2)'
        e.currentTarget.style.textShadow = '0 0 6px #00f5ff88'
      }}
    >
      [[{pageName}]]
    </button>
  )
}
