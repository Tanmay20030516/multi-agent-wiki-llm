import ReactMarkdown from 'react-markdown'
import CitationLink from './CitationLink'
import SaveToWikiButton from './SaveToWikiButton'

function renderWithCitations(content, onOpenSource) {
  const parts = content.split(/(\[\[.+?\]\])/g)
  return parts.map((part, i) => {
    const match = part.match(/^\[\[(.+?)\]\]$/)
    if (match) {
      return <CitationLink key={i} pageName={match[1]} onOpen={onOpenSource} />
    }
    return (
      <ReactMarkdown key={i} components={{ p: ({ children }) => <span>{children}</span> }}>
        {part}
      </ReactMarkdown>
    )
  })
}

export default function MessageBubble({ message, question, onOpenSource }) {
  const isUser = message.role === 'user'

  if (isUser) {
    return (
      <div className="flex justify-end fade-in-up">
        <div className="max-w-[78%] px-4 py-2.5 text-sm font-mono text-cyber-bg
                        rounded rounded-tr-none"
          style={{
            background: 'linear-gradient(135deg, #00f5ff, #00c8d4)',
            boxShadow: '0 0 12px #00f5ff66, 0 2px 12px rgba(0,0,0,0.4)',
          }}>
          {message.content}
        </div>
      </div>
    )
  }

  return (
    <div className="flex justify-start fade-in-up">
      <div className="max-w-[88%] space-y-2">
        {/* Streaming progress */}
        {message.progress && !message.content && (
          <p className="text-[0.65rem] glow-cyan font-mono px-1 italic blink">
            {message.progress}
          </p>
        )}

        {/* Message content */}
        {message.content && (
          <div className={`px-4 py-3 text-sm rounded rounded-tl-none
                          prose prose-sm max-w-none prose-cyber relative
                          ${message.isError ? 'cyber-card-red' : 'cyber-card'}`}>
            {renderWithCitations(message.content, onOpenSource)}

            {/* Save to wiki button — bottom-right of bubble */}
            {!message.isError && (
              <div className="flex justify-end mt-2 pt-1.5 border-t border-[#00f5ff0f]">
                <SaveToWikiButton message={message} question={question} />
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
