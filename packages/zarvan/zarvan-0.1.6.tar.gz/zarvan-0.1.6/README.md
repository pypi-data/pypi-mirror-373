# Zarvan: A Hybrid MoE Architecture for Advanced Sequence Modeling

[![PyPI Version](https://img.shields.io/pypi/v/zarvan.svg)](https://pypi.org/project/zarvan/)
[![Build Status](https://img.shields.io/github/actions/workflow/status/systbs/zarvan-torch/main.yml?branch=main)](https://github.com/systbs/zarvan-torch/actions)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/release/python-380/)


**Zarvan** is an advanced neural network architecture designed to overcome the fundamental limitations of Transformers and RNNs. By unifying the strengths of parallel processing and stateful reasoning, Zarvan provides a powerful, scalable solution for the next generation of sequence modeling challenges.

This library is built on pure PyTorch, offering a lightweight, independent, and high-performance implementation of the Zarvan architecture.

---

## 🚀 Key Features

* **Hybrid Mixture-of-Experts (MoE) Architecture**: Employs an intelligent MoE system that dynamically chooses between three "experts" to process a sequence: two for global pattern recognition and a dedicated state machine for step-by-step reasoning.
* **Linear Time Complexity ($O(S)$)**: By replacing the quadratic ($O(S^2)$) self-attention mechanism, Zarvan is significantly more efficient and ideal for processing ultra-long sequences.
* **🧠 Stateful Sequential Reasoning**: Features the **Sequential Extractor**, a deterministic state machine that maintains a perfect, non-decaying memory of the sequence history, enabling it to solve complex, path-dependent tasks where Transformers fail.
* **⚡ Lightweight & Independent**: Built on pure PyTorch with **zero external dependencies** beyond `torch`, ensuring easy integration, maximum flexibility, and no version conflicts.

---

## 🏛️ Architecture Overview

The core of Zarvan is a stack of identical blocks. Each block is a Mixture-of-Experts model that dynamically combines the outputs of three specialist modules via a learned gating network.

1.  **Holistic Extractor**: Captures the "gist" or overall summary of the sequence.
2.  **Associative Extractor**: Acts as a "focused memory" retriever for salient, sparse information.
3.  **Sequential Extractor (The State Machine)**: Functions as a parallelized state machine that tracks the sequence history losslessly using gated accumulation and phase representation.

An **Expert Gate** then learns to weigh the outputs of these three modules for each token, allowing the model to adapt its strategy based on the input.

---

## 🚀 Installation

Install the package directly from PyPI:

```bash
pip install zarvan
```

Or after cloning the repository locally:
```bash
git clone [https://github.com/systbs/zarvan-torch.git](https://github.com/systbs/zarvan-torch.git)
cd zarvan-torch
pip install .
```

## ✨ Quick Start

Using the independent zarvan library is clean and simple.

```python
import torch
from zarvan import Config, Zarvan

# --- Step 1: Create and Save Each Component Independently ---

# 1a. The Backbone
backbone_config = Config.Backbone(
    embed_dim=256,
    hidden_dim=1024,
    num_layers=6,
    num_heads=4,
)
backbone = Zarvan.Backbone(backbone_config)
backbone_save_dir = "./saved-zarvan-backbone"
backbone.save(backbone_save_dir)
print(f"Backbone saved to '{backbone_save_dir}'.")

# 1b. The Text Modality Head
text_modality_config = Config.Text(
    embed_dim=256, # Must match backbone's embed_dim
    vocab_size=30522,
    max_len=128
)
text_modality_head = Zarvan.Modality.Text(text_modality_config)
text_head_save_dir = "./saved-zarvan-text"
text_modality_head.save(text_head_save_dir)
print(f"Text Modality Head saved to '{text_head_save_dir}'.")

# 1c. The Classification Task Head (Finisher)
classification_config = Config.Classification(
    embed_dim=256, # Must match backbone's embed_dim
    num_classes=10
)
classification_task_head = Zarvan.Task.Classification(classification_config)
task_head_save_dir = "./saved-zarvan-classification"
classification_task_head.save(task_head_save_dir)
print(f"Classification Task Head saved to '{task_head_save_dir}'.")
print("-" * 50)


# --- Step 2: Load and Combine Components for Inference ---

# Load each independent component
loaded_backbone = Zarvan.Backbone.load(backbone_save_dir)
loaded_text_head = Zarvan.Modality.Text.load(text_head_save_dir)
loaded_task_head = Zarvan.Task.Classification.load(task_head_save_dir)

# Set all components to evaluation mode
loaded_backbone.eval()
loaded_text_head.eval()
loaded_task_head.eval()

print("All components loaded successfully.")
print("-" * 50)


# --- Step 3: Perform a Forward Pass ---

# Create dummy input data
input_ids = torch.randint(0, text_modality_config.vocab_size, (2, 50)) # (Batch, SeqLen)

# The forward pass is a chain of the three components
with torch.no_grad():
    # 1. Modality head converts tokens to embeddings
    embeddings = loaded_text_head(input_ids)
    # 2. Backbone processes the embeddings
    hidden_states = loaded_backbone(embeddings)
    # 3. Task head produces the final output (logits)
    logits = loaded_task_head(hidden_states, task='classification')

print("--- I/O Shapes ---")
print("Input IDs Shape:     ", input_ids.shape)
print("Embeddings Shape:    ", embeddings.shape)
print("Hidden States Shape: ", hidden_states.shape)
print("Logits Shape:        ", logits.shape)
# Expected Logits shape: torch.Size([2, 10])
print("-" * 50)

print("Model composition and forward pass successful. ✅")
```


