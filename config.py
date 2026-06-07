"""Central configuration: hardware constants, platform detection, paths.

A single ``IS_MOCK`` flag drives the hardware factory in ``hardware/__init__.py``
so the exact same application runs on Windows/macOS (mock hardware) and on the
Raspberry Pi (real hardware).
"""

import os
import platform


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}

# ---------------------------------------------------------------------------
# Platform detection
# ---------------------------------------------------------------------------
# Use mock hardware when we are not on Linux (RPi) or when explicitly forced.
IS_MOCK = platform.system() != "Linux" or _env_flag("MOCK_HARDWARE")

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
# Set to 1 if physical GPIO buttons are connected on the Raspberry Pi.
USE_GPIO_BUTTONS = _env_flag("USE_GPIO_BUTTONS", default=False)

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
# Touch zones in the display: left zone = previous, right zone = next.
TOUCH_PREV_ZONE_RATIO = float(os.getenv("TOUCH_PREV_ZONE_RATIO", "0.35"))
TOUCH_NEXT_ZONE_RATIO = float(os.getenv("TOUCH_NEXT_ZONE_RATIO", "0.65"))

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

# ---------------------------------------------------------------------------
# Printer (CUPS via lp command)
# ---------------------------------------------------------------------------
# Enabled by default so printer tests work on macOS out of the box.
PRINTER_ENABLED = _env_flag("PRINTER_ENABLED", default=True)
# Optional CUPS destination name. If unset, the system default printer is used.
PRINTER_NAME = os.getenv("PRINTER_NAME")
# Backend: auto | cups | serial | raw
PRINTER_BACKEND = os.getenv("PRINTER_BACKEND", "auto").strip().lower()
# Serial settings for ESC/POS thermal printers.
PRINTER_SERIAL_PORT = os.getenv("PRINTER_SERIAL_PORT")
PRINTER_SERIAL_BAUDRATE = int(os.getenv("PRINTER_SERIAL_BAUDRATE", "9600"))
# Raw device path (often /dev/usb/lp0 on Linux CUPS-less setups).
PRINTER_RAW_DEVICE = os.getenv("PRINTER_RAW_DEVICE")
# Try to send full cut command after print (not all thermal printers support it).
PRINTER_ESC_POS_CUT = _env_flag("PRINTER_ESC_POS_CUT", default=False)
# TiMini-Print backend settings (for proprietary mini printer protocols).
PRINTER_TIMINIPRINT_CMD = os.getenv("PRINTER_TIMINIPRINT_CMD", "timiniprint_command_line.py")
PRINTER_TIMINIPRINT_BLUETOOTH = os.getenv("PRINTER_TIMINIPRINT_BLUETOOTH")
PRINTER_TIMINIPRINT_SERIAL = os.getenv("PRINTER_TIMINIPRINT_SERIAL")
PRINTER_TIMINIPRINT_CONFIG = os.getenv("PRINTER_TIMINIPRINT_CONFIG")
PRINTER_TIMINIPRINT_DARKNESS = int(os.getenv("PRINTER_TIMINIPRINT_DARKNESS", "5"))
PRINTER_TIMINIPRINT_PDF_PAGE_GAP = int(os.getenv("PRINTER_TIMINIPRINT_PDF_PAGE_GAP", "3"))
# Auto print scene transitions (useful on the Raspberry Pi with hardware buttons).
PRINTER_AUTO_PRINT_SCENE_CHANGES = _env_flag(
    "PRINTER_AUTO_PRINT_SCENE_CHANGES", default=False
)

# Optional external scenes config file (JSON).
# Default points to the presentation config shipped with this project.
SCENES_CONFIG_PATH = os.getenv(
    "SCENES_CONFIG_PATH",
    os.path.join(BASE_DIR, "scenes", "presentation_scenes.json"),
)
