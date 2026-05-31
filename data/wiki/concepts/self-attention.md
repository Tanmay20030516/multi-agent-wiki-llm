---
title: "Self-Attention"
type: concept
created: 2026-06-01
updated: 2026-06-01
source_count: 2
also_known_as: ["intra-attention"]
introduced_by: "vaswani-2017-attention"
tags: [architecture, transformer, attention]
related: ["attention-mechanism", "transformer", "vaswani-2017-attention", "positional-embeddings-analysis"]
---

# Self-Attention

_also known as: intra-attention_

A specific type of attention mechanism that relates different positions of a single sequence to compute a representation of that sequence.

## Intuition

Imagine reading a sentence and, for every word, you look at all the other words in that same sentence to figure out which ones are most important for understanding the current word. For example, in "The animal didn't cross the street because it was too tired", self-attention helps the model realize that "it" refers to "animal" and not "street".

## How It Works

Self-attention uses three vectors for every input token: a **Query (Q)**, a **Key (K)**, and a **Value (V)**.
1. The model computes a score by taking the dot product of the Query of the current token with the Keys of all other tokens in the sequence.
2. These scores are scaled (usually by $1/\sqrt{d_k}$) and passed through a softmax function to create attention weights.
3. The final output for the token is a weighted sum of the Values of all tokens in the sequence, using the attention weights.

Mathematically:
$$\text{Attention}(Q, K, V) = \text{softmax}\!\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

## Why It Matters

Self-attention allows the model to capture global dependencies regardless of the distance between tokens. This solves the "vanishing gradient" problem found in RNNs and allows for massive parallelization during training, as the entire sequence can be processed at once.

## Key Variants / Related Approaches

- **Multi-Head Attention** — Running multiple self-attention operations in parallel to capture different types of relationships. [[transformer]]
- **Cross-Attention** — Where Queries come from one sequence (e.g., decoder) and Keys/Values come from another (e.g., encoder).

## Limitations

The computational cost is quadratic $O(n^2)$ with respect to the sequence length $n$, making it expensive for very long sequences.

## History

Introduced as the core component of the Transformer architecture in [[vaswani-2017-attention]].

## Sources

- [[vaswani-2017-attention]]
- [[transformer]]
