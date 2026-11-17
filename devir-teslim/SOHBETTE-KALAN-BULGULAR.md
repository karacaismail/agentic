# Yalnız sohbette kalan önemli bilgiler ve bulgular

Tarih: 27.09.2026. Buradaki bilgiler başka hiçbir dosyada yok ya da dosyalara dağılmış hâlde. Konuşma kapanınca kaybolmasınlar diye toplandı. Dosyalarda karşılığı olanlar için yalnız yer gösterildi.

---

## 1. Kullanıcının kuralları (hepsi kalıcı)

**Git kimliği**
- Yeni işte yazar ve committer aynı olmalı: `karacaismail <35493655+karacaismail@users.noreply.github.com>`.
- Commit'lere ve PR'lara yapay zekâ ortak yazarı, "generated with" imzası, başka bir `Co-Authored-By` ya da oturum satırı eklenmez.
- `/Users/w6x/.config/git/author-guard/hooks` koruması devre dışı bırakılmaz. Bunu atlatacak hiçbir şey kullanılmaz: `--no-verify`, `core.hooksPath` değişikliği, başka git yapılandırması, plumbing.
- Başkasının işi sessizce üstlenilmez; çekilmiş upstream geçmişi korunur.
- Bulut oturumları bu Mac'teki korumayla kapsanmaz; orada eşdeğer bir denetim gerekir.
- Bu oturumda hiç git işlemi yapılmadı.

**Konteyner**
- Bu Mac'te konteyner çalışma zamanı Colima. Docker Desktop önerilmez, kurulmaz, kullanılmaz.
- Kullanıcı "Docker ile" derse önce "Tercihiniz Docker yerine Colima idi." denir, sonra Colima ile devam edilir.
- Hetzner/Debian sunucularında Docker Engine kullanılır.

**İletişim ve kapsam**
- Yalnız Türkçe yazılır.
- **Yalnız istenen yapılır.** Araştırma sorusuna yalnız araştırma cevabı verilir. İstenmemiş kod değişikliği, dosya ekleme ya da denetim yapılmaz. Kullanıcı token'ları parayla alıyor.
- Kullanıcının verdiği örnekler bağlamdır, değerlendirilecek nesne değildir: ekran görüntüsü, araç adları, CronHR prototipi. Plane, OpenHands ve n8n gibi araç adları seçim değil, örnektir.

**Harita kuralları**
- İhtiyaç haritası metinleri markasızdır. Ürün adı yerine "LLM", "orkestrasyon", "iş takip sistemi" gibi genel terimler kullanılır.
- Araçlar ve riskler ayrı klasörlerde tutulur.
- Projelendirilmez, ama projelendirme için hiçbir şey eksik bırakılmaz.
- Araştırma derin, tekrarlı ve doğrulanmış olmalı.

**Dokunulmayacak yerler**
- Kullanıcının özgün kaynak dosyaları değiştirilmez.
- `~/Developer/software-factory` (pilot) ve `/Users/w6x/Documents/otomasyon coding 2` (Codex dizini) yalnız okunur. Yazma, silme, orada betik çalıştırma yok.
- `.env` ve kimlik bilgisi dosyaları açılmaz.

**Proje amacı** (kullanıcının sözleri, 27.09): "insanların ve yapay zekâ ajanlarının birlikte, birden fazla ekip üzerinden güvenilir yazılım üretebildiği bir çalışma sistemi kurmak". Dört dayanağı var: insan–ajan birlikte çalışma, çok ekip, güvenilir yazılım ve çalışan sistem. İnsan yalnız onaylayan değil, eş üreticidir.

---

## 2. Ortam bilgileri

**Colima**
- Profil `factory`. Adres: `DOCKER_HOST=unix:///Users/w6x/.colima/factory/docker.sock`.
- Bu Mac'te Docker kimlik yardımcısı (osxkeychain) eksik, bu yüzden imaj çekimi takılıyor. Çözüm: geçici bir `DOCKER_CONFIG` klasöründe tek bir `config.json` oluşturmak.
  - İçeriği: `{"cliPluginsExtraDirs": ["/Users/w6x/.docker/cli-plugins"]}`.
  - Kullanıcının `~/.docker` klasörüne dokunulmadı.

