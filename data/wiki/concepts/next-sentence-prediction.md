---
title: "Next Sentence Prediction"
type: concept
created: 2026-05-31
updated: 2026-05-31
source_count: 1
also_known_as: ["NSP"]
introduced_by: "devlin-2019-bert"
tags: [pretraining, nlp, sentence-relationships]
related: ["devlin-2019-bert", "masked-language-model"]
---

# Next Sentence Prediction

_also known as: NSP_

A pre-training task used in models like BERT, where the model learns to predict whether two given sentences are consecutive in the original text or if the second sentence is a random selection from the corpus.

## Intuition

To understand a conversation or a document, you need to grasp how sentences relate to each other. NSP trains the model to recognize logical flow and coherence between adjacent sentences.

## How It Works

For each training example, the model receives two sentences, A and B. With 50% probability, sentence B is the actual sentence that follows sentence A in the original text (labeled "IsNext"). With the other 50% probability, sentence B is a random sentence from the corpus (labeled "NotNext"). The model uses the representation of the special `[CLS]` token to make this binary classification.

## Why It Matters

This task is crucial for downstream tasks that require understanding relationships between sentences, such as Question Answering (QA) and Natural Language Inference (NLI). By learning to distinguish between consecutive and non-consecutive sentences, the model develops a better grasp of discourse coherence.

## Limitations

While beneficial, the effectiveness of NSP has been debated, with some later models finding it less critical than MLM.

## History

Introduced as a pre-training task in BERT (Devlin et al., 2019).

## Sources

- [[devlin-2019-bert]]
