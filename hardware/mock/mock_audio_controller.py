"""Mock audio controller.

``pygame.mixer`` runs natively on Windows/macOS, so the mock simply reuses the
real :class:`AudioController` unchanged.
"""

from hardware.audio_controller import AudioController as MockAudioController

__all__ = ["MockAudioController"]
