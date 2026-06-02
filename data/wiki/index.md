# Wiki Index

_Last updated: 2026-06-03. 33 pages total._

## Sources (3 pages)

- [[devlin-2019-bert]] — BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. Introduces BERT, MLM, and NSP.
- [[radford-2018-improving]] — Improving Language Understanding by Generative Pre-Training. Introduces a framework for NLP tasks using generative pre-training and discriminative fine-tuning with Transformers.
- [[vaswani-2017-attention]] — "Attention Is All You Need". Introduces the Transformer architecture and self-attention. Vaswani et al., NeurIPS 2017.
## Entities (15 pages)

### Researchers
(none)

### Organizations
- [[google]] — [organization] AI research leader. Developer of Transformer and BERT.
- [[openai]] — [organization] AI research company. Developer of GPT series.

### Models
- [[bert]] — [model] Bidirectional Encoder Representations from Transformers. Pre-trained by Google.
- [[bert-base]] — [model] BERT-Base: 110M parameter variant of BERT.
- [[bert-large]] — [model] BERT-Large: 340M parameter variant of BERT.
- [[gemini]] — [model] Multimodal model family by Google.
- [[gpt]] — [model] Generative Pre-trained Transformer. Pre-trained by OpenAI.
- [[palm]] — [model] Pathways Language Model by Google.

### Datasets
- [[bookscorpus]] — [dataset] Large corpus of unpublished books used for GPT pre-training.

### Tools
(none)

### Benchmarks
- [[glue]] — [benchmark] General Language Understanding Evaluation.
- [[multinli]] — [benchmark] Multi-Genre Natural Language Inference.
- [[race]] — [benchmark] Reading Comprehension Dataset from Examinations.
- [[rte]] — [benchmark] Recognizing Textual Entailment.
- [[squad]] — [benchmark] Stanford Question Answering Dataset.
- [[swag]] — [benchmark] Sycophancy-free Word-Association Game.
## Concepts (13 pages)

- [[alibi]] — Attention with Linear Biases. Positional encoding for length extrapolation.
- [[attention-mechanism]] — Mechanism allowing models to focus on relevant parts of input data.
- [[discriminative-fine-tuning]] — Adapting a pre-trained model to a specific supervised task using a discriminative objective.
- [[generative-pre-training]] — Model is first trained on unlabeled data using a generative task, then fine-tuned.
- [[language-modeling]] — Predicting the probability of a sequence of words or the next word.
- [[masked-language-model]] — MLM: Pre-training objective where model predicts masked tokens.
- [[next-sentence-prediction]] — NSP: Pre-training task where model predicts if two sentences are consecutive.
- [[rlhf]] — Reinforcement learning from human feedback. Alignment technique for LLMs.
- [[rope]] — Rotary Positional Embeddings. Relative positional encoding via rotation.
- [[self-attention]] — Mechanism relating different positions of a single sequence to compute a representation.
- [[supervised-learning]] — Learning from a labeled dataset where each example is paired with the correct output.
- [[transformer-encoder]] — Encoder component of the Transformer architecture.
- [[transformer]] — Transformer: Neural network architecture relying on self-attention mechanisms.
## Analyses (2 pages)

- [[positional-embeddings-analysis]] — Analyzes why positional embeddings are necessary for Transformers to handle sequence order due to the permutation-invariance of self-attention.
- [[positional-embeddings-mathematics]] — Mathematical breakdown of the sinusoidal positional encoding formulas used in the original Transformer.