"""
Photorealistic face renderer - minimal but effective.
Supports 2D photorealistic eyes + mouth with audio sync.
"""

import pygame
import math
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, Dict
import os


class BlinkingController:
    """Simple blinking controller with emotion patterns."""
    
    def __init__(self):
        self.blink_patterns = {
            'neutral': {'frequency': 3.5, 'duration': 0.15},   # blinks per minute
            'happy': {'frequency': 4.0, 'duration': 0.12},
            'sad': {'frequency': 2.5, 'duration': 0.20},
            'angry': {'frequency': 4.5, 'duration': 0.10},
            'focused': {'frequency': 2.0, 'duration': 0.15},
            'tired': {'frequency': 3.0, 'duration': 0.25},
        }
    
    def get_eyelid_openness(self, emotion: str, t: float) -> float:
        """
        Returns eyelid openness (0.0 = closed, 1.0 = fully open).
        Simulates natural blinking with sinusoidal curves.
        """
        pattern = self.blink_patterns.get(emotion, self.blink_patterns['neutral'])
        frequency = pattern['frequency'] / 60.0  # convert to Hz
        duration = pattern['duration']
        
        # Cyclical blink time (0 to 1)
        cycle_time = t * frequency
        cycle_phase = cycle_time % 1.0
        
        # Blink happens in first `duration` of cycle
        if cycle_phase < duration:
            # Smooth blink: close and open
            blink_progress = cycle_phase / duration
            # Using smooth step function (sin-based)
            return 0.5 - 0.5 * math.cos(blink_progress * math.pi)
        else:
            return 1.0
    
    def get_pupil_dilation(self, emotion: str) -> float:
        """Pupil size multiplier based on emotion."""
        dilations = {
            'neutral': 1.0,
            'happy': 1.1,
            'sad': 0.95,
            'angry': 0.85,
            'focused': 0.90,
            'tired': 1.2,
        }
        return dilations.get(emotion, 1.0)


class EyeAssetsManager:
    """Manages loading and blending of eye images."""
    
    def __init__(self, assets_dir: str = 'assets/faces/eyes'):
        self.assets_dir = Path(assets_dir)
        self.cache: Dict[str, pygame.Surface] = {}
        self.blink_states = ['open', 'mid', 'closed']
        self.emotions = ['neutral', 'happy', 'sad', 'angry', 'focused', 'tired']
    
    def load_eye_image(self, emotion: str, blink_state: str) -> Optional[pygame.Surface]:
        """Load eye image with fallback to placeholder."""
        cache_key = f"{emotion}_{blink_state}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Try to load image
        eye_path = self.assets_dir / f"{emotion}_{blink_state}.png"
        
        if eye_path.exists():
            try:
                surface = pygame.image.load(eye_path)
                self.cache[cache_key] = surface
                return surface
            except Exception as e:
                print(f"Error loading {eye_path}: {e}")
        
        # Fallback: create placeholder
        placeholder = self._create_placeholder_eye()
        self.cache[cache_key] = placeholder
        return placeholder
    
    def _create_placeholder_eye(self) -> pygame.Surface:
        """Create a simple placeholder eye."""
        surface = pygame.Surface((250, 150), pygame.SRCALPHA)
        
        # Draw realistic-ish eye: sclera + iris
        center = (125, 75)
        
        # Sclera (white with slight color)
        pygame.draw.ellipse(surface, (250, 248, 245), (*center, 120, 90))
        
        # Iris (bluish)
        iris_color = (70, 120, 180)
        pygame.draw.ellipse(surface, iris_color, (center[0]-35, center[1]-30, 70, 60))
        
        # Pupil
        pygame.draw.circle(surface, (10, 10, 10), center, 18)
        
        # Highlight
        pygame.draw.circle(surface, (255, 255, 255), (center[0]-8, center[1]-10), 8)
        
        return surface
    
    def blend_eyes(self, emotion: str, blink_openness: float) -> pygame.Surface:
        """
        Blend between blink states to create smooth animation.
        blink_openness: 0.0 (fully closed) to 1.0 (fully open)
        """
        if blink_openness >= 0.9:
            return self.load_eye_image(emotion, 'open')
        elif blink_openness <= 0.1:
            return self.load_eye_image(emotion, 'closed')
        else:
            # Blend mid-blink
            alpha = (blink_openness - 0.1) / 0.8
            open_eye = self.load_eye_image(emotion, 'open')
            mid_eye = self.load_eye_image(emotion, 'mid')
            
            # Simple alpha blending
            result = open_eye.copy()
            result.blit(mid_eye, (0, 0), special_flags=pygame.BLEND_RGBA_MAX)
            return result


