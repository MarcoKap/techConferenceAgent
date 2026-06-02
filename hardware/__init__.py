"""Hardware factory.

Selects real or mock controller implementations based on :data:`config.IS_MOCK`
so the rest of the application is platform-agnostic.
"""

from config import IS_MOCK

if IS_MOCK:
    from hardware.mock.mock_button_handler import MockButtonHandler as ButtonHandler
    from hardware.mock.mock_led_controller import MockLedController as LedController
    from hardware.mock.mock_servo_controller import MockServoController as ServoController
    from hardware.mock.mock_audio_controller import MockAudioController as AudioController
else:
    from hardware.button_handler import ButtonHandler
    from hardware.led_controller import LedController
    from hardware.servo_controller import ServoController
    from hardware.audio_controller import AudioController

__all__ = ["ButtonHandler", "LedController", "ServoController", "AudioController"]
