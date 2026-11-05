"""Tek el ile, kararlı bir pozdan Windows ses seviyesini ayarla."""
import sys


def windows_volume_setter():
    if sys.platform != 'win32':
        raise RuntimeError('Ses kontrolü yalnızca Windows üzerinde kullanılabilir.')
    try:
        from pycaw.pycaw import AudioUtilities
    except ImportError as exc:
        raise RuntimeError('Ses kontrolü için Kurulum.bat ile pycaw paketini kurun.') from exc
    device = AudioUtilities.GetSpeakers()
    if device is None:
        raise RuntimeError('Varsayılan ses çıkış aygıtı bulunamadı.')
    endpoint = device.EndpointVolume

    def set_percent(percent):
        endpoint.SetMasterVolumeLevelScalar(percent / 100, None)
        endpoint.SetMute(1 if percent == 0 else 0, None)
    return set_percent


class FingerVolume:
    def __init__(self, setter, hold_seconds=0.6):
        self.setter = setter
        self.hold_seconds = hold_seconds
        self.candidate = None
        self.since = None
        self.percent = None
        self.applied = None

    def update(self, count, hands, now):
        if hands != 1 or count is None or count not in range(6):
            self.candidate = self.since = self.applied = None
            return self.percent
        if count != self.candidate:
            self.candidate, self.since = count, now
            self.applied = None
        if now - self.since >= self.hold_seconds and self.applied != count:
            percent = count * 20
            self.setter(percent)
            self.percent, self.applied = percent, count
        return self.percent
