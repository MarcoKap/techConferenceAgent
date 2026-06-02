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
                button_handler.handle_pygame_event(event)

            while not event_queue.empty():
                ev = event_queue.get()
                if ev == button_events.NEXT:
                    scene_manager.next()
                elif ev == button_events.PREV:
                    scene_manager.prev()

            scene = scene_manager.current_scene
            t = time.monotonic() - start
            self._screen.fill(config.BACKGROUND_COLOR)
            self._eye.draw(self._screen, scene.display, t)
            self._mouth.draw(self._screen, scene.display, t)
            self._draw_caption(scene_manager)
            pygame.display.flip()
            self._clock.tick(config.FPS)

    def _draw_caption(self, scene_manager) -> None:
        scene = scene_manager.current_scene
        index = scene_manager.current_index + 1
        total = scene_manager.scene_count
        label = f"[{index}/{total}] {scene.name}"
        surf = self._font.render(label, True, (90, 90, 90))
        self._screen.blit(surf, (20, config.SCREEN_HEIGHT - 38))

    def close(self) -> None:
        try:
            self._pygame.quit()
        except Exception:
            pass
