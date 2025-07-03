#!/usr/bin/env python3
"""
Simple test script to verify the AutoTablature environment is working.
"""

import sys
import importlib
from pathlib import Path

def test_imports():
    """Test that all critical imports are working."""
    print("Testing AutoTablature environment...")
    print(f"Python version: {sys.version}")
    print()
    
    # Core dependencies
    critical_packages = [
        "numpy",
        "scipy", 
        "librosa",
        "soundfile",
        "pandas",
        "matplotlib"
    ]
    
    # Optional but important packages
    optional_packages = [
        "torch",
        "sklearn",
        "music21",
        "mido",
        "pretty_midi",
        "pydub",
        "mutagen",
        "flask",
        "jupyter",
        "pytest",
        "black",
        "flake8"
    ]
    
    # Machine learning packages (may not be available)
    ml_packages = [
        "tensorflow",
        "guitarpro",
        "essentia",
        "madmom"
    ]
    
    def test_package_group(packages, group_name):
        print(f"\n{group_name} packages:")
        failed = []
        for package in packages:
            try:
                importlib.import_module(package)
                print(f"  ✓ {package}")
            except ImportError as e:
                print(f"  ✗ {package} - {e}")
                failed.append(package)
        return failed
    
    # Test all package groups
    critical_failed = test_package_group(critical_packages, "Critical")
    optional_failed = test_package_group(optional_packages, "Optional")
    ml_failed = test_package_group(ml_packages, "ML/Advanced")
    
    # Test AutoTablature modules
    print("\nAutoTablature modules:")
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    autotablature_modules = [
        "src.audio.processor",
        "src.separation.separator", 
        "src.models.pitch_detector",
        "src.models.rhythm_analyzer",
        "src.tablature.generator",
        "src.utils.config",
        "src.utils.logger"
    ]
    
    module_failed = test_package_group(autotablature_modules, "AutoTablature")
    
    # Summary
    print("\n" + "="*50)
    print("ENVIRONMENT TEST SUMMARY")
    print("="*50)
    
    if not critical_failed:
        print("✓ All critical packages are available")
    else:
        print(f"✗ Critical packages missing: {critical_failed}")
    
    if not module_failed:
        print("✓ All AutoTablature modules can be imported")
    else:
        print(f"✗ AutoTablature modules missing: {module_failed}")
    
    if not optional_failed:
        print("✓ All optional packages are available")
    else:
        print(f"⚠ Optional packages missing: {optional_failed}")
    
    if not ml_failed:
        print("✓ All ML packages are available")
    else:
        print(f"⚠ ML packages missing: {ml_failed}")
    
    # Overall status
    if critical_failed or module_failed:
        print("\n❌ Environment setup FAILED - critical components missing")
        return False
    else:
        print("\n✅ Environment setup SUCCESSFUL - ready for development!")
        return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
