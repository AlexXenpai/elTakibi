# Labirentte Yol Bulan Ajan

**Proje 3 · Python / Matplotlib · BFS + D* Lite hibrit planlama · A* karşılaştırması**

20×50 karelik bir labirentte kullanıcı fareyle engeller çizer. Ajan en kısa yolu bulur; arama, yol ve hareket animasyonla gösterilir. Ajan ilerlerken harita değiştirilirse **önceki arama bilgilerini koruyan D* Lite** yeni yolu hesaplar.

![Uygulama](docs/screenshot.png)

## Hızlı başlangıç

Python **3.10 veya üzeri** gerekir. ZIP'i açın ve bu README'nin bulunduğu klasörde terminal açın:

```bash
python -m venv .venv
```

Sanal ortamı işletim sisteminize göre etkinleştirin:

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
source .venv/bin/activate
```

Ardından:

```bash
python -m pip install -r requirements.txt
python main.py
```

Windows'ta `python` bulunamıyorsa `py` kullanabilirsiniz. PowerShell etkinleştirmeyi engellerse sistem ayarını değiştirmek yerine doğrudan `.venv\Scripts\python.exe -m pip install -r requirements.txt` ve `.venv\Scripts\python.exe main.py` çalıştırın.

Uygulamanın interaktif kullanımı grafik masaüstü gerektirir. Ubuntu/Debian'da Tk eksikse `sudo apt install python3-tk` kurulabilir. Notebook yerine terminalden çalıştırın; yalnızca statik resim gösteren notebook backend'leri fare etkileşimi sunmayabilir.

## Kullanım

Arayüzde sağdaki kontrol panelinden arama başlatabilir, duvar veya silgi aracını seçebilirsiniz. Üstteki kartlar duvar sayısını, en kısa yol uzunluğunu ve animasyonda o ana kadar gösterilen farklı kare sayısını izler. Alt tablo tamamlanmış aramanın toplam sonuçlarını gösterir; seçili algoritmanın satırı vurgulanır. Durum satırı arama, yol çizimi, ajan hareketi, duraklatma ve geçit bulunamaması aşamalarını belirtir.

| Kontrol | İşlev |
|---|---|
| Sol fare / sürükleme | Duvar ekle |
| Sağ fare / sürükleme | Duvar sil |
| **Duvar / D** ve **Silgi / E** | Sol fareyle kullanılacak düzenleme aracını seç |
| **Hibrit başlat** / **1** | İlk planı ters BFS ile bul, sonraki değişiklikleri D* Lite ile onar |
| **BFS** / **2** | Klasik başlangıçtan hedefe BFS çalıştır |
| **A*** / **3** | Başlangıçtan hedefe Manhattan sezgiselli A* çalıştır |
| **Duraklat / Devam et** / **Boşluk** | Animasyonu duraklat veya sürdür |
| **Arama hızı** kaydırıcısı | Kare başına gösterilecek arama adımı sayısını ayarla |
| **Örnek labirente dön** / **R** | Geçitli 9 engel sütununu ve ajanı geri yükle |
| **Tüm duvarları temizle** | Bütün engelleri kaldır |

**Renkler:** koyu = duvar, mor = işlenen kare, sarı = yol, yeşil = başlangıç, kırmızı = hedef, mavi = hareket eden ajan. Ajan başlangıçtayken başlangıç yeşil kalır.

Başlangıç, hedef veya ajanın bulunduğu kare kapatılamaz. Yeni algoritma seçmek ajanı başlangıca döndürür. Hibritte duvar düzenlemek ise ajanı bulunduğu yerde tutar ve eski animasyonu yeni planla değiştirir. Duraklatma durumu korunur. BFS/A* tekil modlarında düzenleme eski sonucu temizler; yeniden başlatmak gerekir. Fareyle çizilen duvarlar oturum içindir; veri dosyası değişmez.

### Dinamik planlamayı dene

**Karşılaştırma tablosu:** Her aramada BFS ve A* aynı harita üzerinde ajanın o anki konumundan çalıştırılır. Tabloda kuyruktan alınıp işlenen farklı kare sayısı ve bulunan yolun adım sayısı gösterilir; başlangıç ve hedef de işlendiğinde sayıma dahildir. Hibrit seçiliyse onun son planı da gösterilir. Dinamik onarımda hibrit önceki bilgiyi kullanırken BFS ve A* sıfırdan başlar. Yol bulunamazsa `Yol yok` yazılır. Tablo tamamlanmış aramanın sonucudur; animasyon bu aramayı sırayla gösterir.

1. **Hibrit başlat** düğmesine basın.
2. Arama ve sarı yolun çizilmesini izleyin.
3. Mavi ajan ilerlerken önündeki sarı karelerden birine sol tıklayın.
4. Ajanın konumu korunur; durum satırında **D* Lite (artımlı onarım)** görünür ve yeni rota çizilir.
5. Geçidi tamamen kapatırsanız **YOL YOK** mesajı gelir. Sağ tıklayıp geçit açınca otomatik olarak yeniden planlanır.

![Hareket sırasında yeni engelden kaçınma](docs/dynamic.png)

[Hızlandırılmış uygulama demosu](docs/demo.gif)

## Ödev gereksinimlerinin karşılığı

| Gereksinim | Projedeki karşılığı |
|---|---|
| En az 20×50 grid | 20 satır × 50 sütun = 1.000 kare |
| Başlangıç ve hedef | `(10, 1)` ve `(10, 48)`; sıfır tabanlı `(satır, sütun)` |
| En az 8 engelden kaçınma | Birbirinden ayrı 9 duvar şeridi, toplam 162 engelli kare; geçitler dönüşümlü |
| Fareyle duvar ekleme | Sol tıklama/sürükleme; sağ tıklamayla silme |
| BFS + dinamik hibrit | BFS ile üretilen mesafe alanının D* Lite tarafından artımlı kullanımı |
| En kısa yol | Dört yön, birim adım maliyeti; her sabit harita anında optimal yol |
| Arama ve yol animasyonu | İşlenen kareler → yol çizimi → ajan hareketi |
| Bonus A* ve kare sayıları | A* düğmesi, canlı sayaçlar, CSV sonuçlar ve karşılaştırma grafiği |
| Kodlar ve README | Python dosyaları, kurulum/kullanım, sonuçlar, kaynaklar |
| Ekran görüntüleri | `docs/screenshot.png`, `docs/dynamic.png` ve demo GIF |
| Veri seti bağlantısı | [data/maze.json](data/maze.json), yeniden üretim betiği |
| Ayrı GitHub reposu | Bu klasör bağımsız repo olarak yüklenmek üzere hazırlanmıştır; yükleme adımları aşağıda |

## Algoritmalar ve gerçek hibrit yapı

### BFS

Kuyruk kullanarak katman katman arar. Tüm kenarlar 1 maliyetli olduğu için hedefe ilk ulaşılan yol en kısa yoldur. Tekil BFS hedefi bulunca durur. Zaman karmaşıklığı `O(V+E)`, bellek `O(V)`.

### A*

Öncelik `f(n) = g(n) + h(n)` ile belirlenir. `h(n)` Manhattan uzaklığıdır. Dört yönlü birim maliyetli gridde bu sezgisel kabul edilebilir ve tutarlıdır. Eşit f değerinde küçük h, ardından eklenme sırası tercih edilir. Bu modelde A* da en kısa yolu bulur. Heap tabanlı uygulamada zaman `O((V+E) log V)`, bellek `O(V+E)` mertebesindedir.

### BFS + D* Lite

Bu uygulamanın hibrit tasarımı:

1. **Başlangıçta hedef köklü tam BFS** ile hedefe erişebilen her karenin tam uzaklığı hesaplanır. Yönsüz gridde bu alan başlangıçtan hedefe en kısa yolu da verir.
2. BFS uzaklıkları D* Lite'ın **g ve rhs** tablolarına aktarılır. Başlangıçta bütün köşeler tutarlıdır: `g = rhs`. Hedefe erişemeyenler sonsuzdur.
3. Kullanıcı bir kareyi değiştirdiğinde o karenin ve geometrik komşularının `rhs` değerleri güncellenir. Tutarsız köşeler öncelik kuyruğuna girer.
4. Ajanın yeni konumuna göre **km** güncellenir. D* Lite `ComputeShortestPath` döngüsü yalnızca mevcut konumun doğru yolu için gerekli tutarsızlıkları onarır.
5. Yol, komşuların g değerleri üzerinden çıkarılır. **g/rhs tabloları ve kuyruk sonraki plan için korunur.**

Bu, yalnızca algoritma seçen bir menü değildir: BFS'nin ürettiği veri D* Lite'ın başlangıç durumudur. Makaledeki standart sonsuz-değerli başlangıç yerine tam BFS alanı kullanılmıştır; bu projeye ait hibrit uyarlamadır. Temel D* Lite anahtar ve onarım kuralları korunmuştur:

```text
key(u) = [min(g(u), rhs(u)) + Manhattan(ajan, u) + km,
          min(g(u), rhs(u))]
