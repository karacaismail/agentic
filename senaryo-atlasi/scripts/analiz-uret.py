"""Salt okunur kaynaklardan karar destek katmanı üretir; kaynakları değiştirmez."""
import json, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=json.loads((ROOT/'src/veri/kanitlar.json').read_text())
rows={r['id']:r for r in source['kayitlar']}
briefs=[]
def add(title,theme,kind,ids,observation,interpretation,boundary,question,options,experiment):
 briefs.append(dict(id=f'B{len(briefs)+1:02}',title=title,theme=theme,evidence_kind=kind,record_ids=ids.split(),observation=observation,interpretation=interpretation,boundary=boundary,decision_question=question,options=[dict(label=a,tradeoff=b) for a,b in options],missing_measurement=experiment,qualification='not_run',default_decision=None))
add('1 GB sınırı tarayıcı testini öldürdü; ajan kapasitesi ölçülmedi.','Kaynak ve ilerleme','Yerel deney + kernel kaydı','K03 CP-05',
'15 Eylül deneyinde 51 testlik birleşik koşu yaklaşık 4,3 saniyede, rapor üretmeden 137 ile bitti. Kernel kaydında cgroup OOM var. Aynı aday 2 GB ile 3/3 geçti; örneklenen tepe 887–942 MiB.',
'Bu olayda darboğaz tarayıcı test konteyneriydi. 137 kodunun tek başına OOM anlamına gelmemesi için kernel kanıtı ayırıcıdır.',
'Bu ölçüm, bir LLM ajanının 1 GB tükettiğini veya 128 GB sunucunun 128 ajan çalıştıracağını göstermez. Örneklenmiş tepe anlık tepeyi kaçırabilir; daha büyük test setinde 2 GB da yetersiz kalmış.',
'Test yükü büyüdüğünde kapasiteyi nasıl yöneteceksin?', [('Sınırı ölçerek büyüt','Bir işi hızla kurtarabilir; host toplam bütçesi ayrıca sınırlandırılır.'),('Testleri partilere böl','Tepe bellek düşebilir; kurulum tekrarı ve toplam süre artabilir.'),('İkisini yük profiline göre birleştir','Daha fazla seçenek verir; kabul deneyi ve zamanlayıcı karmaşıklığı artar.')],
'Aynı commit ve test setini farklı parti/eşzamanlılık ayarlarında çalıştır; cgroup tepe bellek, OOM sayısı, süre ve host toplamını kaydet. Bu atlas bu deneyi çalıştırmadı.')
add('İlerleyen test, 600 saniyelik “ajan sessiz” kuralına takıldı.','Kaynak ve ilerleme','Tarihli deney günlüğü','K10 CP-01',
'18 Eylül günlüğünde bütünleşik test süresi 570 saniyeden yaklaşık 70 dakikaya çıkıyor. Gözetleyici yalnız yeni test makbuzunu ilerleme saydığı için 600 saniyede çağrıyı öldürüyor; üç tekrar sonrası kurtarma sınırına ulaşılıyor.',
'Ajan sessizliği, alt sürecin ilerlemesi ve görevin toplam süresi aynı saatle izlenmiş. Başka orkestratöre geçmek bu sinyal ayrımını kendiliğinden sağlamaz.',
'Bu bulgu bütün timeout’ları kaldırmayı desteklemez. OpenHands SDK kaydı benzer mekanizma ailesidir; aynı olay veya kod değildir.',
'Uzun süren geçerli iş ile kilitlenmeyi hangi sinyalle ayıracaksın?', [('Aşama bazlı süre ve ilerleme','Test/derleme için ayrı sinyal gerekir; yanlış kesmeleri azaltmayı hedefler.'),('Tek uzun üst süre','Kurulumu daha basittir; gerçek kilit daha geç fark edilir.')],
'Aynı gözetleyicide bilerek uzun süren test, gerçek sonsuz döngü ve ölü alt süreç dene; her biri için tespit ve kurtarma süresini ayrı kaydet.')
add('4.762 kuyruk olayı yalnız bir model çağrısı üretti.','Kaynak ve ilerleme','Tarihli deney günlüğü','K13',
'18 Eylül 00:56 kaydı: 93 bin karakterlik inceleme geçmişi CONTEXT_CAPACITY_UNSUPPORTED üretiyor. CAPACITY metni kapasite beklemesi sayılıyor; yaklaşık 10 saniyelik yeniden kabul döngüsünde 4.762 CLAIM/RETRY olayı, yalnız bir model çağrısı var.',
'Kuyruğun hareket etmesi işin ilerlediği anlamına gelmiyor. Hata sınıflandırması, bağlam boyutu ve tekrar kabul koşulu aynı tıkanmayı büyütmüş.',
'4.762 sayısı ajan, bitmiş görev veya model çağrısı sayısı değildir. Tarihli rapor güncel sistemin hâlâ böyle olduğunu kanıtlamaz.',
'Bağlam sınırına gelen işi hangi yoldan sürdüreceksin?', [('Özet + değişmez kanıt referansı','Girdi küçülür; özetin kaybettiği yükümlülükleri kontrol etmek gerekir.'),('Daha geniş bağlamlı çalışan','Özetleme azalabilir; maliyet ve model uyumluluğu ölçülmelidir.'),('İşi bağımsız alt parçalara ayır','Bağlam küçülebilir; entegrasyon ve ana kabul ölçütlerini koruma yükü getirir.')],
'Aynı hata ve değişmeyen girdi altında tekrar sayısını sınırla; değişen bağlam digest’i olmadan yeniden kabulü gözle. Kanıt eksilmesi testi de ekle.')
add('Teşhis ajanı dosyayı okuyamadı; çağrı yine başarılı sayıldı.','Yetki ve kurtarma','Tarihli devir raporu','K08 MA-08',
'15 Eylül devir kaydı, INCIDENT.json okunamadığını söyleyen çıktıya rağmen bakım isteğinin SUCCESS ve engelin diagnosed olduğunu aktarıyor. Prompt dosyayı istiyor; içerik girdide yok, okuma aracı yok, shell yasak.',
'Tamamlama durumu yalnız çağrının bittiğini bildirmiş. Teşhis kanıtı ve araç erişimi ayrıca doğrulanmamış.',
'Bu, modelin isteksiz olduğunu veya tüm shell yetkilerinin açılması gerektiğini göstermez. Kaynak bir tarihî rapordur; aynı çağrı yeniden çalıştırılmadı.',
'Teşhis rolüne olay verisini nasıl ulaştıracaksın?', [('Temizlenmiş içerik girdiye ekle','Az yetkiyle çalışır; boyut ve veri tazeliği yönetilir.'),('Dar kapsamlı salt okunur araç','Güncel kanıtı okuyabilir; dosya kapsamı ve erişim kaydı gerekir.')],
'Bilinen işareti içeren olay dosyası ver; okunduğuna dair doğrulanabilir alan bekle. Erişim yoksa sonuç NEEDS_EVIDENCE olmalı; diagnosed olmamalı.')
add('Engel kaydı ve rol ataması, onarım çalışanını başlatmadı.','Yetki ve kurtarma','Tarihî akış kaydı','K09 K16 DK-08',
'Yerel kayıtlarda NEEDS_TRIAGE, NO_QUALIFIED_REPAIR_PROFILE ve PARALLEL_CHILDREN_PENDING beklemeleri var. Devir raporunda record_repair_observation kaydının worker başlatmadığı açıkça belirtiliyor.',
'Bir “Scrum Master” rolü tanımlamak yetmez: hangi olayın hangi yetkili yürütücüyü başlatacağı ve aynı göreve nasıl dönüleceği ayrı sözleşmedir.',
'Yetki belirsizliği nedeniyle bilinçli duran K16, her durumda yazılım hatası sayılmaz. Bilinmeyen her arızanın insansız çözülebileceğine dair kanıt yok.',
'Havuzda uygun onarım yeteneği yoksa ne olacak?', [('Önceden sınanmış onarım profilleri','Öngörülebilir kapsam; yeni arızalar terminal engelli çıktı üretebilir.'),('Yalıtılmış yetenek hazırlama hattı','Yeni onarım üretilebilir; nitelendirme, yetki ve bütçe sınırı gerekir.'),('Kanıtlı engelli teslim','Sistem tahminle ilerlemez; insanın çıktı incelemesinde karar vermesi gerekir.')],
'Hiçbir onarım profiline uymayan arıza ver. Sahibi, bütçesi, zaman sınırı ve son çıktısı olan tek bir kurtarma vakası oluştuğunu göster.')
add('Uyku kaynaklı lease kaybı ile durum geçişi hatası ayrı olaylar.','Yetki ve kurtarma','Tarihî deneyler','K04 K05',
'K04: Mac uyku döneminde 120 saniyelik heartbeat boşluğu, lease kaybı ve UNKNOWN slotlar var. K05: VERIFIED geçişinin aynı saniyesinde, yalnız CLAIMED/IMPLEMENTED kabul eden yenileme kontrolü sahipliği düşürüyor.',
'Her iki olay “lease lost” görünse de biri zaman/bağlantı, diğeri durum makinesi tutarlılığı sorunu. Aynı otomatik yeniden başlatma reçetesi ikisine eşit kanıt sağlamaz.',
'Mac uyku bulgusu Ubuntu sunucunun uyuduğunu göstermez. Lease uzatmak eski ve yeni çalışanın aynı anda yazması riskini tek başına çözmez.',
'Sahipliği kaybeden iş nasıl geri alınacak?', [('Kısa lease + fencing','Hızlı devralma; eski yazarı durduran nesil kimliği gerekir.'),('Uzun lease + uzlaştırma','Kısa kopmalara tolerans; gerçek kayıpta daha uzun bekleme.')],
'Uyku/bağlantı kesilmesi ile VERIFIED durum geçişini ayrı test et. Eski çalışan geri döndüğünde yazısının reddedildiğini kanıtla.')
add('Daha fazla worker, ortak hesap kotasını genişletmiyor.','Kaynak ve ilerleme','Yerel ve dış raporlar','K11 K12 MA-04 DP-11',
'Yerel reviewer rotasında kota dolarken bazı IMPLEMENTED işler tekrar alınmış, PENDING işler beklemiş. Ayrı prototip incelemesinde süreç içindeki RAM/WIP sayacının worker sayısıyla çoğalabildiği görülmüş.',
'Ekip sayısı, süreç sayısı, test kapasitesi ve model sağlayıcısının ortak kotası farklı kaynaklardır. 12×12 rol şeması eşzamanlı çalışma kapasitesi değildir.',
'DP-11 statik prototip bulgusudur; canlı sunucu ölçümü değildir. Bu veri belirli bir maksimum ekip veya insan sayısı vermez.',
'Eşzamanlılığı hangi kaynak sınırlarına bağlayacaksın?', [('Merkezî bütçe ve adil kuyruk','Ortak limitler görünür; denetleyicinin dayanıklılığı gerekir.'),('Ayrılmış kaynak havuzları','İzolasyon kolaylaşır; kullanılmayan kapasite başka havuza aktarılamayabilir.')],
'Worker sayısını artırırken toplam RAM, API kota tüketimi ve en uzun görev bekleme süresini ölç; aynı üst limitin çoğalmadığını doğrula.')
add('Worktree’de biten iş, bağımlılığı gelince kendiliğinden ilerlemedi.','Bütünleştirme ve teslim','Tarihli deney günlüğü','K14 MA-01',
'UI-54, başka paketten Empty bileşenini bekliyor. Bağımlılık daha sonra birleşse de handoff taşıyan blok yeniden denenmiyor; kök iş COMPONENT_DELIVERY_BLOCKED_WAIT durumunda kalıyor.',
'Yalıtılmış dallar çakışmayı azaltabilir. Bağımlılık yayımlandığında tüketiciyi uyandırma ve güncel tabana göre yeniden doğrulama ayrı mekanizmalardır.',
'Bu olay worktree’nin gereksiz olduğunu göstermez. Dış merge kuyruğu vakası yerel olayın bağımsız tekrar deneyi değildir.',
'Bağımlı paketler hangi anda yeniden doğrulanacak?', [('Birleşim olayında seçici yeniden deneme','Daha az iş tekrar eder; bağımlılık haritasının doğruluğuna bağlıdır.'),('Periyodik bütünleşik yeniden deneme','Kaçan olayları yakalayabilir; daha fazla test maliyeti ve gecikme getirir.')],
'Önce tüketiciyi, sonra bağımlılığı teslim et; tek uyandırma, güncel taban ve eski kanıtın kullanılmaması koşullarını kontrol et.')
add('Yeşil test sayısı, eksiksiz kabul ölçütü kapsamı değil.','Doğruluk ve kabul','Statik inceleme + tasarım karşı örneği','DP-08 DK-01 K18 CP-10',
'Prototipte kabul ölçütü sayıları eşleşirken yinelenen kimliklerin eksik üst yükümlülükleri saklayabildiği yol saptanmış. Yerel kayıtta atlanan test ve ortam hatasının ürün RED’iyle karışması da var.',
'“90/90 geçti” ancak hangi sürümde hangi yükümlülüğün hangi bağımsız kanıtla sınandığı biliniyorsa anlamlıdır. Ajanın yazdığı test, ajanla aynı yanlış varsayımı paylaşabilir.',
'DP-08 statik bir kod yoludur; bu projede üretilmiş bordronun yanlış hesaplandığına dair canlı olay değildir. Tüm bilinmeyenlerin keşfedildiği ispatlanamaz.',
'Tamamlandı kararının dayanağı ne olacak?', [('AC → benzersiz kanıt matrisi','Eksik/yinelenen kapsam görünür; alan kabul verisi hazırlanmalıdır.'),('Matrise bağımsız alan örnekleri ekle','Ortak yanlış varsayımı sınar; beklenen sonuçların sahipliği gerekir.'),('Risk odaklı keşif testleri ekle','Önceden yazılmamış akışları araştırır; sınırsız doğruluk garantisi vermez.')],
'Bir AC’yi eksilt, diğerini iki kez yaz, bir testi skip et ve yanlış ama tutarlı bordro örneği ekle; toplam sayı değişmese bile kabulün durduğunu göster.')
add('İnceleme sonrası değişen kod, eski onayla ilerleyebiliyor.','Doğruluk ve kabul','Statik prototip incelemesi','DP-03 DP-09',
'Sabit prototip incelemesi, CI/entegrasyon onarımı yeni kod ürettikten sonra önceki bağımsız incelemenin kullanılabildiğini gösteriyor. Korunan dosya kontrolünden sonra test kodunun çalışma ağacını değiştirebildiği yol da var.',
'İnceleme bir görev adına değil belirli içerik kimliğine bağlanmalı. Test koşturan işlem de çalışma ağacını değiştirebilir.',
'Kod yolu gözlemi çalışma zamanında sömürü veya teslim hatası yaşandığı anlamına gelmez; bu tur prototip çalıştırılmadı.',
'Onay hangi değişiklikte geçersizleşecek?', [('Her içerik değişiminde tüm inceleme','Basit geçerlilik kuralı; süre/maliyet artar.'),('Değişen alan + etki alanını tekrar incele','Daha az tekrar; etki haritasının eksikliği ayrı risk olur.')],
'Onaydan sonra kaynak dosyayı ve ardından test sırasında korunan dosyayı değiştir. Eski commit/digest’e ait kanıtın teslimi açmadığını doğrula.')
add('Merge sırası ile alpha’ya dağıtım sırası aynı değil.','Bütünleştirme ve teslim','Statik prototip incelemesi','DP-10 DK-02',
'İncelenen akışta A sonra B birleşebiliyor; B’nin CI’ı önce bitip dağıtıldıktan sonra A’nın yavaş CI’ı eski sürümü alpha’ya taşıyabiliyor. Çoklu repo/veri sürümü için kabul birimi ayrıca açık.',
'Trunk tabanlı çalışma tek başına ortam sürüm sırasını korumaz. Commit, build artifact ve etkin ortam sürümü birlikte izlenmelidir.',
'Bu kayıt alpha.example.com üzerinde gözlenmiş geri sürümleme değildir. Birden çok repo kullanmak zorunlu bir karar olarak çıkarılamaz.',
'Alpha ortamını nasıl güncelleyeceksin?', [('Proje başına sıralı teslim kuyruğu','Sıra basitleşir; uzun CI diğer teslimleri bekletir.'),('Paralel CI + güncel hedef karşılaştırması','CI paralel kalır; dağıtım anında atomik sürüm kontrolü gerekir.')],
'A’nın CI’ını geciktir; B’den sonra A bitsin. Ortamın B’den A’ya izinsiz gerilemediğini ve ekranın gerçek artifact kimliğini gösterdiğini doğrula.')
add('Sağlık kapısı, kendi onarımını da engelleyebiliyor.','Bütünleştirme ve teslim','Statik prototip incelemesi','DP-02',
'Prototipte geri alma/onarım yolu, alpha sağlıklı olana kadar bekleyen aynı merge kapısına giriyor. Alpha yalnız bu onarımla düzelecekse koşul kendi çözümünü durduruyor.',
'Yeni özellik, onarım ve geri alma aynı politika kapsamına sokulmuş. Onarım istisnasının yazılı olması çağrı yolunda uygulandığını göstermiyor.',
'Bu, tüm sağlık/test kontrollerini atlama gerekçesi değildir. Kaynak canlı kesinti kaydı değil statik karşı yoldur.',
'Sağlıksız alpha nasıl onarılacak?', [('Ayrı yetkili onarım yolu','Kilit çözülür; hangi artifact ve etki için yetkili olduğu dar tanımlanır.'),('Son doğrulanmış artifacta dönüş','Kod geri dönüşü hızlı olabilir; veri migration’ı ayrıca ele alınmalıdır.')],
'Alpha sağlıksızken sıradan özelliği beklet; aynı hatayı düzelten doğrulanmış onarımı yürüt. Yanlış hedefe yapılan onarım denemesini reddet.')
add('Kalıcı workflow, dış etkinin tek kez oluşmasını garanti etmiyor.','Yetki ve kurtarma','Dış vaka + statik inceleme','WF-03 DP-12',
'Temporal forum vakasında 10 işlem beklenirken heartbeat timeout sonrası ilk 3 işlem yeniden başlayıp toplam 13 altakış doğuruyor. Prototip incelemesi de activity tekrarında aynı dış etkinin uzlaştırılmadığını işaretliyor.',
'Durable history işin nereden sürdürüleceğini kaydeder; dış API çağrısının gerçekten gerçekleşip gerçekleşmediğini ayrıca çözmek gerekir.',
'Bu, tüm Temporal işlerinin çift çalıştığı veya bir ürünün bunu otomatik olarak her entegrasyonda çözdüğü anlamına gelmez.',
'Yanıtı kaybolan GitHub/dağıtım çağrısında ne yapılacak?', [('Etki kimliğiyle uzlaştır, sonra dene','Çift etkiyi sınırlamayı hedefler; hedef API’dan durum okunabilmelidir.'),('Belirsiz etkiyi engelli çıktıya taşı','Tahminle tekrar yapılmaz; bazı işler insan incelemesi bekler.')],
'Dış işlem başarılı olduktan hemen sonra yanıtı düşür. Yeniden denemede yeni PR/dağıtım/maliyet kaydı üretilmeden mevcut etkinin bulunduğunu doğrula.')
add('İnsan reddi, botun daha yeni zaman damgası yüzünden kaybolabiliyor.','Yetki ve kurtarma','Statik prototip incelemesi','DP-07 K16 DK-03',
'İncelenen prototip yolunda botun durum yazımı, eşzamanlı insan reddinden daha yeni görünüyor; reddetme eski olay kabul edilip atılabiliyor. Yerel K16’da ortak aktör kimliği kurtarma yetkisini belirsizleştirmiş.',
'Aktör, komut türü ve görev sürümü olmadan yalnız zamana göre sıralama insan niyetini korumuyor.',
'Prototipteki olasılık kullanıcının gerçek reddinin kaybolduğu kanıtı değildir. Her eski olayın kabul edilmesi de güvenli bir sonuç değildir.',
'İnsan iptali/reddi için hangi öncelik geçerli olacak?', [('Sürümlü niyet + ayrı bot kimliği','Niyet ayırt edilir; olay şeması ve çakışma kuralı gerekir.'),('Çelişkili niyette dur ve raporla','Yanlış devamı azaltır; çıktı inceleme yükü artabilir.')],
'Bot durumu ile insan reddini ters sırada ve tekrar ederek gönder; reddin yutulmadığını, iptalden sonra yeni dış etki açılmadığını sınayarak karar ver.')
add('Tak-çıkar; geçmiş, kanıt ve yetki de taşınırsa anlamlı.','Uyarlanabilirlik','Dış rapor + statik inceleme','CP-06 CP-07 DP-04 DK-07',
'Droid kullanıcı raporunda model değişince eski konuşma şeması HTTP 400 üretiyor; ayrı kayıtta pluginler çalıştığı hâlde list/update görünmüyor. Prototipte workflow politika snapshot’ı alırken activity canlı yapılandırmayı okuyabiliyor.',
'API adresi değiştirmek, çalışan işin durumu ve kanıt semantiği korunuyor demek değildir. Geçmiş şeması, politika sürümü ve yetki sözleşmesi de geçiş kapsamındadır.',
'Bu kayıtlar tüm adaylar arasında sıcak geçiş yapılabildiğini veya yapılamadığını kanıtlamaz. Açık API tek başına taşınabilirlik ölçüsü değil.',
'Çalışan işler sırasında bileşen nasıl değişecek?', [('Yeni işler yeni adaptöre; eskiler tamamlasın','Göç karmaşıklığı azalır; iki sürüm geçici birlikte işletilir.'),('Kontrollü duraklat ve dönüştür','Geçiş daha hızlı olabilir; checkpoint ve kanıt dönüştürme testleri gerekir.')],
'Aynı görev sözleşmesini iki adaptörde çalıştır; iptal, checkpoint, test makbuzu, maliyet ve terminal durum alanlarının kayıpsız karşılığını ölç.')
add('Skill dosyasının varlığı, yüklenebilir ve yetkili olması değil.','Uyarlanabilirlik','Belge ve paket incelemesi','DE-07 DK-08',
'İncelemede 21 etkin olmayan SKILL taslağı sayılmış; doğrudan okunan iki örnekte name alanı ile klasör adı uyuşmuyor. Katalogda bulunmaları çalışan sisteme yüklendikleri anlamına gelmiyor.',
'Havuzdan edinme, şema doğrulama, sürüm sabitleme, izin denetimi ve deneme çalıştırması ayrı adımlardır.',
'21 şablonun hepsinin bozuk olduğu ya da canlı ajanları durdurduğu gösterilmedi. “20–30 skill sınırı” için bağımsız ölçüm bulunmadı.',
'Havuzdan gelen yetenek ne zaman kullanılabilir olacak?', [('Önceden nitelendirilmiş katalog','Öngörülebilir; yeni ihtiyaç için katalog güncellemesi gerekir.'),('Talep anında yalıtılmış nitelendirme','Yeni yeteneğe daha hızlı erişim; tedarik ve izin kontrolü karmaşıklaşır.')],
'Adı hatalı, sürümü değişmiş, aşırı izin isteyen ve testte kalan dört skill paketi dene; hiçbiri onaylı kayıt gibi görünmemeli.')
add('“Temporal kurtaramadı” vakası, yazarı tarafından geri çekilmiş.','Kanıtın sınırı','Birincil kaynak düzeltmesi','WF-06',
'Forum yazarı 24 Mart 2021’de nedenin kendi kodundaki hata olduğunu ve örneğin beklendiği gibi çalıştığını açıklıyor. Son mesaj bu tur birincil kaynaktan tekrar okundu.',
'İlk şikâyet başlığıyla ürün kusuru yazmak yanlış olur. İlk belirti ve son düzeltme aynı kayıt zincirinde tutulmalı.',
'Bu tek düzeltme Temporal’ın her senaryoda sorunsuz olduğunu da kanıtlamaz. Başka olaylara genellenemez.',
'Araç karşılaştırmasında hangi kanıtı geçerli sayacaksın?', [('Sonuç ve sürümüyle olay kaydı','Düzeltme korunur; her kaynak için kapanış takibi gerekir.'),('Yeniden üretilmiş vakalarla daralt','Nedene güven artar; henüz tekrarlanamayan riskler ayrı listede kalır.')],
'Karşılaştırma tablosunda geri çekilmiş bu iddianın “ürün hatası sayısı”na eklenmediğini kontrol et.')
add('Webhook 5xx davranışının bir bölümü hâlâ kanıtlanmamış.','Kanıtın sınırı','Düzeltilmiş arşiv incelemesi','DE-01 DE-02',
'Arşivli Plane yolunda HTTP 5xx yanıtı ile ağ istisnası farklı işleniyor. Ancak kullanılan pinned_fetch uygulaması elde olmadığı için son 5xx davranışının tamamı çıkarılamıyor; kurulu sürümün canlı payload’ı da okunmamış.',
'“Beş hatada kapanır, 5xx yeniden denenmez” ifadesi kurulu sisteme kesin hüküm olarak taşınamaz. Eksik bağımlılık, nedensel zincirde açık bir halkadır.',
'Bu inceleme hiçbir retry olmadığını veya kurulu Plane sürümünün aynı olduğunu kanıtlamaz.',
'Görev kabulünü webhook’a ne kadar bağlayacaksın?', [('Webhook + dönemsel uzlaştırma','Kaçan olayları yakalayabilir; durum sürümü ve tekrar önleme gerekir.'),('Yalnız webhook, teslim garantisi sınanmış','Daha az tarama; kayıp olay deneyinden geçmesi gerekir.')],
'Kurulu sürümde 500, 429, bağlantı kopması ve yinelenen olay üret; retry sayısı, gecikmesi ve kaçan görevleri geri kazanma davranışını kaydet.')
add('Kaynak sayısı, risk araştırmasının tamamlandığını göstermiyor.','Kanıtın sınırı','Kaynak tarama denetimi','DE-06 DE-08',
'Önceki 130/722 danışma kaydı sayıları için başarılı sayfalama manifesti yok. 403/429 erişim hataları ve kopya belgeler ayrıca ayrılmalı; byte eşitliği anlamsal kapsama kanıtı değil.',
'Bir raporun başka raporu tekrar etmesi yeni bağımsız olay değildir. Sayfa sayısı/araç sayısı güvenilirlik puanına çevrilemez.',
'Bu bulgu bütün araştırmanın geçersiz olduğunu söylemez. Eksik tarama ölçüsü varken “tüm sorunlar kapsandı” sonucu çıkarılamaz.',
'Karar vermeden önce hangi araştırma açığı kapanmalı?', [('Seçtiğin adaylar için sürüm odaklı tarama','Daha dar ama izlenebilir kapsam; diğer adaylar açık kalır.'),('Tüm katalog için kapsam manifesti','Karşılaştırma genişler; tarama ve güncellik yükü büyür.')],
'Her sorgu için tarih, sürüm aralığı, sayfa/cursor, başarı/hata ve sonlandırma nedenini kaydet. Erişilemeyen kaynağı sıfır bulgu sayma.')
add('“Bitti” tek durum değil: yürütme, kanıt ve insan kabulü farklı.','Doğruluk ve kabul','Yerel geçmiş + tasarım boşluğu','K15 K17 DE-03 DK-07',
'Yerel belgelerde RUNNING, COMPLETED, VERIFIED ve MERGED farklı nesnelere ait. 18 Eylül toparlanma raporuna karşı 25 Eylül kök işte ERROR/review ve NOT_TESTED görünümü var; uzaktaki alpha kabulü doğrulanmamış.',
'İşin kapanması, testin geçmesi, kodun birleşmesi, doğru sürümün yayında olması ve insanın kabulü ayrı kanıt gerektirir.',
'17 Eylül “kurulum bitti” ifadesi tüm ürünün teslim edildiği iddiası diye yeniden yazılamaz. 25 Eylül snapshot’ı tüm tarih boyunca hiçbir şey çalışmadı demek değildir.',
'Tek ekranda hangi bitiş durumlarını görmek istiyorsun?', [('Ayrı yürütme / kanıt / kabul durumu','Anlam açık kalır; tek renkli “done”dan daha fazla bilgi gösterir.'),('Bir özet durum + zorunlu alt kanıtlar','İlk bakış basittir; ayrıntıların kaybolmaması gerekir.')],
'Kod MERGED iken alpha yanlış sürüm, test PASS iken kabul bekliyor ve iş ERROR iken geri alma tamam senaryolarını ayrı göster.')
add('Karar modeli, teslimin doğru olduğuna tek başına tanıklık edemez.','Doğruluk ve kabul','Tasarım çıkarımı','MA-10 DK-04 DP-08',
'Dış hata atfetme araştırması, LLM’ye teşhis yaptırmanın ilk kritik hatayı güvenilir biçimde bulmayı garanti etmediğini raporluyor. Prototipte kabul sayısı eşleşmesi de gerçek yükümlülük kapsamını kaçırabiliyor.',
'Jev/Laya benzeri tipli karar katmanı yönlendirmeye aday olabilir; test sonucu, yetki ve artifact kimliği için ayrıca doğrulanabilir kurallar gerekir. Bu ayrım araç ismine bağlı değildir.',
'Bu kaynaklar Jev veya Laya’nın senin görevlerinde ölçülmüş doğruluk oranı değildir. Paylaşılan benchmark yüzdeleri bu sistemin kabul eşiğine çevrilemez.',
'Öğrenilmiş kararın rolünü nerede sınırlayacaksın?', [('Yalnız yönlendirme/öncelik adayı','Operasyonel fayda sınanır; nihai geçişler kanıta bağlanır.'),('Gölge modda karşılaştır','Gerçek sonucu değiştirmez; faydayı ölçmek için etiketli veri gerekir.'),('Şimdilik sabit kurallar','Başlangıç daha izlenebilir; yeni örüntüleri elle tarif etmek gerekir.')],
'Etiketli görev örneklerinde yanlış kabul, yanlış engel, kararsızlık ve kalibrasyonu ayrı ölç; sürüm bazında izlemeyi önceden tanımla.')
add('Proje katılımı ve işletim işleri, gizli insan emeği olabilir.','Uyarlanabilirlik','Tasarım boşluğu','DK-05 DK-04',
'Derin incelemede repo ilk kurulumu, sır rotasyonu, veri migration’ı ve erişim onarımı için task içi otonomiden ayrı bir sınır ihtiyacı kaydedilmiş. Bunların insansız işlediğine dair uçtan uca kabul kaydı yok.',
'İnsanın yalnız girdi ve çıktıyı görmesi hedefi, her görevin hangi hazır proje sözleşmesine dayandığı belirtilmeden ölçülemez.',
'Bu bir yaşanmış olay sayımı değil tasarım boşluğudur. İnsan başına sunucu sayısı hesaplayacak iş hacmi veya inceleme süresi ölçümü bulunmuyor.',
'İlk MVP hangi işleri kapsayacak?', [('Hazır proje profili içinde özellik geliştirme','Daha dar ölçüm alanı; onboarding dışarıda açıkça gösterilir.'),('Onboarding ve bakım da kapsamda','Daha geniş otonomi; ek yetki, test ve işletim sözleşmeleri gerekir.')],
'Bir görevin girişinden çıktısına kadar insan müdahalesi günlüğü tut; görev tanımı/kabul, onboarding ve arıza müdahalesini ayrı say.')
add('Koruma aracının kurulmuş olması, kapının doğru kapandığını göstermiyor.','Doğruluk ve kabul','Statik prototip incelemesi','DP-01',
'İncelenen shell yolunda gizli bilgi tarayıcısı sıfır dışı çıkınca “|| echo” kolu başarılı bitiyor; sonuç taramanın geçtiği gibi kayda girebiliyor.',
'Araç varlığı, araç bulgusu ve taramanın çalışamaması farklı sonuçlardır. Son komutun exit 0 olması bu ayrımı kaybediyor.',
'Statik bulgu gerçek sır sızıntısı yaşandığını göstermez. Doğru bağlı bağımsız CI kapısı sonraki aşamada engellemiş olabilir.',
'Tarama sonucunu nasıl temsil edeceksin?', [('Temiz / bulgu / çalışmadı tipleri','Neden görünür; sonuç şeması ve çağıran taraf uyumu gerekir.'),('Zorunlu araç için başarısızlıkta kapalı geçit','Yayın durur; geçici altyapı hatasında kurtarma yolu gerekir.')],
'Sahte test sırrı, eksik tarayıcı ve çalışma hatasını ayrı dene. Üçü de temiz tarama olarak kaydedilmemeli.')
add('Kabul kanıtı; kod, veri ve dış girdinin sürümüne bağlı.','Bütünleştirme ve teslim','Tasarım boşluğu','DK-02 DK-06',
'Derin inceleme, bir URL’nin değişmez içerik kimliği olmadığını ve çoklu repo/veri şemasıyla oluşan alpha sürümünün tek commit’e indirgenemediğini kaydediyor.',
'HRMS gibi üründe aynı kod, farklı kural tablosu veya veri şemasıyla farklı sonuç üretebilir. Dış girdi değiştiğinde önceki test kanıtının geçerliliği yeniden değerlendirilir.',
'Bu, çoklu repo veya belirli ERP seçmen gerektiği sonucu değildir. Bordro mevzuatının güncelliği bu teknik incelemede doğrulanmadı.',
'Teslim paketinin kimliği neleri içerecek?', [('Kod + bağımlılık + test veri kimliği','Tek proje için başlangıç olabilir; dış kural kaynağı ayrıca sürümlenir.'),('Ürün sürüm vektörü','Birden fazla repo/şema/konfigürasyon birlikte izlenir; manifest yönetimi gerekir.')],
'Kod aynı kalırken kural verisini veya şemayı değiştir; eski kabul paketinin yeni ürün durumunu yanlışlıkla onaylamadığını dene.')

