"""Hardware factory.

Selects real or mock controller implementations based on :data:`config.IS_MOCK`
so the rest of the application is platform-agnostic.
"""

from config import IS_MOCK, USE_GPIO_BUTTONS
from hardware.printer_controller import PrinterController

if IS_MOCK:
    from hardware.mock.mock_button_handler import MockButtonHandler as ButtonHandler
    from hardware.mock.mock_led_controller import MockLedController as LedController
    from hardware.mock.mock_servo_controller import MockServoController as ServoController
    from hardware.mock.mock_audio_controller import MockAudioController as AudioController
else:
    if USE_GPIO_BUTTONS:
        from hardware.button_handler import ButtonHandler
    else:
        from hardware.noop_button_handler import NoopButtonHandler as ButtonHandler
    from hardware.noop_led_controller import NoopLedController as LedController
    from hardware.noop_servo_controller import NoopServoController as ServoController
    from hardware.audio_controller import AudioController

__all__ = [
    "ButtonHandler",
    "LedController",
    "ServoController",
    "AudioController",
    "PrinterController",
]
