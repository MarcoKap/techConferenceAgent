"""No-op LED controller for setups where the WS2812B ring is unavailable.

Used when rpi_ws281x / /dev/mem access is not available (e.g. permission issues).
The real implementation is in led_controller.py and can be re-enabled via
hardware/__init__.py once the ws2811 driver permissions are resolved.
"""

from hardware.base import ThreadedController, interruptible_sleep


class NoopLedController(ThreadedController):
    def _run(self, cfg, stop_event):
        while not stop_event.is_set():
            if not interruptible_sleep(stop_event, 0.2):
                return

    def close(self):
        self.stop()
