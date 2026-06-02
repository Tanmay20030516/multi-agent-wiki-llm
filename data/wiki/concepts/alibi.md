---
title: "ALiBi"
type: concept
created: 2026-06-03
updated: 2026-06-03
source_count: 0
also_known_as: ["Attention with Linear Biases"]
tags: [architecture, transformer, positional-embeddings]
related: ["positional-embeddings-analysis", "self-attention"]
---

# ALiBi

_also known as: Attention with Linear Biases_

A positional encoding technique that adds a linear penalty to the attention scores based on the distance between the query and key tokens.

## Intuition

The model is told: "The further away a word is, the less you should trust it by default." This penalty is applied directly to the attention matrix, rather than adding vectors to the embeddings.

## How It Works

In the self-attention calculation, a bias term is subtracted from the dot product of $Q$ and $K$. This bias is proportional to the distance $|i - j|$ between the positions of the query and key. The slope of the penalty varies across different attention heads.

## Why It Matters

ALiBi allows models to extrapolate to much longer sequences than they were trained on, as the linear penalty remains consistent regardless of the absolute position.

## Limitations

It does not provide the same fine-grained absolute position information that sinusoidal or learned embeddings do.

## History

Introduced as a way to improve the length extrapolation of Transformers.

## Sources

- *No dedicated source page yet.*
