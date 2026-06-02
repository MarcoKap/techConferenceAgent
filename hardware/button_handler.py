"""Real button handler using RPi.GPIO with hardware debounce.

Two momentary buttons (next / previous) are wired to GPIO pins with internal
pull-ups. Falling-edge interrupts push :mod:`hardware.button_events` values into
a shared :class:`queue.Queue` consumed by the main loop.
"""

import config
from hardware.button_events import NEXT, PREV


class ButtonHandler:
    def __init__(self, event_queue):
        self._queue = event_queue
        self._gpio = None

    def start(self) -> None:
        import RPi.GPIO as GPIO

        self._gpio = GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(config.BUTTON_NEXT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(config.BUTTON_PREV_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(
            config.BUTTON_NEXT_PIN, GPIO.FALLING,
            callback=self._on_next, bouncetime=config.BUTTON_DEBOUNCE_MS,
        )
        GPIO.add_event_detect(
            config.BUTTON_PREV_PIN, GPIO.FALLING,
            callback=self._on_prev, bouncetime=config.BUTTON_DEBOUNCE_MS,
        )

    def _on_next(self, _channel) -> None:
        self._queue.put(NEXT)

    def _on_prev(self, _channel) -> None:
        self._queue.put(PREV)

    def handle_pygame_event(self, _event) -> None:
        """No-op on real hardware; buttons come from GPIO interrupts."""

    def stop(self) -> None:
        if self._gpio is not None:
            try:
                self._gpio.cleanup()
            except Exception:
                pass
            self._gpio = None

    def close(self) -> None:
        self.stop()
