"""Scene state machine that orchestrates all subsystems.

Holds the active scene index and, on every transition, stops the currently
running hardware animations and starts the ones described by the new scene. The
display reads :attr:`current_scene` each frame to render the matching eyes.
"""

import threading

import config
from scenes.scene_loader import load_scenes


class SceneManager:
    def __init__(self, led, servo, audio, printer=None):
        self._led = led
        self._servo = servo
        self._audio = audio
        self._printer = printer
        self._scenes = load_scenes()
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
        if self._printer is not None and config.PRINTER_AUTO_PRINT_SCENE_CHANGES:
            self._printer.print_scene_ticket(scene, index + 1, len(self._scenes))
        if self._printer is not None and scene.printing.auto_print_on_enter:
            self._printer.print_pdf(scene.printing.pdf_path)

    def print_test(self) -> None:
        if self._printer is None:
            print("[printer] not configured")
            return
        scene = self.current_scene
        self._printer.print_test_ticket(
            scene,
            self.current_index + 1,
            self.scene_count,
        )

    def print_current_scene_pdf(self) -> None:
        if self._printer is None:
            print("[printer] not configured")
            return
        scene = self.current_scene
        self._printer.print_pdf(scene.printing.pdf_path)
