# Wiki Schema
# AI/ML Research Knowledge Base

This document is the authoritative reference for how this wiki is structured,
maintained, and written. Read it in full at the start of every session before
taking any action. Follow every rule here precisely and consistently.

---

## 1. Core Philosophy

This wiki is a **persistent, compounding knowledge base** for AI/ML research.
Its value comes from consistency. Every page follows the same conventions.
Every cross-reference uses the same format. Every ingest updates the same
files in the same order. Drift from these conventions — even slightly — degrades
the wiki over time.

**The maintenance agent writes. The user reads.** Never ask the user to edit
wiki files manually. Your job is to keep the wiki so clean and consistent that
the user never needs to touch it directly.

**Accuracy over completeness.** If you are uncertain about a claim, say so
explicitly on the page with a `> **Uncertain:** ...` blockquote. Never invent
facts to fill a gap.

---

## 2. Directory Layout

```
data/wiki/
    schema.md         ← this file. never modify without user instruction.
    index.md          ← master catalog. update on every ingest.
    log.md            ← append-only activity record. update on every operation.

    sources/          ← one page per ingested raw source
    entities/         ← people, orgs, models, datasets, tools, benchmarks
    concepts/         ← techniques, algorithms, paradigms, ideas
    analyses/         ← promoted query results, comparisons, syntheses
```

Raw sources live in `data/raw/`. You may **read** from there. You **never write**
there under any circumstances.

---

## 3. Page Types

There are exactly four page types. Every wiki page is one of these. When in
doubt about classification, ask the user before creating the page.

### 3.1 `source`

**What it is:** A structured summary of one raw source document. Created during
ingest. One source page per raw file ingested.

**When to create:** Once per ingest, always. This is the record that the source
was processed.

**File location:** `sources/{slug}.md`

**Slug format:** For papers — `{first-author-lastname}-{year}-{short-title}`
e.g. `vaswani-2017-attention`. For articles — `{yyyy-mm-dd}-{short-title}`
e.g. `2024-03-15-rlhf-overview`. For pasted text — `{yyyy-mm-dd}-{topic}`
e.g. `2026-05-24-moe-discussion`.

---

### 3.2 `entity`

**What it is:** A page about a named, real-world thing in the AI/ML world.

**Sub-types** (stored in frontmatter `entity_type` field):

| entity_type   | Examples                                              |
|---------------|-------------------------------------------------------|
| `researcher`  | Yann LeCun, Andrej Karpathy, Ilya Sutskever           |
| `organization`| OpenAI, DeepMind, Anthropic, Hugging Face             |
| `model`       | GPT-4, Gemini 2.5, Llama 3, DALL-E 3                 |
| `dataset`     | ImageNet, Common Crawl, The Pile, MMLU                |
| `tool`        | PyTorch, JAX, Weights & Biases, vLLM                  |
| `benchmark`   | MMLU, HumanEval, HellaSwag, BIG-Bench                 |

**File location:** `entities/{slug}.md`

**Slug format:** Lowercase, hyphenated. For people — `{firstname}-{lastname}`
e.g. `andrej-karpathy`. For models with version numbers — include the version
`gpt-4o`, `llama-3-70b`. For organizations — short, canonical name `deepmind`,
`hugging-face`.

---

### 3.3 `concept`

**What it is:** A technique, algorithm, paradigm, idea, or theoretical construct.
Things that are not specific named entities but intellectual building blocks.

**Examples:** `attention-mechanism`, `reinforcement-learning-from-human-feedback`,
`mixture-of-experts`, `speculative-decoding`, `constitutional-ai`,
`chain-of-thought`, `tokenization`, `byte-pair-encoding`, `lora`.

**File location:** `concepts/{slug}.md`

**Slug format:** Lowercase, hyphenated. Use the most common name, not the
acronym, so the page is self-describing. Exception: if the acronym is more
widely known than the full name (e.g. `rlhf` vs
`reinforcement-learning-from-human-feedback`) use the acronym — but include
the full name in the title and first line of the page.

---

### 3.4 `analysis`

**What it is:** A synthesized page created by promoting a good query result.
Comparisons, deep-dives, literature reviews, synthesis across multiple sources.
These are not summaries of a single source — they pull from multiple sources
and represent the user's accumulated understanding.

**File location:** `analyses/{slug}.md`

**Slug format:** Descriptive of the question answered.
e.g. `rlhf-vs-dpo-comparison`, `transformer-scaling-laws-synthesis`,
`attention-variants-overview`.

