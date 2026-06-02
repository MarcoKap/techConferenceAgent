"""Real servo controller for head rotation via PCA9685 (I2C).

Each movement profile runs in the worker thread and polls ``stop_event`` so a
scene change interrupts it cleanly. Angles are clamped to the safe range from
:mod:`config`.
"""

import math

import config
from hardware.base import ThreadedController, interruptible_sleep


class ServoController(ThreadedController):
    def __init__(self):
        super().__init__()
        import board
        import busio
        from adafruit_pca9685 import PCA9685
        from adafruit_motor import servo

        i2c = busio.I2C(board.SCL, board.SDA)
        self._pca = PCA9685(i2c, address=config.PCA9685_I2C_ADDRESS)
        self._pca.frequency = config.PCA9685_FREQUENCY
        self._servo = servo.Servo(self._pca.channels[config.SERVO_CHANNEL])
        self._set_angle(config.SERVO_CENTER_ANGLE)

    def _set_angle(self, angle):
        angle = max(config.SERVO_MIN_ANGLE, min(config.SERVO_MAX_ANGLE, angle))
        self._servo.angle = angle

    def _run(self, cfg, stop_event):
        profiles = {
            "center": self._center,
            "slow_sweep": self._slow_sweep,
            "nod": self._nod,
            "shake": self._shake,
            "droop": self._droop,
        }
        profiles.get(cfg.angle_profile, self._center)(cfg, stop_event)

    # -- profiles -----------------------------------------------------------
    def _center(self, cfg, stop_event):
        phase = 0.0
        while not stop_event.is_set():
            sway = 6 * math.sin(phase)
            self._set_angle(config.SERVO_CENTER_ANGLE + sway)
            phase += 0.08 * cfg.speed
            if not interruptible_sleep(stop_event, 0.05):
                return

    def _slow_sweep(self, cfg, stop_event):
        amp = (config.SERVO_MAX_ANGLE - config.SERVO_MIN_ANGLE) / 2
        phase = 0.0
        while not stop_event.is_set():
            self._set_angle(config.SERVO_CENTER_ANGLE + amp * math.sin(phase))
            phase += 0.05 * cfg.speed
            if not interruptible_sleep(stop_event, 0.04):
                return

    def _nod(self, cfg, stop_event):
        self._set_angle(config.SERVO_MIN_ANGLE)
        if not interruptible_sleep(stop_event, 0.12):
            return
        self._set_angle(config.SERVO_MAX_ANGLE)
        if not interruptible_sleep(stop_event, 0.12):
            return
        self._set_angle(config.SERVO_CENTER_ANGLE)
        while not stop_event.is_set():
            if not interruptible_sleep(stop_event, 0.2):
                return

    def _shake(self, cfg, stop_event):
        amp = (config.SERVO_MAX_ANGLE - config.SERVO_MIN_ANGLE) / 2
        toggle = True
        while not stop_event.is_set():
            offset = amp if toggle else -amp
            self._set_angle(config.SERVO_CENTER_ANGLE + offset)
            toggle = not toggle
            if not interruptible_sleep(stop_event, 0.12 / max(cfg.speed, 0.1)):
                return

    def _droop(self, cfg, stop_event):
        self._set_angle(config.SERVO_MIN_ANGLE)
        while not stop_event.is_set():
            if not interruptible_sleep(stop_event, 0.2):
                return

    def close(self):
        self.stop()
        try:
            self._set_angle(config.SERVO_CENTER_ANGLE)
            self._pca.deinit()
        except Exception:
            pass
