"""Declarative definitions for the six robot scenes.

Each :class:`SceneConfig` bundles the parameters every subsystem needs. The
``SceneManager`` reads these and hands the relevant sub-config to each
controller, keeping behaviour fully data-driven.
"""

from dataclasses import dataclass
from typing import Optional, Tuple

import config

RGB = Tuple[int, int, int]


@dataclass(frozen=True)
class DisplayConfig:
    """Parameters for the eye/mouth renderers."""

    eye_color: RGB
    eye_shape: str          # normal | wide | narrow | x | angry
    pupil_animation: str    # idle | wander | jitter | still | glow
    mouth_type: str         # none | line | smile | frown | open | flat


@dataclass(frozen=True)
class LedConfig:
    """Parameters for the WS2812B ring animation."""

    animation_name: str     # idle_pulse | thinking_swipe | surprised_burst |
                            # alarm_flash | evil_glow | error_off
    color_primary: RGB
    color_secondary: RGB
    speed: float            # animation speed multiplier (1.0 = baseline)


@dataclass(frozen=True)
class ServoConfig:
    """Parameters for the head servo movement profile."""

    angle_profile: str      # center | slow_sweep | nod | shake | droop
    speed: float = 1.0


@dataclass(frozen=True)
class AudioConfig:
    """Audio playback for a scene; ``filename`` may be ``None`` for silence."""

    filename: Optional[str]
    loop: bool = False


@dataclass(frozen=True)
class SceneConfig:
    """Full description of one scene."""

    id: str
    name: str
    display: DisplayConfig
    leds: LedConfig
    servo: ServoConfig
    audio: AudioConfig


# ---------------------------------------------------------------------------
# The six scenes, in navigation order.
# ---------------------------------------------------------------------------
SCENES = [
    SceneConfig(
        id="normal_operation",
        name="Normaler Betrieb",
        display=DisplayConfig(
            eye_color=config.COLOR_BLUE,
            eye_shape="normal",
            pupil_animation="idle",
            mouth_type="line",
        ),
        leds=LedConfig(
            animation_name="idle_pulse",
            color_primary=config.COLOR_BLUE,
            color_secondary=config.COLOR_WHITE,
            speed=0.6,
        ),
        servo=ServoConfig(angle_profile="center", speed=0.4),
        audio=AudioConfig(filename=None, loop=False),
    ),
    SceneConfig(
        id="thinking",
        name="Denkend",
        display=DisplayConfig(
            eye_color=config.COLOR_YELLOW,
            eye_shape="normal",
            pupil_animation="wander",
            mouth_type="line",
        ),
        leds=LedConfig(
            animation_name="thinking_swipe",
            color_primary=config.COLOR_YELLOW,
            color_secondary=config.COLOR_ORANGE,
            speed=0.8,
        ),
        servo=ServoConfig(angle_profile="slow_sweep", speed=0.5),
        audio=AudioConfig(filename="thinking.wav", loop=True),
    ),
    SceneConfig(
        id="surprised",
        name="Überrascht",
        display=DisplayConfig(
            eye_color=config.COLOR_WHITE,
            eye_shape="wide",
            pupil_animation="jitter",
            mouth_type="open",
        ),
        leds=LedConfig(
            animation_name="surprised_burst",
            color_primary=config.COLOR_WHITE,
            color_secondary=config.COLOR_YELLOW,
            speed=1.6,
        ),
        servo=ServoConfig(angle_profile="nod", speed=1.4),
        audio=AudioConfig(filename="surprised.wav", loop=False),
    ),
    SceneConfig(
        id="warning",
        name="Warnend / Alarm",
        display=DisplayConfig(
            eye_color=config.COLOR_RED,
            eye_shape="angry",
            pupil_animation="still",
            mouth_type="frown",
        ),
        leds=LedConfig(
            animation_name="alarm_flash",
            color_primary=config.COLOR_RED,
            color_secondary=config.COLOR_BLACK,
            speed=1.8,
        ),
        servo=ServoConfig(angle_profile="shake", speed=1.6),
        audio=AudioConfig(filename="warning_alarm.wav", loop=True),
    ),
    SceneConfig(
        id="evil_agent",
        name="Böser Agent",
        display=DisplayConfig(
            eye_color=config.COLOR_RED,
            eye_shape="narrow",
            pupil_animation="glow",
            mouth_type="smile",
        ),
        leds=LedConfig(
            animation_name="evil_glow",
            color_primary=(120, 0, 0),
            color_secondary=config.COLOR_PURPLE,
            speed=0.4,
        ),
        servo=ServoConfig(angle_profile="slow_sweep", speed=0.3),
        audio=AudioConfig(filename="evil_agent.wav", loop=True),
    ),
    SceneConfig(
        id="out_of_order",
        name="Out of Order",
        display=DisplayConfig(
            eye_color=config.COLOR_GREY,
            eye_shape="x",
            pupil_animation="still",
            mouth_type="flat",
        ),
        leds=LedConfig(
            animation_name="error_off",
            color_primary=config.COLOR_BLACK,
            color_secondary=config.COLOR_BLACK,
            speed=1.0,
        ),
        servo=ServoConfig(angle_profile="droop", speed=0.5),
        audio=AudioConfig(filename="out_of_order.wav", loop=False),
    ),
]
