---
title: "Rotary Positional Embeddings"
type: concept
created: 2026-06-03
updated: 2026-06-03
source_count: 0
also_known_as: ["RoPE"]
tags: [architecture, transformer, positional-embeddings]
related: ["positional-embeddings-analysis", "self-attention"]
---

# Rotary Positional Embeddings

_also known as: RoPE_

A method of encoding positional information by rotating the query and key representations in a complex plane.

## Intuition

Instead of adding a fixed vector to the embedding, RoPE "twists" the vectors. The amount of rotation depends on the position of the token, and the dot product between two rotated vectors naturally depends on the relative distance between them.

## How It Works

RoPE applies a rotation matrix to the Query (Q) and Key (K) vectors. The rotation angle is a function of the token's position $p$. Because the dot product of two vectors is invariant to a shared rotation, but the relative rotation between two different positions is preserved, the attention mechanism can naturally capture relative distance.

## Why It Matters

RoPE allows for better extrapolation to sequence lengths longer than those seen during training compared to absolute positional embeddings. It is used in many modern LLMs (e.g., Llama).

## Limitations

Implementation is slightly more complex than simple additive embeddings.

## History

Introduced as an alternative to the sinusoidal embeddings in [[vaswani-2017-attention]].

## Sources

- *No dedicated source page yet.*
