# Multi Agent wikiLLM

A multi-agent LLM-powered knowledge base system implementing Andrej Karpathy's wiki concept. Build, maintain, and query a structured wiki powered by autonomous agents and large language models.

**Reference:** [Karpathy&#39;s wiki concept gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)

---

## Features

### 🤖 Multi-Agent Architecture

- **Maintenance Agent** — ingest sources, extract entities/concepts, lint for inconsistencies, auto-fix issues
- **Query Agent** — retrieve relevant wiki pages, synthesize answers with citations, promote valuable responses back to the wiki

### 📚 Knowledge Management

- Auto-extract text from PDFs, parse markdown files, build semantic relationships
- Graph visualization of entities, concepts, and their connections
- Wiki wikilink parsing (`[[page_name]]`) for automatic cross-references
- Lint system detects redundancy, missing definitions, broken links

### 🎨 Modern UI

- **Admin Console** — cyberpunk neon theme, manage ingest/lint/schema with real-time progress
- **Query Interface** — chat-style interface with source citations and wiki promotion
- Interactive force-directed graph visualization of knowledge base
- Responsive design with terminal-style components

### 🔧 LLM Provider Support

- Groq (fast inference, serverless)
- Google Gemini (advanced reasoning)
- Pluggable architecture for additional providers

---

## Tech Stack

**Backend:**

- Python 3.10+
- FastAPI (REST API + WebSocket)
- Groq SDK, Google Gemini SDK
- pydantic (config & validation)
- pypdf (PDF text extraction)

**Frontend:**

- React 19 with Vite
- Tailwind CSS v4 (with `@theme` tokens)
- react-force-graph-2d (graph visualization)
- react-markdown (wiki rendering)
- WebSocket for real-time agent progress

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- `GROQ_API_KEY` and `GOOGLE_API_KEY` environment variables

### Installation

```bash
# Clone the repo
git clone https://github.com/Tanmay20030516/multi-agent-wiki-llm.git
cd multi-agent-wiki-llm

# Set up Python environment
python3 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
pip install -r backend/requirements-backend.txt

# Set up environment variables
cp backend/env.example backend/.env
# Edit backend/.env with your API keys

# Initialize wiki directory structure
python scripts/init_wiki.py

# Install frontend dependencies
cd admin-ui && npm install
cd ../chat-ui && npm install
cd ..
```

### Running the Project

**Terminal 1 — Backend:**

```bash
source .venv/bin/activate
uvicorn backend.main:app --reload --reload-dir backend --host 0.0.0.0 --port 8000
```

**Terminal 2 — Admin UI (port 3001):**

```bash
cd admin-ui
npm run dev
```

**Terminal 3 — Chat UI (port 3002):**

```bash
cd chat-ui
npm run dev
```

Then open:

- Admin: http://localhost:3001
- Chat: http://localhost:3002

---

## Workflow

### 1. Ingest Sources

1. Admin console → **INGEST** tab
2. Upload PDFs or paste text
3. Agent extracts text, identifies entities/concepts, creates initial wiki pages
4. Review suggested pages → Approve to write to wiki

### 2. Lint & Fix

1. Admin console → **LINT** tab
2. Agent analyzes wiki for issues: redundancy, undefined terms, broken links
3. Review report → Choose fix level (all, errors only) → Agent applies fixes

### 3. Query & Learn

1. Chat interface → Ask a question about the knowledge base
2. Query agent retrieves relevant wiki pages, synthesizes answer with citations
3. Save valuable responses back to wiki (promote)

### 4. Maintain Schema

1. Admin console → **SCHEMA** tab
2. Define custom entity/concept types
3. Lint agent enforces schema consistency

---

## Project Structure

```
multi-agent-wiki-llm/
├── backend/
│   ├── main.py                 # FastAPI app, WebSocket handlers
│   ├── core/
│   │   ├── config.py           # Settings, env loading
│   │   ├── logger.py           # Structured logging
│   │   └── wiki_manager.py     # Wiki I/O (read/write pages)
│   ├── llm/
│   │   ├── groq_client.py      # Groq provider
│   │   ├── gemini_client.py    # Google Gemini provider
│   │   └── base.py             # LLM base interface
│   ├── tools/
│   │   ├── registry.py         # Tool dispatcher
│   │   └── *.py                # read_index, read_page, write_page, search, etc.
│   ├── agents/
│   │   ├── maintenance.py      # Ingest, lint, promote
│   │   └── query.py            # Chat query synthesis
│   └── api/
│       └── routes/
│           ├── ingest.py       # POST /ingest, /ingest/confirm
│           ├── lint.py         # POST /lint, /lint/confirm
│           ├── sources.py      # POST /promote
│           └── wiki.py         # GET /wiki/tree, /wiki/graph
│
├── admin-ui/                   # React + Vite (Tailwind v4)
│   ├── src/
│   │   ├── App.jsx             # Tab navigation
│   │   ├── index.css           # Cyberpunk design system
│   │   ├── api/
│   │   │   └── admin.js        # HTTP client
│   │   ├── hooks/
│   │   │   ├── useIngest.js    # Ingest flow
│   │   │   └── useLint.js      # Lint flow
│   │   └── components/
│   │       ├── IngestPanel.jsx
│   │       ├── LintPanel.jsx
│   │       ├── WikiBrowser.jsx
│   │       ├── WikiGraph.jsx   # Force-directed graph
│   │       ├── LogViewer.jsx
│   │       └── SchemaEditor.jsx
│   └── vite.config.js
│
├── chat-ui/                    # React + Vite (Tailwind v4)
│   ├── src/
│   │   ├── App.jsx
│   │   ├── index.css           # Cyberpunk design system
│   │   ├── api/
│   │   │   └── query.js
│   │   ├── hooks/
│   │   │   └── useChat.js      # Chat flow
│   │   └── components/
│   │       ├── ChatWindow.jsx
│   │       ├── MessageBubble.jsx
│   │       ├── SourcePanel.jsx
│   │       └── SaveToWikiButton.jsx
│   └── vite.config.js
│
├── data/                       # Wiki storage (auto-created)
│   ├── raw/                    # Ingested files
│   └── wiki/
│       ├── sources/            # Auto-generated from PDFs
│       ├── entities/           # GPT-extracted entities
│       ├── concepts/           # GPT-extracted concepts
│       └── analyses/           # Chat responses promoted to wiki
│
├── scripts/
│   └── init_wiki.py            # Initialize wiki directory + .git
│
└── backend/
    ├── .env                    # API keys, models, config
    └── requirements-backend.txt
```

---

## Key Features

### Real-Time Agent Progress

Both ingest and lint flows stream agent activity via WebSocket:

- Tool calls (e.g., "reading page index…")
- LLM responses (intermediate reasoning)
- Plan presentation (awaiting user confirmation)
- Execution status (writing changes)

### Wiki Graph Visualization

- Force-directed layout with physics simulation
- Nodes color-coded by type: cyan (source), magenta (entity), violet (concept), amber (analysis)
- Neon glow halos, interactive node selection
- Click nodes to highlight relationships

### Chat with Citations

- Query agent searches wiki, retrieves relevant pages
- Response includes source citations with wikilink format
- One-click promotion: save valuable answers back to wiki

---

## API Endpoints

### Maintenance Flow

- `POST /api/ingest` — Start ingest from uploaded file
- `POST /api/ingest/text` — Ingest pasted text
- `POST /api/ingest/confirm` — Confirm/reject ingest plan
- `GET /api/ingest/status/{session_id}` — Poll ingest progress
- `POST /api/lint` — Analyze wiki for issues
- `POST /api/lint/confirm` — Apply lint fixes

### Query Flow

- `POST /api/query` — Ask a question (HTTP poll or WebSocket)
- `WS /ws/query` — WebSocket stream for real-time responses

### Wiki Management

- `GET /api/wiki/tree` — Fetch wiki directory structure
- `GET /api/wiki/graph` — Fetch graph (nodes + edges from wikilinks)
- `GET /api/wiki/page/{path}` — Read a wiki page
- `POST /api/promote` — Save chat response to wiki

### Admin

- `GET /api/schema` — Current wiki schema
- `POST /api/schema` — Update schema

---

## Configuration

All settings in `backend/.env`:

```env
# LLM Providers
GROQ_API_KEY=your_groq_api_key
GOOGLE_API_KEY=your_google_api_key

# Model selection
MAINTENANCE_MODEL=gemini-2.5-flash        # For ingest/lint/promote
QUERY_MODEL=meta-llama/llama-4-scout-17b-16e-instruct  # For queries
QUERY_MODEL_FALLBACK=llama-3.1-8b-instant

# Data paths (relative to project root)
DATA_PATH=data
WIKI_PATH=data/wiki

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
```

---



## Known Limitations

- Wiki pages stored as flat markdown files (not a database)
- No authentication/multi-user support yet
- Graph rendering requires good internet for WebSocket stability
- Groq rate limits: ~1 request/second
- Large PDFs (>100 pages) may timeout on extraction

---

## Future Ideas

- [ ] User authentication & multi-user wiki ownership
- [ ] Collaborative editing with conflict resolution
- [ ] Advanced search: full-text + semantic similarity
- [ ] Custom entity type extraction via schema
- [ ] Prompt engineering UI for model tuning
- [ ] Export wiki as static HTML/PDF
- [ ] Mobile app for query interface

---

## License

MIT (Educational purposes)
