---
title: "Masked Language Model"
type: concept
created: 2026-05-31
updated: 2026-05-31
source_count: 1
also_known_as: ["MLM"]
introduced_by: "devlin-2019-bert"
tags: [pretraining, nlp, language-modeling]
related: ["devlin-2019-bert", "transformer-encoder", "next-sentence-prediction"]
---

# Masked Language Model

_also known as: MLM_

A pre-training objective used in models like BERT, where a certain percentage of input tokens are randomly masked, and the model's task is to predict the original identity of these masked tokens based on their surrounding context.

## Intuition

Imagine reading a sentence with a few words blanked out. To fill in the blanks correctly, you need to understand the meaning of the words before and after the blank. MLM works similarly, forcing the model to learn contextual relationships between words.

## How It Works

During pre-training, a fraction of the input tokens (typically 15% in BERT) are replaced with a special `[MASK]` token, a random token, or left unchanged. The model then processes this corrupted sequence and attempts to predict the original tokens at the masked positions. This is achieved by feeding the final hidden states corresponding to the masked tokens into a softmax layer over the vocabulary.

## Why It Matters

MLM enables the training of deep bidirectional language representations. Unlike traditional language models that predict the next word based only on preceding words (left-to-right), MLM allows the model to consider context from both directions simultaneously. This is crucial for understanding nuances in language and performing well on tasks that require a holistic understanding of text.

## Key Variants / Related Approaches

- **Denoising Autoencoders:** Similar in spirit, but typically reconstruct the entire input, not just masked tokens.
- **Traditional Language Modeling:** Unidirectional (left-to-right or right-to-left), predicting the next token based on past tokens.

## Limitations

A potential drawback is the mismatch between pre-training (where `[MASK]` tokens are present) and fine-tuning (where they are absent). Strategies like replacing masked tokens with random words or leaving them unchanged help mitigate this.

## History

Introduced as a core pre-training task in BERT (Devlin et al., 2019).

## Sources

- [[devlin-2019-bert]]
