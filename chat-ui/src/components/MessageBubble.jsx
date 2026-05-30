// Single message in the chat thread
// Renders markdown, detects [[citations]], shows progress status

import ReactMarkdown from 'react-markdown'
import CitationLink from './CitationLink'
import SaveToWikiButton from './SaveToWikiButton'

function renderWithCitations(content, onOpenSource) {
  // Split on [[page-name]] pattern
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
      <div className="flex justify-end">
        <div className="max-w-[75%] rounded-2xl rounded-tr-sm px-4 py-2.5
                        bg-indigo-600 text-white text-sm">
          {message.content}
        </div>
      </div>
    )
  }

  return (
    <div className="flex justify-start">
      <div className="max-w-[85%] space-y-2">
        {/* Progress indicator while streaming */}
        {message.progress && !message.content && (
          <p className="text-xs text-slate-400 italic px-1">{message.progress}</p>
        )}

        {/* Message content */}
        {message.content && (
          <div className={`rounded-2xl rounded-tl-sm px-4 py-3 text-sm
                          prose prose-sm max-w-none
                          ${message.isError
                            ? 'bg-red-50 text-red-700 border border-red-200'
                            : 'bg-white border border-slate-200 text-slate-800'}`}>
            {renderWithCitations(message.content, onOpenSource)}
          </div>
        )}

        {/* Save to wiki — only on completed messages */}
        {message.content && !message.isError && (
          <div className="px-1">
            <SaveToWikiButton message={message} question={question} />
          </div>
        )}
      </div>
    </div>
  )
}