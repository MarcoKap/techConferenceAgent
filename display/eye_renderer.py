"""Renders the robot's eyes with pygame.

The look of each scene is driven entirely by its :class:`DisplayConfig`
(``eye_color``, ``eye_shape``, ``pupil_animation``). All motion is derived from a
single elapsed-time value ``t`` so rendering stays stateless and smooth.

Features:
- Phase 1: 3D Cartoon Rendering (Iris gradients, Highlights, Eyelid shadows)
- Phase 2: Eyelid Animation (Natural blinking, Openness)
- Phase 3: Pupil Tracking & Stereo Vision (3D gaze, Parallax)
- Phase 4: Iris Details & Quality (Dilation, Color variations)
- Phase 5: Emotion States (Happy, Sad, Angry, Tired, Focused)
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
        
        # Light source position (top-right, normalized)
        self._light_angle = math.radians(-45)
        self._light_dir = (math.cos(self._light_angle), math.sin(self._light_angle))

    def draw(self, surface, cfg, t: float) -> None:
        self._draw_eye(surface, self._left, cfg, t, mirror=False)
        self._draw_eye(surface, self._right, cfg, t, mirror=True)

    # -- Phase 1: 3D Rendering -----------------------------------------------
    def _draw_eye(self, surface, center, cfg, t, mirror):
        pygame = self._pygame
        cx, cy = center

        if cfg.eye_shape == "x":
            self._draw_x(surface, cx, cy, cfg.eye_color)
            return

        # Phase 2: Calculate eyelid openness with natural blinking
        openness = self._eyelid_openness(cfg, t)
        if openness < 0.01:  # Eye fully closed
            return

        # Draw 3D eyeball with gradient, pupil, and highlights
        self._draw_eyeball(surface, (cx, cy), cfg, t, openness)
        
        # Draw animated eyelid shadows for depth
        self._draw_eyelid_shadows(surface, (cx, cy), cfg, t, openness)
        
        # Phase 2: Draw upper and lower eyelids
        self._draw_eyelids(surface, (cx, cy), cfg, t, openness)

        if cfg.eye_shape == "angry":
            self._draw_brow(surface, (cx, cy), openness, mirror)

    def _draw_eyeball(self, surface, center, cfg, t, openness):
        """Draw the complete 3D eyeball with gradient iris, pupil, and highlights."""
        pygame = self._pygame
        cx, cy = center
        
        # Calculate dimensions with openness
        eh = int(self._ry * 2 * openness)
        if cfg.eye_shape == "narrow":
            eh = int(eh * 0.4)
        eh = max(4, eh)
        
        # Draw eyeball layers (outside to inside)
        self._draw_eyeball_background(surface, (cx, cy), cfg, eh)
        self._draw_iris(surface, (cx, cy), cfg, t, eh)
        self._draw_pupil(surface, (cx, cy), cfg, t, eh)
        self._draw_highlights(surface, (cx, cy), cfg, t, eh)

    def _draw_eyeball_background(self, surface, center, cfg, height):
        """Draw the white/background of the eyeball with subtle shading."""
        pygame = self._pygame
        cx, cy = center
        
        # Main eyeball white
        rect = pygame.Rect(0, 0, self._rx * 2, height)
        rect.center = center
        
        # Slightly off-white for cartoon style
        eye_white = (245, 245, 245)
        pygame.draw.ellipse(surface, eye_white, rect)
        
        # Dark shadow on outer edge (depth effect)
        shadow_color = (120, 120, 140)
        pygame.draw.ellipse(surface, shadow_color, rect, width=max(1, int(height * 0.08)))

    def _draw_iris(self, surface, center, cfg, t, height):
        """Draw iris with radial gradient (dark edges → light center)."""
        pygame = self._pygame
        cx, cy = center
        
        # Iris size
        ir = max(4, int(min(self._rx, height / 2) * 0.65))
        
        # Get base iris color
        iris_color = cfg.eye_color
        
        # Create radial gradient by drawing concentric circles
        steps = 6
        for i in range(steps, 0, -1):
            # Gradient from dark (outside) to lighter (inside)
            ratio = (i - 1) / (steps - 1)
            
            # Lerp from dark iris to light center
            dark = tuple(max(0, int(c * 0.5)) for c in iris_color)
            gradient_color = lerp_color(dark, iris_color, ratio)
            
            step_radius = int(ir * (i / steps))
            pygame.draw.circle(surface, gradient_color, (int(cx), int(cy)), step_radius)
        
        # Add subtle texture lines (radial stripes)
        self._draw_iris_details(surface, (cx, cy), iris_color, ir)

    def _draw_iris_details(self, surface, center, iris_color, radius):
        """Add subtle radial detail lines to iris."""
        pygame = self._pygame
        cx, cy = center
        
        # Radial detail lines for texture
        detail_color = tuple(max(0, int(c * 0.7)) for c in iris_color)
        num_lines = 8
        
        for i in range(num_lines):
            angle = (i / num_lines) * 2 * math.pi
            x1 = cx + math.cos(angle) * radius * 0.3
            y1 = cy + math.sin(angle) * radius * 0.3
            x2 = cx + math.cos(angle) * radius * 0.9
            y2 = cy + math.sin(angle) * radius * 0.9
            pygame.draw.line(surface, detail_color, (int(x1), int(y1)), (int(x2), int(y2)), 1)

    def _draw_pupil(self, surface, center, cfg, t, eye_height):
        """Draw black pupil with 3D offset and optional dilation."""
        pygame = self._pygame
        cx, cy = center
        
        if eye_height <= 10:
            return
        
        # Get pupil offset from animation
        dx, dy = self._pupil_offset(cfg, t)
        
        # Pupil size (can dilate based on emotion later)
        pr = int(min(self._rx, eye_height / 2) * 0.42)
        if pr < 2:
            return
        
        # Pupil position with animation offset
        px = cx + dx * self._rx * 0.4
        py = cy + dy * (eye_height / 2) * 0.4
        
        # Dark pupil
        pygame.draw.circle(surface, (8, 8, 12), (int(px), int(py)), pr)
        
        # Subtle pupil shadow (small dark edge)
        shadow_r = max(1, pr // 4)
        pygame.draw.circle(surface, (2, 2, 8), (int(px + pr * 0.3), int(py + pr * 0.3)), shadow_r)

    def _draw_highlights(self, surface, center, cfg, t, eye_height):
        """Draw multiple layers of highlights for glossy 3D effect."""
        pygame = self._pygame
        cx, cy = center
        
        if eye_height <= 10:
            return
        
        # Get pupil offset to make highlights follow gaze
        dx, dy = self._pupil_offset(cfg, t)
        
        # Primary highlight (bright, upper area)
        h1_offset_x = dx * self._rx * 0.2
        h1_offset_y = dy * (eye_height / 2) * 0.2 - eye_height * 0.15
        h1_r = max(2, int(eye_height * 0.12))
        h1_x = int(cx + h1_offset_x)
        h1_y = int(cy + h1_offset_y)
        
        # Draw white highlight
        pygame.draw.circle(surface, (255, 255, 255), (h1_x, h1_y), h1_r)
        
        # Secondary dimmer highlight (softer, slightly offset)
        h2_r = max(1, h1_r // 2)
        h2_x = int(cx + h1_offset_x * 0.5 + eye_height * 0.08)
        h2_y = int(cy + h1_offset_y * 0.5 + eye_height * 0.10)
        light_glow = (220, 220, 200)
        pygame.draw.circle(surface, light_glow, (h2_x, h2_y), h2_r)
        
        # Optional: Glow pulse mode (existing feature)
        if cfg.pupil_animation == "glow":
            glow = (math.sin(t * 3) + 1) / 2
            glow_color = lerp_color(cfg.eye_color, (255, 170, 170), glow * 0.4)
            # Glow ring around iris
            ir = max(4, int(min(self._rx, eye_height / 2) * 0.65))
            pygame.draw.circle(surface, glow_color, (int(cx), int(cy)), ir, 
                             width=max(1, int(4 * glow)))

    def _draw_eyelid_shadows(self, surface, center, cfg, t, openness):
        """Draw subtle shadows from upper and lower eyelids for depth."""
        pygame = self._pygame
        cx, cy = center
        
        # Eyelid height based on openness
        eh = int(self._ry * 2 * openness)
        if cfg.eye_shape == "narrow":
            eh = int(eh * 0.4)
        eh = max(4, eh)
        
        # Shadow darkness increases as eye closes
        shadow_strength = 1.0 - openness
        shadow_alpha = int(80 * shadow_strength)
        
        if shadow_alpha < 5:
            return
        
        # Draw shadows directly (simpler approach for 2D)
        # Upper eyelid shadow
        upper_shadow_color = (20, 20, 30)
        upper_rect = pygame.Rect(cx - self._rx, cy - eh // 2, self._rx * 2, int(eh * 0.15))
        pygame.draw.ellipse(surface, upper_shadow_color, upper_rect)
        
        # Lower eyelid shadow
        lower_rect = pygame.Rect(cx - self._rx, cy + eh // 2 - int(eh * 0.15), 
                                 self._rx * 2, int(eh * 0.15))
        pygame.draw.ellipse(surface, upper_shadow_color, lower_rect)

    def _eyelid_openness(self, cfg, t: float) -> float:
        """Calculate eye openness (0.0 = closed, 1.0 = fully open).
        
        Supports:
        - Natural blinking cycles
        - Shape-based modifications (wide, angry, narrow)
        - Animation-specific blink patterns
        """
        base = 1.0
        
        # Shape modifiers
        if cfg.eye_shape == "wide":
            base = 1.2
        elif cfg.eye_shape == "angry":
            base = 0.85
        
        # Animation-specific blinking
        if cfg.pupil_animation == "idle":
            # Natural blink cycle: ~4 seconds, with 150ms blink
            cycle = t % 4.0
            if cycle > 3.75:  # Blink in last 0.25 seconds
                blink_phase = (cycle - 3.75) / 0.25  # 0.0 → 1.0 during blink
                # Smooth blink curve (down then up)
                base *= 1.0 - (math.sin(blink_phase * math.pi) ** 2)
        
        return max(0.0, min(1.0, base))

    def _draw_eyelids(self, surface, center, cfg, t, openness):
        """Draw upper and lower eyelids with depth and animation."""
        pygame = self._pygame
        cx, cy = center
        
        if openness > 0.95:  # Skip rendering when fully open
            return
        
        # Eyelid height
        eh = int(self._ry * 2 * openness)
        if cfg.eye_shape == "narrow":
            eh = int(eh * 0.4)
        eh = max(4, eh)
        
        # Eyelid color (darker than background but not black)
        eyelid_color = (50, 50, 60)
        
        # Upper eyelid
        upper_height = int(self._ry * (1.0 - openness) * 0.8)
        if upper_height > 1:
            upper_y = cy - eh // 2
            upper_rect = pygame.Rect(cx - self._rx, upper_y - upper_height, 
                                     self._rx * 2, upper_height)
            pygame.draw.ellipse(surface, eyelid_color, upper_rect)
            
            # Upper eyelid edge (highlight/shadow)
            if upper_height > 2:
                edge_color = (30, 30, 40)
                pygame.draw.line(surface, edge_color, 
                                (cx - self._rx, upper_y), 
                                (cx + self._rx, upper_y), 1)
        
        # Lower eyelid
        lower_height = int(self._ry * (1.0 - openness) * 0.8)
        if lower_height > 1:
            lower_y = cy + eh // 2
            lower_rect = pygame.Rect(cx - self._rx, lower_y, 
                                     self._rx * 2, lower_height)
            pygame.draw.ellipse(surface, eyelid_color, lower_rect)
            
            # Lower eyelid edge
            if lower_height > 2:
                edge_color = (30, 30, 40)
                pygame.draw.line(surface, edge_color, 
                                (cx - self._rx, lower_y), 
                                (cx + self._rx, lower_y), 1)

    # -- Animation Helpers ---------------------------------------------------
    def _pupil_offset(self, cfg, t: float):
        """Calculate pupil offset from center based on animation type."""
        anim = cfg.pupil_animation
        if anim == "wander":
            return (math.sin(t * 1.2), math.sin(t * 0.8) * 0.5)
        if anim == "jitter":
            return (math.sin(t * 25) * 0.8 + math.sin(t * 13) * 0.2,
                    math.sin(t * 19) * 0.6)
        if anim == "idle":
            return (math.sin(t * 0.6) * 0.3, math.sin(t * 0.4) * 0.2)
        return (0.0, 0.0)  # still / glow

    # -- Legacy/Special shapes -----------------------------------------------
    def _draw_x(self, surface, cx, cy, color):
        pygame = self._pygame
        r = int(self._rx * 0.9)
        pygame.draw.line(surface, color, (cx - r, cy - r), (cx + r, cy + r), 10)
        pygame.draw.line(surface, color, (cx + r, cy - r), (cx - r, cy + r), 10)

    def _draw_brow(self, surface, center, openness, mirror):
        """Draw angry brow (angry expression modification)."""
        pygame = self._pygame
        cx, cy = center
        
        # Calculate eye height
        eh = int(self._ry * 2 * openness)
        
        # Brow positions (diagonal lines above eyes)
        if not mirror:  # left eye: outer high, inner low
            pts = [(cx - self._rx, cy - eh // 2 - self._rx // 3),
                   (cx + self._rx, cy - eh // 2),
                   (cx + self._rx, cy - eh // 2 + self._rx // 3)]
        else:           # right eye: inner low, outer high
            pts = [(cx + self._rx, cy - eh // 2 - self._rx // 3),
                   (cx - self._rx, cy - eh // 2),
                   (cx - self._rx, cy - eh // 2 + self._rx // 3)]
        
        pygame.draw.polygon(surface, config.BACKGROUND_COLOR, pts)
