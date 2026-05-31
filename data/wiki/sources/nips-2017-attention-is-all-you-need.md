---
slug: nips-2017-attention-is-all-you-need
page_type: source
title: "Attention Is All You Need"
authors: ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar", "Jakob Uszkoreit", "Llion Jones", "Aidan N. Gomez", "Łukasz Kaiser", "Illia Polosukhin"]
date: 2017
references: ["vaswani2017attention"]
---

This paper introduces the Transformer, a novel neural network architecture that dispenses with recurrence and convolutions, relying solely on attention mechanisms. It achieves state-of-the-art results in machine translation tasks, demonstrating superior quality, parallelizability, and reduced training time compared to previous models.

**Key Takeaways:**
*   The Transformer architecture is based entirely on attention mechanisms, eliminating the need for RNNs or CNNs.
*   It utilizes multi-head self-attention and position-wise feed-forward networks.
*   Positional encodings are added to input embeddings to account for sequence order.
*   The model achieves state-of-the-art results on WMT 2014 English-to-German and English-to-French translation tasks with significantly less training time.
*   Self-attention offers advantages in computational complexity and parallelization over recurrent and convolutional layers.