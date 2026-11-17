# Kanıttan karara: derin inceleme ve arayüz düzeltmeleri

27 Eylül 2026

## Kapsam

82 gömülü kayıt üzerinden sentez; 5 özgün yerel aralık ve 3 dış kaynak tekrar okundu. Güncel servis/alpha/araç uygunluğu test edilmedi.

24 sentez başlığı yeni olay sayısı değildir. 82 kaynak kaydı bağımsız 82 hata değildir. Eski raporlar kaynak metni olarak korundu. Hiçbir mimari veya araç kullanıcı adına seçilmedi. Fabrika ve uzak sistemde değişiklik yapılmadı.

## Öne çıkan ayrımlar

- 1 GB ölçümü tarayıcı test konteynerine aittir; ajan başına RAM hesabı vermez.
- 4.762 CLAIM/RETRY, 4.762 model çağrısı değildir; ilgili kayıtta bir model çağrısı var.
- 600 saniyelik idle saati, yaklaşık 70 dakika süren geçerli testi kesmiş.
- Teşhis dosyasını okuyamamak SUCCESS olarak kaydedilmiş; çağrı bitişi ile kanıt yeterliliği ayrılmalı.
- WF-06 yazarı ürün arızası izlenimini geri çekmiş.
- DE-02 için pinned_fetch eksik; kurulu Plane sürümünün retry davranışı kanıtlanmadı.
- DP kayıtları statik kod yollarıdır; DK kayıtları tasarım boşluklarıdır. Canlı olay gibi sayılamaz.

## Arayüzde değişenler

- Gruplanmış gezinme ve kanıt odaklı giriş sayfası.
- 24 bulguda gözlem, yorum, sınır, seçenek/bedel ve eksik deney.
- Kullanıcı notları başlangıçta boş; senaryo ayarlarına otomatik aktarılmaz.
- 82 kaydın okunabilir kanıt görünümü, ham JSON ve kaynak izi.
- Markdown okuma görünümü; belge içeriğinde arama.
- Önlem seçimini başarı gibi gösteren yüzde halkaları kaldırıldı.
- Tarihî araç hükümleri güncel tavsiye olarak etiketlenmiyor.
- Kullanıcı notları JSON ve PDF çıktısına eklenir.

## Özgün dosya tekrar okumaları

- `S11` · /Users/w6x/Developer/software-factory/experiments/runner-environment-20260915/README.md · satır 8–23 · önceki hash eşleşmesi: True

- `S14` · /Users/w6x/Developer/software-factory/experiments/foundation-repair-20260915/README.md · satır 507–513 · önceki hash eşleşmesi: True

- `S14` · /Users/w6x/Developer/software-factory/experiments/foundation-repair-20260915/README.md · satır 536–542 · önceki hash eşleşmesi: True

- `S06` · /Users/w6x/Developer/software-factory/docs/handoffs/2026-09-15-claude/DEVIR-RAPORU.md · satır 93–109 · önceki hash eşleşmesi: True

- `S20` · Özgün Claude JSONL transkriptinin 1573. satırındaki tool_result yeniden okundu. Kernel cgroup OOM satırları MainThread ve headless_shell için doğrulandı. Kaynak dosyasının SHA-256 değeri önceki envanterle eşleşti; yalnız ilgili satır alıntıları analiz JSON’unda saklandı. Yinelenen satırlar bağımsız olay sayılmadı.

## Dış kaynak tekrar okumaları