# Birincil kaynak tekrar okumaları: yeni olay/yerel tekrar deneyi olarak sayılmaz.
web=[dict(record_id='CP-01',url='https://github.com/OpenHands/software-agent-sdk/issues/762',checked='2026-09-27',finding='Sabit stuck eşikleri meşru bekleme/tekrarları kesebiliyor; eşik yapılandırma önerisi.',boundary='Issue metni okundu; yerel tekrar deneyi yapılmadı.'),dict(record_id='CP-05',url='https://github.com/Factory-AI/factory/issues/33',checked='2026-09-27',finding='Kullanıcı raporu: ps yokken liveness kontrolü SIGKILL üretiyor.',boundary='Yazarın mekanizma açıklaması; maintainer tarafından doğrulanmış genel ürün kusuru diye sayılmadı.'),dict(record_id='WF-06',url='https://community.temporal.io/t/workflow-not-recovered-after-crash/1770',checked='2026-09-27',finding='Yazar 24 Mart 2021 son mesajında kendi kod hatasını kabul ediyor.',boundary='Başlıktaki ürün kusuru izlenimi son mesajla düzeltilmeli.')]
# Bu tur gerçekten yeniden okunan özgün yerel dosyalar ve aralıklar.
inv=json.loads(Path('/Users/w6x/Documents/otomasyon coding 2/kestra-gecmis-incelemesi/kaynaklar/envanter.json').read_text())
evidence=json.loads(Path('/Users/w6x/Documents/otomasyon coding 2/kestra-gecmis-incelemesi/kaynaklar/kanitlar.json').read_text())['evidence']
originals=[]
for sid,lo,hi in [('S11',8,23),('S14',507,513),('S14',536,542),('S06',93,109)]:
 s=next(s for s in inv['sources'] if s['id']==sid);p=Path(s['path']);b=p.read_bytes()
 originals.append(dict(source_id=sid,path=str(p),line_start=lo,line_end=hi,sha256=hashlib.sha256(b).hexdigest(),prior_hash_matches=hashlib.sha256(b).hexdigest()==s['sha256'],excerpt='\n'.join(b.decode().splitlines()[lo-1:hi]),checked='2026-09-27',kind=s['kind']))
