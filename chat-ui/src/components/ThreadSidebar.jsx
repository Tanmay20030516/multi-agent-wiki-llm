export default function ThreadSidebar({ threads, activeId, onNew, onSwitch, onDelete }) {
  return (
    <aside className="w-52 shrink-0 flex flex-col border-r border-[#00f5ff0f]"
      style={{ background: '#080818' }}>

      {/* Header + New button */}
      <div className="flex items-center justify-between px-3 py-3
                      border-b border-[#00f5ff0f]">
        <span className="cyber-label text-[0.6rem]">// THREADS</span>
        <button
          onClick={onNew}
          title="New thread"
          className="text-cyber-muted hover:text-cyber-cyan transition-colors text-sm font-mono"
          style={{ lineHeight: 1 }}
        >
          ＋
        </button>
      </div>

      {/* Thread list */}
      <div className="flex-1 overflow-y-auto py-1">
        {threads.length === 0 && (
          <p className="text-cyber-muted text-[0.65rem] font-mono px-3 py-4 opacity-50">
            no threads yet
          </p>
        )}
        {threads.map((thread) => {
          const active = thread.id === activeId
          return (
            <div
              key={thread.id}
              className="group flex items-center gap-1 px-2 py-1.5 cursor-pointer
                         transition-all"
              style={active
                ? { background: 'rgba(0,245,255,0.06)', borderLeft: '2px solid #00f5ff' }
                : { borderLeft: '2px solid transparent' }
              }
              onClick={() => onSwitch(thread.id)}
            >
              {/* Thread icon */}
              <span className="shrink-0 text-[0.55rem]"
                style={{ color: active ? '#00f5ff' : '#6b7a9e' }}>
                ›
              </span>

              {/* Title */}
              <span
                className="flex-1 text-[0.68rem] font-mono truncate"
                style={{ color: active ? '#00f5ff' : '#6b7a9e',
                         textShadow: active ? '0 0 6px #00f5ff66' : 'none' }}
              >
                {thread.title}
              </span>

              {/* Delete button — shows on hover */}
              <button
                onClick={(e) => { e.stopPropagation(); onDelete(thread.id) }}
                className="opacity-0 group-hover:opacity-100 shrink-0
                           text-cyber-muted hover:text-cyber-red transition-all text-[0.65rem]"
                title="Delete thread"
              >
                ✕
              </button>
            </div>
          )
        })}
      </div>

      {/* Footer */}
      <div className="px-3 py-2 border-t border-[#00f5ff0f]">
        <p className="text-[0.55rem] font-mono text-cyber-muted opacity-40">
          {threads.length} thread{threads.length !== 1 ? 's' : ''}
        </p>
      </div>
    </aside>
  )
}
