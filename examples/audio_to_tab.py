"""
Example script for generating guitar tablature from an audio file.

Usage:
    python examples/audio_to_tab.py --input path/to/audio.mp3 --output path/to/output.gp5

This script demonstrates the full pipeline from audio input to Guitar Pro tablature output.
"""

import argparse
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# Import the AutoTablature system
from src.autotablature import AutoTablature

def main():
    """Run the audio to tablature conversion process."""
    parser = argparse.ArgumentParser(description="Generate guitar tablature from audio.")
    parser.add_argument("--input", "-i", required=True, help="Path to input audio file (MP3, WAV)")
    parser.add_argument("--output", "-o", required=True, help="Path for output tablature file (gp5, gpx, json)")
    parser.add_argument("--config", "-c", help="Path to custom configuration file")
    parser.add_argument("--title", "-t", help="Title for the tablature")
    parser.add_argument("--artist", "-a", help="Artist name for the tablature")
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found.")
        return 1
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Initialize the AutoTablature system
    at = AutoTablature(config_path=args.config)
    
    # Process the audio file
    print(f"Processing audio file: {args.input}")
    tablature = at.process_audio(args.input, args.output)
    
    # Set metadata if provided
    if args.title:
        tablature.title = args.title
    if args.artist:
        tablature.artist = args.artist
    
    # Save the tablature
    print(f"Saving tablature to: {args.output}")
    tablature.save(args.output)
    print("Done!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
