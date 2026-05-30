// Renders [[page-name]] style citations as clickable links

export default function CitationLink({ pageName, onOpen }) {
  return (
    <button
      onClick={() => onOpen(pageName)}
      className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-xs
                 bg-indigo-50 text-indigo-700 hover:bg-indigo-100
                 border border-indigo-200 font-mono transition-colors"
    >
      [[{pageName}]]
    </button>
  )
}