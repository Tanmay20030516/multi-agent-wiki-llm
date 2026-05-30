// API wrappers for the query and promote endpoints

export async function postQuery(question) {
  const res = await fetch('/api/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  })
  if (!res.ok) throw new Error(`Query failed: ${res.status}`)
  return res.json()
}

export async function promoteToWiki({ title, content, source_question }) {
  const res = await fetch('/api/promote', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, content, source_question }),
  })
  if (!res.ok) throw new Error(`Promote failed: ${res.status}`)
  return res.json()
}

export async function fetchWikiPage(path) {
  const res = await fetch(`/api/wiki/page/${path}`)
  if (!res.ok) throw new Error(`Page fetch failed: ${res.status}`)
  return res.json()
}