"""
Model training script for AutoTablature.

This script demonstrates how to train custom models for various
components of the AutoTablature system.
"""

import argparse
import os
import logging
from pathlib import Path

from src.models.trainer import ModelTrainer
from src.utils.config import Config
from src.utils.logger import setup_logger


def main():
    """Run the model training script."""
    parser = argparse.ArgumentParser(description="Train custom models for AutoTablature")
    parser.add_argument("--data-path", required=True, help="Path to training data directory")
    parser.add_argument("--model-type", default="all", choices=["pitch", "rhythm", "separation", "all"], 
                        help="Type of model to train")
    parser.add_argument("--config", help="Path to custom configuration file")
    parser.add_argument("--output-dir", default="models", help="Directory to save trained models")
    parser.add_argument("--epochs", type=int, default=None, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=None, help="Training batch size")
    parser.add_argument("--learning-rate", type=float, default=None, help="Learning rate")
    parser.add_argument("--device", default=None, choices=["cpu", "cuda"], help="Training device (cpu or cuda)")
    
    args = parser.parse_args()
    
    # Setup logger
    logger = setup_logger("model_training")
    
    # Load configuration
    config = Config(args.config)
    
    # Override config with command line arguments if provided
    if args.epochs:
        config.set("training.epochs", args.epochs)
    if args.batch_size:
        config.set("training.batch_size", args.batch_size)
    if args.learning_rate:
        config.set("training.learning_rate", args.learning_rate)
    if args.device:
        config.set("training.device", args.device)
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Initialize trainer
    trainer = ModelTrainer(config)
    
    # Set output directory
    trainer.set_output_dir(args.output_dir)
    
    # Train models
    logger.info(f"Starting training for model type: {args.model_type}")
    
    try:
        trainer.train(args.data_path, args.model_type)
        logger.info("Training completed successfully")
    except Exception as e:
        logger.error(f"Training failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
