"""Entry point for the conference robot.

Initialises the display and all hardware controllers (real on the Raspberry Pi,
mock on Windows/macOS), wires them into the :class:`SceneManager`, and runs the
pygame render loop on the main thread until the user quits.
"""

import queue

import config
from hardware import (
    AudioController,
    ButtonHandler,
    LedController,
    PrinterController,
    ServoController,
)
from display.display_manager import DisplayManager
from scene_manager import SceneManager


def main() -> None:
    print(f"Conference Robot starting (mock_hardware={config.IS_MOCK})")

    # Display first so pygame (and its mixer) is initialised before the audio
    # controller checks for an existing mixer.
    display = DisplayManager()

    led = LedController()
    servo = ServoController()
    audio = AudioController()
    printer = PrinterController()

    event_queue: "queue.Queue[str]" = queue.Queue()
    button = ButtonHandler(event_queue)

    scene_manager = SceneManager(led, servo, audio, printer)
    button.start()
    scene_manager.start()

    try:
        display.run(scene_manager, button, event_queue)
    finally:
        print("Shutting down...")
        button.close()
        led.close()
        servo.close()
        audio.close()
        printer.close()
        display.close()


if __name__ == "__main__":
    main()
