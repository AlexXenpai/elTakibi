"""El Takibi Studio — masaüstü kamera ve el takibi uygulaması."""
import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import os
import queue
import random
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

ROOT = Path(__file__).resolve().parent
DATA = Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'ElTakibiStudio'
DATA.mkdir(parents=True, exist_ok=True)
handler = RotatingFileHandler(DATA / 'app.log', maxBytes=1_000_000, backupCount=2, encoding='utf-8')
logging.basicConfig(handlers=[handler], level=logging.INFO)

from tracking import CONNECTIONS, count_fingers, ensure_model
from volume_control import FingerVolume, windows_volume_setter

DEFAULTS = dict(camera=0, backend='Otomatik', mirror=True, skeleton=True,
                threshold=155, smoothing=7, mode='Takip')


from camera import open_camera


class Worker(threading.Thread):
    def __init__(self, config, output):
        super().__init__(daemon=True)
        self.config, self.output = config, output
        self.stop = threading.Event()

    def send(self, kind, data):
        # En yeni görüntü yeterli; arayüz yavaşlarsa kuyruk büyümez.
        if kind == 'frame':
            try:
                self.output.put_nowait((kind, data))
            except queue.Full:
                pass
        else:
            while not self.stop.is_set():
                try:
                    self.output.put((kind, data), timeout=0.1)
                    break
                except queue.Full:
                    continue

    def run(self):
        camera = None
        try:
            import cv2
            import mediapipe as mp
            from mediapipe.tasks import python
            from mediapipe.tasks.python import vision
            from collections import Counter, deque
            c = self.config
            self.send('status', 'Model hazırlanıyor… İlk indirme internet gerektirir.')
            model = DATA / 'hand_landmarker.task'
            # Önceki sürümün indirdiği model varsa tekrar indirme.
            if not model.exists() and (ROOT / 'hand_landmarker.task').exists():
                model = ROOT / 'hand_landmarker.task'
            ensure_model(model)
            if self.stop.is_set():
                return
            self.send('status', f'Kamera {c["camera"]} açılıyor…')
            camera, frame = open_camera(cv2, c['camera'], c['backend'], self.stop)
            options = vision.HandLandmarkerOptions(
                base_options=python.BaseOptions(model_asset_path=str(model)),
                running_mode=vision.RunningMode.VIDEO, num_hands=2,
                min_hand_detection_confidence=0.6, min_tracking_confidence=0.6)
            history = deque(maxlen=c['smoothing'])
            last_signature = None
            last_time, stamp, failures = time.monotonic(), -1, 0
            with vision.HandLandmarker.create_from_options(options) as detector:
                while not self.stop.is_set():
                    if frame is None:
                        ok, frame = camera.read()
                        if not ok or frame is None:
                            frame = None
                            failures += 1
                            if failures < 5:
                                continue
                            self.send('status', 'Kamera bağlantısı kesildi; yeniden deneniyor…')
                            camera.release()
                            camera, frame = open_camera(cv2, c['camera'], c['backend'], self.stop)
                            history.clear()
                            failures = 0
                    failures = 0
                    if c['mirror']:
                        frame = cv2.flip(frame, 1)
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    stamp = max(stamp + 1, time.monotonic_ns() // 1_000_000)
                    result = detector.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), stamp)
                    h, w = frame.shape[:2]
                    counts = []
                    for i, landmarks in enumerate(result.hand_landmarks):
                        count = count_fingers(result.hand_world_landmarks[i], c['threshold'])
                        counts.append(count)
                        points = [(int(p.x*w), int(p.y*h)) for p in landmarks]
                        if c['skeleton']:
                            for a, b in CONNECTIONS:
                                cv2.line(frame, points[a], points[b], (110, 230, 60), 2, cv2.LINE_AA)
                            for p in points:
                                cv2.circle(frame, p, 4, (0, 190, 255), -1, cv2.LINE_AA)
                        cv2.putText(frame, str(count), points[0], cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    signature = len(counts)
                    if signature != last_signature:
                        history.clear()
                    last_signature = signature
                    if counts:
                        history.append(sum(counts))
                        total = Counter(history).most_common(1)[0][0]
                    else:
                        history.clear()
                        total = None
                    now = time.monotonic()
                    fps = 1 / max(now-last_time, 0.001)
                    last_time = now
                    self.send('frame', (cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), total, len(counts), fps))
                    frame = None
        except Exception as exc:
            logging.exception('Takip hatası')
            self.send('error', str(exc))
        finally:
            if camera is not None:
                camera.release()