---

## 4. Frontmatter

Every wiki page begins with a YAML frontmatter block. Fields marked
**(required)** must always be present. Fields marked **(optional)** should be
included when the information is available.

### 4.1 All Pages — Common Fields

```yaml
---
title: ""           # (required) Human-readable title. Sentence case.
type: ""            # (required) source | entity | concept | analysis
created: ""         # (required) ISO date: YYYY-MM-DD
updated: ""         # (required) ISO date: YYYY-MM-DD. Update on every edit.
tags: []            # (required) list of lowercase keyword tags, min 2
related: []         # (required) list of slugs of directly related wiki pages
---
```

### 4.2 Source Pages — Additional Fields

```yaml
---
# ... common fields above, then:
source_type: ""     # (required) paper | article | note | paste
raw_path: ""        # (required) path relative to data/ e.g. raw/papers/vaswani-2017.pdf
authors: []         # (optional) list of author names — for papers and articles
published: ""       # (optional) ISO date or year: YYYY-MM-DD or YYYY
venue: ""           # (optional) conference, journal, or publication name
                    #   e.g. NeurIPS 2017, Nature, Hugging Face Blog
arxiv_id: ""        # (optional) e.g. 1706.03762
url: ""             # (optional) canonical URL
---
```

### 4.3 Entity Pages — Additional Fields

```yaml
---
# ... common fields above, then:
entity_type: ""     # (required) researcher | organization | model | dataset
                    #            | tool | benchmark
source_count: 0     # (required) number of raw sources that reference this entity.
                    #            increment on every ingest that touches this page.
# For model entities:
model_family: ""    # (optional) e.g. GPT, Gemini, Llama
parameters: ""      # (optional) e.g. 70B, 1.7T (MoE)
released: ""        # (optional) ISO date or year
developer: ""       # (optional) slug of the organization entity
# For researcher entities:
affiliation: ""     # (optional) slug of the organization entity
known_for: []       # (optional) list of slugs (concepts or models) they are known for
---
```

### 4.4 Concept Pages — Additional Fields

```yaml
---
# ... common fields above, then:
source_count: 0     # (required) number of raw sources that reference this concept.
introduced_by: ""   # (optional) slug of source page that introduced this concept
also_known_as: []   # (optional) list of alternative names or acronyms
---
```

### 4.5 Analysis Pages — Additional Fields

```yaml
---
# ... common fields above, then:
sources_used: []    # (required) list of source page slugs that informed this analysis
promoted_from: ""   # (optional) brief description of the query that generated this
---
```

---

## 5. Naming Conventions

### 5.1 File Slugs

- Always lowercase
- Words separated by hyphens, never underscores or spaces
- No special characters except hyphens
- No version suffixes unless they distinguish meaningfully different things
  (`gpt-4` and `gpt-4o` are different enough; `bert-base` and `bert-large`
  may both live on a single `bert.md` page)
- Keep slugs as short as is unambiguous

**Good:** `mixture-of-experts.md`, `yann-lecun.md`, `gpt-4o.md`
**Bad:** `Mixture_Of_Experts.md`, `yannLecun.md`, `GPT4o_Model.md`

### 5.2 Titles (in frontmatter and headings)

- Title case for proper nouns and model names: `GPT-4o`, `Llama 3`
- Sentence case for concepts: `Mixture of experts`, `Attention mechanism`
- Spell out acronyms in the title; put the acronym in parentheses or
  `also_known_as`: `Reinforcement learning from human feedback` not `RLHF`

### 5.3 Tags

Tags are lowercase, single-word or hyphenated where necessary.
Standard tags for this wiki:

`training`, `inference`, `architecture`, `alignment`, `scaling`,
`fine-tuning`, `pretraining`, `evaluation`, `multimodal`, `reasoning`,
`efficiency`, `open-source`, `closed-source`, `transformer`, `diffusion`,
`reinforcement-learning`, `nlp`, `vision`, `speech`, `robotics`, `agents`

