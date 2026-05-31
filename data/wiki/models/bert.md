---
title: "BERT"
type: entity
entity_type: model
created: 2026-05-31
updated: 2026-05-31
source_count: 1
model_family: "BERT"
released: "2019"
developer: "google"
tags: [nlp, language-understanding, pretraining, transformer]
related: ["devlin-2019-bert", "google", "transformer-encoder", "masked-language-model", "next-sentence-prediction"]
---

# BERT

BERT (Bidirectional Encoder Representations from Transformers) is a language representation model developed by Google AI Language. It is designed to pre-train deep bidirectional representations from unlabeled text by jointly conditioning on both left and right context in all layers.

## Overview

BERT revolutionized natural language processing by introducing a pre-training approach that leverages bidirectional context. Unlike previous models that were largely unidirectional, BERT's architecture and pre-training tasks (Masked Language Model and Next Sentence Prediction) allow it to capture a deeper understanding of language nuances. After pre-training on a massive corpus, BERT can be fine-tuned with minimal task-specific architecture modifications to achieve state-of-the-art performance on a wide array of NLP tasks.

## Key Contributions / Capabilities

-   **Bidirectional Pre-training:** Achieved through the Masked Language Model (MLM) objective, allowing context from both directions.
-   **State-of-the-Art Performance:** Set new benchmarks on numerous NLP tasks, including GLUE, SQuAD, and others, upon its release.
-   **Transfer Learning:** Enables effective transfer learning by fine-tuning a single pre-trained model for various downstream tasks.
-   **Unified Architecture:** Minimal changes required between pre-training and fine-tuning, simplifying application.

## Connections

BERT is built upon the Transformer encoder architecture and utilizes the attention mechanism. Its pre-training relies heavily on the Masked Language Model (MLM) and Next Sentence Prediction (NSP) objectives. It was developed by researchers at Google and has since become a foundational model for many subsequent NLP advancements.

## Sources

- [[devlin-2019-bert]]