class MouthAssetsManager:
    """Manages mouth phoneme images."""
    
    def __init__(self, assets_dir: str = 'assets/faces/mouth'):
        self.assets_dir = Path(assets_dir)
        self.cache: Dict[str, pygame.Surface] = {}
        # 8 phonemes for basic speech
        self.phonemes = ['neutral', 'a', 'e', 'i', 'o', 'u', 'm', 's']
    
    def load_mouth(self, phoneme: str) -> pygame.Surface:
        """Load mouth image for phoneme with fallback."""
        if phoneme not in self.cache:
            mouth_path = self.assets_dir / f"{phoneme}.png"
            
            if mouth_path.exists():
                try:
                    self.cache[phoneme] = pygame.image.load(mouth_path)
                except Exception as e:
                    print(f"Error loading mouth {phoneme}: {e}")
                    self.cache[phoneme] = self._create_placeholder_mouth(phoneme)
            else:
                self.cache[phoneme] = self._create_placeholder_mouth(phoneme)
        
        return self.cache[phoneme]
    
    def _create_placeholder_mouth(self, phoneme: str) -> pygame.Surface:
        """Create simple placeholder mouth based on phoneme."""
        surface = pygame.Surface((180, 90), pygame.SRCALPHA)
        
        # Mouth outline (simple shapes)
        mouth_positions = {
            'neutral': 45,
            'a': 35,
            'e': 30,
            'i': 50,
            'o': 25,
            'u': 35,
            'm': 40,
            's': 38,
        }
        
        openness = mouth_positions.get(phoneme, 40)
        
        # Lip shape (simple ellipse)
        pygame.draw.ellipse(surface, (200, 100, 100), (30, 35, 120, openness))
        pygame.draw.ellipse(surface, (180, 80, 80), (35, 40, 110, openness-10))
        
        return surface