**Python ve testler**
- Sistemdeki python3 sürüm 3.9 ve `yaml` modülü yok. Testler konteynerde koşar:

  ```bash
  cd "/Users/w6x/Documents/otomasyon coding/agentic-fabrika"
  docker build -q --build-arg GELISTIRME=1 -t fabrika-test:yerel .
  docker run --rm -e FABRIKA_ENTEGRASYON=1 -v /var/run/docker.sock:/var/run/docker.sock -v /var/lib/fabrika:/var/lib/fabrika fabrika-test:yerel python -m pytest -q
  bash e2e/calistir.sh   # uçtan uca; son satır "UÇTAN UCA BAŞARILI"
  ```

- `/var/lib/fabrika` Colima sanal makinesinin içindedir; entegrasyon testleri orayı kullanır.
- Son durum (27.09): 58 test geçti, uçtan uca senaryo geçti. Plane, GitHub ve model sahteydi.

**Diğer ortam notları**
- macOS izin kısıtı (TCC) yüzünden `python3 -m http.server`, Documents altında `getcwd` hatası veriyor. Çözüm: `sh -c "cd <scratchpad> && exec python3 -m http.server"`.
- Pilotta takılı kalmış `happy_banach` konteyneri bilerek olduğu gibi bırakıldı.
- Bilgisayarda Codex (ChatGPT uygulaması) da çalışıyor ve `otomasyon coding 2` dizininde aynı sorular üzerinde paralel iş yapıyor.

**Alt ajanlarla çalışma**
- Uzun alt ajanlar 600 saniyelik bekçiye takılabiliyor. 27.09'da hepsi aynı anda takıldı; bu genel bir kesintiydi.
- Önlem: ajana adımları küçük tutmasını, ara sonuçları sık yazmasını ve toplu karşılaştırmaları betikle yapmasını söylemek.
- Takılan ajan, ne yapacağı söylenerek kaldığı yerden devam ettirilir.
- Araştırma ajanlarının oturum başına web arama kotası (200) doldu. Kalan doğrulamalar `gh api`, WebFetch ve resmî PDF'lerle yapıldı.

---

## 3. Önceki Kestra pilotu hakkında gerçekler

`~/Developer/software-factory` klasörü; ayrıntılar A0 ve E6 dosyalarında.

- Dört kök görevin hiçbiri müdahalesiz üretime çıkmadı.
- Yedi günde 98 modül ve yaklaşık 27 bin satıra büyüdü. Bunların 17'si birbiriyle örtüşen onarım/kurtarma modülüydü. Kodun büyük kısmı sürüm kontrolü dışındaydı.
- Tek abonelik hesabında 330 kapasite hatası ve 46 hata döngüsü görüldü. Mac uykuya geçince kiralamalar (lease) kayboldu.
- Pilot commit'leri "Factory Bot" kimliğiyle atmıştı. Bu, kullanıcının git politikasına aykırı.
- **1 GB (E6 düzeltmesi):** Bellek taşması gerçekti ama sınıra takılan, tarayıcı testlerini koşturan konteynerin 1g sınırıydı.
  - 2g'de testler 3/3 geçti. 150 testten sonra 2g de yetmedi, testler 50'lik gruplarla koşturuldu.
  - Sunucunun RAM'i darboğaz değildi.
- **7 günlük zaman aşımı (E6):**
  - Kabul adımı 18.09 16:14 UTC'den itibaren panoda bir insan eylemini bekledi.
  - Tam 7 gün sonra `P7D` ile `KESTRA_FAILED` oldu.
  - İnsana düşen iş sahipsiz kaldı.
- **"Bayat RUNNING":** 9 çocuk iş RUNNING görünüyordu, ama takımlar 18.09'da birleşmişti. Takılan bir iş yoktu; bayat olan durum kaydıydı.
- **Codex'in bulduğu ek dersler (E6):**
  - 600 saniyelik boşta kalma sınırı uzun bir testi öldürdü.
  - "CAPACITY" alt dizesi 4.762 CLAIM'lik bir döngüye yol açtı.
  - Kapasite yanlış rolden ölçüldü.
  - Canlı onarım başka bir kapıyı bozdu.
  - BlockageStoreError'da 1.385 satır var, hepsi 3 gözlem kimliğinden geliyor.

