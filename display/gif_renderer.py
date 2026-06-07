"""Loads and renders animated GIFs (or static images) using Pillow + pygame.

GIF frames are extracted once at load time via Pillow and cached as pygame
Surface objects so they can be blitted efficiently in the render loop.

Usage
-----
    renderer = GifRenderer(pygame)
    if renderer.load("assets/images/hacked.gif"):
        renderer.draw(screen, "assets/images/hacked.gif", (cx, cy), t)

Falls back gracefully when a file is missing or Pillow is unavailable.
GIF files can be placed in ``assets/images/`` and referenced by path.

Internet GIFs
-------------
Use ``download_gif(url, dest_path)`` at startup to pre-fetch a GIF once and
cache it locally. On subsequent runs the local copy is used directly:

    from display.gif_renderer import download_gif
    download_gif("https://example.com/animation.gif", "assets/images/example.gif")
    renderer.load("assets/images/example.gif")
"""

from __future__ import annotations

import os
from typing import Optional


def download_gif(url: str, dest_path: str, timeout: int = 10) -> bool:
    """Download a GIF from *url* and save to *dest_path* if not already present.

    Returns ``True`` on success or if the file already exists.
    """
    if os.path.exists(dest_path):
        return True
    try:
        import urllib.request
        os.makedirs(os.path.dirname(dest_path) or ".", exist_ok=True)
        urllib.request.urlretrieve(url, dest_path)
        return os.path.exists(dest_path)
    except Exception:
        return False


class GifRenderer:
    """Frame-based GIF / image renderer backed by Pillow.

    A class-level cache stores extracted frames so the same file is only
    decoded once across multiple :class:`GifRenderer` instances.
    """

    _cache: dict[str, list[tuple[object, int]]] = {}  # path → [(surface, ms), …]

    def __init__(self, pygame_module):
        self._pygame = pygame_module

    def load(self, path: str) -> bool:
        """Extract and cache frames from *path*. Returns ``True`` on success."""
        if path in self._cache:
            return True
        if not os.path.exists(path):
            return False
        try:
            from PIL import Image
            img = Image.open(path)
            frames: list[tuple[object, int]] = []
            try:
                while True:
                    rgba = img.convert("RGBA")
                    w, h = rgba.size
                    data = rgba.tobytes()
                    surf = self._pygame.image.fromstring(data, (w, h), "RGBA")
                    duration_ms = img.info.get("duration", 100)
                    frames.append((surf, int(duration_ms)))
                    img.seek(img.tell() + 1)
            except EOFError:
                pass
            if frames:
                self._cache[path] = frames
                return True
        except Exception:
            pass
        return False

    def get_frame(self, path: str, t: float) -> Optional[object]:
        """Return the :class:`pygame.Surface` for elapsed time *t* (seconds)."""
        frames = self._cache.get(path)
        if not frames:
            return None
        if len(frames) == 1:
            return frames[0][0]
        total_ms = sum(d for _, d in frames)
        ms = int(t * 1000) % total_ms
        elapsed = 0
        for surf, dur in frames:
            elapsed += dur
            if ms < elapsed:
                return surf
        return frames[-1][0]

    def draw(
        self,
        surface,
        path: str,
        center: tuple[int, int],
        t: float,
        scale: Optional[tuple[int, int]] = None,
    ) -> bool:
        """Blit the current frame centred at *center*. Returns ``False`` if not loaded."""
        frame = self.get_frame(path, t)
        if frame is None:
            return False
        if scale:
            frame = self._pygame.transform.scale(frame, scale)
        rect = frame.get_rect(center=center)
        surface.blit(frame, rect)
        return True
