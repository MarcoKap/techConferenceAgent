"""Owns the pygame window and the main render loop.

The display runs on the main thread (pygame requires this) at ~30 fps. Each
frame it: forwards input events to the button handler, drains button events into
scene transitions, then renders the current scene's eyes and mouth. All hardware
animations (LEDs, servo, audio) run independently in their own threads.
"""

import time

import config
from display.eye_renderer import EyeRenderer
from display.mouth_renderer import MouthRenderer
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

    def _draw_multi_faces(self, scene, t: float) -> None:
        import math

        self._draw_overlay_lines(scene.display.overlay_lines)
        count = 2 + int((math.sin(t * 0.7) + 1) * 6)
        cols = 4
        spacing_x = config.SCREEN_WIDTH // (cols + 1)
        spacing_y = 90
        start_y = 120
        for i in range(count):
            col = i % cols
            row = i // cols
            cx = spacing_x * (col + 1)
            cy = start_y + row * spacing_y
            # draw stylized mini face dots so accumulation is visible
            self._pygame.draw.circle(self._screen, (180, 180, 180), (cx - 10, cy), 8)
            self._pygame.draw.circle(self._screen, (180, 180, 180), (cx + 10, cy), 8)
            self._pygame.draw.arc(self._screen, (150, 150, 150), (cx - 20, cy + 8, 40, 20), 0.2, 2.9, 2)

    def _draw_tool_control(self, scene, t: float) -> None:
        import math

        self._eye.draw(self._screen, scene.display, t)
        self._mouth.draw(self._screen, scene.display, t)
        self._draw_overlay_lines(scene.display.overlay_lines)

        # robotic arm
        base = (560, 320)
        joint = (640, 250)
        end = (680 + int(math.sin(t * 1.7) * 22), 180)
        self._pygame.draw.circle(self._screen, (120, 120, 120), base, 18)
        self._pygame.draw.line(self._screen, (170, 170, 170), base, joint, 8)
        self._pygame.draw.line(self._screen, (170, 170, 170), joint, end, 8)
        self._pygame.draw.rect(self._screen, (180, 120, 80), (end[0] - 16, end[1] - 8, 32, 16), 2)

        # remote control icon
        self._pygame.draw.rect(self._screen, (90, 90, 90), (90, 290, 90, 150), border_radius=10)
        self._pygame.draw.circle(self._screen, (220, 70, 70), (135, 325), 10)
        self._pygame.draw.circle(self._screen, (70, 170, 220), (120, 360), 8)
        self._pygame.draw.circle(self._screen, (70, 170, 220), (150, 360), 8)

    def _draw_printer_leak(self, scene, t: float) -> None:
        import math

        self._eye.draw(self._screen, scene.display, t)
        self._mouth.draw(self._screen, scene.display, t)
        self._draw_overlay_lines(scene.display.overlay_lines)

        # printer body + moving paper
        px, py = 520, 250
        self._pygame.draw.rect(self._screen, (140, 140, 140), (px, py, 180, 100), border_radius=8)
        self._pygame.draw.rect(self._screen, (220, 220, 220), (px + 20, py - 80, 140, 80))
        flow = int((math.sin(t * 2.5) + 1) * 18)
        self._pygame.draw.line(self._screen, (40, 40, 40), (px + 35, py - 65 + flow), (px + 145, py - 65 + flow), 2)

        if t > 60:
            laugh = self._font_big.render("HA!", True, (255, 120, 120))
            self._screen.blit(laugh, (340, 140))

    def _draw_hacked_chaos(self, t: float) -> None:
        import math

        flicker = int((math.sin(t * 17.0) + 1) * 70)
        self._screen.fill((flicker, 0, 0))
        msg = self._font_big.render("YOU ARE HACKED!", True, (255, 255, 255))
        msg2 = self._font_big.render("X X X", True, (230, 230, 230))
        self._screen.blit(msg, (170 + int(math.sin(t * 6) * 8), 130))
        self._screen.blit(msg2, (315 + int(math.cos(t * 8) * 8), 210))
        self._screen.blit(msg, (170 + int(math.sin(t * 5) * 8), 290))

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
