"""Kaynak kod incelemesine dayanan Türkçe, 16:9 PDF sunumu."""
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor

HERE = Path(__file__).resolve().parent
pdfmetrics.registerFont(TTFont('Arial', '/mnt/c/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('ArialBold', '/mnt/c/Windows/Fonts/arialbd.ttf'))
W, H = 960, 540
BG, PANEL, TEXT, MUTED, GREEN = '#101722', '#1c293b', '#edf3fc', '#adbed4', '#57dec1'
c = canvas.Canvas(str(HERE / 'El_Takibi_Pro_Sunum.pdf'), pagesize=(W, H))
c.setTitle('El Takibi Pro — Parmak Sayısıyla Ses Kontrolü')
c.setAuthor('El Takibi Pro')
page = 0

def text(s, x, y, size=18, color=TEXT, bold=False, width=840):
    style = ParagraphStyle('p', fontName='ArialBold' if bold else 'Arial', fontSize=size,
                           leading=size*1.34, textColor=HexColor(color))
    p = Paragraph(escape(s).replace('\n','<br/>'), style)
    _, height = p.wrap(width, H)
    p.drawOn(c, x, H-y-height)
    assert y+height < 500, (page, s, y+height)
    return height

def slide(title, subtitle=''):
    global page
    if page: c.showPage()
    page += 1
    c.setFillColor(HexColor(BG)); c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(HexColor(GREEN)); c.rect(40,H-42,34,4,fill=1,stroke=0)
    text('EL TAKİBİ PRO  /  PROJE SUNUMU', 87, 29, 10, MUTED)
    text(title, 40, 66, 30, bold=True)
    if subtitle: text(subtitle,40,112,15,MUTED)
    c.setStrokeColor(HexColor(PANEL)); c.line(40,40,920,40)
    c.setFont('Arial',10); c.setFillColor(HexColor(MUTED))
    c.drawString(40,23,'Webcam • El takibi • Parmak sayımı • Windows ses kontrolü')
    c.drawRightString(920,23,f'{page:02d}')

def card(x,y,w,title,body):
    c.setFillColor(HexColor(PANEL)); c.roundRect(x,H-y-126,w,126,12,fill=1,stroke=0)
    text(title,x+18,y+16,18,GREEN,True,w-36)
    text(body,x+18,y+48,16,TEXT,False,w-36)

def rows(items, start=158, step=74):
    for i,(title,body) in enumerate(items):
        y=start+i*step
        text(title,40,y,18,GREEN,True)
        text(body,40,y+27,16,TEXT,width=870)

slide('El Takibi Pro', 'Webcam görüntüsünden parmak sayısına, parmak sayısından ses kontrolüne')
text('El hareketleriyle\nbilgisayar sesini yönetmek',40,181,36,bold=True,width=600)
text('Python ile geliştirilen masaüstü görüntü işleme projesi',40,300,21,MUTED)
text('Kapsam: canlı görüntü, eklem çizimi, açık parmak sayımı ve ses seviyesi kontrolü.',40,375,19,width=800)

slide('1. Projenin amacı ve gereksinimleri','Kamera görüntüsünü anlaşılır bir kontrol komutuna dönüştürmek')
card(40,158,425,'01  Canlı görüntü','Webcamden kareleri alıp arayüzde göstermek.')
card(485,158,435,'02  El ve eklem tespiti','Eli algılamak, 21 eklem noktasını ve bağlantılarını çizmek.')
card(40,304,425,'03  Parmak sayımı','Açık parmakları hesaplamak; toplamı ekrana yazmak.')
card(485,304,435,'04  Ses kontrolü','Tek eldeki 0–5 parmağı %0–100 ses seviyesine dönüştürmek.')

slide('2. Kullanılan teknolojiler','Her kütüphane uygulamanın farklı bir görevini üstlenir')
rows([
('Python + Tkinter / ttk','Uygulama mantığı, pencere, düğmeler, mod seçimi ve durum göstergeleri.'),
('OpenCV + MediaPipe','Kameradan görüntü alma, el noktalarını algılama ve görüntü üzerine çizim.'),
('Pillow + threading / queue','Kareleri arayüzde gösterme; takip işlemini ayrı iş parçacığında yürütme.'),
('Pycaw + Windows Core Audio','Varsayılan ses çıkışının seviyesini ve sessiz durumunu değiştirme.')],step=76)

slide('3. Sistemin çalışma akışı','Görüntü işleme ile arayüz birbirinden ayrılır')
steps=['Webcam','El tespiti','Parmak sayımı','Arayüz','Ses kontrolü']
for i,label in enumerate(steps):
    x=40+i*178
    c.setFillColor(HexColor(PANEL)); c.roundRect(x,285,160,65,9,fill=1,stroke=0)
    text(label,x+10,214,17,GREEN,True,142)
    if i<4: text('→',x+162,214,18,GREEN,width=20)
text('Worker.run(): kareyi al → RGB’ye çevir → modeli çalıştır → say → çiz',40,294,20,bold=True)
text('Worker.send() → sınırlı kuyruk → Studio.poll() → Studio.render()',40,339,19)
text('Ses kontrolü modu açıksa kararlı parmak sayısı Windows ses seviyesine uygulanır.',40,392,18,MUTED)

slide('4. Kamera ve model fonksiyonları','camera.py • tracking.py • main.py')
rows([
('open_camera(cv2, index, backend, stop)','Kamerayı açar; Windows’ta otomatik modda sürücüleri sırayla dener. İlk geçerli kareyi döndürür.'),
('ensure_model(path)','Model mevcutsa kullanır; yoksa indirir. İndirme tamamlanınca geçici dosyayı asıl dosyaya taşır.'),
('Worker.run()','Kamerayı ve modeli yönetir; her karede el tespiti ve parmak sayımını yürütür.'),
('HandLandmarker.detect_for_video(image, timestamp)','MediaPipe çağrısıdır. Görüntüdeki ellerin eklem noktalarını ve 3B dünya koordinatlarını üretir.')],step=77)

slide('5. El eklemleri ekrana nasıl çizilir?','main.py → Worker.run() içindeki çizim adımları')
rows([
('Koordinat dönüşümü','Normalize noktalar piksele çevrilir: x_piksel = int(x × genişlik), y_piksel = int(y × yükseklik).'),
('cv2.line() ve cv2.circle()','CONNECTIONS listesindeki eklemler çizgilerle bağlanır; her eklem noktası daireyle gösterilir.'),
('cv2.putText()','Her elin hesaplanan parmak sayısını bilek noktasının yanına yazar.'),
('Studio.render()','Pillow ile kareyi önizlemeye yerleştirir; toplam parmak sayısını, el sayısını ve FPS bilgisini günceller.')],step=77)

slide('6. Açık parmak sayımı nasıl yapılır?','tracking.py → count_fingers(landmarks, threshold=155)')
rows([
('angle(a, b, c)','Üç noktanın B ekleminde oluşturduğu açıyı vektörler ve kosinüs bağıntısıyla hesaplar.'),
('distance(a, b)','İki 3B nokta arasındaki Öklid uzaklığını hesaplar; parmak ve avuç ölçümlerinde kullanılır.'),
('count_fingers()','Dört parmakta iki eklem açısını ve bileğe uzaklığı kontrol eder. Başparmak için ayrı açılma koşulları uygular.'),
('Çıktı: el başına 0–5','Açık kabul edilen parmak durumlarını toplar. Bu geometrik yaklaşım yaklaşık sayım yapar.')],step=77)

slide('7. Sayımın dengelenmesi','Kısa süreli algılama değişimlerinin etkisini azaltmak')
rows([
('deque(maxlen=smoothing)','Son birkaç karenin toplam parmak sayısını tutar. Varsayılan pencere 7 karedir.'),
('Counter(history).most_common(1)','Pencerede en sık görülen toplamı seçer; ekranda daha kararlı bir sayı gösterir.'),
('El sayısı değişirse geçmiş sıfırlanır','Hiç el görünmüyorsa sonuç None olur. Bu durum, görünen kapalı yumruktan (0 parmak) farklıdır.'),
('Ses için ek bekleme: 0,6 saniye','Dengelenmiş sayı tek elde sabit kalınca ses uygulanır. Dengeleme toplam tepki süresine ek gecikme katabilir.')],step=77)

slide('8. Parmak sayısından ses seviyesine','Ses kontrolü modunda tek el kullanılır')
for i in range(6):
    x=40+i*148
    c.setFillColor(HexColor(PANEL)); c.roundRect(x,247,135,120,10,fill=1,stroke=0)
    text(f'{i} parmak',x+14,190,18,bold=True,width=110)
    text(f'%{i*20}',x+14,232,29,GREEN,True,width=110)
text('Ses yüzdesi = açık parmak sayısı × 20',40,320,24,bold=True)
text('0 parmak sesi sıfırlar ve sessize alır. Pozitif seviye sessizi kaldırır.',40,369,18)
text('El yoksa veya iki el varsa ses değişmez. Takip durunca son seviye korunur.',40,411,18,MUTED)

slide('9. Ses kontrolünün önemli fonksiyonları','volume_control.py → Windows’a ses komutu gönderme')
rows([
('windows_volume_setter()','Windows ve bağımlılık kontrolünü yapar. AudioUtilities.GetSpeakers() ile varsayılan çıkışı alır.'),
('FingerVolume.update(count, hands, now)','Tek el, geçerli sayı ve 0,6 saniyelik sabit poz koşullarını kontrol eder. Yeni seviyeyi bir kez uygular.'),
('set_percent(percent)','İç fonksiyon: SetMasterVolumeLevelScalar(percent / 100, None) ile seviyeyi ayarlar; SetMute() ile sessizi yönetir.'),
('Hata davranışı','Ses aygıtı hatasında kullanıcıya mesaj gösterilir ve ses kontrolü durur. Kamera takibi devam eder.')],step=77)

slide('10. Arayüzü yöneten önemli metotlar','main.py → Studio sınıfı')
rows([
('Studio.start() / Studio.stop()','Ayarları doğrular, takip iş parçacığını başlatır veya durdurma işaretini gönderir.'),
('Studio.poll() / Studio.render()','Kuyruktaki durum ve kareleri işler; canlı görüntüyü, sayımı ve seçilen modun bilgilerini günceller.'),
('Studio.save_image()','Kullanıcının seçtiği konuma o anki görüntüyü PNG olarak kaydeder.'),
('Studio.close() / Worker.send()','Kapanışı yönetir; kareleri ve durum mesajlarını iş parçacıkları arasında taşır.')],step=77)

slide('11. Sunumda gösterilecek demo','Windows çalışma izni ve bağımlılıklar hazır olduktan sonra')
rows([
('1  Kamerayı başlat','Kamera numarasını seç; canlı görüntüyü ve eklem çizgilerini göster.'),
('2  Parmak sayımını göster','Önce tek elde, sonra iki elde açık parmak sayısını değiştir; ekrandaki toplamı izle.'),
('3  Ses kontrolü moduna geç','Takibi durdur, modu seç ve yeniden başlat. 1, 2 ve 3 parmağı sabit tutarak %20, %40, %60 seviyelerini göster.'),
('4  El kaybını ve durdurmayı göster','Elini kadrajdan çıkar: ses sabit kalmalı. Durdur düğmesiyle kamerayı serbest bırak.')],step=77)

slide('12. Test sonuçları ve mevcut sınırlar','Kod düzeyindeki doğrulama ile gerçek cihaz testi ayrıdır')
card(40,158,425,'7 otomatik test başarılı','Açı hesabı, bozuk el verisi, kamera sürücü geçişi ve ses kontrolü durumları test edildi.')
card(485,158,435,'Donanım doğrulaması bekliyor','Canlı webcam, gerçek ses çıkışı ve uçtan uca performans bu çalışmada doğrulanmadı.')
text('Mevcut engel',40,316,20,GREEN,True)
text('Windows grup ilkesi projenin Python dosyasını engelledi. Çalıştırma izni sağlanmalı; Kurulum.bat ile ses bağımlılığı kurulmalı.',40,350,18)
text('Sayım; örtüşen eller, yan görünüş ve kıvrık parmaklarda yanılabilir. Ölçülmüş doğruluk oranı veya FPS sonucu bulunmuyor.',40,416,17,MUTED)

slide('13. Sonuç ve kaynaklar','Kamera görüntüsünden temassız bir kontrol arayüzüne')
text('Proje; görüntü alma, el tespiti, geometrik parmak sayımı ve işletim sistemi ses kontrolünü tek uygulamada birleştirir.',40,163,23,bold=True)
text('İncelenen proje dosyaları',40,266,18,GREEN,True)
text('main.py • camera.py • tracking.py • volume_control.py\ntests/test_core.py • tests/test_volume.py • requirements.txt',40,299,16)
text('Ses API başvurusu',40,369,18,GREEN,True)
text('Pycaw — AudioDevice.EndpointVolume ve ses seviyesi API’si',40,401,16)
text('https://andremiras.github.io/pycaw/api/index.html',40,432,14,MUTED)
c.linkURL('https://andremiras.github.io/pycaw/api/index.html',(40,80,580,110),relative=0)
c.save()
print(f'{page} sayfa oluşturuldu: {HERE / "El_Takibi_Pro_Sunum.pdf"}')
