// Fetch wrappers for all admin endpoints

// Wiki
export async function fetchWikiTree() {
  const res = await fetch('/api/wiki/tree')
  if (!res.ok) throw new Error(`Failed to fetch wiki tree: ${res.status}`)
  return res.json()
}

export async function fetchWikiPage(path) {
  const res = await fetch(`/api/wiki/page/${path}`)
  if (!res.ok) throw new Error(`Failed to fetch page: ${res.status}`)
  return res.json()
}

export async function fetchWikiIndex() {
  const res = await fetch('/api/wiki/index')
  if (!res.ok) throw new Error(`Failed to fetch index: ${res.status}`)
  return res.json()
}

export async function fetchLog() {
  const res = await fetch('/api/wiki/log')
  if (!res.ok) throw new Error(`Failed to fetch log: ${res.status}`)
  return res.json()
}

// Schema
export async function fetchSchema() {
  const res = await fetch('/api/wiki/schema')
  if (!res.ok) throw new Error(`Failed to fetch schema: ${res.status}`)
  return res.json()
}

export async function saveSchema(content) {
  const res = await fetch('/api/wiki/schema', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
  })
  if (!res.ok) throw new Error(`Failed to save schema: ${res.status}`)
  return res.json()
}

// Ingest
export async function uploadSource(file) {
  const formData = new FormData()
  formData.append('file', file)
  const res = await fetch('/api/ingest/upload', {
    method: 'POST',
    body: formData,
  })
  if (!res.ok) throw new Error(`Upload failed: ${res.status}`)
  return res.json()
}

export async function ingestText(text, filename) {
  const res = await fetch('/api/ingest/text', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, filename }),
  })
  if (!res.ok) throw new Error(`Ingest failed: ${res.status}`)
  return res.json()
}

export async function triggerIngest(sourcePath) {
  const res = await fetch('/api/ingest', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ source_path: sourcePath }),
  })
  if (!res.ok) throw new Error(`Ingest trigger failed: ${res.status}`)
  return res.json()
}

// Lint
export async function triggerLint() {
  const res = await fetch('/api/lint', { method: 'POST' })
  if (!res.ok) throw new Error(`Lint failed: ${res.status}`)
  return res.json()
}

export async function approveFix(issueId) {
  const res = await fetch(`/api/lint/approve/${issueId}`, { method: 'POST' })
  if (!res.ok) throw new Error(`Approve failed: ${res.status}`)
  return res.json()
}

export async function rejectFix(issueId) {
  const res = await fetch(`/api/lint/reject/${issueId}`, { method: 'POST' })
  if (!res.ok) throw new Error(`Reject failed: ${res.status}`)
  return res.json()
}

// Sources
export async function fetchSources() {
  const res = await fetch('/api/sources/list')
  if (!res.ok) throw new Error(`Failed to fetch sources: ${res.status}`)
  return res.json()
}