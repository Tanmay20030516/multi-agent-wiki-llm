---
title: "Supervised Learning"
type: concept
created: 2026-06-01
updated: 2026-06-01
source_count: 1
also_known_as: []
introduced_by: ""
tags: [machine-learning, training, nlp]
related: ["discriminative-fine-tuning", "radford-2018-improving"]
---

# Supervised Learning

A machine learning paradigm where a model is trained on a labeled dataset, meaning each training example is paired with the correct output.

## Intuition

It is like a student learning from a teacher who provides the correct answers to a set of practice problems. The student adjusts their approach based on the difference between their guess and the correct answer.

## How It Works

In supervised learning, the model makes a prediction based on input data, and a loss function measures the error between the prediction and the ground-truth label. An optimization algorithm (like SGD or Adam) then updates the model's weights to minimize this error.

## Why It Matters

Supervised learning is the foundation for most practical AI applications, including image classification, sentiment analysis, and the fine-tuning stage of LLMs.

## Key Variants / Related Approaches

- **Discriminative Fine-tuning** — A specific application of supervised learning to adapt pre-trained models. [[discriminative-fine-tuning]]
- **Unsupervised Learning** — Learning from unlabeled data, often used as a pre-training step.

## Limitations

- Requires large amounts of high-quality labeled data, which can be expensive or impossible to obtain.

## History

Supervised learning has been a core part of ML for decades, but its role in the "pre-train then fine-tune" pipeline has become central to modern NLP.

## Sources

- [[radford-2018-improving]]
