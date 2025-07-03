"""
Model training module for AutoTablature.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import os
import numpy as np
import logging
from datetime import datetime
import json
from typing import Dict, List, Tuple

from ..utils.logger import setup_training_logger
from ..separation.separator import UNetSeparator
from ..models.pitch_detector import PitchCNN


class ModelTrainer:
    """Train models for AutoTablature system."""
    
    def __init__(self, config):
        """Initialize the model trainer."""
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Generate unique run ID
        self.run_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.logger = setup_training_logger(__name__, self.run_id)
        
        self.logger.info(f"Model trainer initialized with device: {self.device}")
        self.logger.info(f"Training run ID: {self.run_id}")
    
    def train(self, data_path, model_type="all"):
        """
        Train models on the provided dataset.
        
        Args:
            data_path (str): Path to training data directory
            model_type (str): Type of model to train
        """
        self.logger.info(f"Starting training for model type: {model_type}")
        self.logger.info(f"Data path: {data_path}")
        
        if model_type in ["separation", "all"]:
            self._train_separation_model(data_path)
        
        if model_type in ["pitch", "all"]:
            self._train_pitch_model(data_path)
        
        self.logger.info("Training completed!")
    
    def _train_separation_model(self, data_path):
        """Train the instrument separation model."""
        self.logger.info("Training separation model...")
        
        # Load separation dataset
        dataset = SeparationDataset(data_path, self.config)
        
        # Split dataset
        train_size = int(0.8 * len(dataset))
        val_size = len(dataset) - train_size
        train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])
        
        # Create data loaders
        batch_size = self.config.get('training.batch_size', 32)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
        
        # Initialize model
        model = UNetSeparator(
            input_channels=1,
            output_channels=len(self.config.get('separation.instruments', [])),
            features=64
        ).to(self.device)
        
        # Setup training
        criterion = nn.MSELoss()
        optimizer = optim.Adam(model.parameters(), lr=self.config.get('training.learning_rate', 0.001))
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=10)
        
        # Training loop
        epochs = self.config.get('training.epochs', 100)
        best_val_loss = float('inf')
        
        for epoch in range(epochs):
            # Training phase
            model.train()
            train_loss = 0.0
            
            for batch_idx, (inputs, targets) in enumerate(train_loader):
                inputs, targets = inputs.to(self.device), targets.to(self.device)
                
                optimizer.zero_grad()
                outputs = model(inputs)
                loss = criterion(outputs, targets)
                loss.backward()
                optimizer.step()
                
                train_loss += loss.item()
                
                if batch_idx % 10 == 0:
                    self.logger.debug(f'Epoch {epoch}, Batch {batch_idx}, Loss: {loss.item():.6f}')
            
            # Validation phase
            model.eval()
            val_loss = 0.0
            
            with torch.no_grad():
                for inputs, targets in val_loader:
                    inputs, targets = inputs.to(self.device), targets.to(self.device)
                    outputs = model(inputs)
                    val_loss += criterion(outputs, targets).item()
            
            train_loss /= len(train_loader)
            val_loss /= len(val_loader)
            
            self.logger.info(f'Epoch {epoch}: Train Loss: {train_loss:.6f}, Val Loss: {val_loss:.6f}')
            
            # Learning rate scheduling
            scheduler.step(val_loss)
            
            # Save best model
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                self._save_model(model, optimizer, epoch, val_loss, 'separation')
        
        self.logger.info(f"Separation model training completed. Best validation loss: {best_val_loss:.6f}")
    
    def _train_pitch_model(self, data_path):
        """Train the pitch detection model."""
        self.logger.info("Training pitch detection model...")
        
        # Load pitch dataset
        dataset = PitchDataset(data_path, self.config)
        
        # Split dataset
        train_size = int(0.8 * len(dataset))
        val_size = len(dataset) - train_size
        train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])
        
        # Create data loaders
        batch_size = self.config.get('training.batch_size', 32)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
        
        # Initialize model
        model = PitchCNN(
            input_size=self.config.get('audio.n_fft', 2048) // 2 + 1,
            n_bins=self.config.get('pitch.n_bins', 360)
        ).to(self.device)
        
        # Setup training
        criterion = nn.BCELoss()  # Multi-label classification
        optimizer = optim.Adam(model.parameters(), lr=self.config.get('training.learning_rate', 0.001))
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=10)
        
        # Training loop
        epochs = self.config.get('training.epochs', 100)
        best_val_loss = float('inf')
        
        for epoch in range(epochs):
            # Training phase
            model.train()
            train_loss = 0.0
            
            for batch_idx, (inputs, targets) in enumerate(train_loader):
                inputs, targets = inputs.to(self.device), targets.to(self.device)
                
                optimizer.zero_grad()
                outputs = model(inputs)
                loss = criterion(outputs, targets)
                loss.backward()
                optimizer.step()
                
                train_loss += loss.item()
                
                if batch_idx % 10 == 0:
                    self.logger.debug(f'Epoch {epoch}, Batch {batch_idx}, Loss: {loss.item():.6f}')
            
            # Validation phase
            model.eval()
            val_loss = 0.0
            
            with torch.no_grad():
                for inputs, targets in val_loader:
                    inputs, targets = inputs.to(self.device), targets.to(self.device)
                    outputs = model(inputs)
                    val_loss += criterion(outputs, targets).item()
            
            train_loss /= len(train_loader)
            val_loss /= len(val_loader)
            
            self.logger.info(f'Epoch {epoch}: Train Loss: {train_loss:.6f}, Val Loss: {val_loss:.6f}')
            
            # Learning rate scheduling
            scheduler.step(val_loss)
            
            # Save best model
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                self._save_model(model, optimizer, epoch, val_loss, 'pitch')
        
        self.logger.info(f"Pitch model training completed. Best validation loss: {best_val_loss:.6f}")
    
    def _save_model(self, model, optimizer, epoch, loss, model_type):
        """Save model checkpoint."""
        models_dir = "models"
        if not os.path.exists(models_dir):
            os.makedirs(models_dir)
        
        checkpoint = {
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'epoch': epoch,
            'loss': loss,
            'config': self.config.to_dict(),
            'run_id': self.run_id,
            'model_type': model_type
        }
        
        filename = os.path.join(models_dir, f"{model_type}_model_{self.run_id}.pth")
        torch.save(checkpoint, filename)
        
        # Also save as the default model
        default_filename = os.path.join(models_dir, f"{model_type}_model.pth")
        torch.save(checkpoint, default_filename)
        
        self.logger.info(f"Model saved: {filename}")


class SeparationDataset(Dataset):
    """Dataset for training instrument separation models."""
    
    def __init__(self, data_path, config):
        """Initialize the separation dataset."""
        self.data_path = data_path
        self.config = config
        self.samples = self._load_samples()
    
    def _load_samples(self):
        """Load training samples from data directory."""
        samples = []
        
        # Look for paired audio files (mixed and separated)
        mixed_dir = os.path.join(self.data_path, "mixed")
        separated_dir = os.path.join(self.data_path, "separated")
        
        if os.path.exists(mixed_dir) and os.path.exists(separated_dir):
            for filename in os.listdir(mixed_dir):
                if filename.endswith(('.wav', '.mp3', '.flac')):
                    mixed_path = os.path.join(mixed_dir, filename)
                    
                    # Look for corresponding separated files
                    base_name = os.path.splitext(filename)[0]
                    separated_files = {}
                    
                    instruments = self.config.get('separation.instruments', [])
                    for instrument in instruments:
                        sep_filename = f"{base_name}_{instrument}.wav"
                        sep_path = os.path.join(separated_dir, sep_filename)
                        
                        if os.path.exists(sep_path):
                            separated_files[instrument] = sep_path
                    
                    if separated_files:
                        samples.append({
                            'mixed': mixed_path,
                            'separated': separated_files
                        })
        
        return samples
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        """Get a training sample."""
        sample = self.samples[idx]
        
        # Load mixed audio
        import librosa
        mixed_audio, sr = librosa.load(sample['mixed'], sr=self.config.get('audio.sample_rate'))
        
        # Compute STFT
        stft = librosa.stft(mixed_audio, hop_length=self.config.get('audio.hop_length'))
        magnitude = np.abs(stft)
        
        # Load separated tracks and create masks
        instruments = self.config.get('separation.instruments', [])
        masks = np.zeros((len(instruments), *magnitude.shape))
        
        for i, instrument in enumerate(instruments):
            if instrument in sample['separated']:
                sep_audio, _ = librosa.load(sample['separated'][instrument], sr=sr)
                sep_stft = librosa.stft(sep_audio, hop_length=self.config.get('audio.hop_length'))
                sep_magnitude = np.abs(sep_stft)
                
                # Create ideal binary mask
                mask = sep_magnitude / (magnitude + 1e-8)
                masks[i] = np.clip(mask, 0, 1)
        
        # Convert to tensors
        input_tensor = torch.FloatTensor(magnitude).unsqueeze(0)
        target_tensor = torch.FloatTensor(masks)
        
        return input_tensor, target_tensor


class PitchDataset(Dataset):
    """Dataset for training pitch detection models."""
    
    def __init__(self, data_path, config):
        """Initialize the pitch dataset."""
        self.data_path = data_path
        self.config = config
        self.samples = self._load_samples()
    
    def _load_samples(self):
        """Load training samples from data directory."""
        samples = []
        
        # Look for audio files with corresponding pitch annotations
        audio_dir = os.path.join(self.data_path, "audio")
        annotations_dir = os.path.join(self.data_path, "annotations")
        
        if os.path.exists(audio_dir) and os.path.exists(annotations_dir):
            for filename in os.listdir(audio_dir):
                if filename.endswith(('.wav', '.mp3', '.flac')):
                    audio_path = os.path.join(audio_dir, filename)
                    
                    # Look for corresponding annotation file
                    base_name = os.path.splitext(filename)[0]
                    annotation_path = os.path.join(annotations_dir, f"{base_name}.json")
                    
                    if os.path.exists(annotation_path):
                        samples.append({
                            'audio': audio_path,
                            'annotation': annotation_path
                        })
        
        return samples
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        """Get a training sample."""
        sample = self.samples[idx]
        
        # Load audio
        import librosa
        audio, sr = librosa.load(sample['audio'], sr=self.config.get('audio.sample_rate'))
        
        # Compute STFT
        stft = librosa.stft(audio, hop_length=self.config.get('audio.hop_length'))
        magnitude = np.abs(stft)
        
        # Load pitch annotations
        with open(sample['annotation'], 'r') as f:
            annotations = json.load(f)
        
        # Create pitch target matrix
        n_bins = self.config.get('pitch.n_bins', 360)
        n_frames = magnitude.shape[1]
        pitch_target = np.zeros((n_frames, n_bins))
        
        # Fill in pitch targets based on annotations
        for annotation in annotations.get('pitches', []):
            frame_start = int(annotation['time_start'] * sr / self.config.get('audio.hop_length'))
            frame_end = int(annotation['time_end'] * sr / self.config.get('audio.hop_length'))
            
            for freq in annotation['frequencies']:
                pitch_bin = self._frequency_to_bin(freq)
                if 0 <= pitch_bin < n_bins:
                    pitch_target[frame_start:frame_end, pitch_bin] = 1.0
        
        # Convert to tensors
        input_tensor = torch.FloatTensor(magnitude.T)  # (time, frequency)
        target_tensor = torch.FloatTensor(pitch_target)
        
        return input_tensor, target_tensor
    
    def _frequency_to_bin(self, frequency):
        """Convert frequency to pitch bin index."""
        # Logarithmic pitch scale centered on A4 (440 Hz)
        if frequency <= 0:
            return -1
        
        cents_from_a4 = 1200 * np.log2(frequency / 440.0)
        n_bins = self.config.get('pitch.n_bins', 360)
        cents_per_bin = 1200 / n_bins
        
        bin_index = int(cents_from_a4 / cents_per_bin + n_bins // 2)
        return bin_index
