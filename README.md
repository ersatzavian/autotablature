# AutoTablature - AI-Powered Guitar Tablature Generation

An advanced AI system that analyzes MP3 files and automatically generates guitar tablature in Guitar Pro format, with intelligent instrument separation and multi-track output.

## Features

- **Audio Analysis**: Advanced audio processing using librosa and essentia
- **Instrument Separation**: ML-powered source separation for multi-instrument tracks
- **Pitch Detection**: High-accuracy pitch and note detection algorithms
- **Rhythm Analysis**: Automatic tempo and rhythm pattern recognition
- **Multi-Track Output**: Separate tablature tracks for each identified instrument
- **Guitar Pro Format**: Native support for .gp5/.gpx file generation
- **Custom Model Training**: Infrastructure for training on your own Guitar Pro + audio datasets

## Architecture

```
AutoTablature/
├── src/
│   ├── audio/          # Audio processing and analysis
│   ├── models/         # ML models and training
│   ├── separation/     # Instrument separation
│   ├── tablature/      # Tablature generation
│   └── utils/          # Utility functions
├── data/               # Training data and datasets
├── models/             # Trained model files
├── notebooks/          # Jupyter notebooks for experimentation
└── tests/              # Unit tests
```

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Basic Usage**:
   ```python
   from src.autotablature import AutoTablature
   
   # Initialize the system
   at = AutoTablature()
   
   # Process an MP3 file
   tablature = at.process_audio("path/to/song.mp3")
   
   # Save as Guitar Pro format
   tablature.save("output.gp5")
   ```

3. **Command Line Usage**:
   ```bash
   # Process an audio file and generate tablature
   python examples/audio_to_tab.py --input song.mp3 --output tablature.gp5 --title "My Song" --artist "My Band"
   ```

4. **Data Collection and Training**:
   ```bash
   # Collect data from Guitar Pro and audio files
   python -m src.utils.data_collector --gp-dir path/to/gp/files --audio-dir path/to/audio/files --output data --all
   
   # Train custom models
   python -m src.autotablature train_custom_model --data-path data/training --model-type all
   ```

## Example Notebooks

- [Audio to Tablature Demo](notebooks/audio_to_tablature_demo.ipynb): Complete pipeline demonstration
- [Audio Analysis Training](notebooks/audio_analysis_training.ipynb): Model training and evaluation

3. **Train Custom Model**:
   ```python
   from src.models.trainer import ModelTrainer
   
   trainer = ModelTrainer()
   trainer.train_from_dataset("data/training/")
   ```

## Data Collection

The system supports training on your own datasets:
- **Guitar Pro Files**: Place .gp5/.gpx files in `data/guitar_pro/`
- **Audio Files**: Corresponding audio files in `data/audio/`
- **Automatic Matching**: Built-in tools to match GP files with Spotify/YouTube audio

## Model Training

The system includes several specialized models:
- **Source Separation Model**: Separates instruments from mixed audio
- **Pitch Detection Model**: Identifies individual notes and their timing
- **Rhythm Analysis Model**: Detects tempo, time signatures, and rhythmic patterns
- **Tablature Generation Model**: Converts detected notes to guitar tablature

## Output Formats

- **Guitar Pro (.gp5, .gpx)**: Native Guitar Pro format support
- **AlphaTab Integration**: Web-based tablature display
- **MIDI Export**: Standard MIDI file output
- **JSON Format**: Structured data for custom applications

## Requirements

- Python 3.8+
- CUDA-compatible GPU (recommended for model training)
- 8GB+ RAM for audio processing
- FFmpeg for audio format support

## License

MIT License - See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Roadmap

- [ ] Real-time audio processing
- [ ] Bass and drum tablature support
- [ ] Advanced chord recognition
- [ ] Integration with popular DAWs
- [ ] Mobile app development

## Development with DevContainer

This project includes a DevContainer configuration for Visual Studio Code, which provides a consistent development environment with all dependencies pre-installed.

### Prerequisites

- [Visual Studio Code](https://code.visualstudio.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [VS Code Remote - Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

### Getting Started with DevContainer

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/AutoTablature.git
   cd AutoTablature
   ```

2. **Open in VS Code**:
   ```bash
   code .
   ```

3. **Launch DevContainer**:
   When VS Code opens, it will detect the DevContainer configuration. Click on "Reopen in Container" in the notification or press F1 and select "Remote-Containers: Reopen in Container".

4. **Wait for Container Setup**:
   The first build may take several minutes as it installs all dependencies. Subsequent loads will be much faster.

5. **Start Developing**:
   Once the container is ready, you can run tasks, launch Jupyter notebooks, and develop as normal.

### Features of the DevContainer

- Python 3.11 with all dependencies installed
- GPU support (if available on the host)
- Jupyter notebook server
- Pre-configured VS Code settings and extensions
- Persistent volumes for data and models

### Troubleshooting DevContainer Issues

If you encounter issues with the DevContainer:

1. **Package Installation Failures**: Some advanced ML packages (like `tensorflow` or `essentia`) may fail to install. The container is configured to continue with basic functionality.

2. **Guitar Pro Support**: If `PyGuitarPro` package installation fails, the system will fall back to JSON output format.

3. **Building Issues**: 
   - Try rebuilding the container: `Ctrl+Shift+P` → "Remote-Containers: Rebuild Container"
   - Clear Docker cache: `docker system prune`
   - Check Docker Desktop has enough resources allocated

4. **Testing Installation**: Run `python test_environment.py` inside the container to verify what packages are available.