- [CP-01](https://github.com/OpenHands/software-agent-sdk/issues/762) · Sabit stuck eşikleri meşru bekleme/tekrarları kesebiliyor; eşik yapılandırma önerisi. Issue metni okundu; yerel tekrar deneyi yapılmadı.

- [CP-05](https://github.com/Factory-AI/factory/issues/33) · Kullanıcı raporu: ps yokken liveness kontrolü SIGKILL üretiyor. Yazarın mekanizma açıklaması; maintainer tarafından doğrulanmış genel ürün kusuru diye sayılmadı.

- [WF-06](https://community.temporal.io/t/workflow-not-recovered-after-crash/1770) · Yazar 24 Mart 2021 son mesajında kendi kod hatasını kabul ediyor. Başlıktaki ürün kusuru izlenimi son mesajla düzeltilmeli.

## Karar soruları

### B01 · 1 GB sınırı tarayıcı testini öldürdü; ajan kapasitesi ölçülmedi.

**Kanıt türü:** Yerel deney + kernel kaydı · **Kayıtlar:** K03, CP-05

**Gözlem:** 15 Eylül deneyinde 51 testlik birleşik koşu yaklaşık 4,3 saniyede, rapor üretmeden 137 ile bitti. Kernel kaydında cgroup OOM var. Aynı aday 2 GB ile 3/3 geçti; örneklenen tepe 887–942 MiB.

**Yorum:** Bu olayda darboğaz tarayıcı test konteyneriydi. 137 kodunun tek başına OOM anlamına gelmemesi için kernel kanıtı ayırıcıdır.

**Çıkarılamayacak sonuç:** Bu ölçüm, bir LLM ajanının 1 GB tükettiğini veya 128 GB sunucunun 128 ajan çalıştıracağını göstermez. Örneklenmiş tepe anlık tepeyi kaçırabilir; daha büyük test setinde 2 GB da yetersiz kalmış.

**Senin karar sorunun:** Test yükü büyüdüğünde kapasiteyi nasıl yöneteceksin?

- Sınırı ölçerek büyüt: Bir işi hızla kurtarabilir; host toplam bütçesi ayrıca sınırlandırılır.
- Testleri partilere böl: Tepe bellek düşebilir; kurulum tekrarı ve toplam süre artabilir.
- İkisini yük profiline göre birleştir: Daha fazla seçenek verir; kabul deneyi ve zamanlayıcı karmaşıklığı artar.

**Eksik ölçüm / çalıştırılmamış deney:** Aynı commit ve test setini farklı parti/eşzamanlılık ayarlarında çalıştır; cgroup tepe bellek, OOM sayısı, süre ve host toplamını kaydet. Bu atlas bu deneyi çalıştırmadı.

### B02 · İlerleyen test, 600 saniyelik “ajan sessiz” kuralına takıldı.

**Kanıt türü:** Tarihli deney günlüğü · **Kayıtlar:** K10, CP-01

**Gözlem:** 18 Eylül günlüğünde bütünleşik test süresi 570 saniyeden yaklaşık 70 dakikaya çıkıyor. Gözetleyici yalnız yeni test makbuzunu ilerleme saydığı için 600 saniyede çağrıyı öldürüyor; üç tekrar sonrası kurtarma sınırına ulaşılıyor.

**Yorum:** Ajan sessizliği, alt sürecin ilerlemesi ve görevin toplam süresi aynı saatle izlenmiş. Başka orkestratöre geçmek bu sinyal ayrımını kendiliğinden sağlamaz.

**Çıkarılamayacak sonuç:** Bu bulgu bütün timeout’ları kaldırmayı desteklemez. OpenHands SDK kaydı benzer mekanizma ailesidir; aynı olay veya kod değildir.

**Senin karar sorunun:** Uzun süren geçerli iş ile kilitlenmeyi hangi sinyalle ayıracaksın?

- Aşama bazlı süre ve ilerleme: Test/derleme için ayrı sinyal gerekir; yanlış kesmeleri azaltmayı hedefler.
- Tek uzun üst süre: Kurulumu daha basittir; gerçek kilit daha geç fark edilir.

**Eksik ölçüm / çalıştırılmamış deney:** Aynı gözetleyicide bilerek uzun süren test, gerçek sonsuz döngü ve ölü alt süreç dene; her biri için tespit ve kurtarma süresini ayrı kaydet.

### B03 · 4.762 kuyruk olayı yalnız bir model çağrısı üretti.

**Kanıt türü:** Tarihli deney günlüğü · **Kayıtlar:** K13

**Gözlem:** 18 Eylül 00:56 kaydı: 93 bin karakterlik inceleme geçmişi CONTEXT_CAPACITY_UNSUPPORTED üretiyor. CAPACITY metni kapasite beklemesi sayılıyor; yaklaşık 10 saniyelik yeniden kabul döngüsünde 4.762 CLAIM/RETRY olayı, yalnız bir model çağrısı var.

**Yorum:** Kuyruğun hareket etmesi işin ilerlediği anlamına gelmiyor. Hata sınıflandırması, bağlam boyutu ve tekrar kabul koşulu aynı tıkanmayı büyütmüş.

**Çıkarılamayacak sonuç:** 4.762 sayısı ajan, bitmiş görev veya model çağrısı sayısı değildir. Tarihli rapor güncel sistemin hâlâ böyle olduğunu kanıtlamaz.

**Senin karar sorunun:** Bağlam sınırına gelen işi hangi yoldan sürdüreceksin?

- Özet + değişmez kanıt referansı: Girdi küçülür; özetin kaybettiği yükümlülükleri kontrol etmek gerekir.
- Daha geniş bağlamlı çalışan: Özetleme azalabilir; maliyet ve model uyumluluğu ölçülmelidir.
- İşi bağımsız alt parçalara ayır: Bağlam küçülebilir; entegrasyon ve ana kabul ölçütlerini koruma yükü getirir.

**Eksik ölçüm / çalıştırılmamış deney:** Aynı hata ve değişmeyen girdi altında tekrar sayısını sınırla; değişen bağlam digest’i olmadan yeniden kabulü gözle. Kanıt eksilmesi testi de ekle.

### B04 · Teşhis ajanı dosyayı okuyamadı; çağrı yine başarılı sayıldı.

**Kanıt türü:** Tarihli devir raporu · **Kayıtlar:** K08, MA-08

**Gözlem:** 15 Eylül devir kaydı, INCIDENT.json okunamadığını söyleyen çıktıya rağmen bakım isteğinin SUCCESS ve engelin diagnosed olduğunu aktarıyor. Prompt dosyayı istiyor; içerik girdide yok, okuma aracı yok, shell yasak.

**Yorum:** Tamamlama durumu yalnız çağrının bittiğini bildirmiş. Teşhis kanıtı ve araç erişimi ayrıca doğrulanmamış.

**Çıkarılamayacak sonuç:** Bu, modelin isteksiz olduğunu veya tüm shell yetkilerinin açılması gerektiğini göstermez. Kaynak bir tarihî rapordur; aynı çağrı yeniden çalıştırılmadı.

**Senin karar sorunun:** Teşhis rolüne olay verisini nasıl ulaştıracaksın?

- Temizlenmiş içerik girdiye ekle: Az yetkiyle çalışır; boyut ve veri tazeliği yönetilir.
- Dar kapsamlı salt okunur araç: Güncel kanıtı okuyabilir; dosya kapsamı ve erişim kaydı gerekir.

**Eksik ölçüm / çalıştırılmamış deney:** Bilinen işareti içeren olay dosyası ver; okunduğuna dair doğrulanabilir alan bekle. Erişim yoksa sonuç NEEDS_EVIDENCE olmalı; diagnosed olmamalı.

### B05 · Engel kaydı ve rol ataması, onarım çalışanını başlatmadı.

**Kanıt türü:** Tarihî akış kaydı · **Kayıtlar:** K09, K16, DK-08

**Gözlem:** Yerel kayıtlarda NEEDS_TRIAGE, NO_QUALIFIED_REPAIR_PROFILE ve PARALLEL_CHILDREN_PENDING beklemeleri var. Devir raporunda record_repair_observation kaydının worker başlatmadığı açıkça belirtiliyor.

**Yorum:** Bir “Scrum Master” rolü tanımlamak yetmez: hangi olayın hangi yetkili yürütücüyü başlatacağı ve aynı göreve nasıl dönüleceği ayrı sözleşmedir.

**Çıkarılamayacak sonuç:** Yetki belirsizliği nedeniyle bilinçli duran K16, her durumda yazılım hatası sayılmaz. Bilinmeyen her arızanın insansız çözülebileceğine dair kanıt yok.

**Senin karar sorunun:** Havuzda uygun onarım yeteneği yoksa ne olacak?

- Önceden sınanmış onarım profilleri: Öngörülebilir kapsam; yeni arızalar terminal engelli çıktı üretebilir.
- Yalıtılmış yetenek hazırlama hattı: Yeni onarım üretilebilir; nitelendirme, yetki ve bütçe sınırı gerekir.
- Kanıtlı engelli teslim: Sistem tahminle ilerlemez; insanın çıktı incelemesinde karar vermesi gerekir.

**Eksik ölçüm / çalıştırılmamış deney:** Hiçbir onarım profiline uymayan arıza ver. Sahibi, bütçesi, zaman sınırı ve son çıktısı olan tek bir kurtarma vakası oluştuğunu göster.

### B06 · Uyku kaynaklı lease kaybı ile durum geçişi hatası ayrı olaylar.

**Kanıt türü:** Tarihî deneyler · **Kayıtlar:** K04, K05

**Gözlem:** K04: Mac uyku döneminde 120 saniyelik heartbeat boşluğu, lease kaybı ve UNKNOWN slotlar var. K05: VERIFIED geçişinin aynı saniyesinde, yalnız CLAIMED/IMPLEMENTED kabul eden yenileme kontrolü sahipliği düşürüyor.

**Yorum:** Her iki olay “lease lost” görünse de biri zaman/bağlantı, diğeri durum makinesi tutarlılığı sorunu. Aynı otomatik yeniden başlatma reçetesi ikisine eşit kanıt sağlamaz.

**Çıkarılamayacak sonuç:** Mac uyku bulgusu Ubuntu sunucunun uyuduğunu göstermez. Lease uzatmak eski ve yeni çalışanın aynı anda yazması riskini tek başına çözmez.

**Senin karar sorunun:** Sahipliği kaybeden iş nasıl geri alınacak?

- Kısa lease + fencing: Hızlı devralma; eski yazarı durduran nesil kimliği gerekir.
- Uzun lease + uzlaştırma: Kısa kopmalara tolerans; gerçek kayıpta daha uzun bekleme.

**Eksik ölçüm / çalıştırılmamış deney:** Uyku/bağlantı kesilmesi ile VERIFIED durum geçişini ayrı test et. Eski çalışan geri döndüğünde yazısının reddedildiğini kanıtla.

### B07 · Daha fazla worker, ortak hesap kotasını genişletmiyor.

**Kanıt türü:** Yerel ve dış raporlar · **Kayıtlar:** K11, K12, MA-04, DP-11

**Gözlem:** Yerel reviewer rotasında kota dolarken bazı IMPLEMENTED işler tekrar alınmış, PENDING işler beklemiş. Ayrı prototip incelemesinde süreç içindeki RAM/WIP sayacının worker sayısıyla çoğalabildiği görülmüş.

**Yorum:** Ekip sayısı, süreç sayısı, test kapasitesi ve model sağlayıcısının ortak kotası farklı kaynaklardır. 12×12 rol şeması eşzamanlı çalışma kapasitesi değildir.

**Çıkarılamayacak sonuç:** DP-11 statik prototip bulgusudur; canlı sunucu ölçümü değildir. Bu veri belirli bir maksimum ekip veya insan sayısı vermez.

**Senin karar sorunun:** Eşzamanlılığı hangi kaynak sınırlarına bağlayacaksın?

- Merkezî bütçe ve adil kuyruk: Ortak limitler görünür; denetleyicinin dayanıklılığı gerekir.
- Ayrılmış kaynak havuzları: İzolasyon kolaylaşır; kullanılmayan kapasite başka havuza aktarılamayabilir.

**Eksik ölçüm / çalıştırılmamış deney:** Worker sayısını artırırken toplam RAM, API kota tüketimi ve en uzun görev bekleme süresini ölç; aynı üst limitin çoğalmadığını doğrula.

### B08 · Worktree’de biten iş, bağımlılığı gelince kendiliğinden ilerlemedi.

**Kanıt türü:** Tarihli deney günlüğü · **Kayıtlar:** K14, MA-01

**Gözlem:** UI-54, başka paketten Empty bileşenini bekliyor. Bağımlılık daha sonra birleşse de handoff taşıyan blok yeniden denenmiyor; kök iş COMPONENT_DELIVERY_BLOCKED_WAIT durumunda kalıyor.

**Yorum:** Yalıtılmış dallar çakışmayı azaltabilir. Bağımlılık yayımlandığında tüketiciyi uyandırma ve güncel tabana göre yeniden doğrulama ayrı mekanizmalardır.

**Çıkarılamayacak sonuç:** Bu olay worktree’nin gereksiz olduğunu göstermez. Dış merge kuyruğu vakası yerel olayın bağımsız tekrar deneyi değildir.

**Senin karar sorunun:** Bağımlı paketler hangi anda yeniden doğrulanacak?

- Birleşim olayında seçici yeniden deneme: Daha az iş tekrar eder; bağımlılık haritasının doğruluğuna bağlıdır.
- Periyodik bütünleşik yeniden deneme: Kaçan olayları yakalayabilir; daha fazla test maliyeti ve gecikme getirir.

**Eksik ölçüm / çalıştırılmamış deney:** Önce tüketiciyi, sonra bağımlılığı teslim et; tek uyandırma, güncel taban ve eski kanıtın kullanılmaması koşullarını kontrol et.

### B09 · Yeşil test sayısı, eksiksiz kabul ölçütü kapsamı değil.

**Kanıt türü:** Statik inceleme + tasarım karşı örneği · **Kayıtlar:** DP-08, DK-01, K18, CP-10

**Gözlem:** Prototipte kabul ölçütü sayıları eşleşirken yinelenen kimliklerin eksik üst yükümlülükleri saklayabildiği yol saptanmış. Yerel kayıtta atlanan test ve ortam hatasının ürün RED’iyle karışması da var.

**Yorum:** “90/90 geçti” ancak hangi sürümde hangi yükümlülüğün hangi bağımsız kanıtla sınandığı biliniyorsa anlamlıdır. Ajanın yazdığı test, ajanla aynı yanlış varsayımı paylaşabilir.

**Çıkarılamayacak sonuç:** DP-08 statik bir kod yoludur; bu projede üretilmiş bordronun yanlış hesaplandığına dair canlı olay değildir. Tüm bilinmeyenlerin keşfedildiği ispatlanamaz.

**Senin karar sorunun:** Tamamlandı kararının dayanağı ne olacak?

- AC → benzersiz kanıt matrisi: Eksik/yinelenen kapsam görünür; alan kabul verisi hazırlanmalıdır.
- Matrise bağımsız alan örnekleri ekle: Ortak yanlış varsayımı sınar; beklenen sonuçların sahipliği gerekir.
- Risk odaklı keşif testleri ekle: Önceden yazılmamış akışları araştırır; sınırsız doğruluk garantisi vermez.

**Eksik ölçüm / çalıştırılmamış deney:** Bir AC’yi eksilt, diğerini iki kez yaz, bir testi skip et ve yanlış ama tutarlı bordro örneği ekle; toplam sayı değişmese bile kabulün durduğunu göster.

### B10 · İnceleme sonrası değişen kod, eski onayla ilerleyebiliyor.

**Kanıt türü:** Statik prototip incelemesi · **Kayıtlar:** DP-03, DP-09

**Gözlem:** Sabit prototip incelemesi, CI/entegrasyon onarımı yeni kod ürettikten sonra önceki bağımsız incelemenin kullanılabildiğini gösteriyor. Korunan dosya kontrolünden sonra test kodunun çalışma ağacını değiştirebildiği yol da var.

**Yorum:** İnceleme bir görev adına değil belirli içerik kimliğine bağlanmalı. Test koşturan işlem de çalışma ağacını değiştirebilir.

**Çıkarılamayacak sonuç:** Kod yolu gözlemi çalışma zamanında sömürü veya teslim hatası yaşandığı anlamına gelmez; bu tur prototip çalıştırılmadı.

**Senin karar sorunun:** Onay hangi değişiklikte geçersizleşecek?

- Her içerik değişiminde tüm inceleme: Basit geçerlilik kuralı; süre/maliyet artar.
- Değişen alan + etki alanını tekrar incele: Daha az tekrar; etki haritasının eksikliği ayrı risk olur.

**Eksik ölçüm / çalıştırılmamış deney:** Onaydan sonra kaynak dosyayı ve ardından test sırasında korunan dosyayı değiştir. Eski commit/digest’e ait kanıtın teslimi açmadığını doğrula.

### B11 · Merge sırası ile alpha’ya dağıtım sırası aynı değil.

**Kanıt türü:** Statik prototip incelemesi · **Kayıtlar:** DP-10, DK-02

**Gözlem:** İncelenen akışta A sonra B birleşebiliyor; B’nin CI’ı önce bitip dağıtıldıktan sonra A’nın yavaş CI’ı eski sürümü alpha’ya taşıyabiliyor. Çoklu repo/veri sürümü için kabul birimi ayrıca açık.

**Yorum:** Trunk tabanlı çalışma tek başına ortam sürüm sırasını korumaz. Commit, build artifact ve etkin ortam sürümü birlikte izlenmelidir.

**Çıkarılamayacak sonuç:** Bu kayıt alpha.example.com üzerinde gözlenmiş geri sürümleme değildir. Birden çok repo kullanmak zorunlu bir karar olarak çıkarılamaz.

**Senin karar sorunun:** Alpha ortamını nasıl güncelleyeceksin?

- Proje başına sıralı teslim kuyruğu: Sıra basitleşir; uzun CI diğer teslimleri bekletir.
- Paralel CI + güncel hedef karşılaştırması: CI paralel kalır; dağıtım anında atomik sürüm kontrolü gerekir.

**Eksik ölçüm / çalıştırılmamış deney:** A’nın CI’ını geciktir; B’den sonra A bitsin. Ortamın B’den A’ya izinsiz gerilemediğini ve ekranın gerçek artifact kimliğini gösterdiğini doğrula.

### B12 · Sağlık kapısı, kendi onarımını da engelleyebiliyor.

**Kanıt türü:** Statik prototip incelemesi · **Kayıtlar:** DP-02

**Gözlem:** Prototipte geri alma/onarım yolu, alpha sağlıklı olana kadar bekleyen aynı merge kapısına giriyor. Alpha yalnız bu onarımla düzelecekse koşul kendi çözümünü durduruyor.

**Yorum:** Yeni özellik, onarım ve geri alma aynı politika kapsamına sokulmuş. Onarım istisnasının yazılı olması çağrı yolunda uygulandığını göstermiyor.

**Çıkarılamayacak sonuç:** Bu, tüm sağlık/test kontrollerini atlama gerekçesi değildir. Kaynak canlı kesinti kaydı değil statik karşı yoldur.

**Senin karar sorunun:** Sağlıksız alpha nasıl onarılacak?

- Ayrı yetkili onarım yolu: Kilit çözülür; hangi artifact ve etki için yetkili olduğu dar tanımlanır.
- Son doğrulanmış artifacta dönüş: Kod geri dönüşü hızlı olabilir; veri migration’ı ayrıca ele alınmalıdır.

**Eksik ölçüm / çalıştırılmamış deney:** Alpha sağlıksızken sıradan özelliği beklet; aynı hatayı düzelten doğrulanmış onarımı yürüt. Yanlış hedefe yapılan onarım denemesini reddet.

### B13 · Kalıcı workflow, dış etkinin tek kez oluşmasını garanti etmiyor.

**Kanıt türü:** Dış vaka + statik inceleme · **Kayıtlar:** WF-03, DP-12

**Gözlem:** Temporal forum vakasında 10 işlem beklenirken heartbeat timeout sonrası ilk 3 işlem yeniden başlayıp toplam 13 altakış doğuruyor. Prototip incelemesi de activity tekrarında aynı dış etkinin uzlaştırılmadığını işaretliyor.

**Yorum:** Durable history işin nereden sürdürüleceğini kaydeder; dış API çağrısının gerçekten gerçekleşip gerçekleşmediğini ayrıca çözmek gerekir.

**Çıkarılamayacak sonuç:** Bu, tüm Temporal işlerinin çift çalıştığı veya bir ürünün bunu otomatik olarak her entegrasyonda çözdüğü anlamına gelmez.

**Senin karar sorunun:** Yanıtı kaybolan GitHub/dağıtım çağrısında ne yapılacak?

- Etki kimliğiyle uzlaştır, sonra dene: Çift etkiyi sınırlamayı hedefler; hedef API’dan durum okunabilmelidir.
- Belirsiz etkiyi engelli çıktıya taşı: Tahminle tekrar yapılmaz; bazı işler insan incelemesi bekler.

**Eksik ölçüm / çalıştırılmamış deney:** Dış işlem başarılı olduktan hemen sonra yanıtı düşür. Yeniden denemede yeni PR/dağıtım/maliyet kaydı üretilmeden mevcut etkinin bulunduğunu doğrula.

### B14 · İnsan reddi, botun daha yeni zaman damgası yüzünden kaybolabiliyor.

**Kanıt türü:** Statik prototip incelemesi · **Kayıtlar:** DP-07, K16, DK-03

**Gözlem:** İncelenen prototip yolunda botun durum yazımı, eşzamanlı insan reddinden daha yeni görünüyor; reddetme eski olay kabul edilip atılabiliyor. Yerel K16’da ortak aktör kimliği kurtarma yetkisini belirsizleştirmiş.

**Yorum:** Aktör, komut türü ve görev sürümü olmadan yalnız zamana göre sıralama insan niyetini korumuyor.

**Çıkarılamayacak sonuç:** Prototipteki olasılık kullanıcının gerçek reddinin kaybolduğu kanıtı değildir. Her eski olayın kabul edilmesi de güvenli bir sonuç değildir.

**Senin karar sorunun:** İnsan iptali/reddi için hangi öncelik geçerli olacak?

- Sürümlü niyet + ayrı bot kimliği: Niyet ayırt edilir; olay şeması ve çakışma kuralı gerekir.
- Çelişkili niyette dur ve raporla: Yanlış devamı azaltır; çıktı inceleme yükü artabilir.

**Eksik ölçüm / çalıştırılmamış deney:** Bot durumu ile insan reddini ters sırada ve tekrar ederek gönder; reddin yutulmadığını, iptalden sonra yeni dış etki açılmadığını sınayarak karar ver.

### B15 · Tak-çıkar; geçmiş, kanıt ve yetki de taşınırsa anlamlı.

**Kanıt türü:** Dış rapor + statik inceleme · **Kayıtlar:** CP-06, CP-07, DP-04, DK-07

**Gözlem:** Droid kullanıcı raporunda model değişince eski konuşma şeması HTTP 400 üretiyor; ayrı kayıtta pluginler çalıştığı hâlde list/update görünmüyor. Prototipte workflow politika snapshot’ı alırken activity canlı yapılandırmayı okuyabiliyor.

**Yorum:** API adresi değiştirmek, çalışan işin durumu ve kanıt semantiği korunuyor demek değildir. Geçmiş şeması, politika sürümü ve yetki sözleşmesi de geçiş kapsamındadır.

**Çıkarılamayacak sonuç:** Bu kayıtlar tüm adaylar arasında sıcak geçiş yapılabildiğini veya yapılamadığını kanıtlamaz. Açık API tek başına taşınabilirlik ölçüsü değil.

**Senin karar sorunun:** Çalışan işler sırasında bileşen nasıl değişecek?

- Yeni işler yeni adaptöre; eskiler tamamlasın: Göç karmaşıklığı azalır; iki sürüm geçici birlikte işletilir.
- Kontrollü duraklat ve dönüştür: Geçiş daha hızlı olabilir; checkpoint ve kanıt dönüştürme testleri gerekir.

**Eksik ölçüm / çalıştırılmamış deney:** Aynı görev sözleşmesini iki adaptörde çalıştır; iptal, checkpoint, test makbuzu, maliyet ve terminal durum alanlarının kayıpsız karşılığını ölç.

### B16 · Skill dosyasının varlığı, yüklenebilir ve yetkili olması değil.

**Kanıt türü:** Belge ve paket incelemesi · **Kayıtlar:** DE-07, DK-08

**Gözlem:** İncelemede 21 etkin olmayan SKILL taslağı sayılmış; doğrudan okunan iki örnekte name alanı ile klasör adı uyuşmuyor. Katalogda bulunmaları çalışan sisteme yüklendikleri anlamına gelmiyor.

**Yorum:** Havuzdan edinme, şema doğrulama, sürüm sabitleme, izin denetimi ve deneme çalıştırması ayrı adımlardır.

**Çıkarılamayacak sonuç:** 21 şablonun hepsinin bozuk olduğu ya da canlı ajanları durdurduğu gösterilmedi. “20–30 skill sınırı” için bağımsız ölçüm bulunmadı.

**Senin karar sorunun:** Havuzdan gelen yetenek ne zaman kullanılabilir olacak?

- Önceden nitelendirilmiş katalog: Öngörülebilir; yeni ihtiyaç için katalog güncellemesi gerekir.
- Talep anında yalıtılmış nitelendirme: Yeni yeteneğe daha hızlı erişim; tedarik ve izin kontrolü karmaşıklaşır.

**Eksik ölçüm / çalıştırılmamış deney:** Adı hatalı, sürümü değişmiş, aşırı izin isteyen ve testte kalan dört skill paketi dene; hiçbiri onaylı kayıt gibi görünmemeli.

### B17 · “Temporal kurtaramadı” vakası, yazarı tarafından geri çekilmiş.

**Kanıt türü:** Birincil kaynak düzeltmesi · **Kayıtlar:** WF-06

**Gözlem:** Forum yazarı 24 Mart 2021’de nedenin kendi kodundaki hata olduğunu ve örneğin beklendiği gibi çalıştığını açıklıyor. Son mesaj bu tur birincil kaynaktan tekrar okundu.

**Yorum:** İlk şikâyet başlığıyla ürün kusuru yazmak yanlış olur. İlk belirti ve son düzeltme aynı kayıt zincirinde tutulmalı.

**Çıkarılamayacak sonuç:** Bu tek düzeltme Temporal’ın her senaryoda sorunsuz olduğunu da kanıtlamaz. Başka olaylara genellenemez.

**Senin karar sorunun:** Araç karşılaştırmasında hangi kanıtı geçerli sayacaksın?

- Sonuç ve sürümüyle olay kaydı: Düzeltme korunur; her kaynak için kapanış takibi gerekir.
- Yeniden üretilmiş vakalarla daralt: Nedene güven artar; henüz tekrarlanamayan riskler ayrı listede kalır.

**Eksik ölçüm / çalıştırılmamış deney:** Karşılaştırma tablosunda geri çekilmiş bu iddianın “ürün hatası sayısı”na eklenmediğini kontrol et.

### B18 · Webhook 5xx davranışının bir bölümü hâlâ kanıtlanmamış.

**Kanıt türü:** Düzeltilmiş arşiv incelemesi · **Kayıtlar:** DE-01, DE-02

**Gözlem:** Arşivli Plane yolunda HTTP 5xx yanıtı ile ağ istisnası farklı işleniyor. Ancak kullanılan pinned_fetch uygulaması elde olmadığı için son 5xx davranışının tamamı çıkarılamıyor; kurulu sürümün canlı payload’ı da okunmamış.

**Yorum:** “Beş hatada kapanır, 5xx yeniden denenmez” ifadesi kurulu sisteme kesin hüküm olarak taşınamaz. Eksik bağımlılık, nedensel zincirde açık bir halkadır.

**Çıkarılamayacak sonuç:** Bu inceleme hiçbir retry olmadığını veya kurulu Plane sürümünün aynı olduğunu kanıtlamaz.

**Senin karar sorunun:** Görev kabulünü webhook’a ne kadar bağlayacaksın?

- Webhook + dönemsel uzlaştırma: Kaçan olayları yakalayabilir; durum sürümü ve tekrar önleme gerekir.
- Yalnız webhook, teslim garantisi sınanmış: Daha az tarama; kayıp olay deneyinden geçmesi gerekir.

**Eksik ölçüm / çalıştırılmamış deney:** Kurulu sürümde 500, 429, bağlantı kopması ve yinelenen olay üret; retry sayısı, gecikmesi ve kaçan görevleri geri kazanma davranışını kaydet.

### B19 · Kaynak sayısı, risk araştırmasının tamamlandığını göstermiyor.

**Kanıt türü:** Kaynak tarama denetimi · **Kayıtlar:** DE-06, DE-08

**Gözlem:** Önceki 130/722 danışma kaydı sayıları için başarılı sayfalama manifesti yok. 403/429 erişim hataları ve kopya belgeler ayrıca ayrılmalı; byte eşitliği anlamsal kapsama kanıtı değil.

**Yorum:** Bir raporun başka raporu tekrar etmesi yeni bağımsız olay değildir. Sayfa sayısı/araç sayısı güvenilirlik puanına çevrilemez.

**Çıkarılamayacak sonuç:** Bu bulgu bütün araştırmanın geçersiz olduğunu söylemez. Eksik tarama ölçüsü varken “tüm sorunlar kapsandı” sonucu çıkarılamaz.

**Senin karar sorunun:** Karar vermeden önce hangi araştırma açığı kapanmalı?

- Seçtiğin adaylar için sürüm odaklı tarama: Daha dar ama izlenebilir kapsam; diğer adaylar açık kalır.
- Tüm katalog için kapsam manifesti: Karşılaştırma genişler; tarama ve güncellik yükü büyür.

**Eksik ölçüm / çalıştırılmamış deney:** Her sorgu için tarih, sürüm aralığı, sayfa/cursor, başarı/hata ve sonlandırma nedenini kaydet. Erişilemeyen kaynağı sıfır bulgu sayma.

### B20 · “Bitti” tek durum değil: yürütme, kanıt ve insan kabulü farklı.

**Kanıt türü:** Yerel geçmiş + tasarım boşluğu · **Kayıtlar:** K15, K17, DE-03, DK-07

**Gözlem:** Yerel belgelerde RUNNING, COMPLETED, VERIFIED ve MERGED farklı nesnelere ait. 18 Eylül toparlanma raporuna karşı 25 Eylül kök işte ERROR/review ve NOT_TESTED görünümü var; uzaktaki alpha kabulü doğrulanmamış.

**Yorum:** İşin kapanması, testin geçmesi, kodun birleşmesi, doğru sürümün yayında olması ve insanın kabulü ayrı kanıt gerektirir.

**Çıkarılamayacak sonuç:** 17 Eylül “kurulum bitti” ifadesi tüm ürünün teslim edildiği iddiası diye yeniden yazılamaz. 25 Eylül snapshot’ı tüm tarih boyunca hiçbir şey çalışmadı demek değildir.

**Senin karar sorunun:** Tek ekranda hangi bitiş durumlarını görmek istiyorsun?

- Ayrı yürütme / kanıt / kabul durumu: Anlam açık kalır; tek renkli “done”dan daha fazla bilgi gösterir.
- Bir özet durum + zorunlu alt kanıtlar: İlk bakış basittir; ayrıntıların kaybolmaması gerekir.

**Eksik ölçüm / çalıştırılmamış deney:** Kod MERGED iken alpha yanlış sürüm, test PASS iken kabul bekliyor ve iş ERROR iken geri alma tamam senaryolarını ayrı göster.

### B21 · Karar modeli, teslimin doğru olduğuna tek başına tanıklık edemez.

**Kanıt türü:** Tasarım çıkarımı · **Kayıtlar:** MA-10, DK-04, DP-08

**Gözlem:** Dış hata atfetme araştırması, LLM’ye teşhis yaptırmanın ilk kritik hatayı güvenilir biçimde bulmayı garanti etmediğini raporluyor. Prototipte kabul sayısı eşleşmesi de gerçek yükümlülük kapsamını kaçırabiliyor.

**Yorum:** Jev/Laya benzeri tipli karar katmanı yönlendirmeye aday olabilir; test sonucu, yetki ve artifact kimliği için ayrıca doğrulanabilir kurallar gerekir. Bu ayrım araç ismine bağlı değildir.

**Çıkarılamayacak sonuç:** Bu kaynaklar Jev veya Laya’nın senin görevlerinde ölçülmüş doğruluk oranı değildir. Paylaşılan benchmark yüzdeleri bu sistemin kabul eşiğine çevrilemez.

**Senin karar sorunun:** Öğrenilmiş kararın rolünü nerede sınırlayacaksın?

- Yalnız yönlendirme/öncelik adayı: Operasyonel fayda sınanır; nihai geçişler kanıta bağlanır.
- Gölge modda karşılaştır: Gerçek sonucu değiştirmez; faydayı ölçmek için etiketli veri gerekir.
- Şimdilik sabit kurallar: Başlangıç daha izlenebilir; yeni örüntüleri elle tarif etmek gerekir.

**Eksik ölçüm / çalıştırılmamış deney:** Etiketli görev örneklerinde yanlış kabul, yanlış engel, kararsızlık ve kalibrasyonu ayrı ölç; sürüm bazında izlemeyi önceden tanımla.

### B22 · Proje katılımı ve işletim işleri, gizli insan emeği olabilir.

**Kanıt türü:** Tasarım boşluğu · **Kayıtlar:** DK-05, DK-04

**Gözlem:** Derin incelemede repo ilk kurulumu, sır rotasyonu, veri migration’ı ve erişim onarımı için task içi otonomiden ayrı bir sınır ihtiyacı kaydedilmiş. Bunların insansız işlediğine dair uçtan uca kabul kaydı yok.

**Yorum:** İnsanın yalnız girdi ve çıktıyı görmesi hedefi, her görevin hangi hazır proje sözleşmesine dayandığı belirtilmeden ölçülemez.

**Çıkarılamayacak sonuç:** Bu bir yaşanmış olay sayımı değil tasarım boşluğudur. İnsan başına sunucu sayısı hesaplayacak iş hacmi veya inceleme süresi ölçümü bulunmuyor.

**Senin karar sorunun:** İlk MVP hangi işleri kapsayacak?

- Hazır proje profili içinde özellik geliştirme: Daha dar ölçüm alanı; onboarding dışarıda açıkça gösterilir.
- Onboarding ve bakım da kapsamda: Daha geniş otonomi; ek yetki, test ve işletim sözleşmeleri gerekir.

**Eksik ölçüm / çalıştırılmamış deney:** Bir görevin girişinden çıktısına kadar insan müdahalesi günlüğü tut; görev tanımı/kabul, onboarding ve arıza müdahalesini ayrı say.

### B23 · Koruma aracının kurulmuş olması, kapının doğru kapandığını göstermiyor.

**Kanıt türü:** Statik prototip incelemesi · **Kayıtlar:** DP-01

**Gözlem:** İncelenen shell yolunda gizli bilgi tarayıcısı sıfır dışı çıkınca “|| echo” kolu başarılı bitiyor; sonuç taramanın geçtiği gibi kayda girebiliyor.

**Yorum:** Araç varlığı, araç bulgusu ve taramanın çalışamaması farklı sonuçlardır. Son komutun exit 0 olması bu ayrımı kaybediyor.

**Çıkarılamayacak sonuç:** Statik bulgu gerçek sır sızıntısı yaşandığını göstermez. Doğru bağlı bağımsız CI kapısı sonraki aşamada engellemiş olabilir.

**Senin karar sorunun:** Tarama sonucunu nasıl temsil edeceksin?

- Temiz / bulgu / çalışmadı tipleri: Neden görünür; sonuç şeması ve çağıran taraf uyumu gerekir.
- Zorunlu araç için başarısızlıkta kapalı geçit: Yayın durur; geçici altyapı hatasında kurtarma yolu gerekir.

**Eksik ölçüm / çalıştırılmamış deney:** Sahte test sırrı, eksik tarayıcı ve çalışma hatasını ayrı dene. Üçü de temiz tarama olarak kaydedilmemeli.

### B24 · Kabul kanıtı; kod, veri ve dış girdinin sürümüne bağlı.

**Kanıt türü:** Tasarım boşluğu · **Kayıtlar:** DK-02, DK-06

**Gözlem:** Derin inceleme, bir URL’nin değişmez içerik kimliği olmadığını ve çoklu repo/veri şemasıyla oluşan alpha sürümünün tek commit’e indirgenemediğini kaydediyor.

**Yorum:** HRMS gibi üründe aynı kod, farklı kural tablosu veya veri şemasıyla farklı sonuç üretebilir. Dış girdi değiştiğinde önceki test kanıtının geçerliliği yeniden değerlendirilir.

**Çıkarılamayacak sonuç:** Bu, çoklu repo veya belirli ERP seçmen gerektiği sonucu değildir. Bordro mevzuatının güncelliği bu teknik incelemede doğrulanmadı.

**Senin karar sorunun:** Teslim paketinin kimliği neleri içerecek?

- Kod + bağımlılık + test veri kimliği: Tek proje için başlangıç olabilir; dış kural kaynağı ayrıca sürümlenir.
- Ürün sürüm vektörü: Birden fazla repo/şema/konfigürasyon birlikte izlenir; manifest yönetimi gerekir.

**Eksik ölçüm / çalıştırılmamış deney:** Kod aynı kalırken kural verisini veya şemayı değiştir; eski kabul paketinin yeni ürün durumunu yanlışlıkla onaylamadığını dene.

## Doğrulama sınırı

Bu çalışma arayüz ve belge sentezidir. Güncel Kestra/Temporal/OpenHands davranışını, sunucu kapasitesini veya alpha kabulünü sınamadı. Kaynak hash’i inceleme anındaki dosyayı tanımlar; kaydın tarihsel özgünlüğünü tek başına ispatlamaz. Uygulama kontrollerinin sonuçları audit/ altında ayrıca bulunur.
