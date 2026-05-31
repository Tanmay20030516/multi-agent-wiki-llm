---
title: "Transformer"
type: concept
created: 2026-05-31
updated: 2026-05-31
source_count: 1
also_known_as: []
introduced_by: "vaswani-2017-attention"
tags: ["architecture", "nlp", "deep-learning", "sequence-models"]
related: ["vaswani-2017-attention", "radford-2018-improving", "attention-mechanism", "self-attention"]
---

# Transformer

{1-2 sentence definition. What is this concept? Be precise.}

The Transformer is a neural network architecture, introduced in "Attention Is All You Need", that relies entirely on self-attention mechanisms to process input data, dispensing with recurrence and convolutions. It has become the dominant architecture for many NLP tasks.

## Intuition

Instead of processing words one by one in order (like RNNs), the Transformer looks at all the words in a sentence simultaneously and figures out how important each word is to every other word. This allows it to better understand context and relationships between words, even if they are far apart.

## How It Works

The Transformer architecture consists of an encoder and a decoder (though variations exist, like decoder-only models). Both components heavily utilize self-attention mechanisms. Self-attention allows the model to weigh the importance of different input tokens when processing a particular token. This is achieved through query, key, and value vectors. Multi-head attention allows the model to focus on different aspects of the input simultaneously. Positional encodings are added to the input embeddings to retain information about the order of tokens, as the self-attention mechanism itself is permutation-invariant.

## Why It Matters

The Transformer architecture revolutionized NLP by enabling parallel processing of input sequences, significantly speeding up training compared to recurrent models. Its ability to effectively capture long-range dependencies through self-attention has led to state-of-the-art performance on a wide array of tasks, including machine translation, text summarization, and language modeling. It forms the backbone of most modern large language models.

## Key Variants / Related Approaches

- **Encoder-Decoder Transformers:** The original architecture used for machine translation (e.g., [[vaswani-2017-attention]]).
- **Encoder-Only Transformers:** Used for tasks requiring understanding of input sequences, like text classification (e.g., BERT).
- **Decoder-Only Transformers:** Used for generative tasks, like language modeling (e.g., GPT, [[radford-2018-improving]]).
- **Attention Mechanism:** The core component enabling the Transformer's effectiveness. [[attention-mechanism]]

## Limitations

- The self-attention mechanism has a quadratic computational complexity with respect to the input sequence length, making it computationally expensive for very long sequences.
- While effective, understanding the exact reasoning process within the attention layers can be challenging.

## History

Introduced by Vaswani et al. in 2017 with the paper "Attention Is All You Need" [[vaswani-2017-attention]], the Transformer quickly became the de facto standard for sequence modeling tasks, particularly in NLP. Its success has led to its adoption in various other domains as well.

## Sources

- [[vaswani-2017-attention]]
- [[radford-2018-improving]]
