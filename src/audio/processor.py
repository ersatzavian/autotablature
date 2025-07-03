"""
Audio processing and analysis module.

Handles loading, preprocessing, and feature extraction from audio files.
"""

import librosa
import numpy as np
import soundfile as sf
from scipy import signal
import logging


class AudioProcessor:
    """Handle audio loading, preprocessing, and feature extraction."""
    
    def __init__(self, config):
        """Initialize the audio processor."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Audio processing parameters
        self.sample_rate = config.get('audio.sample_rate', 44100)
        self.hop_length = config.get('audio.hop_length', 512)
        self.n_fft = config.get('audio.n_fft', 2048)
        self.n_mels = config.get('audio.n_mels', 128)
    
    def load_audio(self, file_path):
        """
        Load audio file with proper preprocessing.
        
        Args:
            file_path (str): Path to audio file
            
        Returns:
            tuple: (audio_data, sample_rate)
        """
        try:
            # Load audio file
            audio, sr = librosa.load(file_path, sr=self.sample_rate, mono=True)
            
            self.logger.info(f"Loaded audio: {file_path}")
            self.logger.info(f"Duration: {len(audio) / sr:.2f} seconds")
            self.logger.info(f"Sample rate: {sr} Hz")
            
            return audio, sr
            
        except Exception as e:
            self.logger.error(f"Error loading audio file {file_path}: {e}")
            raise
    
    def preprocess(self, audio_data):
        """
        Preprocess audio data for analysis.
        
        Args:
            audio_data (np.ndarray): Raw audio data
            
        Returns:
            dict: Preprocessed audio features
        """
        self.logger.info("Preprocessing audio data...")
        
        # Normalize audio
        audio_normalized = librosa.util.normalize(audio_data)
        
        # Remove silence
        audio_trimmed, _ = librosa.effects.trim(
            audio_normalized, 
            top_db=self.config.get('audio.trim_db', 20)
        )
        
        # Extract various audio features
        features = {
            'audio': audio_trimmed,
            'stft': self._compute_stft(audio_trimmed),
            'melspectrogram': self._compute_melspectrogram(audio_trimmed),
            'chroma': self._compute_chroma(audio_trimmed),
            'tempo': self._estimate_tempo(audio_trimmed),
            'onset_frames': self._detect_onsets(audio_trimmed)
        }
        
        self.logger.info("Audio preprocessing completed")
        return features
    
    def _compute_stft(self, audio):
        """Compute Short-Time Fourier Transform."""
        return librosa.stft(
            audio, 
            hop_length=self.hop_length, 
            n_fft=self.n_fft
        )
    
    def _compute_melspectrogram(self, audio):
        """Compute mel-spectrogram."""
        return librosa.feature.melspectrogram(
            y=audio,
            sr=self.sample_rate,
            hop_length=self.hop_length,
            n_fft=self.n_fft,
            n_mels=self.n_mels
        )
    
    def _compute_chroma(self, audio):
        """Compute chromagram for pitch class analysis."""
        return librosa.feature.chroma_stft(
            y=audio,
            sr=self.sample_rate,
            hop_length=self.hop_length,
            n_fft=self.n_fft
        )
    
    def _estimate_tempo(self, audio):
        """Estimate tempo of the audio."""
        tempo, _ = librosa.beat.beat_track(
            y=audio,
            sr=self.sample_rate,
            hop_length=self.hop_length
        )
        return tempo
    
    def _detect_onsets(self, audio):
        """Detect onset frames in the audio."""
        return librosa.onset.onset_detect(
            y=audio,
            sr=self.sample_rate,
            hop_length=self.hop_length,
            units='frames'
        )
    
    def extract_guitar_features(self, audio_data):
        """
        Extract guitar-specific features for tablature generation.
        
        Args:
            audio_data (np.ndarray): Audio data
            
        Returns:
            dict: Guitar-specific features
        """
        self.logger.info("Extracting guitar-specific features...")
        
        features = {}
        
        # Harmonic-percussive separation
        harmonic, percussive = librosa.effects.hpss(audio_data)
        features['harmonic'] = harmonic
        features['percussive'] = percussive
        
        # Pitch tracking
        pitches, magnitudes = librosa.piptrack(
            y=harmonic,
            sr=self.sample_rate,
            hop_length=self.hop_length,
            fmin=80,  # Low E string fundamental
            fmax=1000  # High guitar frequencies
        )
        features['pitches'] = pitches
        features['magnitudes'] = magnitudes
        
        # Spectral features for timbre analysis
        features['spectral_centroid'] = librosa.feature.spectral_centroid(
            y=audio_data, sr=self.sample_rate
        )
        features['spectral_rolloff'] = librosa.feature.spectral_rolloff(
            y=audio_data, sr=self.sample_rate
        )
        features['zero_crossing_rate'] = librosa.feature.zero_crossing_rate(
            audio_data
        )
        
        # MFCC for timbral characteristics
        features['mfcc'] = librosa.feature.mfcc(
            y=audio_data,
            sr=self.sample_rate,
            n_mfcc=13
        )
        
        return features
    
    def apply_guitar_effects_modeling(self, audio_data, effect_type="clean"):
        """
        Apply guitar effects modeling to better match training data.
        
        Args:
            audio_data (np.ndarray): Input audio
            effect_type (str): Type of guitar effect to model
            
        Returns:
            np.ndarray: Processed audio
        """
        # This would include modeling of common guitar effects
        # like distortion, compression, EQ, etc.
        # For now, return the original audio
        return audio_data
