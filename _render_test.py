"""Exercise the eye/mouth renderer code paths using a minimal pygame stub.

This can't validate visual output, but it executes every drawing branch for all
six scenes to catch geometry/API mistakes in an environment without pygame.
"""
import os, sys, types, math
os.environ["MOCK_HARDWARE"] = "1"


class Rect:
    def __init__(self, x=0, y=0, w=0, h=0):
        self.x, self.y, self.width, self.height = x, y, w, h

    @property
    def center(self):
        return (self.x + self.width // 2, self.y + self.height // 2)

    @center.setter
    def center(self, value):
        cx, cy = value
        self.x = cx - self.width // 2
        self.y = cy - self.height // 2

    @property
    def top(self):
        return self.y

    @property
    def left(self):
        return self.x

    @property
    def right(self):
        return self.x + self.width

    @property
    def topleft(self):
        return (self.x, self.y)

    @property
    def topright(self):
        return (self.x + self.width, self.y)


calls = {"ellipse": 0, "line": 0, "circle": 0, "polygon": 0, "arc": 0}


def _rec(name):
    def fn(*a, **k):
        calls[name] += 1
    return fn


fake = types.ModuleType("pygame")
fake.Rect = Rect
fake.draw = types.SimpleNamespace(
    ellipse=_rec("ellipse"), line=_rec("line"), circle=_rec("circle"),
    polygon=_rec("polygon"), arc=_rec("arc"),
)
sys.modules["pygame"] = fake

from display.eye_renderer import EyeRenderer
from display.mouth_renderer import MouthRenderer
import scenes.scene_definitions as sd

eye = EyeRenderer(800, 480)
mouth = MouthRenderer(800, 480)
surface = object()

for scene in sd.SCENES:
    for t in (0.0, 1.3, 3.9, 7.5):
        eye.draw(surface, scene.display, t)
        mouth.draw(surface, scene.display, t)

print("draw calls:", calls)
assert sum(calls.values()) > 0
print("RENDERER STUB TEST OK")
