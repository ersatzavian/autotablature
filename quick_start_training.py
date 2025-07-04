#!/usr/bin/env python3
"""
Quick start script for AutoTablature model training.

This script helps users quickly set up and start training models
for the AutoTablature system.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'torch', 'librosa', 'numpy', 'guitarpro'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install missing packages with:")
        print("   pip install -r requirements.txt")
        return False
    
    print("✅ All required dependencies are installed")
    return True

def check_gpu():
    """Check if GPU is available for training."""
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            print(f"✅ GPU available: {gpu_name}")
            return True
        else:
            print("⚠️  No GPU detected - training will use CPU (slower)")
            return False
    except ImportError:
        print("⚠️  Cannot check GPU - PyTorch not installed")
        return False

def setup_data_directory(data_dir):
    """Set up the data directory structure."""
    data_path = Path(data_dir)
    
    # Create directory structure
    directories = [
        'gp',
        'audio', 
        'annotations',
        'training/audio',
        'training/annotations',
        'separated',
        'output'
    ]
    
    for dir_name in directories:
        dir_path = data_path / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
    
    print(f"✅ Created data directory structure at: {data_path.absolute()}")
    return str(data_path.absolute())

def collect_training_data(gp_dir, audio_dir, output_dir):
    """Run the data collection process."""
    print("\n🔄 Collecting and organizing training data...")
    
    cmd = [
        'python', '-m', 'src.utils.data_collector',
        '--all',
        '--output', output_dir
    ]
    
    if gp_dir:
        cmd.extend(['--gp-dir', gp_dir])
    
    if audio_dir:
        cmd.extend(['--audio-dir', audio_dir])
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Data collection completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Data collection failed: {e}")
        print("Error output:", e.stderr)
        return False

def start_training(data_dir, model_type, epochs, batch_size, learning_rate):
    """Start the model training process."""
    print(f"\n🚀 Starting training for {model_type} model(s)...")
    
    training_data = os.path.join(data_dir, 'training')
    
    if not os.path.exists(training_data) or not os.listdir(training_data):
        print("❌ No training data found. Please collect data first.")
        return False
    
    cmd = [
        'python', 'examples/train_models.py',
        '--data-path', training_data,
        '--model-type', model_type,
        '--epochs', str(epochs),
        '--batch-size', str(batch_size),
        '--learning-rate', str(learning_rate)
    ]
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        # Run training in real-time so user can see progress
        process = subprocess.Popen(cmd)
        process.wait()
        
        if process.returncode == 0:
            print("✅ Training completed successfully!")
            return True
        else:
            print("❌ Training failed")
            return False
            
    except KeyboardInterrupt:
        print("\n⚠️  Training interrupted by user")
        return False
    except Exception as e:
        print(f"❌ Training failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Quick start script for AutoTablature model training",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic training with sample data
  python quick_start_training.py --data-dir data

  # Training with custom data directories
  python quick_start_training.py \\
      --data-dir data \\
      --gp-dir /path/to/guitar_pro_files \\
      --audio-dir /path/to/audio_files

  # Train only pitch detection model
  python quick_start_training.py \\
      --data-dir data \\
      --model-type pitch \\
      --epochs 50
        """
    )
    
    # Data arguments
    parser.add_argument('--data-dir', default='data', 
                       help='Directory to store training data (default: data)')
    parser.add_argument('--gp-dir', 
                       help='Directory containing Guitar Pro files')
    parser.add_argument('--audio-dir', 
                       help='Directory containing audio files')
    
    # Training arguments
    parser.add_argument('--model-type', default='all',
                       choices=['pitch', 'rhythm', 'separation', 'all'],
                       help='Type of model to train (default: all)')
    parser.add_argument('--epochs', type=int, default=50,
                       help='Number of training epochs (default: 50)')
    parser.add_argument('--batch-size', type=int, default=32,
                       help='Training batch size (default: 32)')
    parser.add_argument('--learning-rate', type=float, default=0.001,
                       help='Learning rate (default: 0.001)')
    
    # Action arguments
    parser.add_argument('--skip-data-collection', action='store_true',
                       help='Skip data collection step')
    parser.add_argument('--skip-training', action='store_true',
                       help='Skip training step (only collect data)')
    parser.add_argument('--check-only', action='store_true',
                       help='Only check system requirements')
    
    args = parser.parse_args()
    
    print("🎸 AutoTablature Model Training Quick Start")
    print("=" * 50)
    
    # Check system requirements
    print("\n📋 Checking system requirements...")
    if not check_dependencies():
        return 1
    
    gpu_available = check_gpu()
    
    if args.check_only:
        print("\n✅ System check completed")
        return 0
    
    # Set up data directory
    print(f"\n📁 Setting up data directory...")
    data_dir = setup_data_directory(args.data_dir)
    
    # Collect training data
    if not args.skip_data_collection:
        if args.gp_dir or args.audio_dir:
            if not collect_training_data(args.gp_dir, args.audio_dir, data_dir):
                return 1
        else:
            print("\n⚠️  No data directories specified.")
            print("💡 Add --gp-dir and --audio-dir to collect training data")
            print("   Or place your files manually in:")
            print(f"   - Guitar Pro files: {data_dir}/gp/")
            print(f"   - Audio files: {data_dir}/audio/")
    
    # Start training
    if not args.skip_training:
        # Adjust batch size for CPU training
        batch_size = args.batch_size
        if not gpu_available and batch_size > 16:
            batch_size = 16
            print(f"⚠️  Reduced batch size to {batch_size} for CPU training")
        
        if not start_training(data_dir, args.model_type, args.epochs, 
                            batch_size, args.learning_rate):
            return 1
    
    print("\n🎉 Quick start completed successfully!")
    print(f"\nNext steps:")
    print(f"- Check training logs in: logs/")
    print(f"- Trained models saved to: models/")
    print(f"- Test your models with: python examples/audio_to_tab.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
