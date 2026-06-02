"""Mock button handler: arrow keys replace the physical GPIO buttons.

Key events arrive via :meth:`handle_pygame_event`, which the display loop calls
for every pygame event (the display owns the only pygame window/event queue).
"""

from hardware.button_events import NEXT, PREV


class MockButtonHandler:
    def __init__(self, event_queue):
        self._queue = event_queue

    def start(self) -> None:
        print("[mock-button] Steuerung: \u2190 zurueck / \u2192 weiter / ESC beenden")

    def handle_pygame_event(self, event) -> None:
        import pygame

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self._queue.put(NEXT)
            elif event.key == pygame.K_LEFT:
                self._queue.put(PREV)

    def stop(self) -> None:
        pass

    def close(self) -> None:
        pass
