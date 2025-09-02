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
from zarvan import Config, TextConfig, VisionConfig, VideoConfig, AudioConfig, ZarvanBackbone, ZarvanForText, ZarvanForVision, ZarvanForVideo, ZarvanForAudio

# --- Step 1: Create and Save the Shared Backbone ---

# Define the configuration for the core backbone architecture.
# These hyperparameters are shared across all modalities.
backbone_config = Config(
    embed_dim=256,
    hidden_dim=1024,
    num_layers=6,
    num_heads=4,
)

# Instantiate the shared backbone from the configuration.
shared_backbone = ZarvanBackbone(backbone_config)

# It's a good practice to save the backbone independently.
backbone_save_dir = "./saved_zarvan_backbone"
shared_backbone.save_pretrained(backbone_save_dir)
print(f"Backbone created and saved successfully to '{backbone_save_dir}'.")
print("-" * 50)


# --- Step 2: Create Modality-Specific Heads ---

# Now, we'll create a specific head for each modality, injecting the same shared_backbone into each.

# A) Text Head
# TextConfig inherits from Config, so we must provide both general and text-specific parameters.
text_config = TextConfig(
    vocab_size=30522, max_len=128, num_classes=10 # Text-specific
)
text_model = ZarvanForText(text_config, shared_backbone)
print("ZarvanForText head created.")

# B) Vision Head
vision_config = VisionConfig(
    patch_size=16, image_size=224, num_classes=10 # Vision-specific
)
vision_model = ZarvanForVision(vision_config, shared_backbone)
print("ZarvanForVision head created.")

# C) Video Head
video_config = VideoConfig(
    patch_size=16, num_classes=10 # Video-specific
)
video_model = ZarvanForVideo(video_config, shared_backbone)
print("ZarvanForVideo head created.")

# D) Audio Head
audio_config = AudioConfig(
    patch_size=16, n_mels=128, n_fft=400, num_classes=10 # Audio-specific
)
audio_model = ZarvanForAudio(audio_config, shared_backbone)
print("ZarvanForAudio head created.")
print("-" * 50)


# --- Step 3: Use the Models for Inference ---

# Set all models to evaluation mode.
text_model.eval()
vision_model.eval()
video_model.eval()
audio_model.eval()

# Create dummy input data for each modality.
input_ids = torch.randint(0, text_config.vocab_size, (2, 50)) # (Batch, SeqLen)
pixel_values = torch.randn(2, 3, 224, 224) # (Batch, Channels, Height, Width)
video_frames = torch.randn(2, 16, 3, 112, 112) # (Batch, Frames, C, H, W)
waveform = torch.randn(2, 16000) # (Batch, Samples)

# Perform a forward pass for each model.
with torch.no_grad():
    text_logits = text_model(input_ids, task='classification')
    vision_logits = vision_model(pixel_values, task='classification')
    video_logits = video_model(video_frames, task='classification')
    audio_logits = audio_model(waveform, task='classification')

print("--- I/O Shapes ---")
print("Text Input Shape:    ", input_ids.shape)
print("Text Logits Shape:   ", text_logits.shape)
print("Vision Input Shape:  ", pixel_values.shape)
print("Vision Logits Shape: ", vision_logits.shape)
print("Video Input Shape:   ", video_frames.shape)
print("Video Logits Shape:  ", video_logits.shape)
print("Audio Input Shape:   ", waveform.shape)
print("Audio Logits Shape:  ", audio_logits.shape)
print("-" * 50)


# --- Step 4: Save and Load a Composed Model ---

# The saving and loading process is the same for any head. Let's demonstrate with the text model.

# 1. Save the head. Its config and weights will be stored.
text_head_save_dir = "./saved_text_head"
text_model.save_pretrained(text_head_save_dir)

# 2. To load, first load the backbone you want to use.
loaded_backbone = ZarvanBackbone.from_pretrained(backbone_save_dir)

# 3. Then, load the head and inject the loaded backbone into it.
loaded_text_model = ZarvanForText.from_pretrained(
    text_head_save_dir,
    backbone=loaded_backbone
)
loaded_text_model.eval()

# Verify that the loaded model produces the same output.
with torch.no_grad():
    loaded_logits = loaded_text_model(input_ids, task='classification')

assert torch.allclose(text_logits, loaded_logits, atol=1e-5)
print("Saved and loaded model outputs match. ✅")
```


