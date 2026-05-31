import { useState, useRef, useEffect } from 'react'
import { useChat } from '../hooks/useChat'
import MessageBubble from './MessageBubble'

export default function ChatWindow({ onOpenSource }) {
  const { messages, loading, connected, sendMessage } = useChat()
  const [input, setInput] = useState('')
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  function handleSubmit(e) {
    e.preventDefault()
    if (!input.trim()) return
    sendMessage(input.trim())
    setInput('')
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  function getPromptFor(index) {
    for (let i = index - 1; i >= 0; i--) {
      if (messages[i].role === 'user') return messages[i].content
    }
    return ''
  }

  return (
    <div className="flex flex-col h-full">
      {/* Connection status bar */}
      <div className="flex items-center gap-2 px-5 py-2 border-b border-[#00f5ff0f]"
        style={{ background: '#0a0a1c' }}>
        <span
          className={`w-1.5 h-1.5 rounded-full transition-all ${connected ? 'bg-cyber-green' : 'bg-cyber-muted'}`}
          style={connected ? { boxShadow: '0 0 6px #00ff88' } : {}}
        />
        <span className="cyber-label" style={{ color: connected ? '#00ff88' : '#6b7a9e' }}>
          {connected ? 'UPLINK ESTABLISHED' : 'CONNECTING…'}
        </span>
      </div>

      {/* Message thread */}
      <div className="flex-1 overflow-y-auto px-5 py-6"
           style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>

        {messages.length === 0 && (
          /* min-h-full + margin:auto centres even inside overflow-y-auto */
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column',
                        alignItems: 'center', justifyContent: 'center', gap: '1rem' }}>
            <div style={{ fontSize: '3.5rem', color: '#00f5ff',
                          textShadow: '0 0 24px #00f5ff, 0 0 48px #00f5ff66' }}>⬡</div>
            <div style={{ textAlign: 'center' }}>
              <p style={{ fontFamily: "'Orbitron', monospace", fontSize: '0.7rem',
                           letterSpacing: '0.3em', color: '#00f5ff',
                           textShadow: '0 0 8px #00f5ff' }}>
                NEURAL INTERFACE READY
              </p>
              <p style={{ fontSize: '0.72rem', color: '#6b7a9e', marginTop: '0.4rem',
                           fontFamily: "'JetBrains Mono', monospace" }}>
                query the wiki knowledge base
              </p>
            </div>
            <div className="cyber-divider" style={{ width: '160px' }} />
            <p style={{ fontSize: '0.6rem', color: '#6b7a9e', letterSpacing: '0.2em',
                         fontFamily: "'JetBrains Mono', monospace" }}>
              ENTER QUERY TO BEGIN
            </p>
          </div>
        )}

        {messages.map((msg, i) => (
          <MessageBubble
            key={msg.id}
            message={msg}
            question={msg.role === 'assistant' ? getPromptFor(i) : ''}
            onOpenSource={onOpenSource}
          />
        ))}

        {/* Typing indicator */}
        {loading && (
          <div className="flex gap-1.5 px-4 py-2">
            {[0, 150, 300].map((delay) => (
              <span
                key={delay}
                className="w-1.5 h-1.5 rounded-full bg-cyber-cyan"
                style={{
                  boxShadow: '0 0 4px #00f5ff',
                  animation: `typing-dot 1.2s ${delay}ms ease-in-out infinite`,
                }}
              />
            ))}
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input area */}
      <form
        onSubmit={handleSubmit}
        className="px-5 py-4 border-t border-[#00f5ff15]"
        style={{ background: '#0a0a1c' }}
      >
        <div className="flex gap-3 items-stretch">
          <div className="flex-1 relative">
            {/* Prompt prefix */}
            <span className="absolute top-1/2 -translate-y-1/2 glow-cyan
                             pointer-events-none select-none font-mono"
                  style={{ left: '10px', fontSize: '0.78rem', lineHeight: 1 }}>›</span>
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="query the wiki..."
              rows={1}
              className="input-cyber"
              style={{ minHeight: '48px', maxHeight: '110px', height: '48px', paddingLeft: '22px' }}
            />
          </div>
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="btn-cyber px-5"
            style={{ height: '48px' }}
          >
            SEND
          </button>
        </div>
        <p className="text-[0.58rem] text-cyber-muted mt-1.5 px-1 tracking-widest font-mono">
          ENTER to send · SHIFT+ENTER for newline
        </p>
      </form>
    </div>
  )
}
