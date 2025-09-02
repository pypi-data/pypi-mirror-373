# zarvan/model.py
import math
import json
from pathlib import Path
from typing import Dict, Any, Optional

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchaudio.transforms import MelSpectrogram

from .config import BackboneConfig, TextConfig, VisionConfig, VideoConfig, AudioConfig

class PositionalEncoding1D(nn.Module):
    """Injects positional information into the input embeddings."""
    def __init__(self, embed_dim: int, max_len: int = 512):
        super().__init__()
        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, embed_dim, 2) * (-math.log(10000.0) / embed_dim))
        pe = torch.zeros(max_len, 1, embed_dim)
        pe[:, 0, 0::2] = torch.sin(position * div_term)
        pe[:, 0, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x (torch.Tensor): Input tensor of shape (batch_size, seq_len, embed_dim).
        Returns:
            torch.Tensor: Tensor with added positional information.
        """
        # x is (batch, seq_len, embed_dim), pe is (max_len, 1, embed_dim)
        # We need to transpose x to (seq_len, batch, embed_dim) for broadcasting
        x = x.permute(1, 0, 2)
        x = x + self.pe[:x.size(0)]
        return x.permute(1, 0, 2)

class PositionalEncoding2D(nn.Module):
    """
    Generates 2D positional embeddings for image patches and handles
    inference-time resizing via interpolation.
    """
    def __init__(self, embed_dim: int, grid_size: int):
        super().__init__()
        self.grid_size = grid_size
        # Simple learnable 2D positional embeddings
        self.pos_embed = nn.Parameter(torch.zeros(1, grid_size * grid_size, embed_dim))
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, S, E = x.shape
        
        # At inference, if sequence length is different, interpolate
        if S != self.pos_embed.shape[1]:
            # Calculate new grid size
            new_grid_size = int(math.sqrt(S))
            # Reshape to 2D grid format for interpolation
            pos_embed_grid = self.pos_embed.view(1, self.grid_size, self.grid_size, E).permute(0, 3, 1, 2)
            # Interpolate to the new size
            new_pos_embed = F.interpolate(
                pos_embed_grid, size=(new_grid_size, new_grid_size), mode='bicubic', align_corners=False
            )
            # Reshape back to sequence format
            new_pos_embed = new_pos_embed.permute(0, 2, 3, 1).view(1, S, E)
            return x + new_pos_embed
        
        return x + self.pos_embed

class HolisticExtractor(nn.Module):
    """Captures the global "gist" of the sequence using a multi-head weighted sum."""
    def __init__(self, config: BackboneConfig):
        super().__init__()
        self.embed_dim = config.embed_dim
        self.num_heads = config.num_heads
        if self.embed_dim % self.num_heads != 0:
            raise ValueError(
                f"Embedding dimension ({self.embed_dim}) must be divisible by the number of heads ({self.num_heads})."
            )
        self.head_dim = self.embed_dim // self.num_heads
        
        self.score_proj = nn.Linear(self.embed_dim, self.embed_dim)
        self.value_proj = nn.Linear(self.embed_dim, self.embed_dim)
        self.output_proj = nn.Linear(self.embed_dim, self.embed_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, S, E = x.shape
        scores = self.score_proj(x).view(B, S, self.num_heads, self.head_dim).permute(0, 2, 1, 3)
        values = self.value_proj(x).view(B, S, self.num_heads, self.head_dim).permute(0, 2, 1, 3)
        
        weights = F.softmax(scores, dim=2) # Softmax over sequence length
        context = torch.sum(weights * values, dim=2) # (B, num_heads, head_dim)
        
        # Reshape and project to get the final holistic context vector
        context = context.reshape(B, E)
        return self.output_proj(context).unsqueeze(1) # (B, 1, E)

class AssociativeExtractor(nn.Module):
    """Focuses on salient tokens by computing a weighted average."""
    def __init__(self, config: BackboneConfig):
        super().__init__()
        self.score_proj = nn.Linear(config.embed_dim, 1)
        self.value_proj = nn.Linear(config.embed_dim, config.embed_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        scores = self.score_proj(x)
        values = self.value_proj(x)
        weights = F.softmax(scores, dim=1)
        context = torch.sum(weights * values, dim=1, keepdim=True)
        return context

class SequentialExtractor(nn.Module):
    """Functions as a parallel state machine to capture historical context."""
    def __init__(self, config: BackboneConfig):
        super().__init__()
        self.gate_proj = nn.Linear(config.embed_dim, config.embed_dim)
        self.value_proj = nn.Linear(config.embed_dim, config.embed_dim)
        self.norm = nn.LayerNorm(config.embed_dim)
        self.phase_calculator = nn.Linear(config.embed_dim, config.embed_dim)
        self.output_proj = nn.Linear(config.embed_dim * 2, config.embed_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, S, E = x.shape
        gates = torch.sigmoid(self.gate_proj(x))
        values = self.value_proj(x)
        
        accumulated_state = torch.cumsum(gates * values, dim=1)
        normalized_state = self.norm(self.phase_calculator(accumulated_state / S))
        
        omega = normalized_state * math.pi
        phases = torch.cat([torch.cos(omega), torch.sin(omega)], dim=-1)
        
        return self.output_proj(phases)

class FeedForward(nn.Module):
    """A standard two-layer feed-forward network with GELU activation."""
    def __init__(self, config: BackboneConfig):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(config.embed_dim, config.hidden_dim),
            nn.GELU(),
            nn.Dropout(config.dropout_prob),
            nn.Linear(config.hidden_dim, config.embed_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)

class ZarvanBlock(nn.Module):
    """A single block of the Zarvan architecture, containing a Mixture-of-Experts."""
    def __init__(self, config: BackboneConfig):
        super().__init__()
        
        self.input_adapter = nn.Sequential(
            nn.Linear(config.embed_dim, config.embed_dim), 
            nn.GELU(), 
            nn.LayerNorm(config.embed_dim)
        )
        
        self.holistic_extractor = HolisticExtractor(config)
        self.associative_extractor = AssociativeExtractor(config)
        self.sequential_extractor = SequentialExtractor(config)

        self.expert_gate = nn.Sequential(
            nn.Linear(config.embed_dim, 3),
            nn.SiLU()
        )
        
        self.ffn = FeedForward(config)
        self.output_norm = nn.LayerNorm(config.embed_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, S, E = x.shape
        residual = x
        
        x_adapted = self.input_adapter(x)

        # Get outputs from all three experts
        q_holistic = self.holistic_extractor(x_adapted)
        q_associative = self.associative_extractor(x_adapted)
        q_sequential = self.sequential_extractor(x_adapted)

        # Compute dynamic gates for each token
        gates = self.expert_gate(x_adapted)
        g_h, g_a, g_s = gates.chunk(3, dim=-1)
        
        # Combine expert outputs with learned gates
        # We need to expand the single context vectors to match the sequence length
        h = (
            g_h * q_holistic.expand(-1, S, -1) +
            g_a * q_associative.expand(-1, S, -1) +
            g_s * q_sequential
        )
        
        # Apply the second residual connection
        x = residual + self.ffn(self.output_norm(h))
        
        return x

class ZarvanBackbone(nn.Module):
    """
    The core of the Zarvan model. A stack of ZarvanBlocks that processes
    a sequence of embeddings. It is modality-agnostic.
    """
    def __init__(self, config: BackboneConfig):
        super().__init__()
        self.config = config
        self.layers = nn.ModuleList([ZarvanBlock(config) for _ in range(config.num_layers)])
        self.dropout = nn.Dropout(config.dropout_prob)

        self.apply(self._init_weights)

    def forward(self, input_embeddings: torch.Tensor) -> torch.Tensor:
        x = self.dropout(input_embeddings)
        for layer in self.layers:
            x = layer(x)
        return x
    
    def _init_weights(self, module: nn.Module):
        """Initializes weights of the model."""
        if isinstance(module, nn.Linear):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.bias is not None:
                module.bias.data.zero_()
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.padding_idx is not None:
                module.weight.data[module.padding_idx].zero_()
        elif isinstance(module, nn.LayerNorm):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0)

    def save_pretrained(self, save_directory: str):
        path = Path(save_directory)
        path.mkdir(parents=True, exist_ok=True)
        
        self.config.save_pretrained(save_directory)
        
        torch.save(self.state_dict(), path / "pytorch_model.bin")
        print(f"Model and config saved to '{save_directory}'")

    @classmethod
    def from_pretrained(cls, save_directory: str):
        path = Path(save_directory)
        
        config = BackboneConfig.from_pretrained(save_directory)
        
        model = cls(config)
        model_weights_path = path / "pytorch_model.bin"
        
        if model_weights_path.exists():
            model.load_state_dict(torch.load(model_weights_path))
            print(f"Model weights loaded from '{model_weights_path}'")
        else:
            print(f"Warning: No model weights found at '{model_weights_path}'. Model is randomly initialized.")
            
        model.eval() # Set to evaluation mode by default
        return model
    
    

class ZarvanForText(nn.Module):
    def __init__(self, config: TextConfig, backbone: ZarvanBackbone):
        super().__init__()
        self.config = config
        
        self.embedding = nn.Embedding(config.vocab_size, backbone.config.embed_dim)
        self.pos_encoder = PositionalEncoding1D(backbone.config.embed_dim, config.max_len)

        self.backbone = backbone

        self.output_head = nn.Linear(backbone.config.embed_dim, config.num_classes)

        self.apply(self._init_weights)

    def forward(self, input_ids: torch.Tensor, task: str = "generation") -> torch.Tensor:
        x = self.embedding(input_ids)
        x = self.pos_encoder(x)

        x = self.backbone(x)

        if task == 'classification':
            x = x.mean(dim=1)

        logits = self.output_head(x)

        return logits 
    
    def get_input_embeddings(self) -> nn.Embedding:
        return self.embedding

    def set_input_embeddings(self, new_embeddings: nn.Embedding):
        self.embedding = new_embeddings

    def resize_token_embeddings(self, new_num_tokens: Optional[int] = None) -> nn.Embedding:
        model_embeds = self.get_input_embeddings()
        old_vocab_size, old_embed_dim = model_embeds.weight.size()

        if new_num_tokens is None:
            return model_embeds

        if new_num_tokens == old_vocab_size:
            return model_embeds

        # Create a new embedding module with the new size
        new_embeddings = nn.Embedding(new_num_tokens, old_embed_dim, device=model_embeds.weight.device)
        
        # Initialize new weights using the model's initializer
        self._init_weights(new_embeddings)
        
        # Copy the old weights over
        num_tokens_to_copy = min(old_vocab_size, new_num_tokens)
        with torch.no_grad():
            new_embeddings.weight[:num_tokens_to_copy, :] = model_embeds.weight[:num_tokens_to_copy, :]

        # Update the model's embedding layer and config
        self.set_input_embeddings(new_embeddings)
        self.config.vocab_size = new_num_tokens
        
        print(f"Resized token embeddings from {old_vocab_size} to {new_num_tokens}.")
        return self.get_input_embeddings()

    def _init_weights(self, module: nn.Module):
        """Initializes weights of the model."""
        if isinstance(module, nn.Linear):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.bias is not None:
                module.bias.data.zero_()
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.padding_idx is not None:
                module.weight.data[module.padding_idx].zero_()
        elif isinstance(module, nn.LayerNorm):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0)

    def save_pretrained(self, save_directory: str):
        path = Path(save_directory)
        path.mkdir(parents=True, exist_ok=True)
        
        self.config.save_pretrained(save_directory)
        
        torch.save(self.state_dict(), path / "pytorch_model.bin")
        print(f"Model and config saved to '{save_directory}'")

    @classmethod
    def from_pretrained(cls, save_directory: str, backbone: ZarvanBackbone):
        path = Path(save_directory)
        
        config = TextConfig.from_pretrained(save_directory)
        
        model = cls(config, backbone)
        model_weights_path = path / "pytorch_model.bin"
        
        if model_weights_path.exists():
            model.load_state_dict(torch.load(model_weights_path))
            print(f"Model weights loaded from '{model_weights_path}'")
        else:
            print(f"Warning: No model weights found at '{model_weights_path}'. Model is randomly initialized.")
            
        model.eval() # Set to evaluation mode by default
        return model
    
class ZarvanForVision(nn.Module):
    def __init__(self, config: VisionConfig, backbone: ZarvanBackbone):
        super().__init__()
        self.config = config
        
        # Efficiently create patches using a single convolutional layer
        self.patch_embedder = nn.Conv2d(
            in_channels=3,
            out_channels=backbone.config.embed_dim,
            kernel_size=config.patch_size,
            stride=config.patch_size
        )
        
        grid_size = config.image_size // config.patch_size
        self.pos_encoder = PositionalEncoding2D(backbone.config.embed_dim, grid_size)

        self.backbone = backbone

        self.output_head = nn.Linear(backbone.config.embed_dim, config.num_classes)

        self.apply(self._init_weights)

    def forward(self, pixel_values: torch.Tensor, task: str = "generation") -> torch.Tensor:
        # pixel_values shape: (B, Channels, Height, Width)
        # 1. Create and project patches
        x = self.patch_embedder(pixel_values) # (B, E, H/P, W/P)
        # 2. Flatten to sequence
        x = x.flatten(2).transpose(1, 2) # (B, NumPatches, E)
        # 3. Add positional information
        x = self.pos_encoder(x)

        x = self.backbone(x)

        if task == 'classification':
            x = x.mean(dim=1)

        logits = self.output_head(x)

        return logits 
    
    def _init_weights(self, module: nn.Module):
        """Initializes weights of the model."""
        if isinstance(module, nn.Linear):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.bias is not None:
                module.bias.data.zero_()
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.padding_idx is not None:
                module.weight.data[module.padding_idx].zero_()
        elif isinstance(module, nn.LayerNorm):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0)

    def save_pretrained(self, save_directory: str):
        path = Path(save_directory)
        path.mkdir(parents=True, exist_ok=True)
        
        self.config.save_pretrained(save_directory)
        
        torch.save(self.state_dict(), path / "pytorch_model.bin")
        print(f"Model and config saved to '{save_directory}'")

    @classmethod
    def from_pretrained(cls, save_directory: str, backbone: ZarvanBackbone):
        path = Path(save_directory)
        
        config = VisionConfig.from_pretrained(save_directory)
        
        model = cls(config, backbone)
        model_weights_path = path / "pytorch_model.bin"
        
        if model_weights_path.exists():
            model.load_state_dict(torch.load(model_weights_path))
            print(f"Model weights loaded from '{model_weights_path}'")
        else:
            print(f"Warning: No model weights found at '{model_weights_path}'. Model is randomly initialized.")
            
        model.eval() # Set to evaluation mode by default
        return model

class ZarvanForVideo(nn.Module):
    """Zarvan with a video-specific head (ZarvanForFrame)."""
    def __init__(self, config: VideoConfig, backbone: ZarvanBackbone):
        super().__init__()
        self.config = config
        
        # Re-use the vision embedder for each frame
        self.frame_embedder = nn.Conv2d(
            in_channels=3,
            out_channels=backbone.config.embed_dim,
            kernel_size=config.patch_size,
            stride=config.patch_size
        )

        self.backbone = backbone

        self.output_head = nn.Linear(backbone.config.embed_dim, config.num_classes)

        self.apply(self._init_weights)

    def forward(self, video_frames: torch.Tensor, task: str = "generation") -> torch.Tensor:
        # video_frames shape: (B, NumFrames, C, H, W)
        B, F, C, H, W = video_frames.shape
        
        # Reshape to process all frames at once
        video_frames = video_frames.view(B * F, C, H, W)
        
        # 1. Create patch embeddings for every frame
        frame_embeds = self.frame_embedder(video_frames) # (B*F, E, H/P, W/P)
        frame_embeds = frame_embeds.flatten(2).transpose(1, 2) # (B*F, NumPatches, E)
        
        # 2. Reshape back and flatten to one long sequence per video
        num_patches_per_frame = frame_embeds.shape[1]
        x = frame_embeds.view(B, F * num_patches_per_frame, self.config.embed_dim)
        
        x = self.backbone(x)

        if task == 'classification':
            x = x.mean(dim=1)

        logits = self.output_head(x)

        return logits 
    
    def _init_weights(self, module: nn.Module):
        """Initializes weights of the model."""
        if isinstance(module, nn.Linear):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.bias is not None:
                module.bias.data.zero_()
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.padding_idx is not None:
                module.weight.data[module.padding_idx].zero_()
        elif isinstance(module, nn.LayerNorm):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0)

    def save_pretrained(self, save_directory: str):
        path = Path(save_directory)
        path.mkdir(parents=True, exist_ok=True)
        
        self.config.save_pretrained(save_directory)
        
        torch.save(self.state_dict(), path / "pytorch_model.bin")
        print(f"Model and config saved to '{save_directory}'")

    @classmethod
    def from_pretrained(cls, save_directory: str, backbone: ZarvanBackbone):
        path = Path(save_directory)
        
        config = VideoConfig.from_pretrained(save_directory)
        
        model = cls(config, backbone)
        model_weights_path = path / "pytorch_model.bin"
        
        if model_weights_path.exists():
            model.load_state_dict(torch.load(model_weights_path))
            print(f"Model weights loaded from '{model_weights_path}'")
        else:
            print(f"Warning: No model weights found at '{model_weights_path}'. Model is randomly initialized.")
            
        model.eval() # Set to evaluation mode by default
        return model
        
class ZarvanForAudio(nn.Module):
    """Zarvan with an audio-specific head."""
    def __init__(self, config: AudioConfig, backbone: ZarvanBackbone):
        super().__init__()
        self.config = config

        # 1. Spectrogram layer
        self.mel_spectrogram = MelSpectrogram(n_mels = config.n_mels, n_fft = config.n_fft)

        # 2. Patch embedder for the spectrogram
        # We treat the spectrogram like a 1-channel image
        self.patch_embedder = nn.Conv2d(
            in_channels=1,
            out_channels=backbone.config.embed_dim,
            kernel_size=config.patch_size,
            stride=(config.patch_size // 2, config.patch_size) # Overlapping stride can work well for audio
        )

        self.backbone = backbone

        self.output_head = nn.Linear(backbone.config.embed_dim, config.num_classes)

        self.apply(self._init_weights)
        
    def forward(self, waveform: torch.Tensor, task: str = "generation") -> torch.Tensor:
        # waveform shape: (B, NumSamples)
        # 1. Convert to Mel Spectrogram
        x = self.mel_spectrogram(waveform).unsqueeze(1) # (B, 1, FreqBands, TimeSteps)
        # 2. Create patch embeddings
        x = self.patch_embedder(x) # (B, E, FreqPatches, TimePatches)
        # 3. Flatten to sequence
        x = x.flatten(2).transpose(1, 2) # (B, NumPatches, E)

        x = self.backbone(x)

        if task == 'classification':
            x = x.mean(dim=1)

        logits = self.output_head(x)

        return logits 
    
    def _init_weights(self, module: nn.Module):
        """Initializes weights of the model."""
        if isinstance(module, nn.Linear):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.bias is not None:
                module.bias.data.zero_()
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.padding_idx is not None:
                module.weight.data[module.padding_idx].zero_()
        elif isinstance(module, nn.LayerNorm):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0)

    def save_pretrained(self, save_directory: str):
        path = Path(save_directory)
        path.mkdir(parents=True, exist_ok=True)
        
        self.config.save_pretrained(save_directory)
        
        torch.save(self.state_dict(), path / "pytorch_model.bin")
        print(f"Model and config saved to '{save_directory}'")

    @classmethod
    def from_pretrained(cls, save_directory: str, backbone: ZarvanBackbone):
        path = Path(save_directory)
        
        config = AudioConfig.from_pretrained(save_directory)
        
        model = cls(config, backbone)
        model_weights_path = path / "pytorch_model.bin"
        
        if model_weights_path.exists():
            model.load_state_dict(torch.load(model_weights_path))
            print(f"Model weights loaded from '{model_weights_path}'")
        else:
            print(f"Warning: No model weights found at '{model_weights_path}'. Model is randomly initialized.")
            
        model.eval() # Set to evaluation mode by default
        return model
               
class Zarvan:
    """
    A namespace for all Zarvan model classes.
    This class is not meant to be instantiated.
    Access models like: Zarvan.Backbone(...) or Zarvan.Text(...)
    """
    Backbone = ZarvanBackbone
    Text = ZarvanForText
    Vision = ZarvanForVision
    Video = ZarvanForVideo
    Audio = ZarvanForAudio

    def __init__(self):
        raise TypeError("Zarvan is a namespace and cannot be instantiated.")
    