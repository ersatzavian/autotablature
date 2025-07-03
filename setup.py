"""
Setup script for AutoTablature.
"""

import os
import subprocess
import sys
from pathlib import Path


def check_ffmpeg():
    """Check if FFmpeg is installed."""
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, capture_output=True)
        print("✓ FFmpeg is installed")
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        print("✗ FFmpeg is not installed")
        print("  Please install FFmpeg: https://ffmpeg.org/download.html")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 8):
        print(f"✗ Python {major}.{minor} is not supported")
        print("  AutoTablature requires Python 3.8 or higher")
        return False
    
    print(f"✓ Python {major}.{minor} is compatible")
    return True


def install_requirements():
    """Install Python dependencies."""
    # Try lite requirements first
    lite_requirements_path = os.path.join(os.path.dirname(__file__), "requirements-lite.txt")
    full_requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    
    # Check which requirements file to use
    if os.path.exists(lite_requirements_path):
        requirements_path = lite_requirements_path
        print("Installing lightweight Python dependencies...")
    else:
        requirements_path = full_requirements_path
        print("Installing Python dependencies...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", requirements_path], check=True)
        print("✓ Dependencies installed successfully")
        
        # Try to install additional packages that might fail
        optional_packages = ["tensorflow>=2.13.0", "essentia"]
        for package in optional_packages:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", package], 
                             check=True, capture_output=True)
                print(f"✓ Optional package installed: {package}")
            except subprocess.SubprocessError:
                print(f"⚠ Optional package failed to install: {package}")
        
        return True
    except subprocess.SubprocessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        print("Trying to continue with partial installation...")
        return False


def create_directories():
    """Create necessary directories."""
    directories = [
        "data",
        "data/samples",
        "data/training",
        "data/output",
        "models",
        "logs"
    ]
    
    print("Creating directories...")
    for directory in directories:
        path = os.path.join(os.path.dirname(__file__), directory)
        os.makedirs(path, exist_ok=True)
    
    print("✓ Directories created")
    return True


def setup():
    """Run the setup process."""
    print("AutoTablature Setup")
    print("===================")
    
    # Check requirements
    python_ok = check_python_version()
    ffmpeg_ok = check_ffmpeg()
    
    if not python_ok:
        print("\nSetup failed: Python version not compatible")
        return False
    
    # Create directories
    create_directories()
    
    # Install dependencies
    deps_ok = install_requirements()
    
    # Run environment test
    print("\nTesting environment...")
    try:
        subprocess.run([sys.executable, "test_environment.py"], check=True)
    except subprocess.SubprocessError:
        print("⚠ Environment test had issues, but continuing...")
    
    if not deps_ok:
        print("\nSetup completed with warnings: Some dependencies failed to install")
        print("The basic functionality should still work.")
        return True
    else:
        print("\n✅ Setup completed successfully!")
        print("You can now use AutoTablature!")
        return True
    
    print("\nSetup completed successfully!")
    
    if not ffmpeg_ok:
        print("\nWarning: FFmpeg is not installed, which is required for audio processing.")
        print("Please install FFmpeg manually.")
    
    print("\nGetting Started:")
    print("1. Try the example notebook:")
    print("   jupyter notebook notebooks/audio_analysis_training.ipynb")
    print("\n2. Run the test script:")
    print("   python tests/test_basic.py -i <path_to_audio_file> -o output.json")
    print("\n3. Collect training data:")
    print("   python -m src.utils.data_collector --all -o data -g <path_to_gp_files> -a <path_to_audio_files>")
    
    return True


if __name__ == "__main__":
    setup()