class Studio:
    def __init__(self, root):
        self.root = root
        root.title('El Takibi Studio • 2.0')
        root.geometry('1180x780')
        root.minsize(980, 710)
        root.configure(bg='#101722')
        self.worker = None
        self.volume_control = None
        self.volume_error = None
        self.events = queue.Queue(maxsize=2)
        self.image = None
        self.latest = None
        self.closing = False
        self.target = random.randint(0, 5)
        self.score = 0
        self.hold_start = None
        self.cooldown = 0
        self.active = DEFAULTS.copy()
        settings = DEFAULTS.copy()
        try:
            saved = json.loads((DATA / 'settings.json').read_text(encoding='utf-8'))
            settings.update({k: v for k, v in saved.items() if k in DEFAULTS})
        except (OSError, ValueError, TypeError):
            pass
        self.vars = {k: (tk.BooleanVar(value=v) if isinstance(v, bool) else tk.StringVar(value=str(v)))
                     for k, v in settings.items()}
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('.', background='#182231', foreground='#e8eef7', font=('Segoe UI', 10))
        style.configure('TFrame', background='#101722')
        style.configure('TLabel', background='#101722')
        style.configure('TButton', padding=9)
        style.configure('TCheckbutton', background='#101722')
        style.configure('TCombobox', fieldbackground='#223248', foreground='#111111')
        header = ttk.Frame(root, padding=(24, 18))
        header.pack(fill='x')
        ttk.Label(header, text='EL TAKİBİ  /  STUDIO', font=('Segoe UI', 22, 'bold')).pack(side='left')
        ttk.Label(header, text='YEREL İŞLEME • CANLI GÖRÜNTÜ', foreground='#57dec1').pack(side='right')
        body = ttk.Frame(root, padding=(24, 0))
        body.pack(fill='both', expand=True)
        left = ttk.Frame(body, width=245)
        left.pack(side='left', fill='y', padx=(0, 20))
        left.pack_propagate(False)
        ttk.Label(left, text='KAMERA VE TAKİP', font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=(0, 12))
        self.controls = []
        for label, key, values in [
            ('Kamera numarası', 'camera', list(range(6))),
            ('Kamera sürücüsü', 'backend', ['Otomatik', 'DirectShow', 'Media Foundation'] if sys.platform == 'win32' else ['Otomatik']),
            ('Uygulama modu', 'mode', ['Takip', 'Ses kontrolü', 'Parmak oyunu']),
            ('Düz parmak açı eşiği', 'threshold', [145, 150, 155, 160, 165]),
            ('Dengeleme (kare)', 'smoothing', [1, 3, 5, 7, 9])]:
            ttk.Label(left, text=label).pack(anchor='w', pady=(10, 4))
            widget = ttk.Combobox(left, textvariable=self.vars[key], values=values, state='readonly')
            widget.pack(fill='x')
            self.controls.append(widget)
        for text, key in [('Ayna görüntüsü', 'mirror'), ('Eklem çizgilerini göster', 'skeleton')]:
            widget = ttk.Checkbutton(left, text=text, variable=self.vars[key])
            widget.pack(anchor='w', pady=(12, 0))
            self.controls.append(widget)
        self.start_button = ttk.Button(left, text='▶  Kamerayı başlat', command=self.start)
        self.start_button.pack(fill='x', pady=(20, 7))
        self.stop_button = ttk.Button(left, text='■  Durdur', command=self.stop, state='disabled')
        self.stop_button.pack(fill='x', pady=3)
        ttk.Button(left, text='Görüntüyü kaydet', command=self.save_image).pack(fill='x', pady=7)
        ttk.Button(left, text='Yardım / Kamera sorunu', command=self.help).pack(fill='x')
        ttk.Label(left, text='Ayarları değiştirmek için takibi durdurun.\nKamera numaraları 0’dan başlar.\n\nKısayollar: Enter başlat • Esc durdur',
                  wraplength=240, foreground='#99abc2').pack(anchor='w', pady=15)
        right = ttk.Frame(body)
        right.pack(side='left', fill='both', expand=True)
        self.preview = tk.Canvas(right, bg='#090f18', highlightthickness=1, highlightbackground='#28374d')
        self.preview.pack(fill='both', expand=True)
        self.preview.bind('<Configure>', self.placeholder)
        metrics = ttk.Frame(right, padding=(0, 15))
        metrics.pack(fill='x')
        self.count_label = ttk.Label(metrics, text='—  parmak', font=('Segoe UI', 26, 'bold'), foreground='#57dec1')
        self.count_label.pack(side='left')
        self.info_label = ttk.Label(metrics, text='0 el  •  — FPS')
        self.info_label.pack(side='right')
        self.game_label = ttk.Label(right, text='Takip modu • İki elde toplam 0–10 parmak', font=('Segoe UI', 12))
        self.game_label.pack(anchor='w', pady=8)
        self.progress = ttk.Progressbar(right, maximum=100)
        self.progress.pack(fill='x', pady=(0, 12))
        self.status = ttk.Label(root, text='Hazır. Kamerayı başlatın.', padding=(24, 14), wraplength=1100)
        self.status.pack(fill='x')
        root.bind('<Return>', lambda e: self.start())
        root.bind('<Escape>', lambda e: self.stop())
        root.protocol('WM_DELETE_WINDOW', self.close)
        root.after(40, self.poll)

    def placeholder(self, event=None):
        if self.latest is None:
            self.preview.delete('all')
            self.preview.create_text(self.preview.winfo_width()/2, self.preview.winfo_height()/2,
                                     text='CANLI ÖNİZLEME\n\nKamerayı başlatın', fill='#8496ae',
                                     font=('Segoe UI', 18), justify='center')

    def start(self):
        if self.closing or (self.worker and self.worker.is_alive()):
            return
        try:
            c = {k: v.get() for k, v in self.vars.items()}
            for key in ('camera', 'threshold', 'smoothing'):
                c[key] = int(c[key])
            if c['camera'] < 0 or c['smoothing'] not in (1, 3, 5, 7, 9) or not 140 <= c['threshold'] <= 170:
                raise ValueError('Geçersiz ayar. Kamera ve takip ayarlarını kontrol edin.')
            self.volume_control = None
            self.volume_error = None
            if c['mode'] == 'Ses kontrolü':
                try:
                    self.volume_control = FingerVolume(windows_volume_setter())
                except Exception as exc:
                    messagebox.showerror('Ses kontrolü başlatılamadı', str(exc))
                    return
            (DATA / 'settings.json').write_text(json.dumps(c, ensure_ascii=False), encoding='utf-8')
        except (ValueError, OSError) as exc:
            messagebox.showerror('Ayarlar', str(exc))
            return
        while not self.events.empty():
            self.events.get_nowait()
        self.latest = None
        self.active = c
        self.score, self.hold_start, self.cooldown = 0, None, 0
        self.target = random.randint(0, 5)
        self.worker = Worker(c, self.events)
        self.worker.start()
        self.start_button.configure(state='disabled')
        self.stop_button.configure(state='normal')
        for widget in self.controls:
            widget.configure(state='disabled')
        self.status.configure(text='Başlatılıyor…')

    def stop(self):
        if self.worker and self.worker.is_alive():
            self.worker.stop.set()
            self.status.configure(text='Kamera kapatılıyor…')
            self.stop_button.configure(state='disabled')

    def poll(self):
        try:
            while True:
                kind, data = self.events.get_nowait()
                if kind == 'frame' and self.worker and not self.worker.stop.is_set():
                    self.render(*data)
                elif kind == 'status':
                    self.status.configure(text=data)
                elif kind == 'error':
                    self.status.configure(text='Hata: ' + data)
                    messagebox.showerror('Takip başlatılamadı', data + '\n\nAyrıntılar: ' + str(DATA / 'app.log'))
        except queue.Empty:
            pass
        if self.worker and not self.worker.is_alive():
            self.worker = None
            self.start_button.configure(state='normal')
            self.stop_button.configure(state='disabled')
            for widget in self.controls:
                widget.configure(state='readonly' if isinstance(widget, ttk.Combobox) else 'normal')
            self.latest = None
            self.count_label.configure(text='—  parmak')
            self.info_label.configure(text='Kamera kapalı')
            self.progress['value'] = 0
            self.placeholder()
            if not str(self.status.cget('text')).startswith('Hata:'):
                self.status.configure(text='Durduruldu. Kamera serbest bırakıldı.')
        if self.closing and self.worker is None:
            self.root.destroy()
            return
        self.root.after(40, self.poll)

    def render(self, rgb, total, hands, fps):
        from PIL import Image, ImageTk
        self.latest = rgb
        image = Image.fromarray(rgb)
        image.thumbnail((max(self.preview.winfo_width()-4, 1), max(self.preview.winfo_height()-4, 1)))
        self.image = ImageTk.PhotoImage(image)
        self.preview.delete('all')
        self.preview.create_image(self.preview.winfo_width()/2, self.preview.winfo_height()/2, image=self.image)
        self.count_label.configure(text=f'{total if total is not None else "—"}  parmak')
        self.info_label.configure(text=f'{hands} el  •  {fps:.0f} FPS')
        self.status.configure(text='Canlı • Görüntü bilgisayarınızda işleniyor.' if hands else 'Canlı • Elinizi kameraya gösterin.')
        now = time.monotonic()
        if self.active['mode'] == 'Ses kontrolü':
            try:
                percent = (self.volume_control.update(total, hands, now)
                           if self.volume_control else None)
            except Exception as exc:
                logging.exception('Ses kontrolü hatası')
                self.volume_control = None
                self.volume_error = 'Ses kontrolü durdu. Ses aygıtını kontrol edip takibi yeniden başlatın.'
                percent = None
                messagebox.showerror('Ses kontrolü', self.volume_error + '\n' + str(exc))
            self.progress['value'] = percent if percent is not None else 0
            level = f'%{percent}' if percent is not None else 'bekleniyor'
            hint = 'Tek el gösterin.' if hands != 1 else 'Parmak sayısını 0,6 saniye sabit tutun.'
            self.game_label.configure(text=self.volume_error or f'Ses: {level} • {hint}')
            self.status.configure(text=self.volume_error or 'Ses kontrolü • 0: %0 / 1: %20 / 2: %40 / 3: %60 / 4: %80 / 5: %100')
        elif self.active['mode'] == 'Parmak oyunu':
            # Tek el ile hedefi 1 saniye sabit tut; yanlış pozda süre sıfırlanır.
            if hands == 1 and total == self.target and now >= self.cooldown:
                if self.hold_start is None:
                    self.hold_start = now
                elapsed = now - self.hold_start
                self.progress['value'] = min(100, elapsed * 100)
                if elapsed >= 1:
                    self.score += 1
                    self.target = random.choice([n for n in range(6) if n != self.target])
                    self.hold_start = None
                    self.cooldown = now + 0.7
                    self.progress['value'] = 0
            else:
                self.hold_start = None
                self.progress['value'] = 0
            self.game_label.configure(text=f'Hedef: {self.target} parmak  •  Puan: {self.score}  •  Tek elle 1 saniye tutun')
        else:
            self.progress['value'] = 0 if total is None else total * 10
            self.game_label.configure(text='Takip modu • İki elde toplam 0–10 parmak')

    def save_image(self):
        if self.latest is None:
            messagebox.showinfo('Görüntü yok', 'Önce kamerayı başlatın.')
            return
        path = filedialog.asksaveasfilename(defaultextension='.png', filetypes=[('PNG görüntüsü', '*.png')],
                                          initialfile=time.strftime('el-takibi-%Y%m%d-%H%M%S.png'))
        if path:
            try:
                from PIL import Image
                Image.fromarray(self.latest).save(path, format='PNG')
                self.status.configure(text='Görüntü kaydedildi: ' + path)
            except OSError as exc:
                messagebox.showerror('Kayıt hatası', str(exc))

    def help(self):
        messagebox.showinfo('Kullanım ve kamera yardımı',
            '1. Kamera numarasını seçip başlatın. Görüntü yoksa 1 veya 2 deneyin.\n'
            '2. Windows’ta Otomatik, DirectShow ve Media Foundation seçeneklerini deneyin.\n'
            '3. Windows Kamera uygulamasını kontrol edin; ardından kapatın.\n'
            '4. Gizlilik ayarlarında masaüstü uygulamalarına kamera izni verin.\n\n'
            'Avucunuzu kameraya çevirin, parmaklar ayrık ve el tamamen görünür olsun. '
            'Daha yüksek açı eşiği daha katı sayım yapar. Örtüşme ve yan görünüş sayımı etkiler.\n\n'
            'Oyun: İstenen parmak sayısını tek elle 1 saniye gösterin.\n'
            'Ses kontrolü: Tek elde 0–5 parmak = %0–100 ses. Sayıyı 0,6 saniye tutun.\n'
            'El yoksa veya iki el görünüyorsa ses değişmez. Pozitif seviye sessizi kaldırır.\n'
            'Görüntüler yalnızca kaydet düğmesine basınca dosyaya yazılır.\n'
            'Ayarlar, model ve dönen hata günlüğü: ' + str(DATA))

    def close(self):
        self.closing = True
        self.stop()
        self.status.configure(text='Kapatılıyor… Kamera/model işleminin bitmesi bekleniyor.')


if __name__ == '__main__':
    app = tk.Tk()
    Studio(app)
    app.mainloop()
