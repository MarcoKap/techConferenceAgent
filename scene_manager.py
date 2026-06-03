"""Scene state machine that orchestrates all subsystems.

Holds the active scene index and, on every transition, stops the currently
running hardware animations and starts the ones described by the new scene. The
display reads :attr:`current_scene` each frame to render the matching eyes.
"""

import threading
from typing import Optional

from scenes.scene_definitions import SCENES


class SceneManager:
    def __init__(self, led, servo, audio):
        self._led = led
        self._servo = servo
        self._audio = audio
        self._scenes = SCENES
        self._index = 0
        self._lock = threading.Lock()
        
        # Face rendering components (optional)
        self._face_renderer: Optional[object] = None
        self._audio_sync: Optional[object] = None
        self._video_ai: Optional[object] = None

    @property
    def current_index(self) -> int:
        return self._index

    @property
    def current_scene(self):
        return self._scenes[self._index]

    @property
    def scene_count(self) -> int:
        return len(self._scenes)
    
    def set_face_renderer(self, renderer: object) -> None:
        """Set photorealistic face renderer."""
        self._face_renderer = renderer
    
    def set_audio_sync(self, audio_sync: object) -> None:
        """Set audio sync controller."""
        self._audio_sync = audio_sync
    
    def set_video_ai(self, video_ai: object) -> None:
        """Set video-AI renderer."""
        self._video_ai = video_ai

    def start(self) -> None:
        """Activate the first scene."""
        self._apply(self._index)

    def next(self) -> None:
        with self._lock:
            self._index = (self._index + 1) % len(self._scenes)
            self._apply(self._index)

    def prev(self) -> None:
        with self._lock:
            self._index = (self._index - 1) % len(self._scenes)
            self._apply(self._index)

    def _apply(self, index: int) -> None:
        scene = self._scenes[index]
        print(f"[scene] -> {index + 1}/{len(self._scenes)} {scene.name}")
        # Stop running animations before starting the new ones so subsystems
        # never overlap during a transition.
        self._led.stop()
        self._servo.stop()
        self._audio.stop()
        
        # Stop face animations
        if self._audio_sync:
            self._audio_sync.stop()
        
        # Start new scene
        self._led.start(scene.leds)
        self._servo.start(scene.servo)
        self._audio.start(scene.audio)
        
        # Load audio sync for face rendering if available
        if self._audio_sync and hasattr(scene, 'audio_file') and scene.audio_file:
            try:
                self._audio_sync.load_audio(scene.audio_file)
                self._audio_sync.play()
            except Exception as e:
                print(f"Warning: Could not load audio sync: {e}")
    
    def get_current_face_emotion(self) -> str:
        """Get current emotion for face rendering from scene."""
        scene = self.current_scene
        if hasattr(scene, 'face_emotion'):
            return scene.face_emotion
        return 'neutral'
    
    def update_face_rendering(self, surface, time_elapsed: float) -> None:
        """Update face rendering for current frame."""
        if not self._face_renderer:
            return
        
        emotion = self.get_current_face_emotion()
        
        try:
            # Update audio sync if available
            if self._audio_sync:
                self._audio_sync.update(1.0/60.0)  # Assume 60 FPS
            
            # Render photorealistic face
            self._face_renderer.render(
                surface,
                emotion=emotion,
                t=time_elapsed,
            )
        except Exception as e:
            print(f"Error rendering face: {e}")
