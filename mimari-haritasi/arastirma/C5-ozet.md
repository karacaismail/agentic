# C5 — Türkiye'de HRMS için "DoD'ye kadar tamam" ne demek, oracle nereden gelir?

Tarih: 2026-09-27 · Ayrıntılar ve tüm kaynaklar: `C5-hrms-alan-ve-oracle.json` (28 modül, 25 risk maddesi, 2026 parametreleri). Alt ajanların dosyaları: `_C5-alt-karsilastirma.json` (10 ürün) ve `_C5-alt-oracle-entegrasyon.json` (12 entegrasyon, 24 oracle kaynağı).

## 1. "Tamam" ne demek?

Beş koşulun hepsi aynı anda sağlanırsa bu HRMS "tamam" sayılır:

1. **Kapsam.** Alt ajanın çıkardığı "ortak minimum" 18 madde (çalışan, org, izin, PDKS, vardiya, puantaj, bordro motoru, ATS, yaşam döngüsü, performans, eğitim, vaka, portal, çok şirket, denetim vb.) karşılanmış olmalı. Buna "Türkiye farkı" 16 madde eklenir: SGK/GİB bildirimleri, MUHSGK, teşvik, kıdem/ihbar, BES, icra, e-bordro, banka dosyası. JSON'da CronHR'ın 28 ekranının her biri için yetenek listesi var.
2. **Doğruluk.** Her yasal kuralın hangi kanun maddesine ve Resmî Gazete'nin hangi tarih/sayısına dayandığı izlenebilir olmalı. Kurallar resmi örneklerden türetilmiş veya uzmanın imzaladığı altın setlerle doğrulanmalı.
3. **Entegrasyon.** Test ortamı olan tek yer SGK 4/a işe giriş/ayrılış servisi; orada uçtan uca test yapılmalı ([SGK](https://e.sgk.gov.tr/Uygulamalar/Detay/4a-Sigortali-Ise-Giris-ve-Isten-Ayrilis-Bildirgesi-2024-10-02-10-08-51)). MUHSGK, e-Bildirge, banka ve BES için test ortamı yok. Bunlar şema doğrulaması, paralel koşum ve gönderimin insan tarafından yapılmasıyla kanıtlanır.
4. **İşletim.** Şunlar çalışır durumda olmalı: sürümlü yasal parametreler, mevzuat izleme, dönem kilidi/yeniden açma, denetim izi, retro fark ve veri göçü mutabakatı.
5. **İnsan kabulü.** Mali müşavir (bordro/MPHB), İK hukukçusu (fesih, izin, çalışma süreleri) ve SGK uzmanı (teşvik, eksik gün) imzalamalı; ardından kullanıcı UX kabulü gelir.

Katmanlı DoD:
- **Hikâye:** kaynak etiketli kabul kriteri, birim ve property testleri, negatif yetki testi, a11y taraması.
- **Modül:** resmi örneklerin %100'ü testte, mutasyon skoru eşiği aşılmış, ilgili risk maddeleri kapatılmış, uzman imzası alınmış.
- **Sürüm:** işgücü zincirinin tamamı uçtan uca çalışıyor (org → vardiya → PDKS → izin → puantaj → bordro → MPHB/SGK → ödeme → muhasebe) ve en az bir dönemlik paralel koşum farkı onaylanmış.

**"90/90" tuzağına karşı** satır kapsamı ölçmek yetmez. Ölçülmesi gerekenler: kural→test izlenebilirlik matrisi, mutasyon skoru, resmi örnek kapsamı ve risk listesindeki her madde için kapanış kanıtı. Uzman imzası olmayan modül "AI-doğrulandı / insan onayı bekliyor" diye ayrı işaretlenir, "bitti" sayılmaz.

## 2. Oracle sorunu: somut örnekler

AI'ın yazdığı bordro kodu ve AI'ın yazdığı test aynı yanlış yorumdan türeyebilir. Bu durumda testler yeşil kalır ama sonuç hukuken yanlıştır. Bu araştırmada karşılaşılan örnekler:

- **CronHR prototipi:**
  - **Fazla mesai:** "Yasal aylık üst sınır" diye 270 saatten ve kalan aylık sınırdan söz ediyor. Oysa 4857 md.41 yalnızca **yıllık** 270 saat sınırı koyar ([mevzuat](https://www.mevzuat.gov.tr/mevzuatmetin/1.5.4857.pdf)).
  - **İstifa:** İstifa eden çalışana kıdem ve ihbar hesaplanmış. 1475 md.14'teki istisnalar dışında istifada kıdem hakkı doğmaz ([1475](https://www.mevzuat.gov.tr/mevzuatmetin/1.5.1475.pdf)). SGK çıkış kodu 03, "işçi tarafından fesih" anlamına gelir ([SGK kılavuzu](https://e.sgk.gov.tr/Download/DownloadFile?f=ccda7d7e-d99b-40f5-9622-63246763b4b0.doc&d=bf271de4-fea9-4557-a460-957858589cf9)).
  - **SGK parametreleri:** İşveren payı %20,5 ve "5 puan", tavan "×7,5" alınmış. 2026 değerleri farklı: 7566 sayılı Kanun'la indirimsiz işveren payı **%21,75** oldu. İndirim imalatta 5 puan, diğer sektörlerde **2 puan**. Tavan **9 kat** ([RG 19.12.2025](https://www.resmigazete.gov.tr/eskiler/2025/12/20251219-1.htm), [ÇSGB tablo](https://www.csgb.gov.tr/Media/gm2fekds/asgari-%C3%BCcret-2026.pdf)).
  - **Gece vardiyası:** 22–06 arası 8 saatlik gece vardiyasına fazla mesai eklenmiş. Md.69'a göre gece çalışması 7,5 saati geçemez; md.41 gece çalışmasında fazla mesaiyi yasaklar.
  - **Deneme süresi:** Yaklaşık 22 ay gösterilmiş. Md.15'e göre en çok 2 ay, TİS ile 4 ay olabilir.
- **KVKK atfı doğru çıktı:** Prototipin atıf yaptığı KVKK 2026/921 biyometri ilke kararı gerçekten var ([KVKK](https://www.kvkk.gov.tr/Icerik/8762/mesai-takibi-amaciyla-biyometrik-veri-islenmesi-hakkinda-kisisel-verileri-koruma-kurulunun-29-04-2026-tarihli-ve-2026-921-sayili-ilke-kararina-iliskin-kamuoyu-duyurusu)). Bu yüzden şüphe tek başına ölçüt olamaz; her atıf doğrulanmalı.
- **Odoo'nun resmi Türkiye bordro dokümanı** ABD şablonundan kalma "federal and state regulations" ifadesini içeriyor. SGK işveren payını "%15" diye yuvarlıyor ve 2025 dilimlerini gösteriyor ([Odoo](https://www.odoo.com/documentation/19.0/applications/hr/payroll/payroll_localizations/turkey.html)). Resmi bir ürün dokümanı bile tek başına oracle olamaz.
- **Kanun geliştirme sırasında değişiyor.** 7578 sayılı Kanun (22.04.2026) analık iznini toplam 16 haftadan **24 haftaya**, eşin doğumunda verilen izni 5 günden **10 güne** çıkardı ([4857 konsolide](https://www.mevzuat.gov.tr/mevzuatmetin/1.5.4857.pdf)). Nisan'da doğru olan testler Mayıs'ta yanlış olur.

**Oracle hiyerarşisi (güvenilirlik sırasıyla):**
1. Kanun metni ve Resmî Gazete.
2. Tebliğ örnekleri: [GVGT 319](https://www.resmigazete.gov.tr/eskiler/2022/01/20220127-5.htm) asgari ücret istisnasıyla ilgili 18 sayısal örnek içerir (2022 parametreleriyle).
3. Resmi yayınlar:
   - [SGK Sigorta Primi Teşvikleri 2026](https://www.sgk.gov.tr/Download/DownloadFile?d=de85036d-ef64-49f1-834c-916a79f1a923&f=c94c643d-2190-4d85-9b14-a8c7c5d241e8.pdf): her teşvik için 2026 rakamlı örnek var, doğrudan altın test olarak kullanılabilir.
   - ÇSGB asgari ücret tablosu.
   - [GİB Ücret Geliri Rehberi 2026](https://cdn.gib.gov.tr/api/gibportal-file/file/getFile?objectKey=DUYURU/UNIVERSAL/2026/2026_Ucret_Geliri.pdf).
   - [MUHSGK kılavuzu](https://ebeyanname.gib.gov.tr/muphb1.pdf).
4. Parametre tabloları ve SGK kod listeleri (eksik gün, çıkış nedeni, belge türü).
5. Resmi hesaplayıcılar: [GİB](https://dijital.gib.gov.tr/hesaplamalar/GelirVergisiHesaplama) (API yok). Resmi bir kıdem hesaplayıcısı bulunamadı; en yakın seçenek [TÜRMOB](https://www.turmob.org.tr/hesaplamalar/kidemihbarvetazminati).
6. Meslek örgütü yayınları (TÜRMOB, İSMMMO, Lebib Yalkın).
7. Karşılaştırma testi (differential): aynı girdiyle eski bordro yazılımının ya da müşterinin son 12 aylık tahakkuklarının verdiği sonuç.
8. Uzman imzası.

**Yalnız insanın karar verebileceği konular** (7 tür, alt ajan):
- teşvik seçimi ve teşviklerin birlikte uygulanıp uygulanamayacağı,
- feshin haklı/geçerli sayılması ve buna bağlı çıkış kodu,
- "giydirilmiş ücret",
- yan hakların vergi istisnası mı ücret mi sayılacağı,
- eksik gün nedeni ve belge türü seçimi,
- fazla mesai, izin ve bayram ücreti uyuşmazlıkları,
- e-bordronun delil değeri.

**Pratik mimari:**
- Her kural `{kanun, madde, RG, geçerlilik}` etiketi taşır; kaynağı olmayan kural CI'dan geçemez.
- Altın set şu beşliden oluşur: yıl-parametre seti, girdi, beklenen çıktı, kaynak, imzalayan.
- Hesap iki kez yapılır: üretim motoru ve ondan bağımsız bir referans hesaplayıcı. Sonuçlar farklıysa kayıt insan kuyruğuna düşer.
- Metamorfik testler (brüt artarken net düşmemeli, net→brüt→net aynı sonucu vermeli, dilim geçiş ayı doğru hesaplanmalı).
- Mevzuat izleme işi yeni parametre sürümünü açar; bu sürüm insan onayıyla devreye girer.

## 3. 2026 parametreleri (resmi kaynaklı)

| Parametre | Değer | Kaynak |
|---|---|---|
| Brüt / net asgari ücret | 33.030,00 / 28.075,50 TL (Temmuz'da ara zam yapıldığına dair resmi karar bulunamadı) | [ÇSGB](https://www.csgb.gov.tr/Media/gm2fekds/asgari-%C3%BCcret-2026.pdf) |
| İşveren SGK payı | İndirimsiz %21,75, imalat %16,75, diğer sektörler %19,75; işsizlik %2 | ÇSGB + [7566](https://www.resmigazete.gov.tr/eskiler/2025/12/20251219-1.htm) |
| PEK alt / üst sınır | 33.030 / 297.270 TL (9 kat) | [SGK teşvik 2026](https://www.sgk.gov.tr/Download/DownloadFile?d=de85036d-ef64-49f1-834c-916a79f1a923&f=c94c643d-2190-4d85-9b14-a8c7c5d241e8.pdf) |
| Gelir vergisi (ücret) dilimleri | 190.000 / 400.000 / 1.500.000 / 5.300.000 TL eşikleri; %15 / 20 / 27 / 35 / 40 | [GİB](https://cdn.gib.gov.tr/api/gibportal-file/file/getFileResources?objectKey=arsiv%2Fyardim-kaynaklar%2Fyararli-bilgiler%2Fgelir-vergisi-tarifeleri%2Fgelir-vergisi-tarifesi-2026.pdf) |
| Engellilik indirimi | 12.000 / 7.000 / 3.000 TL | GİB rehberi |
| Kıdem tavanı | 64.948,77 TL (1. yarı); 73.729,87 TL (01.07–31.12) | [TÜRMOB](https://www.turmob.org.tr/ekutuphane/download/4bca3949-fb63-40cd-90c6-3f5e2a0e69d4) |
| Asgari ücret desteği | 42,33 TL/gün (5510 geç. 112) | SGK teşvik 2026 |
| Güncel teşvikler | 14 adet; 6111 için işe alım tarihi 31.12.2026'ya kadar, 5746 31.12.2028'e kadar. 7103 listede yok | SGK teşvik 2026 |
| Asgari ücret GV istisnası | 4.211,33 / 4.537,75 / 5.615,10 TL; damga vergisi istisnası 250,70 TL. **Türetilmiş değer**, GİB'in resmi aylık tablosu doğrulanamadı | GVK 23/18 |
| Damga vergisi oranı | Binde 7,59 (kısmen doğrulandı) | — |
| MPHB son tarihi | Takip eden ayın 26'sı, saat 23.59 | [kılavuz](https://ebeyanname.gib.gov.tr/muphb1.pdf) |

## 4. En riskli 20 bilinmeyen-bilinmeyen (riske göre sıralı)

1. **Kritik: Geliştirme sırasında mevzuat değişikliği.** Örnekler: 7566, 7578, KVKK 2026/921, Haziran 2026'da MPHB format değişikliği.
2. **Kritik: Kümülatif GV matrahı.** Sorunlu durumlar: yıl içinde işveren değişikliği (grup içi transfer dahil), aynı ayda birden fazla ödeme, istisnanın aylara göre değişmesi.
3. **Kritik: Retro değişiklikler.** Gelir vergisi ve SGK açısından farklı dönemlere düşebilir; ek/iptal belge ve gecikme zammı doğurur.
4. **Kritik: Teşvik seçimi ve kombinasyonu.** 6111 yıl sonunda bitiyor; teşvik puanı imalatta 5, diğer sektörlerde 2; işyerinin borçlu olduğu ay teşviksiz hesaplanır.
5. **Kritik: Fesih zinciri.** Fesih nedeni → kıdem/ihbar → çıkış kodu; buna giydirilmiş ücret ve 01.07'deki tavan geçişi eklenir.
6. **Yüksek: SGK hesabının incelikleri.** 30 gün kuralı, ay ortasında giriş/çıkış, eksik gün kodu ve belge türü seçimi ([5510](https://www.mevzuat.gov.tr/mevzuatmetin/1.5.5510.pdf) md.86).
7. **Yüksek: Test ortamı eksikliği.** MUHSGK'da test ortamı yok. SGK test ortamı gerçek işyeri sicili istiyor. İlk gerçek test canlı gönderim oluyor.
8. **Yüksek: Zaman kuralları.** Gece yarısını aşan vardiya, 7,5 saatlik gece sınırı, gece fazla mesai yasağı, 2 aylık denkleştirme, arifede 13.00 kuralı ([2429](https://www.mevzuat.gov.tr/mevzuatmetin/1.5.2429.pdf)).
9. **Yüksek: Dönem kilidi.** Kilitleme, yeniden açma ve denetim izi; beyanname gönderildikten sonra değişiklik yapılması.
10. **Yüksek: Çoklu yapı.** Birden fazla SGK işyeri ve tüzel kişilik, ay ortasında işyeri değişikliği, konsolidasyon, şirketler arasında veri sızıntısı.
11. **Yüksek: Hassas veri erişimi.** Maaş ve sağlık verisine AI erişimi; yurt dışındaki bir AI sağlayıcısına veri aktarımı ([6698](https://www.mevzuat.gov.tr/mevzuatmetin/1.5.6698.pdf) md.9).
12. **Yüksek: Veri göçü.** Taşınması gerekenler: kümülatif matrah, izin bakiyesi ve hak ediş tarihi, kıdem başlangıcı, teşvik geçmişi.
13. **Yüksek: AI özelliklerinin hukuki riski.** Ayrılma riski skoru ve aday puanı; otomatik işlemeye itiraz hakkı ve ayrımcılık.
14. **Orta-Yüksek: Ar-Ge ve teknopark.** 5746 ve 4691 istisnaları, işlem sırası ve 40 kat sınırı.
15. **Orta-Yüksek: Yuvarlama.** Kalem bazında mı toplamda mı yapılacağı ve net→brüt iterasyonu. Resmi kuralı doğrulanamadı; karşılaştırma testiyle çözülmeli.
16. **Orta: İzin hak edişi.** Yıldönümünün ötelenmesi, 18 yaş altı ve 50 yaş üstü için 20 gün, en az 10 günlük bölünme, yol izni, 5 yıllık zamanaşımı.
17. **Orta: Kesintiler.** İcra sırası ve "en az 1/4" kuralı ([İİK 83](https://www.mevzuat.gov.tr/mevzuatmetin/1.3.2004.pdf)); BES'te 45 yaş sınırı, %3 kesinti ve 2 aylık cayma ([4632](https://www.mevzuat.gov.tr/mevzuatmetin/1.5.4632.pdf)).
18. **Orta: Özel sigortalı türleri.** SGDP'ye tabi emekli, yabancı, çırak, kısa çalışma ödeneği.
19. **Orta: Saklama çatışması.** 5510 md.86'ya göre 10 yıl saklama, 4857 Ek md.3'e göre 5 yıllık zamanaşımı ve KVKK imha yükümlülüğü birbiriyle çelişebilir.
20. **Orta: 29 Ekim.** 2429 md.2 "özel işyerleri kapanır" diyor, 4857 md.44 ise çalışmaya izin veriyor. Yorum ister; prototip o gün Depo vardiyası planlamış.

Diğer 5 madde (saat dilimi, asgari ücrete ara zam ihtimali, banka ve BES formatları, MPHB için ayrı şifre, ölçek) JSON'da.

## 5. AI neyi test edebilir, insan neyi onaylar?

**AI'ın yapabilecekleri:**
- resmi örneklerden altın testler,
- property ve metamorfik testler,
- iki bağımsız hesaplama ve eski sistemle karşılaştırma,
- XSD, WSDL ve banka dosyası sözleşme testleri,
- mutasyon testi,
- uçtan uca yolculuklar (SGK test ortamı veya mock ile),
- negatif yetki ve tenant sızıntısı testleri,
- WCAG 2.2 AA otomatik tarama,
- performans testi,
- tr-TR yerelleştirme kontrolleri,
- mevzuat izleme uyarıları.

**İnsanın yapması gerekenler:**
- hukuki doğruluk imzası,
- canlı gönderim yetkisi,
- paralel koşumun kabulü,
- UX kabulü,
- KVKK ve etik kararları,
- tam erişilebilirlik denetimi.

## 6. Çerçeve üzerine mi, sıfırdan mı?

**Kanıtlar:**
- **Frappe HRMS** ([repo](https://github.com/frappe/hrms), GPL-3; ERPNext'e bağımlı):
  - 160 DocType (106 ana, 54 alt tablo),
  - yaklaşık 73 bin satır Python, 18 bin satır JS, 10 bin satır Vue,
  - 128 test dosyası, 53 yama kaydı.
  - `regional` klasöründe yalnızca Hindistan ve BAE var; Türkiye yok.
  - Salary Slip vergiyi **yıllık projeksiyonla** hesaplıyor (Hindistan modeli). Türkiye'de kümülatif fiili matrah kullanılır, bu yüzden bu kısmın override edilmesi gerekir.
- **Odoo:**
  - Community'de bordro yok.
  - Enterprise'da `l10n_tr_hr_payroll` var ama hesap çekirdeğiyle sınırlı: MUHSGK, SGK, teşvik ve kıdem yok.
- **OCA:** `l10n-turkey` 11.0'dan 19.0'a kadar boş. `OCA/payroll`'da Türkiye kuralı yok.
- **Türk yazılımları** (Logo, Luca, Mikro, Kolay İK, Netsis): Türkiye katmanını kapsıyorlar ama kapalı kaynak.

**Hüküm:** Hazır bir çerçeve **genel HR genişliğini** ciddi ölçüde azaltır: izin, vardiya, ATS, yaşam döngüsü, performans, eğitim, yetki, workflow ve çok şirket yapısı hazır gelir. Ama işin **riskini belirleyen Türkiye bordro/SGK/GİB katmanını ve oracle işini azaltmaz**; bu kısım hiçbir açık kaynakta yok.

**Öneri** (mühendislik yargısı, ölçüm değil):
- Frappe HRMS + ERPNext üzerine ayrı bir **Türkiye app'i** kurulur.
- **Türkiye bordro çekirdeği** çerçeveden bağımsız, saf bir kütüphane olarak yazılır. Altın ve karşılaştırma testleri bunu hedefler; hızlı ve izole çalışır.
- **CronHR ön yüzü** headless olarak kalır (REST veya frappe-ui).

**Koşullar:**
- GPL-3 yükümlülükleri hukukçu onayından geçmeli.
- Yıllık major sürüm yükseltmesi için bütçe ayrılmalı.
- Override'lar için sözleşme testleri yazılmalı.

**Etkisi:** Çalışma birimi DocType olur (JSON + .py + .js + test). Değişiklikler `patches.txt` ile göç ettirilir, özelleştirmeler fixtures ile taşınır, testler `bench run-parallel-tests` ile koşar.

**Alternatifler:**
- Odoo EE: hesap çekirdeği hazır ama EE lisansı gerekir ve Türkiye katmanı yine yazılmalı.
- Sıfırdan: CronHR UX'ine tam uyar ama iş hacmi en büyük seçenek bu.
