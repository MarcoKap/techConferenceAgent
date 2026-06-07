"""Renders the robot's eyes with pygame.

The look of each scene is driven entirely by its :class:`DisplayConfig`
(``eye_color``, ``eye_shape``, ``pupil_animation``). All motion is derived from a
single elapsed-time value ``t`` so rendering stays stateless and smooth.

Design: layered eye with socket rim → glow halo → iris → inner iris ring →
pupil → specular highlight. This gives visual depth and a distinctly robotic look.
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
            base = 1.3
        elif cfg.eye_shape == "angry":
            base = 0.9
        if cfg.pupil_animation == "idle":
            cycle = t % 4.0
            if cycle > 3.85:  # brief blink near the end of each cycle
                base *= 0.10
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
            eh = int(eh * 0.32)
        eh = max(4, eh)
        ew = self._rx * 2

        # ── socket rim (dark oval behind eye for depth) ────────────────
        rim = pygame.Rect(0, 0, ew + 12, eh + 10)
        rim.center = (cx, cy)
        pygame.draw.ellipse(surface, (14, 14, 22), rim)

        # ── glow halo (drawn before iris so it reads as outer aura) ───
        if cfg.pupil_animation == "glow":
            glow = (math.sin(t * 3.0) + 1) / 2
            for i in range(4, 0, -1):
                pad = i * 6
                g_rect = pygame.Rect(0, 0, ew + pad * 2, eh + pad)
                g_rect.center = (cx, cy)
                blend = min(1.0, glow * 0.55 * i / 4)
                gcolor = lerp_color(cfg.eye_color, (255, 80, 80), blend)
                pygame.draw.ellipse(surface, gcolor, g_rect, width=max(2, int(3 * glow) + 1))

        # ── iris ───────────────────────────────────────────────────────
        rect = pygame.Rect(0, 0, ew, eh)
        rect.center = (cx, cy)
        pygame.draw.ellipse(surface, cfg.eye_color, rect)

        # ── inner iris ring (darker centre gives depth) ────────────────
        if eh > 18:
            inner = pygame.Rect(0, 0, int(ew * 0.62), int(eh * 0.62))
            inner.center = (cx, cy)
            dark = tuple(max(0, int(c * 0.52)) for c in cfg.eye_color)
            pygame.draw.ellipse(surface, dark, inner)

        # ── pupil + specular highlight ─────────────────────────────────
        if eh > 10:
            dx, dy = self._pupil_offset(cfg, t)
            pr = int(min(self._rx, eh / 2) * 0.44)
            if pr > 1:
                px = int(cx + dx * self._rx * 0.38)
                py = int(cy + dy * (eh / 2) * 0.38)
                pygame.draw.circle(surface, (4, 4, 10), (px, py), pr)
                # specular highlight: small bright dot offset top-right
                if pr >= 4:
                    hx = px + max(1, pr // 3)
                    hy = py - max(1, pr // 3)
                    pygame.draw.circle(surface, (225, 235, 255), (hx, hy), max(2, pr // 4))

        # ── angry brow ────────────────────────────────────────────────
        if cfg.eye_shape == "angry":
            self._draw_brow(surface, rect, mirror, cfg.eye_color)

    def _draw_x(self, surface, cx, cy, color):
        pygame = self._pygame
        r = int(self._rx * 0.95)
        # dark socket
        pygame.draw.circle(surface, (16, 16, 26), (cx, cy), r + 8)
        # dim border ring
        border_col = tuple(max(0, c // 4) for c in color)
        pygame.draw.circle(surface, border_col, (cx, cy), r + 3)
        # X lines
        pygame.draw.line(surface, color, (cx - r, cy - r), (cx + r, cy + r), 11)
        pygame.draw.line(surface, color, (cx + r, cy - r), (cx - r, cy + r), 11)
        # centre dot
        pygame.draw.circle(surface, color, (cx, cy), max(3, r // 5))

    def _draw_brow(self, surface, rect, mirror, eye_color):
        pygame = self._pygame
        top = rect.top
        mid_h = rect.height // 2
        thick = max(5, rect.height // 5)
        if not mirror:  # left eye: outer high → inner low
            mask_pts = [rect.topleft, (rect.right, top), (rect.right, top + mid_h)]
            brow_pts = [
                (rect.left - 6, top - thick - 6),
                (rect.right + 2, top - 2),
                (rect.right + 2, top - 2 + thick),
                (rect.left - 6, top - 6 + thick),
            ]
        else:           # right eye: inner low → outer high
            mask_pts = [rect.topright, (rect.left, top), (rect.left, top + mid_h)]
            brow_pts = [
                (rect.left - 2, top - 2),
                (rect.right + 6, top - thick - 6),
                (rect.right + 6, top - 6 + thick),
                (rect.left - 2, top - 2 + thick),
            ]
        # cut the top of the iris with background colour
        pygame.draw.polygon(surface, config.BACKGROUND_COLOR, mask_pts)
        # draw visible brow in a brightened version of the eye colour
        brow_col = tuple(min(255, int(c * 1.3) + 30) for c in eye_color)
        pygame.draw.polygon(surface, brow_col, brow_pts)