rhs(hedef) = 0
rhs(u) = min(1 + g(komşu))       # yalnızca geçilebilir kenarlar
```

Duvarın iki yönündeki kenarların maliyeti sonsuz kabul edilir. Duvar silme maliyet azalmasını, duvar ekleme maliyet artışını tetikler. Makalenin temel sürümü kullanılmıştır; kuyrukta eski kayıtlar tembel silinir ve gerektiğinde sıkıştırılır. Büyük bir değişiklikte D* Lite geniş bir alanı yeniden işleyebilir. Her haritada daha az iş yapacağı iddia edilmez.

**Optimalite sınırı:** Her plan, o anda bilinen haritada mevcut konumdan hedefe en kısa yoldur. Gelecekteki kullanıcı değişiklikleri bilinmediği için hareketlerin tamamının toplam uzunluğu için küresel optimum garantisi verilmez. Harita bütünüyle bilinmektedir; sensörle keşif simülasyonu yapılmaz.

## Ölçülen sonuçlar

`python benchmark.py` aynı harita/konum/değişiklik dizisini üç yöntemle çalıştırır ve yol uzunluklarının eşitliğini denetler. Sayılar [docs/results.csv](docs/results.csv) dosyasından üretilmiştir.

| Olay | En kısa yol (adım) | BFS kare | A* kare | Hibrit kare |
|---|---:|---:|---:|---:|
| İlk plan | 155 | 802 | 747 | 838 |
| Ajan 3 adım ilerledi | 152 | 802 | 747 | 0 |
| Yola engel eklendi | 154 | 801 | 746 | 6 |
| Engel silindi | 152 | 802 | 747 | 5 |
| Geçit tamamen kapandı | Yol yok | 428 | 428 | 429 |
| Geçit yeniden açıldı | 152 | 802 | 747 | 320 |

![Karşılaştırma grafiği](docs/comparison.png)

### Sayaçları nasıl okumalı?

- **Kare:** bir planlama çağrısında işlenen benzersiz köşe. BFS/A* için kuyruktan çıkarılıp genişletilen köşe; hibritin sonraki planlarında g değeri onarılan köşe. Aynı köşenin aynı plandaki tekrarları tek sayılır. D* Lite engel haline gelmiş bir köşenin eski değerini de onarabilir.
- **İlk hibrit planın maliyeti gizlenmez:** BFS mesafe alanını tam hesapladığı için 838 kare işler; tekil BFS hedefte durduğu için 802 kare işler.
- **0 kare, 0 hesaplama süresi demek değildir:** mevcut alan kullanılabilir durumdadır; buna rağmen harita farkı denetlenir ve yol çıkarılır. Bu ölçüm çalışma süresi karşılaştırması değildir.
- CSV'de D* Lite'ın **kuyruk çıkarma sayısı** (`queue_pops`) ve **UpdateVertex çağrıları** (`vertex_updates`) da ayrıca bulunur. Komşu incelemeleri benzersiz-kare sayacına dahil değildir.
- Arayüzdeki hibrit toplamı, ilk BFS alanını ve her yeniden planlamanın kare sayısını toplar; farklı planlarda tekrar işlenen kareler tekrar sayılır. Karşılaştırma amacıyla ayrıca çalıştırılan BFS/A* bu toplama dahil değildir.
- Arama hızlıca hesaplanır, ardından işlem sırası animasyonla oynatılır. Hız kaydırıcısı algoritmayı değil gösterimi etkiler.

İlk haritada A* ile BFS aynı 155 adımlık yolu bulur; A* 55 daha az kare işler. Yerel değişiklik örneğinde hibrit eski bilgiden yararlanır. Geçit tamamen kapanınca hibritin 429, BFS'nin 428 kare işlemesi, hibritin her durumda üstün olmadığını gösterir.

## Veri seti ve kaynaklar

**Veri seti bağlantısı:** [data/maze.json](data/maze.json).

Harici veri seti kullanılmamıştır. Bu dosya proje için üretilmiş sentetik veridir; grid boyutu, başlangıç/hedef ve duvar koordinatlarını içerir. GitHub'a yüklendiğinde yukarıdaki göreli bağlantı doğrudan reponun veri dosyasını açar. Çevrim içi veri indirmeye gerek yoktur.

Aynı örneği tekrar üretmek için:

```bash
python generate_maze.py
```

Algoritmik kaynak: Sven Koenig ve Maxim Likhachev, **D* Lite**, AAAI 2002, s. 476–483. [Yazarların yayın sayfası ve düzeltme notu](https://idm-lab.org/bib/abstracts/Koen02e.html), [makale PDF](https://idm-lab.org/bib/abstracts/papers/aaai02b.pdf). Bu proje, Figure 3'teki temel D* Lite onarımını BFS başlangıç alanıyla birleştirir. Makale pakete kopyalanmamıştır.

## Testler ve tekrar üretim

```bash
python -m unittest -v
python benchmark.py
python main.py --screenshot
python record_demo.py
```

Ekransız sunucuda `MPLBACKEND=Agg python -m unittest -v` ve `MPLBACKEND=Agg python main.py --screenshot` kullanılabilir. Benchmark ve demo betikleri Agg backend'ini kendileri seçer.

**Doğrulama ortamı:** Python 3.12.14, Matplotlib 3.10.8. **11 test başarılı.**

- 60 sabit tohumlu rastgele 20×50 haritada BFS/A* yol uzunluğu ve adım geçerliliği.
- 40 haritada 36'şar planlama: **1.440 durumda** hibritin BFS referansıyla aynı yol uzunluğunu vermesi; ajan hareketi, tekli/çoklu duvar ekleme ve silme.
- Kapanan/açılan geçit, kısayol, başlangıç=hedef, geçersiz koordinatlar.
- Değişmeyen haritada eski D* Lite nesnesinin ve mesafe alanının korunması.
- Matplotlib'in gerçek `MouseEvent` / `KeyEvent` olaylarıyla tıklama, sürükleme, silme, korunan kareler, tuşlar, hız ayarı ve sıfırlama.
- Ajan hareket ederken yeni duvar ekleme, konumun korunması, yeni engelden kaçınma ve hedefe ulaşma.
- Yol yokken bekleme, geçit açınca toparlanma ve düzenleme sırasında duraklatmanın korunması.

Olay testleri ekransız Matplotlib canvas'ında çalışır; farklı işletim sistemlerindeki fiziksel fare/Tk entegrasyonu burada doğrulanmamıştır. GitHub Actions dosyası Python 3.10 ve 3.12 için hazırlanmıştır; bulutta çalıştığı ancak repo yüklendikten sonra görülebilir.

## Dosya yapısı

| Dosya | Amaç |
|---|---|
| `main.py` | Grafik arayüz, kullanıcı olayları, animasyon |
| `ui.py` | Görsel tasarım, kontrol paneli, canlı sayaçlar ve karşılaştırma tablosu |
| `algorithms.py` | BFS, A*, D* Lite ve hibrit |
| `generate_maze.py` | Sentetik veri üretimi |
| `benchmark.py` | Tekrarlanabilir sonuçlar, CSV ve grafik |
| `record_demo.py` | Uygulama durumlarından hızlandırılmış GIF ve dinamik ekran görüntüsü |
| `test_algorithms.py` | Algoritma doğruluk ve artımlı planlama testleri |
| `test_ui.py` | Matplotlib olay/animasyon akışı testleri |
| `requirements.txt` | Python bağımlılığı |
| `data/maze.json` | Kullanılan veri seti |
| `docs/` | Sonuçlar, grafik, ekran görüntüleri ve demo |
| `.github/workflows/tests.yml` | GitHub Actions test akışı |
| `SUNUM_NOTLARI.md` | Kısa demo akışı ve teknik açıklama |

## Ayrı GitHub reposuna teslim

Bu klasör yalnızca Proje 3 içindir; başka projeleri aynı repoya koymayın. Repo oluşturulup yüklenmeden GitHub teslim koşulu tamamlanmış sayılmaz.

GitHub'da `labirent-ajan` adında boş bir repo oluşturun; ilk aşamada README eklemeyin. Bu klasörde aşağıdaki komutları çalıştırın ve `KULLANICI_ADINIZ` kısmını gerçek hesabınızla değiştirin:

```bash
git init
git add .
git commit -m "Proje 3: BFS ve D* Lite hibrit labirent ajanı"
git branch -M main
git remote add origin https://github.com/KULLANICI_ADINIZ/labirent-ajan.git
git push -u origin main
```

Git kurulu değilse GitHub'ın **Add file → Upload files** özelliğiyle klasörün içindeki dosyaları yükleyebilirsiniz; ZIP'in kendisini yüklemek yerine içeriğini yükleyin. Gizli `.github` klasörünü de ekleyin. Son olarak README resimlerinin ve veri bağlantısının açıldığını, Actions testlerinin başarılı olduğunu kontrol edip repo bağlantısını teslim edin.
