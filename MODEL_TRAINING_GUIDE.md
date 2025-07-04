# AutoTablature Model Training Guide

This comprehensive guide explains how to train the AI models used by the AutoTablature system for guitar tablature generation.

## Overview

The AutoTablature system uses several specialized AI models:

1. **Instrument Separation Model** - Separates different instruments from mixed audio tracks
2. **Pitch Detection Model** - Identifies individual notes and their timing from separated guitar tracks
3. **Rhythm Analysis Model** - Detects tempo, time signatures, and rhythmic patterns

## Prerequisites

### System Requirements
- Python 3.8+ with PyTorch
- CUDA-compatible GPU (recommended, 8GB+ VRAM)
- 16GB+ RAM for processing large audio files
- 100GB+ free disk space for training data and models

### Required Dependencies
Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

Key packages for training:
- `torch` - Deep learning framework
- `librosa` - Audio processing
- `guitarpro` - Guitar Pro file parsing
- `numpy`, `matplotlib` - Data processing and visualization

## Data Collection and Preparation

### Step 1: Organize Your Training Data

The system requires paired Guitar Pro files and corresponding audio recordings. Use the built-in data collector:

```bash
# Collect all data from directories containing Guitar Pro and audio files
python -m src.utils.data_collector --all \
    --output data \
    --gp-dir path/to/guitar_pro_files \
    --audio-dir path/to/audio_files
```

This will:
- Copy and organize your Guitar Pro (.gp5, .gpx, .gp4) files
- Copy and organize audio files (.mp3, .wav, .flac)
- Attempt to match Guitar Pro files with corresponding audio
- Extract annotations from Guitar Pro files
- Prepare the data for training

### Step 2: Directory Structure

After data collection, your directory should look like:
```
data/
├── gp/                     # Guitar Pro files
├── audio/                  # Audio files
├── annotations/            # Extracted Guitar Pro annotations
├── training/               # Prepared training data
│   ├── audio/             # Training audio files
│   └── annotations/       # Training annotation files
├── gp_metadata.json       # Guitar Pro file metadata
├── audio_metadata.json    # Audio file metadata
└── matches.json           # Matched file pairs
```

### Step 3: Data Quality

For best results, ensure:
- **High-quality audio**: 44.1kHz, 16-bit minimum, studio recordings preferred
- **Accurate Guitar Pro files**: Well-timed, correctly notated tablature
- **Good matches**: Audio should closely match the Guitar Pro arrangement
- **Diverse dataset**: Include various genres, playing styles, and guitar tones

## Model Training

### Basic Training Command

Train all models with default settings:
```bash
python examples/train_models.py \
    --data-path data/training \
    --model-type all \
    --epochs 100 \
    --batch-size 32
```

### Training Individual Models

#### 1. Instrument Separation Model
Separates guitar tracks from mixed audio:

```bash
python examples/train_models.py \
    --data-path data/training \
    --model-type separation \
    --epochs 150 \
    --batch-size 16 \
    --learning-rate 0.0001
```

**Data Requirements:**
- Mixed audio tracks with multiple instruments
- Separated instrument tracks (guitar, bass, drums, vocals)
- Audio files should be stereo, 44.1kHz

#### 2. Pitch Detection Model
Identifies individual notes and their timing:

```bash
python examples/train_models.py \
    --data-path data/training \
    --model-type pitch \
    --epochs 200 \
    --batch-size 64 \
    --learning-rate 0.001
```

**Data Requirements:**
- Clean guitar audio (isolated or separated tracks)
- Accurate Guitar Pro annotations with precise timing
- Various playing techniques (single notes, chords, bends, slides)

#### 3. Rhythm Analysis Model
Detects tempo and rhythmic patterns:

```bash
python examples/train_models.py \
    --data-path data/training \
    --model-type rhythm \
    --epochs 100 \
    --batch-size 32 \
    --learning-rate 0.0005
```

**Data Requirements:**
- Audio with clear rhythmic patterns
- Accurate tempo and time signature information
- Various rhythm styles and complexities

### Advanced Training Options

#### Custom Configuration
Create a custom configuration file:

```json
{
  "audio": {
    "sample_rate": 44100,
    "hop_length": 512,
    "n_fft": 2048
  },
  "training": {
    "learning_rate": 0.001,
    "batch_size": 32,
    "epochs": 100,
    "validation_split": 0.2,
    "early_stopping_patience": 20
  },
  "separation": {
    "instruments": ["guitar_lead", "guitar_rhythm", "bass", "drums"]
  },
  "pitch": {
    "n_bins": 360,
    "fmin": 80,
    "fmax": 1000
  }
}
```

