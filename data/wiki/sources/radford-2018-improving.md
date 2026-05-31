---
title: "Improving Language Understanding by Generative Pre-Training"
type: source
source_type: paper
created: 2026-05-31
updated: 2026-05-31
raw_path: "articles/gpt_paper.pdf"
authors: ["Alec Radford", "Karthik Narasimhan", "Tim Salimans", "Ilya Sutskever"]
published: "2018"
venue: ""
arxiv_id: ""
url: ""
tags: ["generative-pre-training", "language-modeling", "transformer", "fine-tuning", "nlp"]
related: ["openai", "transformer", "language-modeling", "generative-pre-training", "discriminative-fine-tuning"]
---

# Improving Language Understanding by Generative Pre-Training

**Authors:** Alec Radford, Karthik Narasimhan, Tim Salimans, Ilya Sutskever | **Published:** 2018

## Summary

This paper introduces a semi-supervised approach for natural language understanding tasks by combining generative pre-training on a large corpus of unlabeled text with discriminative fine-tuning on specific tasks. The authors utilize a Transformer decoder architecture and demonstrate significant improvements across various benchmarks, achieving state-of-the-art results on multiple natural language understanding tasks.

## Key Takeaways

- A two-stage training procedure: unsupervised pre-training using a language modeling objective on unlabeled data, followed by supervised fine-tuning on target tasks.
- The use of the Transformer architecture is crucial for capturing long-range dependencies in text.
- Task-specific input transformations are employed to adapt structured inputs into sequences processable by the pre-trained model, minimizing architectural changes.
- The model achieves state-of-the-art results on 9 out of 12 studied natural language understanding benchmarks, outperforming discriminatively trained models.
- Ablation studies highlight the importance of pre-training, the Transformer architecture, and the auxiliary language modeling objective during fine-tuning.

## Core Ideas

The core idea presented is a two-stage training framework for natural language understanding. The first stage involves unsupervised pre-training of a multi-layer Transformer decoder model on a large corpus of unlabeled text (BooksCorpus) using a standard language modeling objective. This allows the model to learn general linguistic knowledge and capture long-range dependencies. The second stage is discriminative fine-tuning, where the pre-trained model's parameters are adapted to specific downstream tasks using labeled data. Task-specific input transformations are used to convert structured inputs into contiguous token sequences, enabling effective transfer with minimal architectural modifications. The authors also found that including an auxiliary language modeling objective during fine-tuning can improve generalization and accelerate convergence.

## Methodology / Approach

The model architecture is based on the Transformer decoder [62]. For unsupervised pre-training, a multi-layer Transformer decoder with masked self-attention is trained on the BooksCorpus dataset using a language modeling objective to maximize the conditional probability of the next token. For supervised fine-tuning, the pre-trained model is adapted to a target task by adding a linear output layer and optimizing a supervised objective. Task-specific input transformations are applied to handle structured inputs, such as concatenating premise and hypothesis for natural language inference, or processing multiple answer candidates for question answering. The model was trained with Adam optimization, a learning rate schedule, and dropout for regularization. Fine-tuning typically required only 3 epochs with a lower learning rate.

## Results

The model achieved state-of-the-art results on 9 out of 12 natural language understanding tasks evaluated. Notable improvements include absolute gains of 8.9% on commonsense reasoning (Stories Cloze Test), 5.7% on question answering (RACE), and 1.5% on textual entailment (MultiNLI). The model also achieved a competitive score of 72.8 on the GLUE benchmark. Ablation studies demonstrated the significant impact of pre-training, the Transformer architecture over LSTMs, and the auxiliary language modeling objective.

## Limitations & Open Questions

- The paper notes that on the RTE dataset, a smaller dataset, their model's performance (56%) was below that of a multi-task biLSTM model (61.7%), suggesting that multi-task training might further benefit their approach, which was not explored.
- While the model shows strong zero-shot capabilities, further analysis into the specific linguistic functionalities learned during pre-training could be beneficial.

## Pages Created / Updated

- Created: [[radford-2018-improving]]
- Created: [[generative-pre-training]]
- Created: [[discriminative-fine-tuning]]
- Updated: [[openai]] — Added reference to this paper.
- Updated: [[transformer]] — Added reference to this paper.
- Updated: [[language-modeling]] — Added reference to this paper.
