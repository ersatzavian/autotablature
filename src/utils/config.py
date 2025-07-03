"""
Configuration management for AutoTablature.
"""

import json
import yaml
import os
from typing import Any, Dict


class Config:
    """Configuration manager for AutoTablature."""
    
    def __init__(self, config_path=None):
        """Initialize configuration."""
        self.config_data = self._load_default_config()
        
        if config_path and os.path.exists(config_path):
            self._load_config_file(config_path)
    
    def _load_default_config(self):
        """Load default configuration values."""
        return {
            'audio': {
                'sample_rate': 44100,
                'hop_length': 512,
                'n_fft': 2048,
                'n_mels': 128,
                'trim_db': 20
            },
            'separation': {
                'model_path': 'models/separation_model.pth',
                'instruments': ['guitar_lead', 'guitar_rhythm', 'bass', 'drums', 'vocals']
            },
            'pitch': {
                'model_path': 'models/pitch_model.pth',
                'fmin': 80,
                'fmax': 1000,
                'n_bins': 360,
                'confidence_threshold': 0.3
            },
            'guitar': {
                'num_strings': 6,
                'num_frets': 24,
                'standard_tuning': [64, 59, 55, 50, 45, 40]  # MIDI notes
            },
            'training': {
                'learning_rate': 0.001,
                'batch_size': 32,
                'epochs': 100,
                'validation_split': 0.2
            },
            'output': {
                'format': 'gp5',
                'quality': 'high'
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        }
    
    def _load_config_file(self, config_path):
        """Load configuration from file."""
        try:
            with open(config_path, 'r') as f:
                if config_path.endswith('.json'):
                    file_config = json.load(f)
                elif config_path.endswith(('.yml', '.yaml')):
                    file_config = yaml.safe_load(f)
                else:
                    raise ValueError(f"Unsupported config format: {config_path}")
            
            # Merge with default config
            self._merge_config(self.config_data, file_config)
            
        except Exception as e:
            print(f"Warning: Could not load config file {config_path}: {e}")
            print("Using default configuration")
    
    def _merge_config(self, default_config, file_config):
        """Recursively merge file config into default config."""
        for key, value in file_config.items():
            if key in default_config and isinstance(default_config[key], dict) and isinstance(value, dict):
                self._merge_config(default_config[key], value)
            else:
                default_config[key] = value
    
    def get(self, key_path, default=None):
        """
        Get configuration value using dot notation.
        
        Args:
            key_path (str): Dot-separated path (e.g., 'audio.sample_rate')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        current = self.config_data
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path, value):
        """
        Set configuration value using dot notation.
        
        Args:
            key_path (str): Dot-separated path
            value: Value to set
        """
        keys = key_path.split('.')
        current = self.config_data
        
        # Navigate to parent of target key
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set the value
        current[keys[-1]] = value
    
    def save(self, filename):
        """Save current configuration to file."""
        try:
            with open(filename, 'w') as f:
                if filename.endswith('.json'):
                    json.dump(self.config_data, f, indent=2)
                elif filename.endswith(('.yml', '.yaml')):
                    yaml.dump(self.config_data, f, default_flow_style=False)
                else:
                    raise ValueError(f"Unsupported format: {filename}")
        except Exception as e:
            print(f"Error saving config to {filename}: {e}")
    
    def to_dict(self):
        """Return configuration as dictionary."""
        return self.config_data.copy()
