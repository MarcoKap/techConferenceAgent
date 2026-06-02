"""Mock LED controller: logs the active animation to the console.

Mirrors the real controller's threaded lifecycle so scene transitions behave
identically during development.
"""

from hardware.base import ThreadedController, interruptible_sleep


class MockLedController(ThreadedController):
    def _run(self, cfg, stop_event):
        print(
            f"[mock-led] {cfg.animation_name} "
            f"primary={cfg.color_primary} secondary={cfg.color_secondary} "
            f"speed={cfg.speed}"
        )
        while not stop_event.is_set():
            if not interruptible_sleep(stop_event, 0.2):
                return

    def close(self):
        self.stop()
        print("[mock-led] off")
