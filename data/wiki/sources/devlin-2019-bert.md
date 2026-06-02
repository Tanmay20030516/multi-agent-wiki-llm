---
title: "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding"
type: source
source_type: paper
created: 2026-05-31
updated: 2026-05-31
raw_path: "articles/bert-paper.pdf"
authors: ["Jacob Devlin", "Ming-Wei Chang", "Kenton Lee", "Kristina Toutanova"]
published: "2019"
venue: "NAACL"
arxiv_id: "1810.04805"
tags: [pretraining, nlp, transformer, language-understanding, bidirectional]
related: ["bert", "google", "transformer-encoder", "vaswani-2017-attention", "glue", "squad", "swag"]
---

# BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding

**Authors:** Jacob Devlin, Ming-Wei Chang, Kenton Lee, Kristina Toutanova | **Published:** 2019 | **Venue:** NAACL

## Summary

This paper introduces BERT (Bidirectional Encoder Representations from Transformers), a novel language representation model that pre-trains deep bidirectional representations from unlabeled text by conditioning on both left and right context in all layers. BERT achieves state-of-the-art results on a wide range of NLP tasks, including question answering and language inference, by fine-tuning the pre-trained model with an additional output layer.

## Key Takeaways

- BERT utilizes a "masked language model" (MLM) objective, inspired by the Cloze task, to enable bidirectional pre-training.
- A "next sentence prediction" (NSP) task is also used to pre-train text-pair representations, which is beneficial for tasks like QA and NLI.
- BERT's architecture is based on the Transformer encoder, with two primary sizes: BERTBASE and BERTLARGE.
- The paper demonstrates that bidirectional pre-training is crucial for language representations, outperforming unidirectional models.
- BERT achieves state-of-the-art results on eleven NLP tasks, significantly improving upon previous benchmarks.

## Core Ideas

BERT's core innovation lies in its bidirectional pre-training approach, which contrasts with previous unidirectional models like OpenAI GPT. By employing a Masked Language Model (MLM) objective, BERT can condition on both left and right context in all layers of the Transformer encoder. This allows for a deeper understanding of language context. Additionally, the Next Sentence Prediction (NSP) task helps the model understand relationships between sentences, crucial for tasks like Question Answering and Natural Language Inference. The model is then fine-tuned on specific downstream tasks with minimal architectural changes.

## Methodology / Approach

BERT is pre-trained in two unsupervised tasks:

1.  **Masked LM (MLM):** 15% of input tokens are randomly masked, and the model's objective is to predict the original masked tokens based on their context. This forces the model to learn bidirectional representations.
2.  **Next Sentence Prediction (NSP):** The model is given two sentences, A and B, and must predict whether sentence B is the actual next sentence that follows A in the original corpus, or a random sentence.

The model architecture is a multi-layer bidirectional Transformer encoder. Two sizes are primarily used: BERTBASE (L=12, H=768, A=12) and BERTLARGE (L=24, H=1024, A=16).

For fine-tuning, the pre-trained BERT model is initialized with pre-trained parameters, and all parameters are fine-tuned using labeled data from downstream tasks. Task-specific inputs and outputs are plugged into the BERT architecture.

## Results

BERT achieves state-of-the-art results on eleven NLP tasks, including:
-   GLUE benchmark: BERTBASE achieves 79.6 average accuracy, BERTLARGE achieves 82.1 (a 7.0% absolute improvement over prior SOTA).
-   SQuAD v1.1: BERTLARGE (ensemble + TriviaQA) achieves 93.2 F1.
-   SQuAD v2.0: BERTLARGE (single) achieves 83.1 F1.
-   SWAG: BERTLARGE achieves 86.3 accuracy.

## Limitations & Open Questions

- The paper notes that the [MASK] token used during pre-training does not appear during fine-tuning, creating a pre-training/fine-tuning mismatch, though they mitigate this with a specific masking strategy.
- While BERT is powerful, the computational cost of pre-training is significant.

## Pages Created / Updated

- Created: [[devlin-2019-bert]]
- Created: [[masked-language-model]]
- Created: [[next-sentence-prediction]]
- Created: [[transformer-encoder]]
- Created: [[attention-mechanism]]
- Created: [[bert]]
- Created: [[bert-base]]
- Created: [[bert-large]]
- Updated: [[google]]