---

## 4. Teknik gerçekler ve doğrulamalar

**GitHub**
- Aynı sahip (hesap ya da organizasyon) altında "alpha" adında yalnız bir depo olabilir. "Her projenin alpha deposu" için proje başına tam `sahip/depo` eşlemesi gerekir.
- "alpha" depo adı ile alpha ortamı ayrı kavramlardır (E4, Codex).

**Plane Community Edition (CE) v1.4.2**
- Webhook gövdesi v1 biçiminde. İmza `X-Plane-Signature` başlığında: ham gövdenin HMAC-SHA256 hex değeri.
- 5xx yanıtında yeniden denemiyor. Beş ağ hatasından sonra webhook'u kapatıyor.
- İç IP'lere gönderim için `WEBHOOK_ALLOWED_IPS` ayarı gerekir.
- Dakikada 60 istek sınırı var. Özel alan desteği yok. API anahtarı kullanıcıya bağlı.
- Codex'in yalnız v2 kabul eden adaptörü, CE sürümünde her olayı reddeder (E4).

**Model sağlayıcı**
- Sunucu otomasyonu için abonelik değil, API anahtarı kullanılmalı.
- Aylık harcama tavanları: Start 500 $, Build 1.000 $, Scale 200.000 $. Tavana gelindiğinde bütün filo aynı anda durur. Tek ajan 7/24 çalışırsa Start tavanını pilotta bile aşar (C6).

**Kapasite**
- Hetzner AX102 (16 çekirdek, 32 iş parçacığı, 128 GB, aylık 257,30 €) yaklaşık 8–14 orta ölçekli ajan taşır; bu kabaca bir ART eder.
- 144 ajan için 10–18 sunucu ve Kubernetes gerekir (C6).
- "Ajan başına 1 GiB" bir taban değerdir, tavan değil.

