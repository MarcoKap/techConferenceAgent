"""No-op servo controller for setups where the PCA9685 I2C board is unavailable.

The real implementation is in servo_controller.py and can be re-enabled via
hardware/__init__.py once the I2C issues are resolved.
"""

from hardware.base import ThreadedController, interruptible_sleep


class NoopServoController(ThreadedController):
    def _run(self, cfg, stop_event):
        while not stop_event.is_set():
            if not interruptible_sleep(stop_event, 0.2):
                return

    def close(self):
        self.stop()