Use with training:
```bash
python examples/train_models.py \
    --data-path data/training \
    --config custom_config.json \
    --model-type all
```

#### GPU Training
Force GPU usage (if available):
```bash
python examples/train_models.py \
    --data-path data/training \
    --model-type all \
    --device cuda
```

#### Resume Training
Models automatically save checkpoints. To resume training, the system will load the latest checkpoint automatically.

## Training with Jupyter Notebooks

For interactive training and experimentation, use the provided notebook:

```bash
jupyter notebook notebooks/audio_analysis_training.ipynb
```

This notebook provides:
- Data visualization and analysis
- Step-by-step model training
- Interactive parameter tuning
- Training progress monitoring

## Data Augmentation

To improve model robustness, the training system applies several augmentation techniques:

### Audio Augmentation
- **Pitch shifting**: ±2 semitones to simulate different tunings
- **Time stretching**: ±10% to handle tempo variations
- **Noise addition**: Low-level noise to improve robustness
- **EQ adjustments**: Simulate different recording conditions

### Annotation Augmentation
- **Timing variations**: Small random timing adjustments
- **String/fret alternatives**: Multiple valid fingering positions
- **Technique variations**: Different ways to play the same notes

## Monitoring Training Progress

### Training Logs
Monitor training progress in real-time:
```bash
tail -f logs/autotablature_YYYYMMDD.log
```

### TensorBoard (if available)
View training metrics:
```bash
tensorboard --logdir=models/runs
```

### Model Checkpoints
Best models are automatically saved to:
- `models/separation_model.pth`
- `models/pitch_model.pth`
- `models/rhythm_model.pth`

## Training Tips and Best Practices

### Data Quality
1. **Clean Audio**: Remove background noise and artifacts
2. **Consistent Levels**: Normalize audio levels across your dataset
3. **Accurate Timing**: Ensure Guitar Pro files are precisely timed
4. **Variety**: Include different guitars, effects, and playing styles

### Training Parameters
1. **Start Small**: Begin with a subset of data to test your pipeline
2. **Monitor Overfitting**: Use validation loss to detect overfitting
3. **Learning Rate**: Start with 0.001, adjust based on convergence
4. **Batch Size**: Larger batches (32-64) for stable training

### Hardware Optimization
1. **GPU Memory**: Reduce batch size if you encounter out-of-memory errors
2. **CPU Cores**: Use multiple workers for data loading
3. **Storage**: Use SSD for faster data loading during training

## Troubleshooting Common Issues

### CUDA Out of Memory
```bash
# Reduce batch size
python examples/train_models.py --batch-size 16

# Or force CPU training
python examples/train_models.py --device cpu
```

### Poor Model Performance
1. **Check data quality**: Ensure audio and annotations match well
2. **Increase training data**: More diverse data usually improves performance
3. **Adjust hyperparameters**: Try different learning rates and architectures
4. **Longer training**: Some models need more epochs to converge

### Training Crashes
1. **Check GPU memory**: Monitor with `nvidia-smi`
2. **Validate data**: Ensure all audio files are readable
3. **Check annotations**: Verify JSON annotation files are well-formed

## Custom Model Development

### Adding New Models
To add custom models, create new classes inheriting from `torch.nn.Module`:

```python
# In src/models/custom_model.py
import torch.nn as nn

class CustomModel(nn.Module):
    def __init__(self, input_size, output_size):
        super().__init__()
        # Define your architecture
        
    def forward(self, x):
        # Implement forward pass
        return x
```

### Custom Loss Functions
Implement domain-specific loss functions:

```python
class TablatureLoss(nn.Module):
    def __init__(self):
        super().__init__()
        
    def forward(self, predictions, targets):
        # Custom loss calculation for tablature accuracy
        return loss
```

## Performance Evaluation

### Metrics
The system tracks several metrics during training:
- **Separation**: Signal-to-Distortion Ratio (SDR)
- **Pitch Detection**: F1 score, precision, recall
- **Rhythm**: Tempo accuracy, beat detection F-measure

### Validation
Run validation on held-out test data:
```bash
python scripts/evaluate_models.py \
    --test-data data/test \
    --models models/
```

## Next Steps

After training your models:

1. **Test on new audio**: Try your trained models on previously unseen songs
2. **Fine-tune parameters**: Adjust post-processing parameters for better results
3. **Collect feedback**: Use generated tablature to identify areas for improvement
4. **Iterative improvement**: Collect more training data based on model weaknesses

## Getting Help

- Check the training logs for detailed error messages
- Use the interactive notebook for step-by-step debugging
- Refer to the model architectures in `src/models/` for implementation details
- Review the configuration options in `config.json`

For additional support, refer to the project documentation or raise an issue in the repository.
