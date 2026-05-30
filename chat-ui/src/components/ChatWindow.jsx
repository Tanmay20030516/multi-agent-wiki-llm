// Main chat thread + input box

import { useState, useRef, useEffect } from 'react'
import { useChat } from '../hooks/useChat'
import MessageBubble from './MessageBubble'

export default function ChatWindow({ onOpenSource }) {
  const { messages, loading, connected, sendMessage } = useChat()
  const [input, setInput] = useState('')
  const bottomRef = useRef(null)

  // Auto-scroll to latest message
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

  // Find the user message that prompted each assistant reply
  function getPromptFor(index) {
    for (let i = index - 1; i >= 0; i--) {
      if (messages[i].role === 'user') return messages[i].content
    }
    return ''
  }

  return (
    <div className="flex flex-col h-full">
      {/* Connection status */}
      <div className="flex items-center gap-2 px-5 py-2 border-b border-slate-100">
        <span className={`w-2 h-2 rounded-full ${connected ? 'bg-green-400' : 'bg-slate-300'}`} />
        <span className="text-xs text-slate-400">
          {connected ? 'Connected' : 'Connecting…'}
        </span>
      </div>

      {/* Message thread */}
      <div className="flex-1 overflow-y-auto px-5 py-6 space-y-4">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full
                          text-slate-400 space-y-2">
            <span className="text-4xl">📖</span>
            <p className="text-sm">Ask anything about your wiki</p>
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

        {/* Streaming indicator */}
        {loading && (
          <div className="flex gap-1 px-4">
            <span className="w-1.5 h-1.5 bg-slate-300 rounded-full animate-bounce [animation-delay:0ms]" />
            <span className="w-1.5 h-1.5 bg-slate-300 rounded-full animate-bounce [animation-delay:150ms]" />
            <span className="w-1.5 h-1.5 bg-slate-300 rounded-full animate-bounce [animation-delay:300ms]" />
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <form
        onSubmit={handleSubmit}
        className="px-5 py-4 border-t border-slate-100 bg-white"
      >
        <div className="flex gap-3 items-end">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask your wiki a question…"
            rows={1}
            className="flex-1 resize-none rounded-xl border border-slate-200
                       px-4 py-2.5 text-sm text-slate-800 placeholder:text-slate-400
                       focus:outline-none focus:ring-2 focus:ring-indigo-300
                       focus:border-transparent transition-all"
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white
                       px-4 py-2.5 text-sm font-medium transition-colors
                       disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </div>
        <p className="text-xs text-slate-400 mt-1.5 px-1">
          Enter to send · Shift+Enter for newline
        </p>
      </form>
    </div>
  )
}