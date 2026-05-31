---
title: "Transformer Encoder"
type: concept
created: 2026-05-31
updated: 2026-05-31
source_count: 1
also_known_as: []
introduced_by: "vaswani-2017-attention"
tags: [architecture, nlp, transformer]
related: ["attention-mechanism", "devlin-2019-bert", "bert", "vaswani-2017-attention"]
---

# Transformer Encoder

The encoder component of the Transformer architecture, primarily used in natural language processing tasks. It is designed to process input sequences and generate context-aware representations for each element in the sequence.

## Intuition

Think of it as a sophisticated reading comprehension system. It reads a sentence (or sequence of tokens) and, for each word, it considers all other words in the sentence to understand its meaning in context.

## How It Works

The Transformer encoder consists of a stack of identical layers. Each layer has two main sub-layers:
1.  **Multi-Head Self-Attention Mechanism:** This allows each position in the input sequence to attend to all positions in the sequence (including itself) to compute a weighted representation. "Multi-Head" means this attention mechanism is performed multiple times in parallel with different learned linear projections, capturing different aspects of relationships.
2.  **Position-wise Feed-Forward Network:** A fully connected feed-forward network applied independently to each position.

Residual connections are used around each of the two sub-layers, followed by layer normalization. The self-attention mechanism is key, enabling the model to weigh the importance of different words when processing a given word, regardless of their distance.

## Why It Matters

The Transformer encoder, particularly its self-attention mechanism, has revolutionized NLP by effectively capturing long-range dependencies in text, which was a significant challenge for previous architectures like RNNs and LSTMs. Its parallelizable nature also allows for more efficient training on large datasets.

## Key Variants / Related Approaches

-   **Transformer Decoder:** The other half of the original Transformer, typically used for sequence generation tasks.
-   **BERT:** Utilizes a stack of Transformer encoder layers for its pre-training and fine-tuning.

## Limitations

The self-attention mechanism has a computational complexity that is quadratic with respect to the input sequence length ($O(n^2)$), making it computationally expensive for very long sequences.

## History

Introduced in the paper "Attention Is All You Need" by Vaswani et al. (2017). BERT (Devlin et al., 2019) popularized its use in pre-trained language models.

## Sources

- [[vaswani-2017-attention]] (Assumed to exist, will be created if not)
- [[devlin-2019-bert]]
- [[bert]]