# Orijinal tool_result içindeki kernel satırı; transkriptin tamamı kopyalanmaz.
s=next(s for s in inv['sources'] if s['id']=='S20');p=Path(s['path']);digest=hashlib.sha256();target=''
with p.open('rb') as f:
 for n,line in enumerate(f,1):
  digest.update(line)
  if n==1573: target=line.decode()
def all_strings(obj):
 if isinstance(obj,str): yield obj
 elif isinstance(obj,list):
  for value in obj: yield from all_strings(value)
 elif isinstance(obj,dict):
  for value in obj.values(): yield from all_strings(value)
parts=[]
for value in all_strings(json.loads(target)):
 for line in value.splitlines():
  if 'Memory cgroup out of memory' in line and ('headless_shell' in line or 'MainThread' in line): parts.append(line)
parts=list(dict.fromkeys(parts))
assert parts, 'S20:1573 kernel excerpt missing'
originals.append(dict(source_id='S20',path=str(p),line_start=1573,line_end=1573,sha256=digest.hexdigest(),prior_hash_matches=digest.hexdigest()==s['sha256'],excerpt='\n'.join(parts),checked='2026-09-27',kind='transcript_tool_result',boundary='Aynı tool_result içinde yinelenen satırlar tekilleştirildi; satır sayısı bağımsız olay sayısı değildir.'))
# UI için kanıt fihristi; özgün kayıt gövdesine dokunulmaz.
index=[]
for r in source['kayitlar']:
 h=r['ham']; rid=r['id'];local=r['grup']=='Yerel geçmiş';world=r['grup']=='Dünya vakaları'
 kind=('Yerel log' if h.get('evidence_level')=='raw_log' else 'Araç çıktısı + tarihî deney' if h.get('evidence_level')=='tool_output_and_experiment' else 'Yerel tarihî kayıt') if local else ('Dış kaynak kaydı' if world else ('Statik kod incelemesi' if rid.startswith('DP-') else 'Kaynak denetimi / düzeltme' if rid.startswith('DE-') else 'Tasarım boşluğu'))
 if rid=='WF-06':kind='Geri çekilmiş ürün iddiası'
 observation=h.get('symptom') or h.get('what_was_missed') or h.get('gap') or h.get('title') or r['baslik']
 mechanism=h.get('causal_assessment') or h.get('root_cause_and_confidence') or ''
 boundary=h.get('inference_boundary') or h.get('boundaries') or h.get('confidence',{}).get('basis','')
 if not boundary:boundary='Bu bir tasarım boşluğu / kaynak incelemesidir. Canlı sistemde yeniden üretilmiş olay veya uygulanmış çözüm değildir.'
 index.append(dict(id=rid,kind=kind,period=h.get('observed_period') or h.get('event_date') or 'Sabit belge/snapshot incelemesi',observation=observation,mechanism=mechanism,boundary=boundary,test=h.get('recurrence_acceptance_criterion') or h.get('acceptance_experiment') or h.get('acceptance_description') or '',status=h.get('fix_status') or h.get('historical_remediation') or h.get('status') or 'Yeniden sınanmadı',source_ids=h.get('evidence_ids') or h.get('source_ids') or h.get('source_refs') or [],brief_ids=[b['id'] for b in briefs if rid in b['record_ids']]))
for item in index:
 if isinstance(item['test'],dict): item['test']=item['test'].get('proposed_test','')
for b in briefs:
 for rid in b['record_ids']:assert rid in rows,rid
 b['sources']=[dict(record_id=rid,path=rows[rid]['kaynak'],sha256=rows[rid]['sha256'],pointer=rows[rid]['pointer']) for rid in b['record_ids']]
output=dict(schema='decision-evidence/v1',reviewed_at='2026-09-27',scope='82 gömülü kayıt üzerinden sentez; 5 özgün yerel aralık ve 3 dış kaynak tekrar okundu. Güncel servis/alpha/araç uygunluğu test edilmedi.',briefs=briefs,record_index=index,primary_rechecks=web,original_rechecks=originals,local_excerpt_registry=evidence,decision_policy='Alternatifler sıralama veya tavsiye puanı değildir; hiçbir seçenek kullanıcı adına seçilmez.')
(ROOT/'src/analiz/bulgular.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
print(len(briefs),'karar sorusu;',len(index),'sınıflandırılmış kaynak kaydı')
