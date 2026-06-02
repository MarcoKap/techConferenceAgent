"""Renders the robot's eyes with pygame.

The look of each scene is driven entirely by its :class:`DisplayConfig`
(``eye_color``, ``eye_shape``, ``pupil_animation``). All motion is derived from a
single elapsed-time value ``t`` so rendering stays stateless and smooth.
"""

import math

from hardware.base import lerp_color
import config


class EyeRenderer:
    def __init__(self, width: int, height: int):
        self._pygame = __import__("pygame")
        self._w = width
        self._h = height
        self._rx = int(height * 0.16)
        self._ry = int(height * 0.18)
        self._left = (int(width * 0.33), int(height * 0.42))
        self._right = (int(width * 0.67), int(height * 0.42))

    def draw(self, surface, cfg, t: float) -> None:
        self._draw_eye(surface, self._left, cfg, t, mirror=False)
        self._draw_eye(surface, self._right, cfg, t, mirror=True)

    # -- helpers ------------------------------------------------------------
    def _openness(self, cfg, t: float) -> float:
        base = 1.0
        if cfg.eye_shape == "wide":
            base = 1.2
        elif cfg.eye_shape == "angry":
            base = 0.85
        if cfg.pupil_animation == "idle":
            cycle = t % 4.0
            if cycle > 3.85:  # brief blink near the end of each cycle
                base *= 0.12
        return base

    def _pupil_offset(self, cfg, t: float):
        anim = cfg.pupil_animation
        if anim == "wander":
            return (math.sin(t * 1.2), math.sin(t * 0.8) * 0.5)
        if anim == "jitter":
            return (math.sin(t * 25) * 0.8 + math.sin(t * 13) * 0.2,
                    math.sin(t * 19) * 0.6)
        if anim == "idle":
            return (math.sin(t * 0.6) * 0.3, math.sin(t * 0.4) * 0.2)
        return (0.0, 0.0)  # still / glow

    def _draw_eye(self, surface, center, cfg, t, mirror):
        pygame = self._pygame
        cx, cy = center

        if cfg.eye_shape == "x":
            self._draw_x(surface, cx, cy, cfg.eye_color)
            return

        openness = self._openness(cfg, t)
        eh = int(self._ry * 2 * openness)
        if cfg.eye_shape == "narrow":
            eh = int(eh * 0.4)
        eh = max(4, eh)

        rect = pygame.Rect(0, 0, self._rx * 2, eh)
        rect.center = (cx, cy)
        pygame.draw.ellipse(surface, cfg.eye_color, rect)

        if cfg.pupil_animation == "glow":
            glow = (math.sin(t * 3) + 1) / 2
            gcolor = lerp_color(cfg.eye_color, (255, 170, 170), glow * 0.6)
            pygame.draw.ellipse(surface, gcolor, rect, width=max(2, int(8 * glow)))

        if eh > 10:
            dx, dy = self._pupil_offset(cfg, t)
            pr = int(min(self._rx, eh / 2) * 0.42)
            if pr > 1:
                px = cx + dx * self._rx * 0.4
                py = cy + dy * (eh / 2) * 0.4
                pygame.draw.circle(surface, (8, 8, 12), (int(px), int(py)), pr)

        if cfg.eye_shape == "angry":
            self._draw_brow(surface, rect, mirror)

    def _draw_x(self, surface, cx, cy, color):
        pygame = self._pygame
        r = int(self._rx * 0.9)
        pygame.draw.line(surface, color, (cx - r, cy - r), (cx + r, cy + r), 10)
        pygame.draw.line(surface, color, (cx + r, cy - r), (cx - r, cy + r), 10)

    def _draw_brow(self, surface, rect, mirror):
        pygame = self._pygame
        top = rect.top
        if not mirror:  # left eye: outer high, inner low
            pts = [rect.topleft, (rect.right, top), (rect.right, top + rect.height // 2)]
        else:           # right eye: inner low, outer high
            pts = [rect.topright, (rect.left, top), (rect.left, top + rect.height // 2)]
        pygame.draw.polygon(surface, config.BACKGROUND_COLOR, pts)
