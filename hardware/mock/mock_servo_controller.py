"""Mock servo controller: logs the active movement profile to the console."""

from hardware.base import ThreadedController, interruptible_sleep


class MockServoController(ThreadedController):
    def _run(self, cfg, stop_event):
        print(f"[mock-servo] profile={cfg.angle_profile} speed={cfg.speed}")
        while not stop_event.is_set():
            if not interruptible_sleep(stop_event, 0.2):
                return

    def close(self):
        self.stop()
        print("[mock-servo] center")
