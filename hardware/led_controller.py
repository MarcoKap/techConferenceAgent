"""Real WS2812B LED ring controller (rpi_ws281x).

Exposes the named animations referenced by the scenes. Each animation runs in
the :class:`ThreadedController` worker thread and continuously polls
``stop_event`` so scene transitions are responsive.
"""

import math

import config
from hardware.base import ThreadedController, interruptible_sleep, lerp_color


class LedController(ThreadedController):
    def __init__(self):
        super().__init__()
        from rpi_ws281x import PixelStrip, Color

        self._Color = Color
        self._strip = PixelStrip(
            config.LED_COUNT, config.LED_PIN, config.LED_FREQ_HZ,
            config.LED_DMA, config.LED_INVERT, config.LED_BRIGHTNESS,
            config.LED_CHANNEL,
        )
        self._strip.begin()

    # -- low level helpers --------------------------------------------------
    def _fill(self, color):
        c = self._Color(color[0], color[1], color[2])
        for i in range(config.LED_COUNT):
            self._strip.setPixelColor(i, c)
        self._strip.show()

    def _set_pixels(self, colors):
        for i, color in enumerate(colors):
            self._strip.setPixelColor(i, self._Color(color[0], color[1], color[2]))
        self._strip.show()

    # -- dispatch -----------------------------------------------------------
    def _run(self, cfg, stop_event):
        animations = {
            "idle_pulse": self._idle_pulse,
            "thinking_swipe": self._thinking_swipe,
            "surprised_burst": self._surprised_burst,
            "alarm_flash": self._alarm_flash,
            "evil_glow": self._evil_glow,
            "error_off": self._error_off,
        }
        animations.get(cfg.animation_name, self._idle_pulse)(cfg, stop_event)

    # -- animations ---------------------------------------------------------
    def _idle_pulse(self, cfg, stop_event):
        phase = 0.0
        while not stop_event.is_set():
            t = (math.sin(phase) + 1) / 2
            self._fill(lerp_color(cfg.color_primary, cfg.color_secondary, t))
            phase += 0.15 * cfg.speed
            if not interruptible_sleep(stop_event, 0.03):
                return

    def _thinking_swipe(self, cfg, stop_event):
        n = config.LED_COUNT
        head = 0
        while not stop_event.is_set():
            colors = []
            for i in range(n):
                dist = min((i - head) % n, (head - i) % n)
                t = max(0.0, 1.0 - dist / 4.0)
                colors.append(lerp_color(cfg.color_secondary, cfg.color_primary, t))
            self._set_pixels(colors)
            head = (head + 1) % n
            if not interruptible_sleep(stop_event, 0.06 / max(cfg.speed, 0.1)):
                return

    def _surprised_burst(self, cfg, stop_event):
        self._fill(cfg.color_primary)
        if not interruptible_sleep(stop_event, 0.12):
            return
        while not stop_event.is_set():
            self._fill(cfg.color_secondary)
            if not interruptible_sleep(stop_event, 0.08 / max(cfg.speed, 0.1)):
                return
            self._fill(config.COLOR_BLACK)
            if not interruptible_sleep(stop_event, 0.08 / max(cfg.speed, 0.1)):
                return

    def _alarm_flash(self, cfg, stop_event):
        while not stop_event.is_set():
            self._fill(cfg.color_primary)
            if not interruptible_sleep(stop_event, 0.15 / max(cfg.speed, 0.1)):
                return
            self._fill(cfg.color_secondary)
            if not interruptible_sleep(stop_event, 0.15 / max(cfg.speed, 0.1)):
                return

    def _evil_glow(self, cfg, stop_event):
        phase = 0.0
        while not stop_event.is_set():
            t = (math.sin(phase) + 1) / 2
            self._fill(lerp_color(cfg.color_primary, cfg.color_secondary, t))
            phase += 0.05 * cfg.speed
            if not interruptible_sleep(stop_event, 0.04):
                return

    def _error_off(self, cfg, stop_event):
        self._fill(config.COLOR_BLACK)
        while not stop_event.is_set():
            if not interruptible_sleep(stop_event, 0.2):
                return

    def close(self):
        self.stop()
        try:
            self._fill(config.COLOR_BLACK)
        except Exception:
            pass
