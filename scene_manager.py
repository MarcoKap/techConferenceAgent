"""Scene state machine that orchestrates all subsystems.

Holds the active scene index and, on every transition, stops the currently
running hardware animations and starts the ones described by the new scene. The
display reads :attr:`current_scene` each frame to render the matching eyes.
"""

import threading

from scenes.scene_definitions import SCENES


class SceneManager:
    def __init__(self, led, servo, audio):
        self._led = led
        self._servo = servo
        self._audio = audio
        self._scenes = SCENES
        self._index = 0
        self._lock = threading.Lock()

    @property
    def current_index(self) -> int:
        return self._index

    @property
    def current_scene(self):
        return self._scenes[self._index]

    @property
    def scene_count(self) -> int:
        return len(self._scenes)

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
        self._led.start(scene.leds)
        self._servo.start(scene.servo)
        self._audio.start(scene.audio)
