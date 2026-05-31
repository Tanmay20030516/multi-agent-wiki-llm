---
title: "BERT-Base"
type: entity
entity_type: model
created: 2026-05-31
updated: 2026-05-31
source_count: 1
model_family: "BERT"
parameters: "110M"
released: "2019"
developer: "google"
tags: [nlp, language-understanding, pretraining, transformer]
related: ["bert", "devlin-2019-bert"]
---

# BERT-Base

BERT-Base is one of the two initial model sizes for BERT (Bidirectional Encoder Representations from Transformers), developed by Google AI Language. It was designed with a similar size to OpenAI's GPT model for comparative purposes.

## Overview

BERT-Base consists of 12 Transformer encoder layers, a hidden size of 768, and 12 attention heads, totaling approximately 110 million parameters. It was pre-trained using the Masked Language Model (MLM) and Next Sentence Prediction (NSP) objectives.

## Key Contributions / Capabilities

-   **Performance Benchmark:** Provided a strong baseline for the effectiveness of BERT's pre-training approach, achieving state-of-the-art results on various NLP benchmarks at the time of its release.
-   **Comparative Analysis:** Enabled direct comparison with other models like OpenAI GPT due to its comparable size and architecture.

## Connections

As a variant of the BERT model, BERT-Base shares its foundational architecture (Transformer encoder) and pre-training tasks (MLM, NSP). It was introduced alongside BERTLARGE in the original BERT paper.

## Sources

- [[devlin-2019-bert]]
