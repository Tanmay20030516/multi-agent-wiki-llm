---
title: "Reinforcement Learning from Human Feedback"
type: concept
created: 2026-06-03
updated: 2026-06-03
source_count: 0
also_known_as: ["RLHF"]
tags: [alignment, reinforcement-learning, fine-tuning]
related: ["openai", "gpt"]
---

# Reinforcement Learning from Human Feedback

_also known as: RLHF_

A technique used to align large language models with human preferences by using a reward model trained on human rankings of model outputs.

## Intuition

It's like training a dog: you don't just give it a textbook on how to sit; you give it a treat when it actually sits. In RLHF, the "treat" is a high reward score from a model that has learned what humans like.

## How It Works

RLHF typically involves three steps:
1. **Supervised Fine-Tuning (SFT):** The model is fine-tuned on a small set of high-quality demonstrations.
2. **Reward Model Training:** Humans rank multiple outputs from the model. A separate reward model is trained to predict these human preferences.
3. **RL Optimization:** The model is further optimized using a reinforcement learning algorithm (like PPO) to maximize the score given by the reward model.

## Why It Matters

RLHF is critical for making LLMs helpful, honest, and harmless. It allows developers to steer the model's behavior in ways that are difficult to capture with a simple next-token prediction objective.

## Limitations

- **Reward Hacking:** The model may find "shortcuts" to get a high reward without actually improving the output quality.
- **Human Bias:** The model inherits the biases of the human labelers.

## History

While RL has been used in AI for decades, RLHF became widely known through its use in models like InstructGPT and ChatGPT by [[openai]].

## Sources

- *No dedicated source page yet.*
