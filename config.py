"""Central configuration: hardware constants, platform detection, paths.

A single ``IS_MOCK`` flag drives the hardware factory in ``hardware/__init__.py``
so the exact same application runs on Windows/macOS (mock hardware) and on the
Raspberry Pi (real hardware).
"""

import os
import platform

# ---------------------------------------------------------------------------
# Platform detection
# ---------------------------------------------------------------------------
# Use mock hardware when we are not on Linux (RPi) or when explicitly forced.
IS_MOCK = platform.system() != "Linux" or os.getenv("MOCK_HARDWARE") == "1"

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
AUDIO_DIR = os.path.join(ASSETS_DIR, "audio")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")

# ---------------------------------------------------------------------------
# Buttons (GPIO, BCM numbering)
# ---------------------------------------------------------------------------
BUTTON_NEXT_PIN = 23
BUTTON_PREV_PIN = 24
BUTTON_DEBOUNCE_MS = 50

# ---------------------------------------------------------------------------
# WS2812B LED ring (rpi_ws281x)
# ---------------------------------------------------------------------------
LED_COUNT = 24
LED_PIN = 18            # GPIO 18 (PWM0). Use DMA channel 5 if audio runs on HDMI.
LED_FREQ_HZ = 800_000
LED_DMA = 10
LED_BRIGHTNESS = 128    # 0-255
LED_INVERT = False
LED_CHANNEL = 0

# ---------------------------------------------------------------------------
# Servo (PCA9685 over I2C)
# ---------------------------------------------------------------------------
PCA9685_I2C_ADDRESS = 0x40
PCA9685_FREQUENCY = 50      # Hz, standard for hobby servos
SERVO_CHANNEL = 0
SERVO_MIN_ANGLE = 30
SERVO_MAX_ANGLE = 150
SERVO_CENTER_ANGLE = 90

# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480
FPS = 30
# Fullscreen on the Pi, windowed during development for convenience.
FULLSCREEN = not IS_MOCK
BACKGROUND_COLOR = (0, 0, 0)

# ---------------------------------------------------------------------------
# Common colors (RGB)
# ---------------------------------------------------------------------------
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_BLUE = (40, 120, 255)
COLOR_GREEN = (40, 220, 140)
COLOR_YELLOW = (255, 215, 40)
COLOR_ORANGE = (255, 140, 20)
COLOR_RED = (255, 40, 40)
COLOR_PURPLE = (120, 20, 160)
COLOR_GREY = (120, 120, 120)
