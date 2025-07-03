"""
Basic test script for AutoTablature.

This script demonstrates the basic functionality of the AutoTablature system.
"""

import os
import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.autotablature import AutoTablature


def main():
    """Run the test script."""
    parser = argparse.ArgumentParser(description='AutoTablature Test Script')
    parser.add_argument('-i', '--input', required=True, help='Path to input audio file')
    parser.add_argument('-o', '--output', help='Path to output tablature file')
    parser.add_argument('-c', '--config', help='Path to configuration file')
    
    args = parser.parse_args()
    
    print("AutoTablature Test Script")
    print("------------------------")
    print(f"Input file: {args.input}")
    print(f"Output file: {args.output or 'None specified'}")
    print(f"Config file: {args.config or 'Using default'}")
    print("")
    
    # Check if input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file {args.input} not found")
        return
    
    # Initialize AutoTablature
    print("Initializing AutoTablature...")
    at = AutoTablature(args.config)
    
    # Process audio
    print("Processing audio...")
    try:
        tablature = at.process_audio(args.input, args.output)
        
        # Print summary
        print("\nTablature generation complete!")
        print(f"Number of tracks: {len(tablature.tracks)}")
        
        for i, track in enumerate(tablature.tracks):
            print(f"\nTrack {i+1}: {track.instrument}")
            print(f"Tuning: {track.tuning}")
            print(f"Measures: {len(track.measures)}")
            
            # Print some notes from the first measure
            if track.measures:
                first_measure = track.measures[0]
                print(f"First measure notes: {len(first_measure.notes)}")
                
                for j, note in enumerate(first_measure.notes[:5]):
                    print(f"  Note {j+1}: String {note.string}, Fret {note.fret}, " 
                          f"Duration {note.duration}, Position {note.beat_position:.2f}")
        
        if args.output:
            print(f"\nOutput saved to: {args.output}")
        
    except Exception as e:
        print(f"Error processing audio: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
