"""Audio controller using ``pygame.mixer``.

This implementation is fully cross-platform, so the Windows mock simply reuses
it. Missing audio files are tolerated (logged and skipped) so the robot still
runs before the WAV assets are added.
"""

import os

import config


class AudioController:
    def __init__(self):
        self._initialized = False
        self._pygame = None
        self._channel = None
        try:
            import pygame

            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self._pygame = pygame
            self._initialized = True
        except Exception as exc:  # pragma: no cover - depends on audio device
            print(f"[audio] mixer init failed, audio disabled: {exc}")

    def start(self, audio_config) -> None:
        self.stop()
        if (not self._initialized or audio_config is None
                or audio_config.filename is None):
            return
        filename = audio_config.filename
        if os.path.isabs(filename):
            path = filename
        elif os.path.sep in filename:
            path = os.path.join(config.BASE_DIR, filename)
        else:
            path = os.path.join(config.AUDIO_DIR, filename)
        if not os.path.exists(path):
            print(f"[audio] file not found, skipping: {path}")
            return
        try:
            sound = self._pygame.mixer.Sound(path)
            loops = -1 if audio_config.loop else 0
            self._channel = sound.play(loops=loops)
        except Exception as exc:
            print(f"[audio] playback failed: {exc}")

    def stop(self) -> None:
        if self._channel is not None:
            try:
                self._channel.stop()
            except Exception:
                pass
            self._channel = None

    def close(self) -> None:
        self.stop()
