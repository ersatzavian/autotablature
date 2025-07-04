#!/usr/bin/env python3
"""
Example script demonstrating how to train AutoTablature models.

This script shows the complete workflow from data collection to model training,
with practical examples and best practices.
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.utils.config import Config
from src.utils.logger import setup_logger
from src.utils.data_collector import DataCollector
from src.models.trainer import ModelTrainer


def setup_example_data():
    """Set up example data structure for demonstration."""
    logger = logging.getLogger(__name__)
    
    # Create example directory structure
    data_dir = Path("data_example")
    data_dir.mkdir(exist_ok=True)
    
    # Create subdirectories
    for subdir in ["gp", "audio", "training", "output"]:
        (data_dir / subdir).mkdir(exist_ok=True)
    
    logger.info(f"Created example data directory: {data_dir.absolute()}")
    
    # Check if we have sample data
    sample_audio = project_root / "data" / "samples" / "guitar_sample.mp3"
    sample_gp = project_root / "data" / "training" / "gp" / "Manic Street Preachers - Australia.gp4"
    
    if sample_audio.exists():
        logger.info(f"Found sample audio: {sample_audio}")
    else:
        logger.warning("No sample audio found. Place audio files in data_example/audio/")
    
    if sample_gp.exists():
        logger.info(f"Found sample Guitar Pro file: {sample_gp}")
    else:
        logger.warning("No sample Guitar Pro files found. Place .gp files in data_example/gp/")
    
    return str(data_dir)


def demonstrate_data_collection(data_dir, gp_dir=None, audio_dir=None):
    """Demonstrate the data collection process."""
    logger = logging.getLogger(__name__)
    
    logger.info("=== Data Collection Demo ===")
    
    # Initialize data collector
    collector = DataCollector(data_dir, gp_dir, audio_dir)
    
    # Step 1: Collect Guitar Pro files
    if gp_dir and os.path.exists(gp_dir):
        logger.info("Step 1: Collecting Guitar Pro files...")
        collector.collect_gp_files()
    else:
        logger.info("Step 1: No Guitar Pro directory specified or found")
    
    # Step 2: Collect audio files
    if audio_dir and os.path.exists(audio_dir):
        logger.info("Step 2: Collecting audio files...")
        collector.collect_audio_files()
    else:
        logger.info("Step 2: No audio directory specified or found")
    
    # Step 3: Match files
    logger.info("Step 3: Matching Guitar Pro files with audio...")
    collector.match_files()
    
    # Step 4: Extract annotations
    logger.info("Step 4: Extracting annotations from Guitar Pro files...")
    collector.extract_annotations_from_gp()
    
    # Step 5: Prepare training data
    logger.info("Step 5: Preparing training data...")
    collector.prepare_training_data()
    
    logger.info("Data collection completed!")


def demonstrate_model_training(data_dir, model_type="pitch", epochs=10):
    """Demonstrate model training with minimal epochs for testing."""
    logger = logging.getLogger(__name__)
    
    logger.info(f"=== Model Training Demo ({model_type}) ===")
    
    # Load configuration
    config = Config()
    
    # Override training parameters for demonstration
    config.set("training.epochs", epochs)
    config.set("training.batch_size", 16)  # Small batch for demo
    config.set("training.learning_rate", 0.001)
    
    # Initialize trainer
    trainer = ModelTrainer(config)
    
    # Check if training data exists
    training_data_path = os.path.join(data_dir, "training")
    
    if not os.path.exists(training_data_path):
        logger.error(f"Training data not found at: {training_data_path}")
        logger.info("Please run data collection first or place training data manually")
        return False
    
    # Check for audio and annotation files
    audio_files = list(Path(training_data_path).glob("audio/*"))
    annotation_files = list(Path(training_data_path).glob("annotations/*"))
    
    if not audio_files:
        logger.warning("No audio files found in training data")
        return False
    
    if not annotation_files:
        logger.warning("No annotation files found in training data")
        return False
    
    logger.info(f"Found {len(audio_files)} audio files and {len(annotation_files)} annotation files")
    
    try:
        # Train the specified model
        trainer.train(training_data_path, model_type=model_type)
        logger.info(f"Training completed for {model_type} model!")
        return True
        
    except Exception as e:
        logger.error(f"Training failed: {e}")
        return False


def demonstrate_custom_training_config():
    """Demonstrate how to create custom training configurations."""
    logger = logging.getLogger(__name__)
    
    logger.info("=== Custom Training Configuration Demo ===")
    
    # Create custom configuration
    custom_config = {
        "audio": {
            "sample_rate": 44100,
            "hop_length": 512,
            "n_fft": 2048,
            "n_mels": 128
        },
        "training": {
            "learning_rate": 0.0005,
            "batch_size": 32,
            "epochs": 50,
            "validation_split": 0.2,
            "early_stopping_patience": 10
        },
        "pitch": {
            "n_bins": 360,
            "fmin": 82.4,  # Low E string
            "fmax": 1318.5,  # High E string, 24th fret
            "confidence_threshold": 0.3
        },
        "separation": {
            "instruments": [
                "guitar_lead",
                "guitar_rhythm", 
                "bass",
                "drums"
            ]
        }
    }
    
    # Save custom configuration
    config_path = "custom_training_config.json"
    
    import json
    with open(config_path, 'w') as f:
        json.dump(custom_config, f, indent=2)
    
    logger.info(f"Saved custom configuration to: {config_path}")
    
    # Example of how to use it
    logger.info("To use this configuration:")
    logger.info(f"python examples/train_models.py --config {config_path} --data-path data/training")


def demonstrate_evaluation():
    """Demonstrate how to evaluate trained models."""
    logger = logging.getLogger(__name__)
    
    logger.info("=== Model Evaluation Demo ===")
    
    # Check if trained models exist
    models_dir = Path("models")
    
    model_files = {
        "pitch": models_dir / "pitch_model.pth",
        "separation": models_dir / "separation_model.pth",
        "rhythm": models_dir / "rhythm_model.pth"
    }
    
    for model_type, model_path in model_files.items():
        if model_path.exists():
            logger.info(f"✅ Found trained {model_type} model: {model_path}")
        else:
            logger.info(f"❌ No trained {model_type} model found")
    
    logger.info("\nTo evaluate models on test data:")
    logger.info("python scripts/evaluate_models.py --test-data data/test --models models/")
    
    logger.info("\nTo test on a specific audio file:")
    logger.info("python examples/audio_to_tab.py --input song.mp3 --output tablature.gp5")


def main():
    """Main demonstration function."""
    # Setup logging
    logger = setup_logger("training_demo")
    
    logger.info("AutoTablature Model Training Demonstration")
    logger.info("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("src"):
        logger.error("Please run this script from the project root directory")
        return 1
    
    # Setup example data directory
    data_dir = setup_example_data()
    
    # Demonstrate different aspects of training
    try:
        # 1. Data collection
        demonstrate_data_collection(data_dir)
        
        # 2. Custom configuration
        demonstrate_custom_training_config()
        
        # 3. Model training (with minimal epochs for demo)
        logger.info("\n" + "="*50)
        logger.info("NOTE: This demo uses minimal epochs for speed.")
        logger.info("For real training, use 100+ epochs.")
        logger.info("="*50 + "\n")
        
        # Only run training if we have actual data
        training_path = os.path.join(data_dir, "training")
        if os.path.exists(training_path) and os.listdir(training_path):
            demonstrate_model_training(data_dir, model_type="pitch", epochs=5)
        else:
            logger.info("Skipping training demo - no training data available")
            logger.info("Add Guitar Pro files and audio files to see full demo")
        
        # 4. Evaluation
        demonstrate_evaluation()
        
        logger.info("\n" + "="*50)
        logger.info("Training demonstration completed!")
        logger.info("For detailed instructions, see MODEL_TRAINING_GUIDE.md")
        logger.info("="*50)
        
        return 0
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
