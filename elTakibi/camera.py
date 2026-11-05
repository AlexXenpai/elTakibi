"""İşletim sistemine uygun kamera açılışı."""
import sys

def open_camera(cv2, index, backend, stop):
    """Windows'ta işletim sistemine uygun sürücüleri sırayla dene."""
    names = {'DirectShow': cv2.CAP_DSHOW, 'Media Foundation': cv2.CAP_MSMF,
             'Otomatik': cv2.CAP_ANY}
    candidates = ([cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
                  if sys.platform == 'win32' and backend == 'Otomatik'
                  else [names[backend]])
    for api in candidates:
        if stop.is_set():
            break
        camera = cv2.VideoCapture(index, api)
        if camera.isOpened():
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
            for _ in range(8):
                if stop.is_set():
                    break
                ok, frame = camera.read()
                if ok and frame is not None:
                    return camera, frame
        camera.release()
    raise RuntimeError('Kamera açılamadı. Kamera numarasını veya sürücüyü değiştirin. '
                       'Windows Kamera uygulamasında görüntüyü ve gizlilik izinlerini kontrol edin. '
                       'Zoom / Teams gibi kamerayı kullanan uygulamaları kapatın.')