class AudioPhonemeExtractor:
    """Extract phonemes from audio using frequency analysis."""
    
    def __init__(self):
        """Initialize audio analyzer."""
        try:
            import librosa
            self.librosa = librosa
            self.available = True
        except ImportError:
            print("Warning: librosa not available, using simple analysis")
            self.available = False
    
    def extract_phonemes(self, audio_file: str, frame_duration: float = 0.05) -> list:
        """
        Extract phoneme sequence from audio file.
        Returns list of (time, phoneme) tuples.
        """
        if not self.available:
            return self._simple_phoneme_extraction(audio_file, frame_duration)
        
        try:
            # Load audio
            y, sr = self.librosa.load(audio_file, sr=16000)
            
            # Extract STFT
            D = self.librosa.stft(y)
            magnitude = self.librosa.magphase(D)[0]
            
            # Frame-by-frame phoneme detection
            phonemes = []
            frame_length = int(sr * frame_duration)
            
            for i in range(0, len(y), frame_length):
                frame = magnitude[:, i // 512:(i + frame_length) // 512]
                if frame.size == 0:
                    continue
                
                phoneme = self._classify_phoneme(frame)
                time = i / sr
                phonemes.append((time, phoneme))
            
            return phonemes
        except Exception as e:
            print(f"Error extracting phonemes: {e}")
            return []
    
    def _classify_phoneme(self, magnitude: np.ndarray) -> str:
        """Classify phoneme from frequency magnitude."""
        if magnitude.size == 0:
            return 'neutral'
        
        # Simple frequency-based classification
        mean_freq = np.mean(magnitude)
        max_bin = np.argmax(np.mean(magnitude, axis=1))
        
        phoneme_map = {
            0: 'a',      # Low frequency
            1: 'o',
            2: 'e',      # Mid
            3: 'i',
            4: 'u',      # High
            5: 's',
            6: 'm',
            7: 'neutral',
        }
        
        # Quantize to 8 bins
        bin_idx = min(7, max(0, max_bin // 30))
        return phoneme_map.get(bin_idx, 'neutral')
    
    def _simple_phoneme_extraction(self, audio_file: str, frame_duration: float = 0.05) -> list:
        """Fallback: simple phoneme extraction without librosa."""
        # Just return basic neutral phoneme for now
        # In production, would read WAV and do DSP
        return [(0.0, 'neutral'), (0.5, 'a'), (1.0, 'o')]


class PhotorealisticFaceRenderer:
    """Main photorealistic face renderer."""
    
    def __init__(self, width: int = 800, height: int = 200):
        self.width = width
        self.height = height
        
        self.eye_manager = EyeAssetsManager()
        self.mouth_manager = MouthAssetsManager()
        self.blink_controller = BlinkingController()
        self.phoneme_extractor = AudioPhonemeExtractor()
        
        # Current audio sync state
        self.audio_phonemes: Dict[float, str] = {}
        self.audio_offset = 0.0  # seconds
    
    def load_audio_sync(self, audio_file: str) -> None:
        """Pre-load audio and extract phoneme timeline."""
        try:
            phonemes = self.phoneme_extractor.extract_phonemes(audio_file)
            self.audio_phonemes = {time: phoneme for time, phoneme in phonemes}
            print(f"Loaded audio sync with {len(phonemes)} phoneme frames")
        except Exception as e:
            print(f"Error loading audio sync: {e}")
            self.audio_phonemes = {}
    
    def get_current_phoneme(self, t: float) -> str:
        """Get phoneme at time t (seconds)."""
        if not self.audio_phonemes:
            return 'neutral'
        
        # Find closest phoneme time
        times = sorted(self.audio_phonemes.keys())
        closest_time = min(times, key=lambda x: abs(x - t), default=None)
        
        if closest_time is not None:
            return self.audio_phonemes[closest_time]
        return 'neutral'
    
    def render(
        self, 
        surface: pygame.Surface,
        emotion: str = 'neutral',
        t: float = 0.0,
        eye_position: Tuple[int, int] = None,
        mouth_position: Tuple[int, int] = None,
    ) -> None:
        """
        Render face to surface.
        
        Args:
            surface: pygame surface to render to
            emotion: current emotion state
            t: time in seconds (for animations)
            eye_position: (x, y) for eye rendering
            mouth_position: (x, y) for mouth rendering
        """
        if eye_position is None:
            eye_position = (self.width // 3, self.height // 2)
        if mouth_position is None:
            mouth_position = (self.width // 2 + 50, self.height - 60)
        
        # Render left eye
        self._render_eye(surface, emotion, t, (eye_position[0] - 80, eye_position[1]))
        
        # Render right eye
        self._render_eye(surface, emotion, t, (eye_position[0] + 80, eye_position[1]))
        
        # Render mouth
        self._render_mouth(surface, t, mouth_position)
    
    def _render_eye(
        self, 
        surface: pygame.Surface, 
        emotion: str, 
        t: float, 
        position: Tuple[int, int]
    ) -> None:
        """Render single eye with blinking."""
        blink_openness = self.blink_controller.get_eyelid_openness(emotion, t)
        
        if blink_openness < 0.05:
            # Fully closed, skip rendering
            return
        
        eye_image = self.eye_manager.blend_eyes(emotion, blink_openness)
        
        # Apply opacity based on blink state
        eye_image.set_alpha(int(255 * blink_openness))
        
        # Blit to surface
        surface.blit(eye_image, position)
    
    def _render_mouth(
        self, 
        surface: pygame.Surface, 
        t: float, 
        position: Tuple[int, int]
    ) -> None:
        """Render mouth with phoneme animation."""
        phoneme = self.get_current_phoneme(t)
        mouth_image = self.mouth_manager.load_mouth(phoneme)
        
        surface.blit(mouth_image, position)


# Convenience function for easy use in main display loop
def create_face_renderer(width: int = 800, height: int = 200) -> PhotorealisticFaceRenderer:
    """Factory function to create and return a face renderer."""
    return PhotorealisticFaceRenderer(width, height)
