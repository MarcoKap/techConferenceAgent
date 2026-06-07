"""No-op button handler for touchscreen-only setups.

Used on Raspberry Pi when no physical GPIO buttons are connected.
"""


class NoopButtonHandler:
    def __init__(self, _event_queue):
        pass

    def start(self) -> None:
        print("[button] GPIO buttons disabled; using touchscreen navigation")

    def handle_pygame_event(self, _event) -> None:
        pass

    def stop(self) -> None:
        pass

    def close(self) -> None:
        pass
