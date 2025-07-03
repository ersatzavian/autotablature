"""
Data collection tool for AutoTablature.

This script helps collect and organize training data by matching Guitar Pro files
with corresponding audio from YouTube or Spotify.
"""

import os
import sys
import argparse
import json
import glob
from pathlib import Path
import shutil
from typing import Dict, List, Optional
import re
import guitarpro
import numpy as np

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.utils.logger import setup_logger


class DataCollector:
    """Collect and organize training data for AutoTablature."""
    
    def __init__(self, output_dir: str, gp_dir: str = None, audio_dir: str = None):
        """Initialize the data collector."""
        self.logger = setup_logger(__name__)
        
        self.output_dir = os.path.abspath(output_dir)
        self.gp_dir = os.path.abspath(gp_dir) if gp_dir else None
        self.audio_dir = os.path.abspath(audio_dir) if audio_dir else None
        
        # Create output directory structure
        self._create_directories()
        
        self.logger.info(f"Data collector initialized with output directory: {self.output_dir}")
    
    def _create_directories(self):
        """Create the necessary directory structure."""
        # Main directories
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "gp"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "audio"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "separated"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "annotations"), exist_ok=True)
        
        # Training data organization
        os.makedirs(os.path.join(self.output_dir, "training", "mixed"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "training", "separated"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "training", "audio"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "training", "annotations"), exist_ok=True)
        
        self.logger.info("Created directory structure")
    
    def collect_gp_files(self):
        """Collect Guitar Pro files from the source directory."""
        if not self.gp_dir or not os.path.exists(self.gp_dir):
            self.logger.error(f"Guitar Pro directory not found: {self.gp_dir}")
            return
        
        self.logger.info(f"Collecting Guitar Pro files from {self.gp_dir}")
        
        # Find all GP files
        gp_files = []
        for ext in [".gp3", ".gp4", ".gp5", ".gpx", ".gp"]:
            gp_files.extend(glob.glob(os.path.join(self.gp_dir, f"**/*{ext}"), recursive=True))
        
        self.logger.info(f"Found {len(gp_files)} Guitar Pro files")
        
        # Copy files to output directory
        target_dir = os.path.join(self.output_dir, "gp")
        
        for gp_file in gp_files:
            filename = os.path.basename(gp_file)
            target_path = os.path.join(target_dir, filename)
            
            if not os.path.exists(target_path):
                shutil.copy2(gp_file, target_path)
                self.logger.debug(f"Copied {filename}")
        
        self.logger.info(f"Collected Guitar Pro files to {target_dir}")
        
        # Create metadata
        self._create_gp_metadata(target_dir)
    
    def _create_gp_metadata(self, gp_dir):
        """Create metadata for the collected Guitar Pro files."""
        metadata = []
        
        for gp_file in glob.glob(os.path.join(gp_dir, "*.*")):
            filename = os.path.basename(gp_file)
            name, ext = os.path.splitext(filename)
            
            # Parse artist and title from filename
            artist, title = self._parse_filename(name)
            
            metadata.append({
                "filename": filename,
                "path": gp_file,
                "artist": artist,
                "title": title,
                "matched_audio": None
            })
        
        # Save metadata
        metadata_path = os.path.join(self.output_dir, "gp_metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        
        self.logger.info(f"Created metadata for {len(metadata)} files: {metadata_path}")
    
    def _parse_filename(self, name):
        """Parse artist and title from filename."""
        # Try to separate artist and title
        # Common patterns: "Artist - Title", "Artist_Title", "Artist-Title"
        patterns = [
            r"(.+)\s+-\s+(.+)",  # Artist - Title
            r"(.+)_(.+)",        # Artist_Title
            r"(.+)-(.+)"         # Artist-Title
        ]
        
        for pattern in patterns:
            match = re.match(pattern, name)
            if match:
                return match.group(1).strip(), match.group(2).strip()
        
        # If no pattern matches, return the whole name as title
        return None, name
    
    def collect_audio_files(self):
        """Collect audio files from the source directory."""
        if not self.audio_dir or not os.path.exists(self.audio_dir):
            self.logger.error(f"Audio directory not found: {self.audio_dir}")
            return
        
        self.logger.info(f"Collecting audio files from {self.audio_dir}")
        
        # Find all audio files
        audio_files = []
        for ext in [".mp3", ".wav", ".flac", ".ogg", ".m4a"]:
            audio_files.extend(glob.glob(os.path.join(self.audio_dir, f"**/*{ext}"), recursive=True))
        
        self.logger.info(f"Found {len(audio_files)} audio files")
        
        # Copy files to output directory
        target_dir = os.path.join(self.output_dir, "audio")
        
        for audio_file in audio_files:
            filename = os.path.basename(audio_file)
            target_path = os.path.join(target_dir, filename)
            
            if not os.path.exists(target_path):
                shutil.copy2(audio_file, target_path)
                self.logger.debug(f"Copied {filename}")
        
        self.logger.info(f"Collected audio files to {target_dir}")
        
        # Create metadata
        self._create_audio_metadata(target_dir)
    
    def _create_audio_metadata(self, audio_dir):
        """Create metadata for the collected audio files."""
        metadata = []
        
        for audio_file in glob.glob(os.path.join(audio_dir, "*.*")):
            filename = os.path.basename(audio_file)
            name, ext = os.path.splitext(filename)
            
            # Parse artist and title from filename
            artist, title = self._parse_filename(name)
            
            metadata.append({
                "filename": filename,
                "path": audio_file,
                "artist": artist,
                "title": title,
                "matched_gp": None
            })
        
        # Save metadata
        metadata_path = os.path.join(self.output_dir, "audio_metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        
        self.logger.info(f"Created metadata for {len(metadata)} files: {metadata_path}")
    
    def match_files(self):
        """Match Guitar Pro files with audio files."""
        self.logger.info("Matching Guitar Pro files with audio files")
        
        # Load metadata
        gp_metadata_path = os.path.join(self.output_dir, "gp_metadata.json")
        audio_metadata_path = os.path.join(self.output_dir, "audio_metadata.json")
        
        if not os.path.exists(gp_metadata_path) or not os.path.exists(audio_metadata_path):
            self.logger.error("Metadata files not found, run collection first")
            return
        
        with open(gp_metadata_path, "r") as f:
            gp_metadata = json.load(f)
        
        with open(audio_metadata_path, "r") as f:
            audio_metadata = json.load(f)
        
        # Match by artist and title
        matches = []
        
        for gp_item in gp_metadata:
            gp_artist = gp_item.get("artist", "").lower() if gp_item.get("artist") else ""
            gp_title = gp_item.get("title", "").lower()
            
            best_match = None
            best_score = 0
            
            for audio_item in audio_metadata:
                audio_artist = audio_item.get("artist", "").lower() if audio_item.get("artist") else ""
                audio_title = audio_item.get("title", "").lower()
                
                # Calculate match score
                score = 0
                
                # Title match is more important
                if gp_title in audio_title or audio_title in gp_title:
                    score += 2
                elif self._levenshtein_ratio(gp_title, audio_title) > 0.8:
                    score += 1
                
                # Artist match if available
                if gp_artist and audio_artist and (gp_artist in audio_artist or audio_artist in gp_artist):
                    score += 1
                
                if score > best_score:
                    best_score = score
                    best_match = audio_item
            
            if best_match and best_score >= 2:  # Minimum score threshold
                matches.append({
                    "gp_file": gp_item["filename"],
                    "audio_file": best_match["filename"],
                    "score": best_score,
                    "artist": gp_item.get("artist") or best_match.get("artist"),
                    "title": gp_item.get("title") or best_match.get("title")
                })
                
                # Update metadata
                gp_item["matched_audio"] = best_match["filename"]
                best_match["matched_gp"] = gp_item["filename"]
        
        self.logger.info(f"Found {len(matches)} matches")
        
        # Save matches
        matches_path = os.path.join(self.output_dir, "matches.json")
        with open(matches_path, "w") as f:
            json.dump(matches, f, indent=2)
        
        # Update metadata files
        with open(gp_metadata_path, "w") as f:
            json.dump(gp_metadata, f, indent=2)
        
        with open(audio_metadata_path, "w") as f:
            json.dump(audio_metadata, f, indent=2)
        
        self.logger.info(f"Saved matches to {matches_path}")
    
    def _levenshtein_ratio(self, s1, s2):
        """Calculate similarity ratio between two strings."""
        # Based on Levenshtein distance
        # Higher ratio means more similar
        
        if not s1 or not s2:
            return 0
        
        # Remove common words that don't help with matching
        stop_words = ["the", "a", "an", "and", "of", "in", "on", "at", "to", "for"]
        
        for word in stop_words:
            s1 = re.sub(r'\b' + word + r'\b', '', s1)
            s2 = re.sub(r'\b' + word + r'\b', '', s2)
        
        s1 = re.sub(r'\s+', ' ', s1).strip()
        s2 = re.sub(r'\s+', ' ', s2).strip()
        
        # Simple implementation of Levenshtein ratio
        import difflib
        return difflib.SequenceMatcher(None, s1, s2).ratio()
    
    def download_from_youtube(self, query, output_filename=None):
        """Download audio from YouTube."""
        try:
            import yt_dlp
        except ImportError:
            self.logger.error("yt_dlp not installed. Install with: pip install yt-dlp")
            return None
        
        self.logger.info(f"Searching YouTube for: {query}")
        
        # Set output directory
        audio_dir = os.path.join(self.output_dir, "audio")
        
        if not output_filename:
            # Sanitize query for filename
            output_filename = re.sub(r'[^\w\s-]', '', query)
            output_filename = re.sub(r'[-\s]+', '_', output_filename)
            output_filename += ".mp3"
        
        output_path = os.path.join(audio_dir, output_filename)
        
        # Setup options
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': output_path.replace(".mp3", ""),
            'quiet': True,
            'no_warnings': True
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch:{query}", download=True)
                entries = info.get('entries', [])
                
                if not entries:
                    self.logger.error(f"No results found for: {query}")
                    return None
                
                video_id = entries[0].get('id', None)
                title = entries[0].get('title', None)
                
                self.logger.info(f"Downloaded: {title} (ID: {video_id})")
                
                # Return the downloaded file path
                return output_path
                
        except Exception as e:
            self.logger.error(f"Error downloading from YouTube: {e}")
            return None
    
    def download_missing_audio(self):
        """Download missing audio for matched Guitar Pro files."""
        self.logger.info("Checking for missing audio files")
        
        # Load matches
        matches_path = os.path.join(self.output_dir, "matches.json")
        
        if not os.path.exists(matches_path):
            self.logger.error("Matches file not found, run matching first")
            return
        
        with open(matches_path, "r") as f:
            matches = json.load(f)
        
        # Load Guitar Pro metadata
        gp_metadata_path = os.path.join(self.output_dir, "gp_metadata.json")
        
        with open(gp_metadata_path, "r") as f:
            gp_metadata = json.load(f)
        
        # Find Guitar Pro files without matched audio
        missing_audio = []
        
        for gp_item in gp_metadata:
            if not gp_item.get("matched_audio"):
                missing_audio.append(gp_item)
        
        self.logger.info(f"Found {len(missing_audio)} Guitar Pro files without matched audio")
        
        # Ask user if they want to download from YouTube
        print(f"\nFound {len(missing_audio)} Guitar Pro files without matched audio.")
        response = input("Do you want to download the missing audio from YouTube? (y/n): ")
        
        if response.lower() != 'y':
            self.logger.info("Download canceled by user")
            return
        
        # Download missing audio
        for i, gp_item in enumerate(missing_audio):
            artist = gp_item.get("artist", "")
            title = gp_item.get("title", "")
            
            query = f"{artist} {title}" if artist else title
            output_filename = f"{artist} - {title}.mp3" if artist else f"{title}.mp3"
            
            print(f"\n[{i+1}/{len(missing_audio)}] Downloading: {query}")
            
            # Ask for confirmation
            response = input(f"Download this track? (y/n/q): ")
            
            if response.lower() == 'q':
                self.logger.info("Download canceled by user")
                break
            
            if response.lower() != 'y':
                self.logger.info(f"Skipped: {query}")
                continue
            
            # Download from YouTube
            output_path = self.download_from_youtube(query, output_filename)
            
            if output_path:
                # Update metadata
                gp_item["matched_audio"] = os.path.basename(output_path)
                
                # Add to matches
                matches.append({
                    "gp_file": gp_item["filename"],
                    "audio_file": os.path.basename(output_path),
                    "score": 3,  # Manual download
                    "artist": artist,
                    "title": title
                })
                
                # Create audio metadata entry
                audio_metadata_path = os.path.join(self.output_dir, "audio_metadata.json")
                
                with open(audio_metadata_path, "r") as f:
                    audio_metadata = json.load(f)
                
                audio_metadata.append({
                    "filename": os.path.basename(output_path),
                    "path": output_path,
                    "artist": artist,
                    "title": title,
                    "matched_gp": gp_item["filename"]
                })
                
                with open(audio_metadata_path, "w") as f:
                    json.dump(audio_metadata, f, indent=2)
        
        # Save updated matches and metadata
        with open(matches_path, "w") as f:
            json.dump(matches, f, indent=2)
        
        with open(gp_metadata_path, "w") as f:
            json.dump(gp_metadata, f, indent=2)
        
        self.logger.info("Updated matches and metadata")
    
    def extract_annotations_from_gp(self):
        """Extract annotations from Guitar Pro files."""
        self.logger.info("Extracting annotations from Guitar Pro files")
        
        # Check if GP files exist
        gp_dir = os.path.join(self.output_dir, "gp")
        if not os.path.exists(gp_dir) or not any(os.listdir(gp_dir)):
            self.logger.error("No Guitar Pro files found, run collection first")
            return
        
        # Process each GP file
        annotation_dir = os.path.join(self.output_dir, "annotations")
        os.makedirs(annotation_dir, exist_ok=True)
        
        gp_files = []
        for ext in [".gp3", ".gp4", ".gp5", ".gpx", ".gp"]:
            gp_files.extend(glob.glob(os.path.join(gp_dir, f"*{ext}")))
        
        for gp_file in gp_files:
            filename = os.path.basename(gp_file)
            name, _ = os.path.splitext(filename)
            
            self.logger.info(f"Processing Guitar Pro file: {filename}")
            
            try:
                # Parse the Guitar Pro file
                annotations = self._parse_gp_file(gp_file)
                
                # Save annotations
                annotation_path = os.path.join(annotation_dir, f"{name}.json")
                with open(annotation_path, "w") as f:
                    json.dump(annotations, f, indent=2)
                
                self.logger.info(f"Saved annotations to {annotation_path}")
                
            except Exception as e:
                self.logger.error(f"Error processing {filename}: {e}")
    
    def _parse_gp_file(self, gp_file_path):
        """
        Parse a Guitar Pro file and extract note annotations.
        
        Returns:
            dict: Dictionary containing track annotations
        """
        # Load the Guitar Pro file
        try:
            gp_song = guitarpro.parse(gp_file_path)
        except Exception as e:
            self.logger.error(f"Error parsing Guitar Pro file {gp_file_path}: {e}")
            raise
        
        # Extract song information
        song_info = {
            "title": gp_song.title,
            "artist": gp_song.artist,
            "album": gp_song.album,
            "tempo": gp_song.tempo,
        }
        
        # Extract track information
        tracks = []
        
        for track_idx, track in enumerate(gp_song.tracks):
            # Skip drum tracks for tablature
            if track.isPercussionTrack:
                continue
            
            track_info = {
                "name": track.name,
                "instrument": track.channel.instrument,
                "is_percussion": track.isPercussionTrack,
                "string_tuning": [string.value for string in track.strings],
                "measures": []
            }
            
            # Current position in time (quarter notes)
            position = 0.0
            
            # Process each measure
            for measure_idx, measure in enumerate(track.measures):
                measure_info = {
                    "time_signature": [
                        measure.timeSignature.numerator,
                        measure.timeSignature.denominator.value
                    ],
                    "start_time": position,
                    "notes": []
                }
                
                # Calculate measure duration
                measure_duration = (measure.timeSignature.numerator * 4.0 / 
                                   measure.timeSignature.denominator.value)
                
                # Process each voice in the measure
                for voice in measure.voices:
                    beat_position = position
                    
                    # Process each beat in the voice
                    for beat in voice.beats:
                        # Get beat duration in quarter notes
                        duration = 4.0 / beat.duration.value
                        if beat.duration.isDotted:
                            duration *= 1.5
                        if beat.duration.tuplet.enters != beat.duration.tuplet.times:
                            duration *= beat.duration.tuplet.times / beat.duration.tuplet.enters
                        
                        # Process each note in the beat
                        for note in beat.notes:
                            note_info = {
                                "string": note.string,
                                "fret": note.value,
                                "time": beat_position,
                                "duration": duration,
                                "tie_origin": note.type == guitarpro.models.NoteType.tie,
                                "effects": self._extract_note_effects(note)
                            }
                            
                            measure_info["notes"].append(note_info)
                        
                        # Update position
                        beat_position += duration
                
                track_info["measures"].append(measure_info)
                
                # Update position for next measure
                position += measure_duration
            
            tracks.append(track_info)
        
        # Combine everything into final annotations
        annotations = {
            "song_info": song_info,
            "tracks": tracks,
            "total_duration": position  # Total song duration in quarter notes
        }
        
        return annotations
    
    def _extract_note_effects(self, note):
        """Extract effects applied to a note."""
        effects = {}
        
        if note.effect:
            if note.effect.bend:
                effects["bend"] = True
            if note.effect.hammer:
                effects["hammer"] = True
            if note.effect.letRing:
                effects["let_ring"] = True
            if note.effect.palmMute:
                effects["palm_mute"] = True
            if note.effect.slides:
                effects["slide"] = True
            if note.effect.vibrato:
                effects["vibrato"] = True
            if note.effect.tremoloPicking:
                effects["tremolo"] = True
        
        return effects
    
    def prepare_training_data(self):
        """Prepare training data from matched files."""
        self.logger.info("Preparing training data")
        
        # Check if matched files exist
        matches_path = os.path.join(self.output_dir, "matches.json")
        if not os.path.exists(matches_path):
            self.logger.error("No matched files found, run matching first")
            return
        
        # Load matches
        with open(matches_path, "r") as f:
            matches = json.load(f)
        
        # Prepare training data for each match
        for match in matches:
            try:
                gp_path = match["gp_path"]
                audio_path = match["audio_path"]
                annotation_path = os.path.join(
                    self.output_dir, 
                    "annotations", 
                    f"{os.path.splitext(os.path.basename(gp_path))[0]}.json"
                )
                
                # Check if all files exist
                if not os.path.exists(gp_path) or not os.path.exists(audio_path):
                    self.logger.warning(f"Files missing for match: {match['title']}")
                    continue
                
                # Check if annotations exist
                if not os.path.exists(annotation_path):
                    self.logger.warning(f"Annotations missing for: {match['title']}")
                    self._parse_gp_file(gp_path)  # Try to generate annotations
                    if not os.path.exists(annotation_path):
                        continue
                
                # Copy files to training directory
                training_dir = os.path.join(self.output_dir, "training")
                
                # Audio
                audio_name = os.path.basename(audio_path)
                target_audio = os.path.join(training_dir, "audio", audio_name)
                if not os.path.exists(target_audio):
                    shutil.copy2(audio_path, target_audio)
                
                # Annotations
                annotation_name = os.path.basename(annotation_path)
                target_annotation = os.path.join(training_dir, "annotations", annotation_name)
                if not os.path.exists(target_annotation):
                    shutil.copy2(annotation_path, target_annotation)
                
                self.logger.info(f"Prepared training data for: {match['title']}")
                
            except Exception as e:
                self.logger.error(f"Error preparing training data for {match.get('title', 'unknown')}: {e}")
        
        self.logger.info("Training data preparation complete")
    
    def download_missing_audio(self):
        """Download missing audio for matched Guitar Pro files."""
        self.logger.info("Checking for missing audio files")
        
        # Load matches
        matches_path = os.path.join(self.output_dir, "matches.json")
        
        if not os.path.exists(matches_path):
            self.logger.error("Matches file not found, run matching first")
            return
        
        with open(matches_path, "r") as f:
            matches = json.load(f)
        
        # Load Guitar Pro metadata
        gp_metadata_path = os.path.join(self.output_dir, "gp_metadata.json")
        
        with open(gp_metadata_path, "r") as f:
            gp_metadata = json.load(f)
        
        # Find Guitar Pro files without matched audio
        missing_audio = []
        
        for gp_item in gp_metadata:
            if not gp_item.get("matched_audio"):
                missing_audio.append(gp_item)
        
        self.logger.info(f"Found {len(missing_audio)} Guitar Pro files without matched audio")
        
        # Ask user if they want to download from YouTube
        print(f"\nFound {len(missing_audio)} Guitar Pro files without matched audio.")
        response = input("Do you want to download the missing audio from YouTube? (y/n): ")
        
        if response.lower() != 'y':
            self.logger.info("Download canceled by user")
            return
        
        # Download missing audio
        for i, gp_item in enumerate(missing_audio):
            artist = gp_item.get("artist", "")
            title = gp_item.get("title", "")
            
            query = f"{artist} {title}" if artist else title
            output_filename = f"{artist} - {title}.mp3" if artist else f"{title}.mp3"
            
            print(f"\n[{i+1}/{len(missing_audio)}] Downloading: {query}")
            
            # Ask for confirmation
            response = input(f"Download this track? (y/n/q): ")
            
            if response.lower() == 'q':
                self.logger.info("Download canceled by user")
                break
            
            if response.lower() != 'y':
                self.logger.info(f"Skipped: {query}")
                continue
            
            # Download from YouTube
            output_path = self.download_from_youtube(query, output_filename)
            
            if output_path:
                # Update metadata
                gp_item["matched_audio"] = os.path.basename(output_path)
                
                # Add to matches
                matches.append({
                    "gp_file": gp_item["filename"],
                    "audio_file": os.path.basename(output_path),
                    "score": 3,  # Manual download
                    "artist": artist,
                    "title": title
                })
                
                # Create audio metadata entry
                audio_metadata_path = os.path.join(self.output_dir, "audio_metadata.json")
                
                with open(audio_metadata_path, "r") as f:
                    audio_metadata = json.load(f)
                
                audio_metadata.append({
                    "filename": os.path.basename(output_path),
                    "path": output_path,
                    "artist": artist,
                    "title": title,
                    "matched_gp": gp_item["filename"]
                })
                
                with open(audio_metadata_path, "w") as f:
                    json.dump(audio_metadata, f, indent=2)
        
        # Save updated matches and metadata
        with open(matches_path, "w") as f:
            json.dump(matches, f, indent=2)
        
        with open(gp_metadata_path, "w") as f:
            json.dump(gp_metadata, f, indent=2)
        
        self.logger.info("Updated matches and metadata")
    
    def prepare_training_data(self):
        """Prepare training data from matched files."""
        self.logger.info("Preparing training data")
        
        # Check if matched files exist
        matches_path = os.path.join(self.output_dir, "matches.json")
        if not os.path.exists(matches_path):
            self.logger.error("No matched files found, run matching first")
            return
        
        # Load matches
        with open(matches_path, "r") as f:
            matches = json.load(f)
        
        # Prepare training data for each match
        for match in matches:
            try:
                gp_path = match["gp_path"]
                audio_path = match["audio_path"]
                annotation_path = os.path.join(
                    self.output_dir, 
                    "annotations", 
                    f"{os.path.splitext(os.path.basename(gp_path))[0]}.json"
                )
                
                # Check if all files exist
                if not os.path.exists(gp_path) or not os.path.exists(audio_path):
                    self.logger.warning(f"Files missing for match: {match['title']}")
                    continue
                
                # Check if annotations exist
                if not os.path.exists(annotation_path):
                    self.logger.warning(f"Annotations missing for: {match['title']}")
                    self._parse_gp_file(gp_path)  # Try to generate annotations
                    if not os.path.exists(annotation_path):
                        continue
                
                # Copy files to training directory
                training_dir = os.path.join(self.output_dir, "training")
                
                # Audio
                audio_name = os.path.basename(audio_path)
                target_audio = os.path.join(training_dir, "audio", audio_name)
                if not os.path.exists(target_audio):
                    shutil.copy2(audio_path, target_audio)
                
                # Annotations
                annotation_name = os.path.basename(annotation_path)
                target_annotation = os.path.join(training_dir, "annotations", annotation_name)
                if not os.path.exists(target_annotation):
                    shutil.copy2(annotation_path, target_annotation)
                
                self.logger.info(f"Prepared training data for: {match['title']}")
                
            except Exception as e:
                self.logger.error(f"Error preparing training data for {match.get('title', 'unknown')}: {e}")
        
        self.logger.info("Training data preparation complete")
    
    def main():
        """Run the data collection tool."""
        parser = argparse.ArgumentParser(description='AutoTablature Data Collection Tool')
        parser.add_argument('-o', '--output', default='data', help='Output directory for collected data')
        parser.add_argument('-g', '--gp-dir', help='Directory containing Guitar Pro files')
        parser.add_argument('-a', '--audio-dir', help='Directory containing audio files')
        parser.add_argument('--collect-gp', action='store_true', help='Collect Guitar Pro files')
        parser.add_argument('--collect-audio', action='store_true', help='Collect audio files')
        parser.add_argument('--match', action='store_true', help='Match Guitar Pro files with audio')
        parser.add_argument('--download', action='store_true', help='Download missing audio files')
        parser.add_argument('--extract', action='store_true', help='Extract annotations from Guitar Pro files')
        parser.add_argument('--prepare', action='store_true', help='Prepare training data')
        parser.add_argument('--all', action='store_true', help='Run all steps')
        
        args = parser.parse_args()
        
        # Create data collector
        collector = DataCollector(args.output, args.gp_dir, args.audio_dir)
        
        # Run requested steps
        if args.collect_gp or args.all:
            collector.collect_gp_files()
        
        if args.collect_audio or args.all:
            collector.collect_audio_files()
        
        if args.match or args.all:
            collector.match_files()
        
        if args.download or args.all:
            collector.download_missing_audio()
        
        if args.extract or args.all:
            collector.extract_annotations_from_gp()
        
        if args.prepare or args.all:
            collector.prepare_training_data()


def main():
    """Entry point for the module when run as a script."""
    DataCollector.main()
