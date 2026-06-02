---
title: "Mathematics of positional embeddings"
type: analysis
created: 2026-06-02
updated: 2026-06-02
promoted_from: "can you show me mathematically what positional embeddings mean?"
sources_used: ["vaswani-2017-attention"]
tags: [architecture, transformer, mathematics]
related: ["transformer", "positional-embeddings-analysis", "vaswani-2017-attention"]
---

# Mathematics of positional embeddings

> Promoted from query: *"can you show me mathematically what positional embeddings mean?"* — 2026-06-02

## Summary

Positional embeddings in the [[transformer]] architecture provide a way to encode the order of tokens in a sequence. Because the [[self-attention]] mechanism is permutation-invariant, these embeddings are added to the input embeddings to provide a unique signal for each position $p$ in the sequence.

## Analysis

The mathematical representation of positional embeddings, as introduced in [[vaswani-2017-attention]], uses sine and cosine functions of different frequencies.

### The Formula

Let $d$ be the dimensionality of the input embeddings, and $n$ be the length of the input sequence. For a given position $p$ in the sequence, the positional embedding $PE_p$ is defined as:

$$
\begin{aligned}
PE_{p, 2i} &= \sin\left(\frac{p}{10000^{2i/d}}\right) \\
PE_{p, 2i+1} &= \cos\left(\frac{p}{10000^{2i/d}}\right)
\end{aligned}
$$

where:
- $p$ is the position of the token in the sequence.
- $i$ is the dimensionality index (ranging from $0$ to $d/2$).
- $d$ is the total embedding dimension.

### Integration with Input

The input embedding $E$ (which contains the semantic meaning of the token) is added element-wise to the positional embedding $PE$ to obtain the final embedding $X$ that enters the model:

$$
X = E + PE
$$

This additive process ensures that the resulting vector $X$ contains both the semantic information of the token and its specific position in the sequence.

### Intuition behind the Sinusoids

The use of sine and cosine functions allows the model to potentially learn to attend by relative positions. For any fixed offset $k$, $PE_{p+k}$ can be represented as a linear function of $PE_p$. This property enables the [[attention-mechanism]] to easily learn relationships based on the distance between tokens, regardless of their absolute position in the sequence.

## Key Takeaways

- **Additive Signal:** Positional embeddings are added element-wise to input embeddings, preserving the model's dimensionality.
- **Frequency-Based Encoding:** By using a range of frequencies (via the $10000^{2i/d}$ term), the model creates a unique "signature" for every position.
- **Relative Position:** The trigonometric properties allow the model to capture relative distances between tokens.

## Open Questions

- **Learned Embeddings:** How do these fixed sinusoidal embeddings compare in performance to learned positional embeddings (where $PE$ is a trainable matrix)?
- **Extrapolation:** To what extent do these fixed functions allow the model to generalize to sequence lengths longer than those seen during training?

## Sources

- [[vaswani-2017-attention]]
