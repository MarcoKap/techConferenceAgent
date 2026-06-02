import os
os.environ["MOCK_HARDWARE"] = "1"

import time
import queue

import config
import scenes.scene_definitions as sd
from hardware import ButtonHandler, LedController, ServoController, AudioController
from scene_manager import SceneManager

assert config.IS_MOCK, "expected mock mode"
assert len(sd.SCENES) == 6, f"expected 6 scenes, got {len(sd.SCENES)}"
print("scenes:", [s.id for s in sd.SCENES])
print("controller classes:", LedController.__name__, ServoController.__name__,
      ButtonHandler.__name__, AudioController.__name__)
assert LedController.__name__ == "MockLedController"
assert ServoController.__name__ == "MockServoController"
assert ButtonHandler.__name__ == "MockButtonHandler"

led = LedController()
servo = ServoController()
audio = AudioController()
q = queue.Queue()
button = ButtonHandler(q)

sm = SceneManager(led, servo, audio)
button.start()
sm.start()
assert sm.current_index == 0
time.sleep(0.3)

# cycle forward through all scenes and wrap around
for _ in range(len(sd.SCENES)):
    sm.next()
    time.sleep(0.15)
assert sm.current_index == 0, sm.current_index

# go backward once -> wraps to last
sm.prev()
assert sm.current_index == len(sd.SCENES) - 1, sm.current_index
time.sleep(0.15)

# button event queue routing (simulate what DisplayManager does)
sm_prev_index = sm.current_index
from hardware import button_events
q.put(button_events.NEXT)
ev = q.get()
if ev == button_events.NEXT:
    sm.next()
assert sm.current_index == (sm_prev_index + 1) % len(sd.SCENES)

led.close(); servo.close(); audio.close(); button.close()
print("HEADLESS TEST OK")
