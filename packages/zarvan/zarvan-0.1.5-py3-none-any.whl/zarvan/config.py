# zarvan/config.py
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Any

@dataclass
class BaseConfig:
    initializer_range: float = 0.02
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def save_pretrained(self, save_path: str):
        path = Path(save_path)
        path.mkdir(parents=True, exist_ok=True)
        path_config = path / "config.json"
        
        with open(path_config, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=4)

    @classmethod
    def from_pretrained(cls, save_path: str):
        path = Path(save_path)
        path_config = path / "config.json"
        
        with open(path_config, "r", encoding="utf-8") as f:
            config_dict = json.load(f)
            
        return cls(**config_dict)

@dataclass
class BackboneConfig(BaseConfig):
    embed_dim: int = 768
    hidden_dim: int = 3072 # Typically 4 * embed_dim
    num_layers: int = 12
    num_heads: int = 12 # For HolisticExtractor

    dropout_prob: float = 0.1
    
@dataclass
class TextConfig(BaseConfig):
    vocab_size: int = 30522
    max_len: int = 2048
    num_classes: int = 2
    
@dataclass
class VisionConfig(BaseConfig):
    patch_size: int = 16
    image_size: int = 224
    num_classes: int = 2
    
@dataclass
class VideoConfig(BaseConfig):
    patch_size: int = 16
    num_classes: int = 2
    
@dataclass
class AudioConfig(BaseConfig):
    patch_size: int = 16
    n_mels: int = 128
    n_fft: int = 400
    num_classes: int = 2

class Config:
    Backbone = BackboneConfig
    Text = TextConfig
    Vision = VisionConfig
    Video = VideoConfig
    Audio = AudioConfig

    def __init__(self):
        raise TypeError("Config is a namespace and cannot be instantiated.")