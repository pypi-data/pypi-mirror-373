"""
Configuration management for BirdCount.

This module handles loading, validating, and managing configuration
for the bird counting pipeline.
"""

import yaml
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to YAML configuration file
        
    Returns:
        Configuration dictionary
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If YAML is invalid
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    try:
        with open(config_file, 'r') as f:
            user_config = yaml.safe_load(f)
        
        # Merge with defaults and validate
        config = validate_and_merge_config(user_config)
        
        logger.info(f"Loaded configuration from {config_path}")
        return config
        
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Invalid YAML in config file {config_path}: {e}")


def get_default_config() -> Dict[str, Any]:
    """
    Get default configuration for BirdCount.
    
    Returns:
        Dictionary containing default configuration values
    """
    return {
        # Input and output directories
        "input_dir": "data/raw/birds",
        "output_dir": "outputs",
        
        # Bandpass filter settings
        "bandpass": {
            "freq_min": 1500,
            "freq_max": 7000,
            "order": 6
        },
        
        # Call detection settings
        "detection": {
            "mad_multiplier": 2.0,
            "min_duration": 0.4,
            "max_gap": 0.08,
            "frame_length": 2048,
            "hop_length": 512
        },
        
        # Cropping settings
        "cropping": {
            "padding": 0.15
        },
        
        # Spectral subtraction settings
        "spectral_subtraction": {
            "noise_duration": 0.1,
            "noise_factor": 2.5,
            "n_fft": 1024,
            "hop_length": 256
        },
        
        # Logging settings
        "logging": {
            "level": "INFO",
            "save_plots": False,
            "plot_dir": "plots"
        },
        
        # Embedding settings (optional)
        "embedding": {
            "enabled": True,
            "model_url": "https://www.kaggle.com/models/google/bird-vocalization-classifier/TensorFlow2/bird-vocalization-classifier/2",
            "sample_rate": 32000,
            "target_duration": 5.0
        }
    }


def validate_and_merge_config(user_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate user configuration and merge with defaults.
    
    Args:
        user_config: User-provided configuration
        
    Returns:
        Merged and validated configuration
    """
    default_config = get_default_config()
    
    # Simple merge (not deep)
    merged_config = default_config.copy()
    merged_config.update(user_config)
    
    # Validate the merged config
    validate_config(merged_config)
    
    return merged_config


def validate_config(config: Dict[str, Any]) -> None:
    """
    Validate configuration values.
    
    Args:
        config: Configuration to validate
        
    Raises:
        ValueError: If configuration is invalid
    """
    # Check required fields
    if not config.get("input_dir"):
        raise ValueError("input_dir is required in configuration")
    
    # Validate bandpass settings
    bandpass = config.get("bandpass", {})
    if bandpass.get("freq_min", 0) >= bandpass.get("freq_max", float('inf')):
        raise ValueError("bandpass.freq_min must be less than bandpass.freq_max")
    
    # Validate detection settings
    detection = config.get("detection", {})
    if detection.get("min_duration", 0) <= 0:
        raise ValueError("detection.min_duration must be positive")
    
    # Validate logging level
    logging_config = config.get("logging", {})
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
    if logging_config.get("level") not in valid_levels:
        raise ValueError(f"logging.level must be one of {valid_levels}") 