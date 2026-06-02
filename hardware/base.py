"""Small base class giving controllers a uniform threaded animation lifecycle.

Subclasses implement :meth:`_run`, an animation loop that must poll
``stop_event.is_set()`` regularly and exit promptly when it becomes set.
"""

import threading
import time
from typing import Tuple

RGB = Tuple[int, int, int]


def interruptible_sleep(stop_event: threading.Event, seconds: float,
                        step: float = 0.02) -> bool:
    """Sleep up to ``seconds`` but wake early if ``stop_event`` is set.

    Returns ``True`` if the full duration elapsed, ``False`` if interrupted.
    """
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if stop_event.is_set():
            return False
        time.sleep(min(step, max(0.0, deadline - time.monotonic())))
    return not stop_event.is_set()


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def lerp_color(a: RGB, b: RGB, t: float) -> RGB:
    t = max(0.0, min(1.0, t))
    return (int(lerp(a[0], b[0], t)), int(lerp(a[1], b[1], t)),
            int(lerp(a[2], b[2], t)))


class ThreadedController:
    def __init__(self):
        self._stop_event: threading.Event | None = None
        self._thread: threading.Thread | None = None

    def _run(self, scene_config, stop_event: threading.Event) -> None:
        raise NotImplementedError

    def start(self, scene_config) -> None:
        """Stop any running animation and start the one described by config."""
        self.stop()
        self._stop_event = threading.Event()
        self._thread = threading.Thread(
            target=self._run,
            args=(scene_config, self._stop_event),
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        """Signal the running animation to stop and wait for it to finish."""
        if self._stop_event is not None:
            self._stop_event.set()
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        self._thread = None
        self._stop_event = None

    def close(self) -> None:
        self.stop()
