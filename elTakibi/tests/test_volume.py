import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from volume_control import FingerVolume


class VolumeTests(unittest.TestCase):
    def test_all_levels_require_stable_pose(self):
        calls = []
        control = FingerVolume(calls.append)
        for count in range(6):
            start = count * 3
            control.update(count, 1, start)
            self.assertEqual(len(calls), count)
            control.update(count, 1, start + 0.7)
            control.update(count, 1, start + 1)
        self.assertEqual(calls, [0, 20, 40, 60, 80, 100])

    def test_missing_or_two_hands_reset_hold_without_changing_volume(self):
        for count, hands in [(None, 0), (5, 2)]:
            calls = []
            control = FingerVolume(calls.append)
            control.update(3, 1, 0)
            control.update(count, hands, 0.5)
            control.update(3, 1, 1)
            self.assertEqual(calls, [])
            control.update(3, 1, 1.7)
            control.update(count, hands, 2)
            self.assertEqual(calls, [60])
            self.assertEqual(control.percent, 60)

    def test_changing_pose_restarts_hold(self):
        calls = []
        control = FingerVolume(calls.append)
        control.update(5, 1, 0)
        control.update(1, 1, 0.5)
        control.update(1, 1, 0.8)
        self.assertEqual(calls, [])
        control.update(1, 1, 1.2)
        self.assertEqual(calls, [20])

    def test_failed_setter_does_not_report_success(self):
        def fail(percent):
            raise RuntimeError('Aygıt bağlantısı kesildi')
        control = FingerVolume(fail)
        control.update(2, 1, 0)
        with self.assertRaises(RuntimeError):
            control.update(2, 1, 1)
        self.assertIsNone(control.percent)
