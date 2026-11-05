"""Webcam ile tek el takibi, parmak sayma ve top kontrolü."""
import argparse
from collections import Counter, deque
import math
from pathlib import Path
import time
import urllib.request

MODEL_URL = ('https://storage.googleapis.com/mediapipe-models/'
             'hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task')
CONNECTIONS = [(0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (5, 6),
               (6, 7), (7, 8), (5, 9), (9, 10), (10, 11), (11, 12),
               (9, 13), (13, 14), (14, 15), (15, 16), (13, 17),
               (0, 17), (17, 18), (18, 19), (19, 20)]


def distance(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def angle(a, b, c):
    """B eklemindeki açıyı derece olarak döndürür."""
    u = [x - y for x, y in zip(a, b)]
    v = [x - y for x, y in zip(c, b)]
    norm = math.sqrt(sum(x*x for x in u) * sum(x*x for x in v))
    if norm < 1e-12:
        return 0.0
    cosine = max(-1.0, min(1.0, sum(x*y for x, y in zip(u, v)) / norm))
    return math.degrees(math.acos(cosine))


def count_fingers(landmarks, threshold=155):
    """3B dünya koordinatlarıyla yaklaşık sayım; sol/sağ elden bağımsız."""
    p = [(lm.x, lm.y, lm.z) for lm in landmarks]
    palm = max(distance(p[0], p[9]), 1e-6)
    # Başparmak düz ve avuçtan ayrılmış olmalı.
    thumb = (angle(p[1], p[2], p[3]) > 145
             and angle(p[2], p[3], p[4]) > threshold - 5
             and distance(p[4], p[5]) > 0.55 * palm)
    states = [thumb]
    for base in (5, 9, 13, 17):
        states.append(angle(p[base], p[base+1], p[base+2]) > threshold
                      and angle(p[base+1], p[base+2], p[base+3]) > threshold - 5
                      and distance(p[0], p[base+3]) > distance(p[0], p[base+1]))
    return sum(states)


def ensure_model(path):
    if path.is_file():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.download')
    print('El modeli indiriliyor (ilk calistirmada internet gerekir)...')
    try:
        with urllib.request.urlopen(MODEL_URL, timeout=60) as response:
            with temporary.open('wb') as output:
                while chunk := response.read(1024 * 1024):
                    output.write(chunk)
        temporary.replace(path)
    except Exception as exc:
        temporary.unlink(missing_ok=True)
        raise RuntimeError(f'Model indirilemedi: {exc}\nModeli elle indirip {path} konumuna koyun.') from exc

