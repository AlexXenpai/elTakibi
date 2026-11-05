import sys
from pathlib import Path
import threading
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tracking import angle, count_fingers
from camera import open_camera
from types import SimpleNamespace

class CoreTests(unittest.TestCase):
    def test_angles(self):
        self.assertAlmostEqual(angle((0,0,0), (1,0,0), (2,0,0)), 180)
        self.assertAlmostEqual(angle((1,0,0), (0,0,0), (0,1,0)), 90)
        self.assertEqual(angle((0,0,0), (0,0,0), (0,0,0)), 0)

    def test_degenerate_hand_is_not_open(self):
        self.assertEqual(count_fingers([SimpleNamespace(x=0,y=0,z=0)]*21), 0)

    def test_camera_fallback_and_release(self):
        class Camera:
            def __init__(self, valid):
                self.valid, self.released = valid, False
            def isOpened(self): return self.valid
            def set(self, *a): pass
            def read(self): return True, 'frame'
            def release(self): self.released = True
        first, second = Camera(False), Camera(True)
        calls = []
        def capture(index, api):
            calls.append((index, api))
            return [first, second][len(calls)-1]
        cv = SimpleNamespace(CAP_DSHOW=700, CAP_MSMF=1400, CAP_ANY=0,
                             CAP_PROP_FRAME_WIDTH=3, CAP_PROP_FRAME_HEIGHT=4, VideoCapture=capture)
        with patch('sys.platform', 'win32'):
            camera, frame = open_camera(cv, 1, 'Otomatik', threading.Event())
        self.assertEqual(calls, [(1,700), (1,1400)])
        self.assertTrue(first.released)
        self.assertIs(camera, second)
        self.assertEqual(frame, 'frame')
        self.assertFalse(second.released)

if __name__ == '__main__': unittest.main()
