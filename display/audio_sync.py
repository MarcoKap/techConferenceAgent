"""
Audio-driven mouth animation with precise phoneme extraction.
Maps audio to mouth shapes for realistic lip-sync.
"""

import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import os


class AudioAnalyzer:
    """Analyze audio to extract speech features and phoneme timing."""
    
    def __init__(self):
        try:
            import librosa
            self.librosa = librosa
            self.available = True
        except ImportError:
            self.available = False
            print("Warning: librosa not available, audio sync disabled")
    
    def load_audio(self, audio_file: str, sr: int = 16000) -> Tuple[np.ndarray, int]:
        """Load audio file and resample to target rate."""
        if not self.available:
            raise RuntimeError("librosa required for audio analysis")
        
        y, sr_orig = self.librosa.load(audio_file, sr=sr)
        return y, sr
    
    def extract_speech_frames(
        self, 
        audio_file: str, 
        frame_duration: float = 0.05
    ) -> List[Tuple[float, Dict]]:
        """
        Extract speech frames with energy, MFCCs, and spectral features.
        
        Returns list of (time, features) tuples where time is in seconds.
        """
        if not self.available:
            return []
        
        try:
            y, sr = self.load_audio(audio_file)
            
            # Frame parameters
            frame_length = int(sr * frame_duration)
            hop_length = frame_length // 2
            
            # Extract features
            energy = self.librosa.feature.melspectrogram(y=y, sr=sr, hop_length=hop_length)
            mfcc = self.librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, hop_length=hop_length)
            
            # Convert to dB scale
            energy_db = self.librosa.power_to_db(energy)
            
            frames = []
            for i in range(energy_db.shape[1]):
                time = i * hop_length / sr
                
                features = {
                    'energy': float(np.mean(energy_db[:, i])),
                    'mfcc': mfcc[:, i].astype(np.float32),
                    'time': time,
                }
                
                frames.append((time, features))
            
            return frames
        
        except Exception as e:
            print(f"Error extracting speech frames: {e}")
            return []
    
    def classify_phoneme(self, features: Dict) -> str:
        """
        Classify phoneme from audio features using simple heuristics.
        
        Maps energy + MFCC patterns to 8 basic phonemes.
        """
        energy = features.get('energy', 0)
        mfcc = features.get('mfcc', np.zeros(13))
        
        # Simple MFCC-based classification
        if len(mfcc) < 4:
            return 'neutral'
        
        # Use first few MFCCs as features
        mfcc_ratio = mfcc[1] / (abs(mfcc[0]) + 1e-6)
        spectral_centroid = np.mean(mfcc[:4])
        
        # Decision tree for phoneme classification
        if energy < -30:
            return 'neutral'  # Silence
        elif mfcc_ratio > 0.8:
            if spectral_centroid > 5:
                return 'i'  # High frequency
            else:
                return 'a'  # Low-mid frequency
        elif mfcc_ratio > 0.4:
            return 'e'
        elif spectral_centroid > 8:
            return 'o'
        elif spectral_centroid > 3:
            return 'u'
        elif abs(mfcc[0]) > 5:
            return 'm'
        elif abs(mfcc[2]) > 5:
            return 's'
        else:
            return 'neutral'
    
    def extract_phoneme_timeline(self, audio_file: str) -> Dict[float, str]:
        """Extract full phoneme timeline from audio file."""
        frames = self.extract_speech_frames(audio_file)
        
        timeline = {}
        for time, features in frames:
            phoneme = self.classify_phoneme(features)
            timeline[time] = phoneme
        
        return timeline
    
    def smooth_phoneme_timeline(
        self, 
        timeline: Dict[float, str], 
        window_size: int = 3
    ) -> Dict[float, str]:
        """Smooth phoneme changes to reduce jitter."""
        if len(timeline) < window_size:
            return timeline
        
        times = sorted(timeline.keys())
        smoothed = {}
        
        for i, time in enumerate(times):
            # Get surrounding frames
            start_idx = max(0, i - window_size // 2)
            end_idx = min(len(times), i + window_size // 2 + 1)
            
            window_frames = [timeline[times[j]] for j in range(start_idx, end_idx)]
            
            # Majority vote
            from collections import Counter
            phoneme = Counter(window_frames).most_common(1)[0][0]
            smoothed[time] = phoneme
        
        return smoothed
    
    def get_phoneme_at_time(self, timeline: Dict[float, str], t: float) -> str:
        """Get phoneme at specific time with interpolation."""
        if not timeline:
            return 'neutral'
        
        times = sorted(timeline.keys())
        
        # Find closest time
        if t < times[0]:
            return timeline[times[0]]
        if t > times[-1]:
            return timeline[times[-1]]
        
        # Linear search for closest
        closest_time = times[0]
        min_dist = abs(t - times[0])
        
        for time in times:
            dist = abs(t - time)
            if dist < min_dist:
                min_dist = dist
                closest_time = time
        
        return timeline[closest_time]
    
    def get_duration(self, audio_file: str) -> float:
        """Get total duration of audio file in seconds."""
        if not self.available:
            return 0.0
        
        try:
            y, sr = self.load_audio(audio_file)
            return len(y) / sr
        except:
            return 0.0


class AudioSyncController:
    """Manages audio playback sync and phoneme animation."""
    
    def __init__(self, audio_file: Optional[str] = None):
        self.analyzer = AudioAnalyzer()
        self.timeline: Dict[float, str] = {}
        self.playback_time = 0.0
        self.is_playing = False
        self.audio_file = audio_file
        
        if audio_file:
            self.load_audio(audio_file)
    
    def load_audio(self, audio_file: str) -> None:
        """Load and analyze audio file."""
        if not self.analyzer.available:
            print("Audio analysis not available")
            return
        
        self.audio_file = audio_file
        print(f"Loading audio: {audio_file}")
        
        # Extract phoneme timeline
        timeline = self.analyzer.extract_phoneme_timeline(audio_file)
        
        # Smooth to reduce jitter
        self.timeline = self.analyzer.smooth_phoneme_timeline(timeline, window_size=5)
        
        print(f"Extracted {len(self.timeline)} phoneme frames")
    
    def update(self, dt: float) -> None:
        """Update playback time."""
        if self.is_playing:
            self.playback_time += dt
    
    def get_current_phoneme(self) -> str:
        """Get current phoneme based on playback time."""
        return self.analyzer.get_phoneme_at_time(self.timeline, self.playback_time)
    
    def play(self) -> None:
        """Start playback."""
        self.is_playing = True
    
    def stop(self) -> None:
        """Stop playback."""
        self.is_playing = False
    
    def seek(self, time: float) -> None:
        """Seek to specific time."""
        self.playback_time = max(0.0, time)
    
    def get_duration(self) -> float:
        """Get total audio duration."""
        if self.audio_file:
            return self.analyzer.get_duration(self.audio_file)
        return 0.0