**Çıkış vekili (27.09, Colima'da doğrulandı)**
- Sandbox ağından doğrudan internet erişimi yok, dış DNS de çözülmüyor.
- Vekil üzerinden `api.anthropic.com` 401, npm 200 döndü. `example.com` ve `gist.github.com` 403 ile reddedildi.
- Yapılandırma dosyası: `agentic-fabrika/sandbox/vekil/squid.conf`.

**OpenHands**
- Geçiş SSS'i 16.06.2026'da yayımlandı. Eski kod 27.07.2026'da `legacy` deposuna taşınıp arşivlendi (`gh api` ile doğrulandı).

**Resmî 2026 asgari ücret tablosu (ÇSGB PDF'i okunarak doğrulandı; HRMS oracle'ı için)**
- Brüt 33.030,00 TL, net 28.075,50 TL.
- İşveren SGK payı: indirimsiz %21,75, diğer sektörler %19,75, imalat %16,75. İşsizlik sigortası işveren payı %2.

**Fabrikadaki iki teknik açık (E4)**
- Çıkış kodu 137 tek başına bellek taşmasının kanıtı değildir; kesin işaret cgroup `oom_kill` sayacıdır. Bizim kod 137'yi taşma sayıyor.
- `claude -p "$(cat istem)"` kullanımında yaklaşık 128 KiB'lık argv sınırı riski var.

**ACP**
- Hermes Agent ve OpenClaw doğrudan ACP destekliyor.
- Kayıttaki 35 ajandan 12'si `session/resume` destekliyor, hiçbiri `session/stop` desteklemiyor (C2).

---

## 5. Dikkat: haritaları ezebilecek betikler

- `calisma-arsivi/2026-09-27-oturum/arac/birlestir.py` yeniden çalıştırılırsa `arac-haritasi/donguler/D15` ve Harbor düzeltmesi silinir. Aynı ad birleştirme hatasının Glean ve Faker kayıtlarını da bozduğundan şüpheleniliyor; düzeltilmedi (E2).
- `calisma-arsivi/2026-09-27-oturum/risk/` altındaki birleştirme betiği (`risk_birlestir.py`) klasörleri silip yeniden üretir. E3 onun yerine sayaçları yerinde güncelledi.
- E3'ten önce alınan risk haritası yedeği: `calisma-arsivi/2026-09-27-oturum/e3/yedek-risk-haritasi/`.
- Güvenle çalıştırılabilir: `ihtiyac-haritasi/gorsel/uret.py` (E1 çalıştırdı, sorunsuz).
- Codex dizininin parmak izleri: `calisma-arsivi/2026-09-27-oturum/codex-parmak-izi-{once,simdi,son}.txt`.

---

## 6. Codex ile ilişki

**Codex dizini** (`otomasyon coding 2`, yalnız okunur): aynı soruları Codex'e de sordunuz. Karşılaştırma sonuçları E1–E6'da. Özet:

- **Codex'in güçlü olduğu yer:** sözleşme ve tasarım. Çalışan pilotu (`agentic-sistem/uygulama/`) gerçek Temporal üzerinde 9 kontrolü geçti:
  - çift kabul,
  - sonsuz onarım döngüsü olmaması,
  - dış etkiden sonra çökmede çift yazım olmaması,
  - belirsiz etkinin körlemesine tekrar denenmemesi,
  - iptal senaryoları,
  - işçi değişimi ve yeniden oynatma.

  Ancak model, GitHub ve deploy adımları sahte (fixture). Bunu `status.json` dosyasında dürüstçe ayırıyor: neyin uygulandığı, neyin çalıştırılıp denendiği, neyin beklediği.
- **Bizim güçlü olduğumuz yer:** gerçek bileşenlerle, yani Temporal, Postgres, Docker ve git ile çalışan bir uçtan uca akış. Dış servisler (Plane, GitHub, model) sahte.
- **27.09'da Codex bizi de okudu:**
  - 14:46'da bizim klasör ağacımızı kendi dizinine kopyaladı (`claude-karsilastirma/`).
  - Bizim bulgularla kendi tarafını tamamlıyor (`agentic-sistem/data/14_karsilastirmali_tamamlama/`, `research_notes/Claude bulgularıyla kapsam tamamlama/`).
  - Codex'in bir itirazı doğru çıktı: D1'de sdk-python #1894 dört kez tekrar ediyor.
- Bizim ajanlar Codex dizinine hiç yazmadı: sıfır Write/Edit işlemi, sıfır yazan Bash komutu. Parmak izi karşılaştırmasında silinen dosya da yok.

---

## 7. Süreçte yaptığım hatalar (tekrarlanmasın)

1. Araştırma istenirken kodu değiştirdim (S9). Bu, "yalnız isteneni yap" kuralının doğmasına yol açtı.
2. Kapsamı göstermek için verilen CronHR prototipini içerik açısından denetledim ve bunu kullanıcının hatası gibi sundum (S14).
3. Araştırma klasörüne istenmemiş bir sentez dosyası ekledim (`C0-sentez.md`).
4. Bir yanıtı İngilizce yazdım (S18).
5. Codex'in ilk envanteri yüzeysel kaldı (S20):
   - Ortak kaynakların aynı olduğunu kanıtlamadan varsaydım.
   - `uygulama/`, `deneyler/`, `dunya-vakalari/`, PDF gereksinimleri ve ham araştırmayı kaçırdım.
   - İkinci turda bunlar doğrulandı ve kapsandı.

---

## 8. Yayınlanan sayfalar

- **Agentic Fabrika:** https://claude.ai/artifact/GwGkfBNDLzRCpcgKyuYq4b
  - Kaynak: `agentic-fabrika/docs/agentic-fabrika.html`. Eski.
- **İnsan–Ajan Yazılım İhtiyaç Haritası:** https://claude.ai/artifact/PUuCFUAgEZs8TJP44CYe8C
  - Kaynak: `ihtiyac-haritasi/gorsel/ihtiyac-haritasi.html`. Yayın eski; yerel dosya güncel.
- İlgili olabilir, önceki oturumdan: **Agentic-first İş Akışı Panosu**, https://claude.ai/artifact/7fTdGEeGD6dCwpmCvLrG5E
