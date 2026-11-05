# El Takibi Studio 2.0

Türkçe masaüstü arayüzü, iki el takibi, 0–10 parmak sayımı ve parmak hedef oyunu.

## Windows'ta başlatma

1. ZIP'i tamamen yeni bir klasöre çıkarın. Eski sürümün üzerine yazmanız gerekmez.
2. Python 3.11, 3.12 veya 3.13 kurulu olmalı; `python --version` ile kontrol edin.
3. `Kurulum.bat` dosyasına çift tıklayın. Yalnızca ilk kurulumda gerekir. İnternet ve yeterli disk alanı gerekir.
4. `Baslat.bat` dosyasına çift tıklayın.
5. Kamera 0 ve Otomatik ile başlayın. Gerekirse durdurup kamera 1 / 2 veya DirectShow / Media Foundation deneyin.

Kurulum ayrı `.venv` kullanır ve indirme önbelleği oluşturmaz. Önceki global paketleri değiştirmez. Önceki sürümdeki `hand_landmarker.task` dosyasını bu klasöre kopyalarsanız yeniden indirilmez. Aksi halde model ilk başlatmada indirilir.

## Diğer sistemler

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --no-cache-dir -r requirements.txt
python main.py
```

Linux'ta ayrıca sisteminizin Tkinter paketi (ör. python3-tk) ve grafik masaüstü gerekir. Windows/macOS Python dağıtımında Tkinter bulunmalıdır.

## Özellikler

### Parmak sayısıyla Windows ses kontrolü

`Kurulum.bat` yeni ses bağımlılığı olan `pycaw` paketini de kurar. Uygulamada
**Uygulama modu → Ses kontrolü** seçip kamerayı başlatın. Tek elinizi gösterin:
0 parmak %0, 1 parmak %20, 2 parmak %40, 3 parmak %60, 4 parmak %80,
5 parmak %100 ses seviyesine karşılık gelir. Pozu 0,6 saniye sabit tutun.
Bu mod Windows'un varsayılan ses çıkışını değiştirir; pozitif seviyeler sessizi kaldırır.
El kaybolduğunda, iki el göründüğünde veya takip durdurulduğunda son ses seviyesi korunur.
Ses aygıtı hatasında ses kontrolü durur; kamera takibi devam eder. Aygıtı kontrol edip
takibi yeniden başlatın. Takip ve oyun modları ses seviyesini değiştirmez.

Ses API kaynağı: https://andremiras.github.io/pycaw/api/index.html

### Kamera ve takip

- Yeniden boyutlanan, görüntü oranını koruyan canlı önizleme.
- İki elde 42 noktaya kadar çizim ve toplam 0–10 açık parmak sayısı.
- FPS ve el sayısı göstergeleri; el kaybolunca sayım temizlenir.
- Kamera numarası / Windows sürücüsü seçimi ve otomatik sürücü denemesi.
- Bağlantı kesilince aynı kamerayı yeniden açma denemesi; başarısızlıkta açıklamalı hata.
- Ayna ve eklem çizgisi seçenekleri, açı eşiği ve dengeleme ayarı.
- Tek elle 0–5 hedefini bir saniye tutarak puan kazanılan oyun.
- Kullanıcı seçimiyle PNG kaydetme; otomatik video kaydı yok.
- Kalıcı ayarlar ve boyutu sınırlanmış hata günlüğü.
- Arayüzden bağımsız model/kamera iş parçacığı ve sınırlı görüntü kuyruğu.

Ayar değişikliği için durdurun, sonra yeniden başlatın. Enter başlatır, Esc durdurur. Kapatırken devam eden model indirmesi veya kamera sürücüsü işlemi bitene kadar beklemek gerekebilir. İşletim sisteminin bloke olan kamera sürücülerine uygulama düzeyinde kesin zaman aşımı garantisi verilmez.

## Veri ve gizlilik

Kamera görüntüsü yerelde işlenir, sunucuya gönderilmez. Yalnızca ilk model indirmesi Google'a ağ isteği yapar. PNG kaydı açık kullanıcı işlemiyle yapılır. Ayarlar, model ve hata günlüğü Windows'ta `%LOCALAPPDATA%\ElTakibiStudio`, diğer sistemlerde `~/ElTakibiStudio` altındadır. Günlük kamera karelerini içermez.

## Sayımın sınırları

Dünya koordinatlarındaki eklem açıları ve mesafelerle yaklaşık sayım yapılır; tıbbi veya doğrulanmış biyometrik ölçüm değildir. Avuç kameraya dönük, el tamamen kadrajda ve parmaklar ayrık olmalıdır. Yan görünüş, birbirini örten eller ve kıvrık başparmak hatalara yol açabilir. Sayı dengelemesi kısa gecikme yaratır. İki elden biri kaybolunca dengeleme sıfırlanır.

## Sorun giderme

- Windows Kamera uygulamasında da görüntü yoksa kamera bağlantısını ve işletim sistemi izinlerini kontrol edin.
- Kamera uygulamasını / Teams / Zoom'u kapatıp tekrar deneyin.
- Kamera numaraları cihaz sırasıdır; gösterilen 0–5 listesi takılı cihaz envanteri değildir.
- `No space left on device`: kurulum veya geçici dizin diskinde yer açın.
- Model indirme hatası: interneti kontrol edin veya modeli aşağıdaki bağlantıdan indirip uygulama klasörüne `hand_landmarker.task` adıyla koyun.
- Paket hatası: yeni `.venv` kurulumunu kullanın. OpenCV paketleri aynı `cv2` adını paylaşır; bu projede yalnızca `opencv-contrib-python` kurulur.

Model: https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task

## Geliştirme ve doğrulama

```bash
python -m unittest discover -s tests -v
```

Sözdizimi, geometri ve kamera sürücüsü geri dönüş/temizleme davranışları donanımsız testlerle kontrol edilir. Gerçek Windows webcam ve MediaPipe çıkarımı bu geliştirme ortamında doğrulanmamıştır. Üretim kullanımı öncesinde hedef cihazlarda kurulum, izinler, bağlantı kesilmesi ve sayım doğruluğu doğrulanmalıdır. Bu paket imzalı bir EXE değildir; Python kaynak uygulamasıdır.

Resmî API kaynakları:
- https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker/python
- https://docs.opencv.org/4.10.0/d4/d15/group__videoio__flags__base.html