You may introduce new tags but prefer reusing existing ones. Never use
tags that duplicate the page type (don't tag a concept page with `concept`).

---

## 6. Cross-Referencing

### 6.1 Wikilink Format

All internal references use wikilink syntax: `[[slug]]` or `[[slug|display text]]`

- `[[attention-mechanism]]` — links to concepts/attention-mechanism.md
- `[[andrej-karpathy|Karpathy]]` — links with custom display text
- `[[gpt-4o]]` — links to entities/gpt-4o.md

The slug in a wikilink is always just the filename without extension and
without the subdirectory. Slugs are unique across the entire wiki.
**Never create two pages with the same slug in different directories.**

### 6.2 When to Cross-Reference

- **Always** link the first mention of any entity or concept on a page
- Do not link repeated mentions on the same page — first mention only
- Do not link back to the current page itself
- Link liberally — it is better to over-link than under-link

### 6.3 Backlinks

You do not need to maintain backlinks manually. They are derived from
the `related` frontmatter field. Whenever you create or edit a page P
that references page Q, add Q's slug to P's `related` list, and add P's
slug to Q's `related` list. Both directions must be updated.

---

## 7. Page Templates

Use these exact structures. Do not add or remove top-level sections without
user instruction.

### 7.1 Source Page Template

```markdown
---
title: "{Full Title of Source}"
type: source
source_type: {paper|article|note|paste}
created: YYYY-MM-DD
updated: YYYY-MM-DD
raw_path: "{relative path from data/}"
authors: ["{Author One}", "{Author Two}"]
published: "YYYY"
venue: "{Venue Name}"
arxiv_id: "{ID if applicable}"
url: "{URL if applicable}"
tags: [tag1, tag2]
related: [slug1, slug2]
---

# {Full Title of Source}

**Authors:** {comma-separated} | **Published:** {year} | **Venue:** {venue}

## Summary

{2-4 sentence high-level summary. What is this about? What is the main
contribution or argument?}

## Key Takeaways

- {Takeaway 1 — a specific, concrete insight from this source}
- {Takeaway 2}
- {Takeaway 3}
{3-7 bullets. Each should be a standalone insight, not a vague descriptor.}

## Core Ideas

{1-3 paragraphs elaborating on the most important technical ideas.
Use cross-references liberally. This section should be detailed enough
that someone who hasn't read the source understands the core mechanism.}

## Methodology / Approach

{How did they do it? What was the experimental setup, training procedure,
or analytical approach? Omit this section for non-empirical sources.}

## Results

{What did they find? Specific numbers where possible.
e.g. "Achieved 89.4% on MMLU, vs. 86.1% for the previous SOTA."}

## Limitations & Open Questions

- {Limitation or gap acknowledged by the authors or apparent to you}
- {Open question this source raises but doesn't answer}

## Pages Created / Updated

{List every wiki page created or updated as part of this ingest.}
- Created: [[slug]]
- Updated: [[slug]] — {brief note on what changed}
```

---

### 7.2 Entity Page Template

```markdown
---
title: "{Entity Name}"
type: entity
entity_type: {researcher|organization|model|dataset|tool|benchmark}
created: YYYY-MM-DD
updated: YYYY-MM-DD
source_count: 0
tags: [tag1, tag2]
related: [slug1, slug2]
# entity-type-specific fields below
---

# {Entity Name}

{1-2 sentence definition. What is this? Why does it matter in AI/ML?}

## Overview

{2-4 paragraphs of background. For researchers: career arc, research focus,
major contributions. For models: architecture family, capabilities, release
context. For organizations: founding, research focus, notable outputs.
For datasets/tools: what it is, who uses it, why it matters.}

## Key Contributions / Capabilities

- {Most important thing associated with this entity}
- {Second most important}
{3-6 bullets.}

## Connections

{Prose paragraph describing how this entity connects to others in the wiki.
Use cross-references.}

## Notes

{Anything notable that doesn't fit above: controversies, open questions,
things to watch. Optional — omit section if empty.}

## Sources

{Bullet list of [[source-slug]] pages that contributed to this page.}
```

---

### 7.3 Concept Page Template

```markdown
---
title: "{Concept Name}"
type: concept
created: YYYY-MM-DD
updated: YYYY-MM-DD
source_count: 0
also_known_as: []
introduced_by: ""
tags: [tag1, tag2]
related: [slug1, slug2]
---

# {Concept Name}

{also known as: {acronym or alias if applicable}}

{1-2 sentence definition. What is this concept? Be precise.}

## Intuition

{Explain this concept to someone who knows ML broadly but hasn't encountered
this specific idea. Use an analogy if helpful. 2-4 sentences.}

## How It Works

{Technical explanation. As detailed as the sources support. Use equations
in LaTeX fencing ($$...$$) where they add clarity.}

## Why It Matters

{What problem does this solve? What does it enable? 2-4 sentences.}

## Key Variants / Related Approaches

- **{Variant name}** — {1-sentence description and [[link]] if page exists}

## Limitations

- {Known limitation or failure mode}

## History

{When and where was this introduced? By whom? Reference [[source-slug]].}

## Sources

{Bullet list of [[source-slug]] pages that contributed to this page.}
```

---

### 7.4 Analysis Page Template

```markdown
---
title: "{Descriptive Title of the Analysis}"
type: analysis
created: YYYY-MM-DD
updated: YYYY-MM-DD
promoted_from: "{the question that generated this}"
sources_used: [slug1, slug2]
tags: [tag1, tag2]
related: [slug1, slug2]
---

# {Descriptive Title}

> Promoted from query: *"{the original question}"* — {date}

## Summary

{3-5 sentence answer to the question. The most important content.}

## Analysis

{The full synthesized response. Multiple subsections are appropriate.
Use tables for comparisons. Use cross-references throughout.}

## Key Takeaways

- {Distilled insight 1}
- {Distilled insight 2}

## Open Questions

- {What this analysis doesn't resolve, or what to investigate next}

## Sources

{Bullet list of [[source-slug]] pages referenced.}
```

---

## 8. index.md Format

`index.md` is the master catalog. The query agent reads this first on every
query. It must always be accurate and complete.

### Format

```markdown
# Wiki Index

_Last updated: YYYY-MM-DD. {N} pages total._

## Sources ({N} pages)

- [[vaswani-2017-attention]] — "Attention Is All You Need". Introduces the
  transformer architecture. Vaswani et al., NeurIPS 2017.
- [[2024-03-15-rlhf-overview]] — Blog post overview of RLHF training pipeline.

## Entities ({N} pages)

### Researchers
- [[andrej-karpathy]] — AI researcher. Former OpenAI, Tesla. Known for
  micrograd, nanoGPT, LLM visualization work.

### Organizations
- [[openai]] — AI safety and research company. Creator of GPT series,
  DALL-E, Codex, Whisper.

### Models
- [[gpt-4o]] — Multimodal model by OpenAI. Flagship as of mid-2024.

### Datasets
- [[the-pile]] — 825GB diverse text dataset. Used for pretraining many
  open-source LLMs.

### Tools
- [[pytorch]] — Open-source ML framework. Dominant in research settings.

### Benchmarks
- [[mmlu]] — 57-subject multiple choice benchmark. Standard LLM eval.

## Concepts ({N} pages)

- [[attention-mechanism]] — Core mechanism of transformer models. Computes
  weighted sum of values based on query-key similarity.
- [[rlhf]] — Reinforcement learning from human feedback. Fine-tuning
  technique that aligns LLMs with human preferences.

## Analyses ({N} pages)

- [[rlhf-vs-dpo-comparison]] — Compares RLHF and DPO alignment approaches
  across stability, compute cost, and empirical performance.
```

### Update Rules

- Add new pages in the correct section immediately after creation
- Keep the one-line summary to a single line — no wrapping
- Keep entity sub-sections sorted alphabetically
- Update the `_Last updated_` line and page count on every edit
- Never delete entries — if a page is deleted, mark it `~~[[slug]]~~ — removed`

---

## 9. log.md Format

`log.md` is append-only. New entries go at the **top**, below the header.
Never edit or delete existing entries.

### Format

```markdown
# Activity Log

## [YYYY-MM-DD HH:MM] {operation} | {title}

**Operation:** ingest | query→promote | lint | schema-update
**Summary:** {1-2 sentence description of what happened}
**Pages created:** [[slug]], [[slug]]
**Pages updated:** [[slug]] (+ref), [[slug]] (revised claims)
**Notes:** {anything notable — contradictions found, decisions made, etc.}

---
```

### Operations

| operation       | when to use                                          |
|-----------------|------------------------------------------------------|
| `ingest`        | After completing an ingest workflow                  |
| `query→promote` | After promoting a query result to an analysis page   |
| `lint`          | After completing a lint pass                         |
| `schema-update` | After any modification to schema.md                  |

---

## 10. Workflows

### 10.1 Ingest Workflow

Follow these steps **in order** every time a new source is ingested.
Do not skip steps. The discussion step (step 3) is mandatory — never
proceed to writing without explicit user confirmation.

**Step 1 — Read the source**
Read the raw source file in full using `read_source()`. If it is a PDF,
extract all readable text. If it is a markdown article, read as-is.
If it is pasted text, treat it as the source directly.

**Step 2 — Read context**
- Read `schema.md` if not already loaded this session
- Read `index.md` to understand what pages already exist
- Read any existing wiki pages clearly related to this source

**Step 3 — Discuss with the user (MANDATORY)**
Before writing anything, present this to the user and wait for confirmation:

```
📥 Ready to ingest: {source title}

**What this is about:**
{2-3 sentence summary of the source}

**Key takeaways I identified:**
1. {takeaway}
2. {takeaway}
3. {takeaway}

**My plan:**
- Create: sources/{slug}.md
- Create: {list of new entity/concept pages}
- Update: {list of existing pages to update, with brief reason}

**Any contradictions with existing wiki content:**
{list contradictions, or "None found"}

Shall I proceed? Any changes to the plan?
```

**Step 4 — Write on confirmation**
Only after user says yes. Execute in this order:
1. Create the source page
2. Create new entity/concept pages
3. Update existing pages (increment `source_count`, add references)
4. Update `index.md`
5. Append to `log.md`

**Step 5 — Report**
After all writes: list every file created and updated, and total page count
before → after.

---

### 10.2 Query Workflow

1. Read `index.md`
2. Identify 3-5 most relevant pages by title and summary
3. Read those pages in full
4. If more context needed, use `search_wiki()` to find additional pages
5. Synthesize answer with inline `[[wikilink]]` citations
6. Offer to promote: *"This could be saved as analyses/{suggested-slug}.md.
   Want me to promote it?"*

---

### 10.3 Promote Workflow

1. Confirm the slug with the user
2. Write `analyses/{slug}.md` using the analysis template
3. Add to `index.md`
4. Update `related` fields on all pages the analysis references
5. Append to `log.md`

---

### 10.4 Lint Workflow

Check for and report, then fix only what the user approves:

1. **Orphan pages** — no inbound `related` links from other pages
2. **Broken wikilinks** — `[[slug]]` where no file with that slug exists
3. **Missing pages** — entities/concepts mentioned in body text but no page exists
4. **Stale pages** — `updated` date much older than related source pages
5. **Contradictions** — conflicting factual claims across pages
6. **index.md drift** — pages on disk missing from index, or index entries
   with no corresponding file
7. **Frontmatter gaps** — required fields missing from any page

**Output format:**
```
## Lint Report — YYYY-MM-DD

### 🔴 Errors (must fix)
- broken-wikilink: concepts/attention-mechanism.md → [[transfomer]] (typo)

### 🟡 Warnings (should fix)
- orphan: analyses/old-comparison.md — no pages link to this

### 🔵 Suggestions (consider fixing)
- missing-page: "constitutional AI" mentioned in 3 pages but no concept page

✅ 42 pages checked. 3 issues found.
```

---

## 11. Handling Contradictions

When a new source contradicts an existing page:

1. Flag it in the ingest discussion step
2. Never silently overwrite the existing claim
3. Present both claims to the user with sources cited
4. Wait for user to decide
5. If both claims stand unresolved, use this format on the page:

```markdown
> **Conflicting claims:** [[source-a]] states X while [[source-b]] states Y.
> Awaiting resolution. — YYYY-MM-DD
```

---

## 12. Writing Style

- **Terse and precise.** Research wiki, not a blog. No padding.
- **Present tense** for concepts and entities. Past tense for historical events.
- **Specific over vague.** "Achieves 92.3% on MMLU" not "performs well".
- **No editorializing** on source or entity pages. Analysis pages only.
- **LaTeX for math.** Inline: `$x^2$`. Block: `$$\text{Attention}(Q,K,V) = \text{softmax}\!\left(\tfrac{QK^T}{\sqrt{d_k}}\right)V$$`
- **Section headers** are `##` and `###` only. `#` is reserved for the page title.
- **Bullets** for 3+ items. Prose for 1-2 items.

---

## 13. What Not To Do

- **Never write to `data/raw/`** — raw sources are immutable
- **Never modify `schema.md`** without explicit user instruction
- **Never skip the discussion step** in the ingest workflow
- **Never create a page without frontmatter**
- **Never use the same slug** in two different directories
- **Never delete log entries**
- **Never invent facts** — mark uncertainty with `> **Uncertain:** ...`
- **Never use more than one `#` heading** per page
- **Never leave `related` or `tags` empty** — minimum 2 values each

---

_Schema version: 0.1_
_Do not modify this file without explicit user instruction._
