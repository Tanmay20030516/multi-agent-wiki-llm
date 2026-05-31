---
title: "BERT"
type: entity
entity_type: model
created: 2026-06-01
updated: 2026-06-01
source_count: 1
model_family: "BERT"
developer: "google"
tags: [model, nlp, transformer]
related: ["google", "devlin-2019-bert", "masked-language-model", "next-sentence-prediction"]
---

# BERT

Bidirectional Encoder Representations from Transformers. A pre-trained language model that uses a bidirectional approach to understand context from both left and right.

## Overview

Introduced by Google in 2019, BERT changed NLP by using a Masked Language Model (MLM) objective to train a deep bidirectional representation. Unlike previous models, it doesn't read text sequentially but looks at the entire sequence at once.

## Key Contributions / Capabilities

- **Bidirectional Context:** Captures nuance better than unidirectional models.
- **Versatility:** Can be fine-tuned for a wide variety of tasks (QA, NLI, etc.) with minimal changes.

## Connections

Developed by [[google]] and described in [[devlin-2019-bert]]. It utilizes the [[transformer-encoder]].

## Sources

- [[devlin-2019-bert]]
