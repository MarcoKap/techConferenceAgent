"""Renders an optional mouth below the eyes.

The mouth shape is selected by ``DisplayConfig.mouth_type`` and tinted with the
scene's eye color so it reads as part of the same expression.
"""

import math


class MouthRenderer:
    def __init__(self, width: int, height: int):
        self._pygame = __import__("pygame")
        self._w = width
        self._h = height
        self._center = (width // 2, int(height * 0.78))
        self._span = int(width * 0.18)

    def draw(self, surface, cfg, t: float) -> None:
        pygame = self._pygame
        mtype = cfg.mouth_type
        if mtype == "none":
            return

        cx, cy = self._center
        color = cfg.eye_color
        span = self._span

        if mtype == "line":
            pygame.draw.line(surface, color, (cx - span, cy), (cx + span, cy), 8)
        elif mtype == "flat":
            pygame.draw.line(surface, color, (cx - span // 2, cy),
                             (cx + span // 2, cy), 6)
        elif mtype in ("smile", "frown"):
            self._draw_arc(surface, color, cx, cy, span, up=(mtype == "smile"))
        elif mtype == "open":
            scale = 1.0 + 0.15 * math.sin(t * 6)
            rect = pygame.Rect(0, 0, int(span * 1.0), int(span * 0.8 * scale))
            rect.center = (cx, cy)
            pygame.draw.ellipse(surface, color, rect)

    def _draw_arc(self, surface, color, cx, cy, span, up: bool):
        pygame = self._pygame
        h = int(span * 0.7)
        if up:
            rect = pygame.Rect(cx - span, cy - h, span * 2, h * 2)
            pygame.draw.arc(surface, color, rect, math.pi, 2 * math.pi, 8)
        else:
            rect = pygame.Rect(cx - span, cy, span * 2, h * 2)
            pygame.draw.arc(surface, color, rect, 0, math.pi, 8)
