# How to Train AutoTablature Models - Quick Answer

This document provides a direct answer to "how to train the models used by this system."

## What Models Need Training?

The AutoTablature system uses 3 main AI models:

1. **Instrument Separation Model** - Separates guitar from other instruments in mixed audio
2. **Pitch Detection Model** - Identifies individual notes and their timing
3. **Rhythm Analysis Model** - Detects tempo and rhythmic patterns

## Prerequisites

- Python 3.8+ with dependencies installed (`pip install -r requirements.txt`)
- Guitar Pro files (.gp5, .gpx, .gp4) paired with corresponding audio files
- GPU recommended but not required

## Training Steps

### 1. Prepare Your Data

Collect Guitar Pro files and matching audio recordings, then organize them:

```bash
# Automatic data collection and organization
python -m src.utils.data_collector --all \
    --output data \
    --gp-dir /path/to/your/guitar_pro_files \
    --audio-dir /path/to/your/audio_files
```

This will:
- Match Guitar Pro files with audio
- Extract annotations from Guitar Pro files 
- Prepare data for training

### 2. Train the Models

```bash
# Train all models
python examples/train_models.py \
    --data-path data/training \
    --model-type all \
    --epochs 100

# Or train individual models
python examples/train_models.py \
    --data-path data/training \
    --model-type pitch \
    --epochs 150
```

### 3. Quick Start Option

Use the quick start script for guided setup:

```bash
# Interactive setup and training
python quick_start_training.py \
    --data-dir data \
    --gp-dir /path/to/guitar_pro_files \
    --audio-dir /path/to/audio_files
```

## Training Data Requirements

- **High-quality audio**: Studio recordings preferred, 44.1kHz minimum
- **Accurate Guitar Pro files**: Well-timed, correctly notated tablature
- **Good matches**: Audio should closely match the Guitar Pro arrangement
- **Quantity**: More data = better results (aim for 100+ song pairs minimum)

## Key Training Parameters

```bash
# Common training options
--epochs 100              # Number of training cycles
--batch-size 32           # Number of samples per batch
--learning-rate 0.001     # How fast the model learns
--model-type all          # Which models to train (all, pitch, rhythm, separation)
```

## Expected Training Time

- **Pitch Detection**: 2-4 hours (100 epochs, GPU)
- **Instrument Separation**: 4-8 hours (100 epochs, GPU)  
- **Rhythm Analysis**: 1-2 hours (100 epochs, GPU)

Times scale with dataset size and hardware.

## Output

Trained models are saved to:
- `models/pitch_model.pth`
- `models/separation_model.pth`
- `models/rhythm_model.pth`

## Testing Your Trained Models

```bash
# Test on new audio file
python examples/audio_to_tab.py \
    --input new_song.mp3 \
    --output generated_tab.gp5
```

## For More Details

See the complete [MODEL_TRAINING_GUIDE.md](MODEL_TRAINING_GUIDE.md) for:
- Detailed configuration options
- Troubleshooting common issues
- Advanced training techniques
- Custom model development
