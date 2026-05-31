---
title: "Attention Is All You Need"
type: source
source_type: paper
created: 2026-06-01
updated: 2026-06-01
raw_path: "data/raw/papers/vaswani-2017.pdf"
authors: ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar", "Jakob Uszkoreit", "Llion Jones", "Aidan N. Gomez", "Łukasz Kaiser", "Illia Polosukhin"]
published: "2017"
venue: "NeurIPS"
arxiv_id: "1706.03762"
url: "https://arxiv.org/abs/1706.03762"
tags: [architecture, transformer, attention, nlp]
related: ["transformer", "attention-mechanism", "self-attention", "positional-embeddings-analysis"]
---

# Attention Is All You Need

**Authors:** Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Łukasz Kaiser, Illia Polosukhin | **Published:** 2017 | **Venue:** NeurIPS

## Summary

This paper introduces the Transformer, a novel neural network architecture that dispenses with recurrence and convolutions, relying solely on attention mechanisms. It achieves state-of-the-art results in machine translation tasks, demonstrating superior quality, parallelizability, and reduced training time compared to previous models.

## Key Takeaways

- The Transformer architecture is based entirely on attention mechanisms, eliminating the need for RNNs or CNNs.
- It utilizes multi-head self-attention and position-wise feed-forward networks.
- Positional encodings are added to input embeddings to account for sequence order.
- The model achieves state-of-the-art on WMT 2014 English-to-German and English-to-French translation tasks.
- Self-attention offers advantages in computational complexity and parallelization over recurrent and convolutional layers.

## Core Ideas

The core innovation is the replacement of recurrent layers with "Self-Attention". In a Transformer, every position in the sequence can attend to every other position directly, allowing for global dependencies to be captured regardless of distance. This is implemented via Multi-Head Attention, which allows the model to jointly attend to information from different representation subspaces at different positions. The architecture consists of an encoder and a decoder, both composed of stacks of identical layers containing multi-head attention and feed-forward networks.

## Methodology / Approach

The authors proposed the Transformer architecture, which uses:
1. **Scaled Dot-Product Attention:** Computes attention weights using the dot product of Query and Key, scaled by $\sqrt{d_k}$ to prevent gradients from vanishing.
2. **Multi-Head Attention:** Parallel attention layers that allow the model to attend to different parts of the sequence.
3. **Positional Encoding:** Sine and cosine functions of different frequencies are added to the input embeddings to provide the model with information about the relative or absolute position of tokens.
4. **Encoder-Decoder Structure:** The encoder maps an input sequence to a sequence of continuous representations, and the decoder generates an output sequence one token at a time.

## Results

The Transformer outperformed previous SOTA models on WMT 2014 translation tasks. For English-to-German, it achieved a BLEU score of 28.4, surpassing the previous best by over 2 BLEU. For English-to-French, it achieved 41.8 BLEU. Training was significantly faster, taking only 3.5 days on 8 P100 GPUs.

## Limitations & Open Questions

- The quadratic complexity $O(n^2)$ of self-attention relative to sequence length remains a challenge for very long documents.
- The paper focuses primarily on translation; the generalizability to other modalities (like images) was an open question at the time.

## Pages Created / Updated

- Created: [[vaswani-2017-attention]]
- Updated: [[transformer]]
- Updated: [[attention-mechanism]]
- Updated: [[self-attention]]
