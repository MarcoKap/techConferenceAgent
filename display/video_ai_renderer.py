"""
Video-KI integration for ultra-realistic face animations.
Supports D-ID API for prerendering realistic videos.
"""

import requests
import json
import time
import os
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass
import subprocess


@dataclass
class VideoGenerationRequest:
    """Request for video generation."""
    text: str
    avatar_id: str = "jason-medium"  # D-ID default avatar
    emotion: str = "neutral"
    language: str = "en"
    voice_name: str = "en-US-Neural2-A"
    
    def to_dict(self) -> Dict:
        return {
            'script': {
                'type': 'text',
                'subtitles': False,
                'provider': {
                    'type': 'google',
                    'voice_name': self.voice_name,
                },
                'ssml': False,
                'text': self.text,
            },
            'config': {
                'fluent': True,
                'pad_audio': 0,
            },
            'source_url': 'https://create-images.d-id.com/api/default_source_image',
        }


class D_IDVideoClient:
    """D-ID API client for video generation."""
    
    BASE_URL = "https://api.d-id.com/talks"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('DID_API_KEY')
        self.session_id = None
        self.session_token = None
        
        if not self.api_key:
            print("⚠️  Warning: DID_API_KEY not set - video generation disabled")
    
    def _get_headers(self) -> Dict:
        """Get request headers."""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
    
    def create_talk(self, request: VideoGenerationRequest) -> Optional[Dict]:
        """
        Create a new talk (video) with D-ID API.
        Returns talk ID if successful.
        """
        if not self.api_key:
            print("D-ID API key not available")
            return None
        
        try:
            response = requests.post(
                self.BASE_URL,
                json=request.to_dict(),
                headers=self._get_headers(),
                timeout=30,
            )
            
            response.raise_for_status()
            data = response.json()
            
            print(f"✓ Video creation started: {data.get('id')}")
            return data
        
        except Exception as e:
            print(f"✗ Error creating talk: {e}")
            return None
    
    def get_talk_status(self, talk_id: str) -> Optional[Dict]:
        """Get status of a talk."""
        if not self.api_key:
            return None
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/{talk_id}",
                headers=self._get_headers(),
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting talk status: {e}")
            return None
    
    def wait_for_video(self, talk_id: str, max_wait_seconds: int = 300) -> Optional[str]:
        """
        Poll for video completion and return download URL.
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait_seconds:
            status = self.get_talk_status(talk_id)
            
            if not status:
                time.sleep(5)
                continue
            
            state = status.get('status', '')
            
            if state == 'done':
                video_url = status.get('result_url')
                print(f"✓ Video ready: {video_url}")
                return video_url
            
            elif state == 'failed':
                error = status.get('error', 'Unknown error')
                print(f"✗ Video generation failed: {error}")
                return None
            
            elif state == 'processing':
                print(f"  Processing... ({time.time() - start_time:.0f}s)")
            
            time.sleep(5)
        
        print(f"✗ Video generation timeout after {max_wait_seconds}s")
        return None
    
    def download_video(self, url: str, output_path: str) -> bool:
        """Download video file."""
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            print(f"✓ Video downloaded: {output_path}")
            return True
        except Exception as e:
            print(f"✗ Error downloading video: {e}")
            return False


class VideoCache:
    """Cache management for generated videos."""
    
    def __init__(self, cache_dir: str = 'assets/videos/cache'):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.cache_dir / 'index.json'
        self.index = self._load_index()
    
    def _load_index(self) -> Dict:
        """Load cache index."""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_index(self) -> None:
        """Save cache index."""
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)
    
    def get_cache_key(self, text: str, emotion: str) -> str:
        """Generate cache key from text and emotion."""
        import hashlib
        key = f"{text}:{emotion}"
        return hashlib.md5(key.encode()).hexdigest()[:16]
    
    def get_cached_video(self, text: str, emotion: str) -> Optional[str]:
        """Get cached video path if available."""
        cache_key = self.get_cache_key(text, emotion)
        
        if cache_key in self.index:
            video_path = self.index[cache_key]
            if Path(video_path).exists():
                print(f"✓ Using cached video")
                return video_path
            else:
                del self.index[cache_key]
                self._save_index()
        
        return None
    
    def cache_video(self, text: str, emotion: str, video_path: str) -> None:
        """Add video to cache."""
        cache_key = self.get_cache_key(text, emotion)
        self.index[cache_key] = video_path
        self._save_index()


class VideoAIFaceRenderer:
    """Render video-AI generated faces (D-ID integration)."""
    
    def __init__(self, api_key: Optional[str] = None, cache_dir: str = 'assets/videos/cache'):
        self.client = D_IDVideoClient(api_key)
        self.cache = VideoCache(cache_dir)
        self.video_players: Dict[str, 'VideoPlayer'] = {}
    
    def generate_or_get_video(
        self,
        text: str,
        emotion: str = 'neutral',
        force_regenerate: bool = False,
    ) -> Optional[str]:
        """
        Generate or retrieve cached video.
        Returns path to video file.
        """
        # Check cache first
        if not force_regenerate:
            cached = self.cache.get_cached_video(text, emotion)
            if cached:
                return cached
        
        # Generate new video
        request = VideoGenerationRequest(text=text, emotion=emotion)
        result = self.client.create_talk(request)
        
        if not result:
            return None
        
        talk_id = result.get('id')
        if not talk_id:
            return None
        
        # Wait for completion
        video_url = self.client.wait_for_video(talk_id)
        
        if not video_url:
            return None
        
        # Download and cache
        cache_key = self.cache.get_cache_key(text, emotion)
        video_path = str(self.cache.cache_dir / f"{cache_key}.mp4")
        
        if self.client.download_video(video_url, video_path):
            self.cache.cache_video(text, emotion, video_path)
            return video_path
        
        return None


class VideoPlayer:
    """Simple video player using opencv."""
    
    def __init__(self, video_path: str):
        try:
            import cv2
            self.cv2 = cv2
            self.available = True
        except ImportError:
            self.available = False
            print("Warning: opencv not available for video playback")
        
        self.video_path = video_path
        self.cap = None
        self.frame_index = 0
        self.total_frames = 0
        
        if self.available:
            self._open_video()
    
    def _open_video(self) -> None:
        """Open video file."""
        if not self.available:
            return
        
        self.cap = self.cv2.VideoCapture(self.video_path)
        self.total_frames = int(self.cap.get(self.cv2.CAP_PROP_FRAME_COUNT))
        self.frame_index = 0
        
        print(f"✓ Video loaded: {self.total_frames} frames")
    
    def get_frame(self) -> Optional[object]:
        """Get current frame as numpy array."""
        if not self.available or not self.cap:
            return None
        
        ret, frame = self.cap.read()
        if ret:
            self.frame_index += 1
            return frame
        else:
            self.seek(0)  # Loop
            return self.get_frame()
    
    def seek(self, frame_idx: int) -> None:
        """Seek to specific frame."""
        if not self.available or not self.cap:
            return
        
        self.frame_index = max(0, min(frame_idx, self.total_frames - 1))
        self.cap.set(self.cv2.CAP_PROP_POS_FRAMES, self.frame_index)
    
    def close(self) -> None:
        """Close video."""
        if self.cap:
            self.cap.release()
