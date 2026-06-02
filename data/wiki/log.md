# Activity Log

## [2026-06-01 18:21] lint | health-check-2026-06-04

**Operation:** lint
**Summary:** Completed full wiki lint and fixed 4 issues.
**Pages created:** —
**Pages updated:** [[entities/gemini.md]], [[entities/palm.md]], [[concepts/transformer.md]], [[concepts/attention-mechanism.md]], [[concepts/transformer-encoder.md]]
**Notes:** Fixed frontmatter gaps in gemini.md and palm.md (related field < 2). Cleaned up remnant ingest notes in attention-mechanism.md and transformer-encoder.md. Updated related links for consistency.

---

## [2026-05-31 19:57] lint | lint-fix-2026-06-03

**Operation:** lint
**Summary:** Completed full lint fix: reorganized index.md and created 13 missing pages to resolve gaps.
**Pages created:** [[glue]], [[squad]], [[swag]], [[multinli]], [[race]], [[rte]], [[bookscorpus]], [[palm]], [[gemini]], [[rlhf]], [[rope]], [[alibi]]
**Pages updated:** [[index.md]], [[sources/devlin-2019-bert.md]], [[sources/radford-2018-improving.md]], [[entities/google.md]], [[entities/openai.md]], [[analyses/positional-embeddings-analysis.md]]
**Notes:** Fixed index.md formatting drift in Entities section. Created 13 missing entity/concept pages based on mentions in existing wiki content (GLUE, SQuAD, SWAG, MultiNLI, RACE, RTE, BooksCorpus, PaLM, Gemini, RLHF, RoPE, ALiBi). Updated related links on 5 pages.

---

## [2026-05-31 19:33] query->promote | positional-embeddings-mathematics

**Operation:** query->promote
**Summary:** Promoted mathematical explanation of positional embeddings to a permanent analysis page.
**Pages created:** [[positional-embeddings-mathematics]]
**Pages updated:** [[transformer]], [[positional-embeddings-analysis]], [[vaswani-2017-attention]], [[index.md]]
**Notes:** Promoted a query result about the mathematics of positional embeddings. Fixed a page count error in index.md for the Analyses section.

---

## [2026-05-31 12:09] query->promote | positional-embeddings-analysis

**Operation:** query->promote
**Summary:** Promoted query result to analyses/positional-embeddings-analysis.md.
**Pages created:** [[positional-embeddings-analysis]]
**Pages updated:** [[transformer]], [[self-attention]], [[attention-mechanism]], [[vaswani-2017-attention]], [[index]]
**Notes:** Promoted a query about positional embeddings to a full analysis page. Updated related links on core Transformer concepts and the original Vaswani paper.

---

## [2026-05-31 10:13] lint | health-check-2026-06-01

**Operation:** lint
**Summary:** Full wiki health check and repair. Fixed index drift, schema violations, and missing pages.
**Pages created:** [[entities/google]], [[entities/openai]], [[entities/bert]], [[entities/bert-base]], [[entities/bert-large]], [[entities/gpt]], [[concepts/supervised-learning]], [[sources/vaswani-2017-attention]]
**Pages updated:** [[index]], [[sources/devlin-2019-bert]], [[concepts/attention-mechanism]], [[concepts/transformer-encoder]], [[concepts/transformer]], [[concepts/self-attention]]
**Notes:** Fixed major index drift, schema violations in sources/vaswani-2017-attention and concepts/self-attention. Created missing entity pages for Google, OpenAI, BERT, and GPT. Resolved broken wikilinks and frontmatter gaps. Moved google.md from sources to entities.

---

## [2026-05-31 09:50] query->promote | what-is-next-sentence-prediction

**Operation:** query->promote
**Summary:** Promoted query answer to wiki. Question: what is next sentence prediction?
**Pages created:** —
**Pages updated:** —

---

## [2026-05-31 08:48] lint | health-check-2026-05-31

**Operation:** lint
**Summary:** Lint fixes applied (0 tool calls). User approved fixes.
**Pages created:** —
**Pages updated:** —

---

## [2026-05-31 08:47] ingest | radford-2018-improving

**Operation:** ingest
**Summary:** Ingested source 'Improving Language Understanding by Generative Pre-Training'. Created new concept pages for generative pre-training, discriminative fine-tuning, language modeling, and the Transformer architecture. Updated existing pages for OpenAI, Transformer, and Language Modeling.
**Pages created:** [[radford-2018-improving]], [[generative-pre-training]], [[discriminative-fine-tuning]], [[language-modeling]], [[transformer]]
**Pages updated:** [[openai]], [[transformer]], [[language-modeling]]

---

## [2026-05-30 19:21] ingest | devlin-2019-bert

**Operation:** ingest
**Summary:** Ingested BERT paper, creating source page and related concept/model pages.
**Pages created:** [[devlin-2019-bert]], [[masked-language-model]], [[next-sentence-prediction]], [[transformer-encoder]], [[attention-mechanism]], [[bert]], [[bert-base]], [[bert-large]]
**Pages updated:** [[google]]

---

## [2026-05-31 00:00] schema-update | Wiki initialised

**Operation:** schema-update
**Summary:** Wiki initialised by init_wiki.py.
**Pages created:** —
**Pages updated:** —
**Notes:** Ready for first ingest.

---
