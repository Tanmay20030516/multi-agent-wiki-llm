"""
scripts/init_wiki.py

First-run setup for the LLM Wiki.

Creates the full data directory structure, writes stub files for
schema.md, index.md, and log.md, and initialises a git repo in
data/ so the wiki has version history from day one.

Run this once before starting the backend:
    cd backend
    python ../scripts/init_wiki.py

Or from the project root:
    python scripts/init_wiki.py
"""

import sys
import os
import shutil
from pathlib import Path
from datetime import date
 
# Resolve project root and backend path
project_root = Path(__file__).resolve().parent.parent
backend_path = project_root / "backend"
sys.path.insert(0, str(project_root))
 
# Load .env BEFORE importing anything that touches settings.
# The settings module uses lru_cache — if it's imported before env vars
# are set, it caches the wrong values for the entire process.
env_file = backend_path / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ[key.strip()] = value.strip()
    print(f"✓ Loaded .env from {env_file}")
else:
    print(f"✗ No .env found at {env_file}")
    print("  Copy backend/.env.example to backend/.env and fill in your values.")
    print("  At minimum set: DATA_PATH, GEMINI_API_KEY, GROQ_API_KEY")
    sys.exit(1)


# NOW import settings — env vars are already set
from backend.core.config import get_settings
get_settings.cache_clear()  # clear any cached instance from the import chain
from backend.core.config import settings
from backend.core.wiki_manager import wm


def main() -> None:
    print(f"Initialising LLM Wiki at: {settings.data_path}")
    print()

    # Create all directories
    wm.ensure_dirs()
    print("✓ Directories created")
    print(f"  {settings.wiki_path}/")
    for name in ["sources", "entities", "concepts", "analyses"]:
        print(f"    {name}/")
    print(f"  {settings.raw_path}/")
    for name in ["articles", "papers", "notes", "assets"]:
        print(f"    {name}/")

    # Write schema.md stub if it doesn't exist
    if not wm.schema.exists():
        schema_src = project_root / "data" / "wiki" / "schema.md"
        if schema_src.exists():
            import shutil

            shutil.copy(schema_src, wm.schema)
            print("✓ schema.md copied from project data/")
        else:
            wm.schema.write_text(_SCHEMA_STUB, encoding="utf-8")
            print("✓ schema.md stub written")
            print(f"  Edit {wm.schema} to define your wiki conventions")
    else:
        print("  schema.md already exists — skipping")

    # Write empty index.md if it doesn't exist
    if not wm.index.exists():
        wm.index.write_text(_INDEX_STUB, encoding="utf-8")
        print("✓ index.md created")
    else:
        print("  index.md already exists — skipping")

    # Write empty log.md if it doesn't exist
    if not wm.log.exists():
        wm.log.write_text(_LOG_STUB, encoding="utf-8")
        print("✓ log.md created")
    else:
        print("  log.md already exists — skipping")

    # Final check
    print()
    if wm.is_initialised():
        print("✓ Wiki is ready. Start the backend:")
        print("    cd backend && uvicorn main:app --reload")
    else:
        print("✗ Something went wrong — wiki is not fully initialised")
        print(f"  Check that {settings.data_path} is writable")
        sys.exit(1)


# Stub content for first-run files

_SCHEMA_STUB = """\
# Wiki Schema
# AI/ML Research Knowledge Base
#
# This file is your wiki's constitution — the LLM reads it before every
# maintenance operation. Replace this stub with your full schema.
#
# A complete schema.md is included in data/wiki/schema.md in the project repo.
# Copy it here and customise it to your needs.
#
# Minimum required sections:
#   1. Directory layout
#   2. Page types
#   3. Frontmatter format
#   4. Naming conventions
#   5. Workflows (ingest, query, lint)
"""

_INDEX_STUB = f"""\
# Wiki Index

_Last updated: {date.today().isoformat()}. 0 pages total._

## Sources (0 pages)

## Entities (0 pages)

### Researchers

### Organizations

### Models

### Datasets

### Tools

### Benchmarks

## Concepts (0 pages)

## Analyses (0 pages)
"""

_LOG_STUB = f"""\
# Activity Log

## [{date.today().isoformat()} 00:00] schema-update | Wiki initialised

**Operation:** schema-update
**Summary:** Wiki initialised by init_wiki.py.
**Pages created:** —
**Pages updated:** —
**Notes:** Ready for first ingest.

---
"""


if __name__ == "__main__":
    main()
