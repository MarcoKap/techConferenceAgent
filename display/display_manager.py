"""Owns the pygame window and the main render loop.

The display runs on the main thread (pygame requires this) at ~30 fps. Each
frame it: forwards input events to the button handler, drains button events into
scene transitions, then renders the current scene's eyes and mouth. All hardware
animations (LEDs, servo, audio) run independently in their own threads.
"""

import math
import time

import config
from display.eye_renderer import EyeRenderer
from display.mouth_renderer import MouthRenderer
from display.gif_renderer import GifRenderer
from hardware import button_events


class DisplayManager:
    def __init__(self):
        import pygame

        self._pygame = pygame
        pygame.init()
        flags = pygame.FULLSCREEN if config.FULLSCREEN else 0
        self._screen = pygame.display.set_mode(
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT), flags
        )
        pygame.display.set_caption("Conference Robot")
        if config.FULLSCREEN:
            pygame.mouse.set_visible(False)
        self._clock = pygame.time.Clock()
        self._eye = EyeRenderer(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        self._mouth = MouthRenderer(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        self._gif = GifRenderer(pygame)
        # half-width renderers used for the split-layout printer scene
        _hw = config.SCREEN_WIDTH // 2
        self._eye_left = EyeRenderer(_hw, config.SCREEN_HEIGHT)
        self._mouth_left = MouthRenderer(_hw, config.SCREEN_HEIGHT)
        self._left_surf = pygame.Surface((_hw, config.SCREEN_HEIGHT))
        self._font = pygame.font.SysFont("consolas", 22)
        self._font_big = pygame.font.SysFont("consolas", 30, bold=True)
        self._font_mid = pygame.font.SysFont("consolas", 24, bold=True)
        self.running = True

    def run(self, scene_manager, button_handler, event_queue) -> None:
        pygame = self._pygame
        start = time.monotonic()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif (event.type == pygame.KEYDOWN
                      and event.key == pygame.K_ESCAPE):
                    self.running = False
                elif (event.type == pygame.KEYDOWN
                      and event.key == pygame.K_p):
                    event_queue.put(button_events.PRINT_TEST)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._queue_touch_event(event.pos, event_queue)
                elif event.type == pygame.FINGERDOWN:
                    px = int(event.x * config.SCREEN_WIDTH)
                    py = int(event.y * config.SCREEN_HEIGHT)
                    self._queue_touch_event((px, py), event_queue)
                button_handler.handle_pygame_event(event)

            while not event_queue.empty():
                ev = event_queue.get()
                if ev == button_events.NEXT:
                    scene_manager.next()
                elif ev == button_events.PREV:
                    scene_manager.prev()
                elif ev == button_events.PRINT_TEST:
                    scene_manager.print_test()
                elif ev == button_events.PRINT_SCENE:
                    scene_manager.print_current_scene_pdf()

            scene = scene_manager.current_scene
            t = time.monotonic() - start
            self._screen.fill(config.BACKGROUND_COLOR)
            self._draw_scene_visual(scene, t)
            self._draw_caption(scene_manager)
            pygame.display.flip()
            self._clock.tick(config.FPS)

    def _queue_touch_event(self, pos: tuple[int, int], event_queue) -> None:
        x, _ = pos
        left_edge = int(config.SCREEN_WIDTH * config.TOUCH_PREV_ZONE_RATIO)
        right_edge = int(config.SCREEN_WIDTH * config.TOUCH_NEXT_ZONE_RATIO)
        if x <= left_edge:
            event_queue.put(button_events.PREV)
        elif x >= right_edge:
            event_queue.put(button_events.NEXT)
        else:
            event_queue.put(button_events.PRINT_SCENE)

    def _draw_scene_visual(self, scene, t: float) -> None:
        mode = scene.display.visual_mode
        if mode == "openclaw_intro":
            self._draw_openclaw_intro(t)
            return
        if mode == "multi_faces":
            self._draw_multi_faces(scene, t)
            return
        if mode == "tool_control":
            self._draw_tool_control(scene, t)
            return
        if mode == "printer_leak":
            self._draw_printer_leak(scene, t)
            return
        if mode == "hacked_chaos":
            self._draw_hacked_chaos(t)
            return
        if mode == "identity":
            self._draw_identity(scene, t)
            return

        self._eye.draw(self._screen, scene.display, t)
        self._mouth.draw(self._screen, scene.display, t)
        self._draw_overlay_lines(scene.display.overlay_lines)

    def _draw_overlay_lines(self, lines: tuple[str, ...]) -> None:
        y = 20
        for line in lines[:4]:
            surf = self._font_mid.render(line, True, (220, 220, 220))
            rect = surf.get_rect(center=(config.SCREEN_WIDTH // 2, y))
            self._screen.blit(surf, rect)
            y += 28

    def _draw_openclaw_intro(self, t: float) -> None:
        """Stylised red lobster mascot with animated opening/closing claws."""
        pygame = self._pygame
        cx = config.SCREEN_WIDTH // 2
        cy = int(config.SCREEN_HEIGHT * 0.50)

        RED      = (210, 25, 25)
        DARK_RED = (130,  8,  8)
        BRIGHT   = (255, 80, 55)

        # claws cycle open→closed continuously
        claw_open = (math.sin(t * 2.2) + 1) / 2  # 0 = closed, 1 = fully open

        # ── tail fan ─────────────────────────────────────────────────────
        fan_cy = cy + 65 + 5 * 27 + 13
        for a_deg in (-40, -20, 0, 20, 40):
            a = math.radians(90 + a_deg)
            pygame.draw.line(self._screen, RED,
                             (cx, fan_cy),
                             (cx + int(math.cos(a) * 30), fan_cy + int(math.sin(a) * 30)), 6)

        # ── tail segments ────────────────────────────────────────────────
        for i in range(5):
            sw = max(22, 88 - i * 14)
            sh = 26
            sy = cy + 65 + i * 27
            col = DARK_RED if i % 2 == 0 else RED
            pygame.draw.ellipse(self._screen, col,
                                pygame.Rect(cx - sw // 2, sy, sw, sh))
            pygame.draw.ellipse(self._screen, DARK_RED,
                                pygame.Rect(cx - sw // 2, sy, sw, sh), 2)

        # ── body ─────────────────────────────────────────────────────────
        pygame.draw.ellipse(self._screen, RED,      pygame.Rect(cx - 52, cy - 46, 104, 116))
        pygame.draw.ellipse(self._screen, DARK_RED, pygame.Rect(cx - 52, cy - 46, 104, 116), 3)
        # body ridge arcs
        for i in range(3):
            pygame.draw.arc(self._screen, DARK_RED,
                            pygame.Rect(cx - 38 + i * 6, cy - 32, 76 - i * 12, 52),
                            0.3, math.pi - 0.3, 2)

        # ── walking legs (3 pairs) ────────────────────────────────────────
        for side in (-1, 1):
            for li in range(3):
                lx = cx + side * 50
                ly = cy - 5 + li * 30
                end_x = cx + side * (90 + li * 5)
                end_y = cy + 32 + li * 28
                pygame.draw.line(self._screen, RED, (lx, ly), (end_x, end_y), 4)

        # ── claws ────────────────────────────────────────────────────────
        for side in (-1, 1):
            shoulder = (cx + side * 52, cy - 36)
            elbow    = (cx + side * 122, cy - 72)
            pivot    = (cx + side * 172, cy - 88)

            # arm segments
            pygame.draw.line(self._screen, RED, shoulder, elbow, 13)
            pygame.draw.circle(self._screen, RED,      elbow,  9)
            pygame.draw.circle(self._screen, DARK_RED, elbow,  9, 2)
            pygame.draw.line(self._screen, RED, elbow, pivot, 11)
            pygame.draw.circle(self._screen, RED,      pivot, 15)
            pygame.draw.circle(self._screen, DARK_RED, pivot, 15, 2)
            pygame.draw.circle(self._screen, BRIGHT,
                               (pivot[0] - side * 4, pivot[1] - 4), 6)

            # two fingers: upper fixed, lower opens downward
            spread      = claw_open * 40          # degrees
            base_angle  = 0.0 if side > 0 else 180.0
            upper_rad   = math.radians(base_angle - spread / 2)
            lower_rad   = math.radians(base_angle + spread / 2)
            finger_len  = 48

            for angle_rad in (upper_rad, lower_rad):
                tip = (pivot[0] + int(math.cos(angle_rad) * finger_len),
                       pivot[1] + int(math.sin(angle_rad) * finger_len))
                pygame.draw.line(self._screen, RED, pivot, tip, 9)
                pygame.draw.circle(self._screen, DARK_RED, tip, 6)

        # ── head / carapace ──────────────────────────────────────────────
        pygame.draw.ellipse(self._screen, RED,      pygame.Rect(cx - 42, cy - 104, 84, 62))
        pygame.draw.ellipse(self._screen, DARK_RED, pygame.Rect(cx - 42, cy - 104, 84, 62), 3)

        # ── eye stalks ───────────────────────────────────────────────────
        for ex in (-18, 18):
            pygame.draw.line(self._screen, DARK_RED,
                             (cx + ex, cy - 102), (cx + ex, cy - 122), 5)
            pygame.draw.circle(self._screen, (18, 18, 18), (cx + ex, cy - 126), 8)
            pygame.draw.circle(self._screen, (50, 210, 80), (cx + ex, cy - 126), 5)

        # ── antennae ─────────────────────────────────────────────────────
        pygame.draw.line(self._screen, DARK_RED,
                         (cx - 22, cy - 101), (cx - 115, cy - 188), 3)
        pygame.draw.line(self._screen, DARK_RED,
                         (cx + 22, cy - 101), (cx + 115, cy - 188), 3)
        pygame.draw.line(self._screen, RED,
                         (cx - 14, cy - 99), (cx - 62, cy - 136), 2)
        pygame.draw.line(self._screen, RED,
                         (cx + 14, cy - 99), (cx + 62, cy - 136), 2)

    def _draw_multi_faces(self, scene, t: float) -> None:
        self._draw_overlay_lines(scene.display.overlay_lines)
        eye_color = scene.display.eye_color
        count = 2 + int((math.sin(t * 0.7) + 1) * 7)
        count = min(count, 16)
        cols = 4
        spacing_x = config.SCREEN_WIDTH // (cols + 1)
        spacing_y = 100
        start_y = 100
        for i in range(count):
            col = i % cols
            row = i // cols
            cx = spacing_x * (col + 1)
            cy = start_y + row * spacing_y
            # mini robot face
            face_r = 30
            self._pygame.draw.circle(self._screen, (22, 22, 32), (cx, cy), face_r)
            self._pygame.draw.circle(self._screen, (55, 55, 70), (cx, cy), face_r, 2)
            # mini eyes with pulse
            pulse = (math.sin(t * 2.2 + i * 0.9) + 1) / 2
            ec = tuple(int(c * (0.45 + 0.55 * pulse)) for c in eye_color)
            ew, eh = 8, 5
            lx, rx = cx - 11, cx + 11
            ey = cy - 5
            self._pygame.draw.ellipse(
                self._screen, ec, self._pygame.Rect(lx - ew, ey - eh, ew * 2, eh * 2))
            self._pygame.draw.ellipse(
                self._screen, ec, self._pygame.Rect(rx - ew, ey - eh, ew * 2, eh * 2))
            # mini mouth
            self._pygame.draw.arc(
                self._screen, ec,
                self._pygame.Rect(cx - 10, cy + 5, 20, 12), math.pi, 2 * math.pi, 2)

    def _draw_identity(self, scene, t: float) -> None:
        """Scene 201 – floating identity-context labels orbit the robot face."""
        self._eye.draw(self._screen, scene.display, t)
        self._mouth.draw(self._screen, scene.display, t)
        self._draw_overlay_lines(scene.display.overlay_lines)

        labels = [
            "system_prompt", "user context", "permissions",
            "tool access", "memory", "identity?",
        ]
        cx = config.SCREEN_WIDTH // 2
        cy = int(config.SCREEN_HEIGHT * 0.42)
        for i, label in enumerate(labels):
            angle = (i / len(labels)) * 2 * math.pi + t * 0.28
            radius_x = int(config.SCREEN_WIDTH * 0.34)
            radius_y = int(config.SCREEN_HEIGHT * 0.30)
            lx = cx + math.cos(angle) * radius_x
            ly = cy + math.sin(angle) * radius_y
            brightness = int((math.sin(t * 0.9 + i * 1.3) + 1) * 70 + 80)
            color = (min(255, brightness + 20), min(255, brightness + 60), brightness)
            surf = self._font.render(f"[{label}]", True, color)
            rect = surf.get_rect(center=(int(lx), int(ly)))
            self._screen.blit(surf, rect)

    def _draw_tool_control(self, scene, t: float) -> None:
        self._eye.draw(self._screen, scene.display, t)
        self._mouth.draw(self._screen, scene.display, t)
        self._draw_overlay_lines(scene.display.overlay_lines)

        # joystick base
        pygame = self._pygame
        cx, cy = config.SCREEN_WIDTH // 2, int(config.SCREEN_HEIGHT * 0.72)
        base_w, base_h = 120, 50
        base_rect = pygame.Rect(cx - base_w // 2, cy - base_h // 2, base_w, base_h)
        pygame.draw.ellipse(self._screen, (70, 70, 80), base_rect)
        pygame.draw.ellipse(self._screen, (110, 110, 125), base_rect, 3)

        # animated stick (swings left-right)
        max_lean = 40
        lean = math.sin(t * 2.2) * max_lean
        stick_base_x = cx
        stick_base_y = cy - 8
        stick_top_x = cx + int(lean)
        stick_top_y = cy - 80
        pygame.draw.line(self._screen, (160, 160, 175),
                         (stick_base_x, stick_base_y),
                         (stick_top_x, stick_top_y), 10)

        # knob at the top
        knob_col = tuple(min(255, int(c * 1.2)) for c in scene.display.eye_color)
        pygame.draw.circle(self._screen, (40, 40, 50), (stick_top_x, stick_top_y), 20)
        pygame.draw.circle(self._screen, knob_col, (stick_top_x, stick_top_y), 17)
        pygame.draw.circle(self._screen, (220, 225, 255),
                           (stick_top_x - 5, stick_top_y - 5), 5)

        # direction indicator arrow below joystick
        arrow_y = cy + 36
        alpha = math.sin(t * 2.2)
        arrow_col = (
            int(80 + 80 * (1 - alpha)),
            int(140 + 60 * alpha),
            int(80 + 80 * alpha),
        )
        arr_x = cx + int(lean * 0.7)
        arrow_pts = [
            (arr_x, arrow_y - 12),
            (arr_x + 10, arrow_y),
            (arr_x - 10, arrow_y),
        ]
        pygame.draw.polygon(self._screen, arrow_col, arrow_pts)

    def _draw_printer_leak(self, scene, t: float) -> None:
        """Scene 501 – face left, paper grows upward on the right."""
        pygame = self._pygame
        hw = config.SCREEN_WIDTH // 2

        # ── left side: robot face ────────────────────────────────────────
        self._left_surf.fill(config.BACKGROUND_COLOR)
        self._eye_left.draw(self._left_surf, scene.display, t)
        self._mouth_left.draw(self._left_surf, scene.display, t)
        self._screen.blit(self._left_surf, (0, 0))

        # ── right side: paper grows upward from bottom ───────────────────
        PAPER_START_T = 2.5
        if t > PAPER_START_T:
            paper_cx   = hw + hw // 2          # centre of right half
            paper_w    = int(hw * 0.65)
            paper_bottom = config.SCREEN_HEIGHT - 20
            paper_len  = min(
                int((t - PAPER_START_T) * 110),
                paper_bottom - 20,
            )
            if paper_len > 0:
                paper_top  = paper_bottom - paper_len
                paper_rect = pygame.Rect(paper_cx - paper_w // 2, paper_top,
                                         paper_w, paper_len)
                pygame.draw.rect(self._screen, (238, 238, 232), paper_rect)
                pygame.draw.rect(self._screen, (180, 178, 172), paper_rect, 1)

                # scrolling hinted text lines
                scroll   = int((t - PAPER_START_T) * 40)
                line_h   = 14
                margin   = 14
                widths   = [0.75, 0.45, 0.60, 0.80, 0.35, 0.65, 0.50, 0.70]
                num_rows = paper_len // line_h + 2
                for i in range(num_rows):
                    ly = paper_bottom - (
                        i * line_h - scroll % (line_h * len(widths))
                    ) - 6
                    if paper_top + 4 <= ly <= paper_bottom - 4:
                        w = int((paper_w - margin * 2) * widths[i % len(widths)])
                        pygame.draw.line(
                            self._screen, (160, 155, 148),
                            (paper_cx - paper_w // 2 + margin, ly),
                            (paper_cx - paper_w // 2 + margin + w, ly), 2)

    def _draw_hacked_chaos(self, t: float) -> None:
        flicker = int((math.sin(t * 17.0) + 1) * 50)
        self._screen.fill((flicker + 8, 0, 0))

        shake_x = int(math.sin(t * 22) * 6)
        shake_y = int(math.cos(t * 17) * 3)

        # Warning text
        msg = self._font_big.render("⚠  YOU ARE HACKED!  ⚠", True, (255, 255, 255))
        msg2 = self._font_big.render("SYSTEM COMPROMISED", True, (255, 80, 80))
        self._screen.blit(msg, msg.get_rect(centerx=config.SCREEN_WIDTH // 2 + shake_x, top=60 + shake_y))
        self._screen.blit(msg2, msg2.get_rect(centerx=config.SCREEN_WIDTH // 2 + shake_x, top=110 + shake_y))

        # Skull face in the centre
        cx, cy = config.SCREEN_WIDTH // 2, 290
        pygame = self._pygame
        skull_col = (190, 190, 195)
        # head
        pygame.draw.circle(self._screen, (28, 28, 28), (cx, cy), 72)
        pygame.draw.circle(self._screen, skull_col, (cx, cy), 72, 3)
        # eye sockets
        pygame.draw.ellipse(self._screen, (10, 10, 10),
                            pygame.Rect(cx - 42, cy - 22, 34, 30))
        pygame.draw.ellipse(self._screen, (10, 10, 10),
                            pygame.Rect(cx + 8, cy - 22, 34, 30))
        # X in each socket
        x_col = (210, 50, 50)
        for ox in (-28, 25):
            bx = cx + ox
            pygame.draw.line(self._screen, x_col, (bx - 12, cy - 20), (bx + 12, cy + 6), 3)
            pygame.draw.line(self._screen, x_col, (bx + 12, cy - 20), (bx - 12, cy + 6), 3)
        # nose
        pygame.draw.polygon(self._screen, skull_col,
                            [(cx, cy + 14), (cx - 8, cy + 28), (cx + 8, cy + 28)])
        # teeth
        tooth_y = cy + 38
        for j in range(6):
            tx = cx - 36 + j * 14
            pygame.draw.rect(self._screen, skull_col,
                             pygame.Rect(tx, tooth_y, 10, 20), border_radius=2)

        # bottom caption
        msg3 = self._font.render(
            "Agent compromised — trust boundary violated", True, (180, 55, 55))
        self._screen.blit(msg3, msg3.get_rect(
            centerx=config.SCREEN_WIDTH // 2 + shake_x // 2, top=400 + shake_y))

    def _draw_caption(self, scene_manager) -> None:
        scene = scene_manager.current_scene
        index = scene_manager.current_index + 1
        total = scene_manager.scene_count
        label = f"[{index}/{total}] {scene.name}   Touch: links/rechts wechseln, mitte drucken"
        surf = self._font.render(label, True, (90, 90, 90))
        self._screen.blit(surf, (20, config.SCREEN_HEIGHT - 38))

    def close(self) -> None:
        try:
            self._pygame.quit()
        except Exception:
            pass
