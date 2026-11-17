# C0 — Sentez: hazır çözüm var mı, "tak-çıkar" gerçekte ne, HRMS'i DoD'ye kadar kim bitirir?

Tarih: 27.09.2026. Bu belge altı araştırmanın sentezidir. Her iddianın kaynağı ilgili dosyada:

- C1 hazır sistemler: 32 aday, 12 ölçüt
- C2 OpenHands, Symphony, Aperant
- C3 tak-çıkar
- C4 büyük otonom yapım vakaları
- C5 HRMS alanı ve oracle
- C6 144 ekip ölçeği

Önceki araştırmalar (B1–B3) aynı klasörde.

**Kendi doğrulamam.** Raporlar model çıktısı olduğu için kritik birkaç noktayı birincil kaynaktan kendim kontrol ettim:

- OpenHands'in yeniden yapılanma tarihi: `gh api`. Geçiş duyurusu 16.06.2026, eski kodun `legacy` deposuna taşınıp arşivlenmesi 27.07.2026.
- 2026 asgari ücret ve SGK oranları: ÇSGB'nin resmî PDF tablosu.

Tümü raporlarla tutarlı çıktı.

---

## 1. Sorunun doğru hâli

Aranan araç değil, bir **çerçeve**:

> görev girdisi → izole ve paralel ajan yürütücüleri → tek trunk'a (alpha) birleştirme → uzak ortama dağıtım ve doğrulama → insanın alpha üzerinde incelemesi → issue → yeni görev

Bu döngü 12 ART × 12 ekip ölçeğinde çalışmalı ve her katmanı değiştirilebilir olmalı. Plane ve OpenHands yalnızca örnek. Başarı ölçütü "bir modül yazıldı" değil. Ölçüt şu: CronHR'daki HRMS'in tamamı bir ERP modülü olarak DoD'ye kadar bitmiş olmalı; gap ve bilinmeyen-bilinmeyen analizi yapılmış, kabul kriterleri karşılanmış, yapay zekâyla yapılabilecek bütün testler yapılmış olmalı.

---

## 2. Bu döngüyü uygulayan hazır proje var mı?

**Yok.** 32 aday incelendi (C1). Hiçbiri döngünün tamamını belgelenmiş davranış olarak sunmuyor. Döngünün iki halkası **hiçbir üründe** yok:

- **R7:** alpha'ya dağıtmak ve orada doğrulamak.
- **R8:** dağıtılmış ortamdaki incelemeden otomatik görev üretmek.

Sizin tarif ettiğiniz "insan alpha.example.com'da inceler → issue → yeni görev" halkası tam olarak burası.

| Aday | Puan (22 üzerinden) | Not |
|---|---|---|
| GitLab Duo Agent Platform | 17 | En yakın aday. Güçlü puanların yarısı ajan kısmından değil GitLab platformundan geliyor (merge trains, grup/epik hiyerarşisi, self-managed kurulum). Ajan tetikleyicileri yalnız insan eylemiyle çalışıyor; bir bot ya da başka bir akış ajanı başlatamıyor. Dağıtılmış uygulamadan geri bildirim toplayan araç 17.0'da kaldırıldı. |
| Warp Factories | 16 | Kâğıt üzerinde tarifinize en yakın ürün. Ama kapalı erken erişimde, tescilli ve bağımsız kanıt yok. |
| Gas Town + Beads | 14 | Açık kaynaktaki en yakın aday. Tek makinede çalışıyor, fiilen tek geliştiriciye bağlı. Bir ajan admin yetkisiyle CI'ı atlatıp birleştirdi. |
| LangChain Open SWE | 13 | Tek harness'e bağlı; kendi README'si kararlılık garantisi vermiyor. |
| OpenHands | 10 | Yürütücü katmanında güçlü (bkz. §3). |
| OpenAI Symphony | 9 | Ürün değil, spesifikasyon (bkz. §3). |

**Hazır çerçeve yok ama hazır fişler var:**

| Katman | Fiş olabilecekler |
|---|---|
| Görev kaynağı | Plane Agent Run, Linear AgentSession, Jira, GitHub/GitLab issue |
| Orkestratör | Temporal, LangGraph |
| Yürütücü | Claude Code / Agent SDK, Codex app-server, OpenHands Agent Server |
| Sandbox | Coder, E2B, container-use, OpenHands Docker/K8s |
| Merge | GitHub merge queue, GitLab merge trains. Merge kuyruğu ajanın elinde değil, VCS'de zorunlu olmalı; Gas Town olayı bunun gerekçesi. |

144 ekiplik kota, WIP ve öncelik yönetimi, DoD kapıları, alpha doğrulaması ve inceleme→görev döngüsü hiçbir üründe yok. Bunlar çerçevenin kendi sorumluluğunda kalıyor.

---

## 3. OpenHands, Symphony, Aperant

**OpenHands — yürütücü katmanı için güçlü, çerçevenin tamamı için yetersiz** (C2).

- **Yapı.** 27.07.2026'da ana depo "Agent Canvas" arayüzüne dönüştü, eski kod arşivlendi. Çekirdek ve REST/WebSocket Agent Server, MIT lisanslı `software-agent-sdk` deposunda.
- **Dışarıdan paralel sürülebilir.** Varsayılan `max_concurrent_runs` 10. Resmî boyutlandırma sandbox başına 0,5 vCPU ve 4 GiB; 100'den fazla eşzamanlı sandbox için Kubernetes zorunlu.
- **Başka ajanları da çalıştırabiliyor.** `ACPAgent` ile claude-code, codex, gemini-cli ve opencode dahil.
- **Açık kaynakta olmayanlar.** "İzole sandbox", "ölçeklenebilir, sürekli çalışan ajanlar", çok kullanıcılı yapı ve RBAC Enterprise'da. Enterprise lisansı PolyForm Free Trial: açık kaynak değil ve ticari lisans olmadan yılda 30 günle sınırlı.
- **Değişim sıklığı.** 18 ayda V0 → V1 → Canvas. Eski API belgelenmeden kaldırıldı.
- **Açık hatalar.** Eşzamanlılık sınırı uygulanmıyor (#4063). Sandbox durunca konuşma `RUNNING`'de takılı kalıyor (#4893). Ağustos 2026'da deadlock ve serileşme regresyonları yaşandı.
- **Doğru konumu.** "Plane → openhands 1…12" çiziminde OpenHands çerçeve değil, **yürütücü havuzunun bir tipi** olur. Ona doğrudan değil, ince bir yürütücü sözleşmesi (ExecutorPort) ve ACP üzerinden bağlanılmalı.

**Symphony — tasarım referansı, çalıştırılacak ürün değil.**

- Tracker sözleşmesi yalnız iki okuma işleminden oluşuyor.
- Durum makinesi ve uzlaştırma iyi tasarlanmış.
- Yürütücü resmî olarak yalnız Codex.
- Kalıcı veritabanı yok, tek süreçte çalışıyor. OpenAI ürün olarak sürdürmeyecek.
- Plane adaptörü yok.

**Aperant — gözleminiz doğru, ama eksiği "scrum ekibi olmaması" değil.**

- Tek kullanıcılı bir masaüstü uygulaması. Yalnız worktree izolasyonu var, en fazla 12 terminal.
- Tek depoya bağlı; çok depo desteği talebi reddedildi.
- 2.x sürümü bakım modunda; 3.0 kapalı depoda geliştiriliyor.
- Abonelik girişine dayanıyor. Anthropic 2026 Nisan'da bunu üçüncü taraf araçlar için kısıtladı (ikincil kaynak).

WordPress modülü ile HRMS arasındaki fark ekip sayısı değil. Fark şu dört şeyde: **oracle, ayrıştırma, entegrasyon ve inceleme kapasitesi** (bkz. §5–§7).

---

## 4. "Tak-çıkar" gerçekte ne demek?

**Kısa cevap:** Tak-çıkar bir aracın yerine başka bir araç koyabilmek değildir. Bir parça değiştiğinde **sistemin gerçeği kaybolmamalı** (iş durumu, spesifikasyon, kabul testleri, birikmiş bilgi). Ayrıca değişimin çalıştığı **otomatik olarak kanıtlanabilmeli** (C3).

**Neden şart?** Bu katmanlarda araç ömrü 8–18 ay. Son 12 ayda olanlardan örnekler:

- Kapananlar: Roo Code (3 milyon kurulum), Vibe Kanban, Terragon, Crystal.
- Arşivlenen: Flowise (13.08.2026), göç yolu sunulmadan.
- Kaldırılan: OpenAI Assistants API (26.08.2026) ve Agent Builder. Agent Builder duyurusundan yaklaşık 8 ay sonra kaldırıldı.
- Değişen kural: Anthropic'in üçüncü taraf kullanım kuralı 6 ayda 5 kez değişti.
- Emekliye ayrılan: Anthropic modelleri 12–13 ayda.
- Yeniden yapılanan: OpenHands iki kez.

**n8n benzetmesinin sınırı.** n8n'de bir düğümü değiştirmek kolay, çünkü durumu, zamanlayıcıyı, sırları ve sürümlemeyi platform taşıyor. **Aynı sebeple n8n'in kendisini değiştirmek zor.** Üç ayrı değişim türü var:

- Düğüm değişimi = adaptör değişimi.
- Orkestratör değişimi = durum göçü.
- Grafik biçimi değişimi = yeniden yazım.

Pilotunuzdaki Kestra'nın "iki beyin" sorunu Netflix'te de yaşandı. Netflix Temporal'a geçişi eski ve yeni yolu bir arayüzün arkasına koyup bayrakla kademeli kaydırarak yaptı. Geçiş iki çeyrek sürdü ve geçici hata oranı %4'ten %0,0001'e indi.

**Değişimi ucuz ya da pahalı yapan tek şey: sözleşmenin ve verinin kimde durduğu.**

- **Ucuz geçişler** (sözleşme ya da biçim aynı kaldı):
  - Docker → containerd (CRI + OCI)
  - Redis → Valkey (aynı protokol)
  - Terraform → OpenTofu (aynı state dosyası)
- **Pahalı geçiş** (durum sağlayıcıdaydı): Assistants API → Responses.

**Üç koşul:**

1. **Gerçek araçta değil, sizde durur.** Kendi olay defteriniz, ve depodaki spec'ler, kabul testleri ve altın veri setleri.
2. **Her araç dar bir sözleşmenin (port) arkasında durur.** Her yeni adaptör bir uyumluluk test takımını (TCK) geçmeden devreye alınmaz. Kubernetes CRI, MCP conformance ve A2A TCK bunun örnekleri.
3. **Değişim prova edilmiştir.** Bayrakla kademeli geçiş, bitiş tarihi ve çeyrekte bir gerçek işle yapılan değişim tatbikatı.

**Karşı kanıt: soyutlamanın bedeli.**

- Anthropic'in OpenAI uyumluluk katmanı kendi dokümanında "production-ready değil" diye geçiyor.
- LiteLLM gibi ortak geçitler her sağlayıcı sürümünün gerisinden geliyor.
- Hohpe: "bir kilitlenmeden kaçmak çoğu zaman başka bir kilitlenme yaratır."

Pratik sonuçlar:

- Oynaklığı düşük katmanlara (Git, OTLP, SAFe politikası) soyutlama yazılmaz.
- Model tarafında ortak geçit yerine **her sağlayıcı için ayrı, doğrudan adaptör** yazılır.

**Standartlar.**

- **Yürütücüyü orkestratörü yeniden yazmadan değiştirmek:** en yakın standart **ACP** (Agent Client Protocol). Yaklaşık 37 ajan destekliyor ve örneğinizdeki **Hermes Agent ile OpenClaw ikisi de doğrudan ACP konuşuyor**. Ama eksikleri var: kayıttaki 35 ajandan yalnız 12'si oturum devamını, hiçbiri `session/stop`'u destekliyor. Bu boşluklar kendi yürütücü sözleşmenizde kapatılmalı.
- **Araçlar:** MCP.
- **Talimatlar:** AGENTS.md.
- **A2A:** kodlama ajanları için bugün pratik değil.

**Katman oynaklığı** (17 satırlık tablo C3'te):

- En oynak: harness, model, sağlayıcı koşulları, bellek biçimi.
- **En kalıcı olması gereken: kabul spec'leri ve test oracle'ı.** Araçlar değişir; sistemin değeri, ürünün doğrusunu tanımlayan bu varlıklardadır.

---

## 5. Ajanlar ERP/HRMS ölçeğinde bir şeyi DoD'ye kadar bitirdi mi?

**Kamuya açık bir örnek yok** (C4, 23 vaka).

| Vaka | Ne üretildi | DoD'ye göre durumu |
|---|---|---|
| Cursor tarayıcısı | ~2.000 eşzamanlı ajan, 1M+ satır | Derlenmedi, CI işlerinin %88'i kırmızıydı |
| Anthropic C derleyicisi | 16 ajan, ~100K satır, ~20K $ | GCC torture testlerinin %99'unu geçiyor, Linux'u derliyor. Ama README'deki "hello world" adımları çalışmadı; assembler/linker hatalı |
| OpenAI "elle kod yazılmayan" ürün | ~1M satır, 3–7 mühendis, 5 ay | Dahili beta; dış DoD doğrulanamadı |

**Büyük başarıların hepsinde hazır bir dış oracle vardı:**

- C derleyicisi: GCC ve torture testleri
- Ladybird: test262, lockstep karşılaştırma
- vinext: Next.js'in test paketi
- JustHTML: html5lib-tests
- Sora Android: iOS uygulaması

**Türk bordrosu, SGK ve beyanname için böyle bir hazır oracle yok. Önce onun inşa edilmesi gerekiyor.**

**"90/90" neden oluyor?** Ölçümler:

- **Testi geçmek teslim edilebilir olmak demek değil.** METR'in incelediği 15 ajan PR'ının hiçbiri olduğu gibi birleştirilebilir değildi. SWE-bench'i geçen PR'ların yalnızca yaklaşık yarısını bakımcılar birleştirirdi.
- **Uzun ufuklu işte başarı düşük:**
  - SWE-EVO: %25
  - FeatBench: %29,9
  - Commit0 tam set: %6
- **Uzun kuyruk ayrıca zor.** Spotify'da ilk %70'i deterministik betikler hallettiği hâlde, kalan %30 "son derece zor"du. Airbnb'de son %3 elle bitirildi.

**Son %10'u kapatan belgelenmiş teknikler:**

- Referans sistemle diferansiyel karşılaştırma
- Başka projenin test paketini taşıma
- Fuzzing
- Bağımsız değerlendirici ve LLM yargıç
- Sınırlı CI turu, ardından insana devir
- Ortam hazırlığı: dotnet/runtime'da başarıyı %38'den %69'a çıkardı
- Planlı insan müdahalesi: insan dokunuşlu PR'larda başarı %86, tam otonomda %55

---

## 6. HRMS için "tamam" ne demek, oracle nereden gelir?

**DoD için beş koşulun hepsi gerekli** (C5):

1. **Kapsam.** 18 maddelik genel HR minimumu ve 16 maddelik Türkiye farkı: SGK/GİB, MUHSGK, teşvik, kıdem/ihbar, BES, icra, e-bordro, banka dosyası.
2. **Kural izlenebilirliği.** Her kuralın kanun maddesi ve Resmî Gazete kaydıyla izlenebilmesi.
3. **Uzman imzası.** Uzmanın (mali müşavir, İK hukukçusu) imzaladığı altın test setleri.
4. **Entegrasyon kanıtı.** Test ortamı olmayan entegrasyonların paralel koşumla kanıtlanması.
5. **İşletim altyapısı.** Parametre sürümleme, mevzuat izleme, dönem kilidi ve denetim izi.

**Kanun geliştirme sırasında değişiyor:**

- 7566 sayılı Kanun (Aralık 2025) SGK oranlarını değiştirdi.
- 7578 sayılı Kanun (Nisan 2026) analık iznini 24 haftaya, babalık iznini 10 güne çıkardı.

Nisan'da doğru olan bir test Mayıs'ta yanlış olabilir.

**Resmî oracle kaynakları:**

- SGK Teşvikler 2026 kitapçığı: her teşvik için rakamlı örnek var.
- ÇSGB 2026 tablosu.
- GVGT 319: 18 sayısal örnek.
- GİB Ücret Geliri Rehberi 2026.
- GİB MUHSGK kılavuzu.
- SGK kod listeleri.

**Test ortamı durumu.** Test ortamı yalnızca SGK 4/a işe giriş/ayrılış servisinde var, o da gerçek işyeri sicili istiyor. MUHSGK, e-Bildirge, banka ve BES için test ortamı yok; bunlarda ilk gerçek test canlı gönderim olacak.

**Hazır çerçeve mi, sıfırdan mı?**

- **Frappe HRMS:** GPL-3; 160 DocType, ~73 bin satır Python, 128 test dosyası. Türkiye yerelleştirmesi yok. Vergiyi Hindistan modeliyle yıllık projeksiyonla hesaplıyor; Türkiye'de kümülatif fiili matrah kullanılır.
- **Odoo:** Türkiye bordrosu yalnız Enterprise'da var ve dar kapsamlı.
- **OCA:** `l10n-turkey` deposu boş.
- **Açık kaynakta hiçbir üründe Türkiye bordro/SGK/GİB katmanı yok.**

Hazır çerçeve genel HR işini ciddi ölçüde azaltır. Ama **riski belirleyen Türkiye katmanını ve oracle işini azaltmaz.** Araştırmanın önerisi, ki bu bir mühendislik yargısı:

- Frappe üzerine ayrı bir Türkiye uygulaması
- Çerçeveden bağımsız, saf bir Türkiye bordro çekirdeği; altın ve diferansiyel testler bu çekirdeği hedefler
- CronHR ön yüzü

---

## 7. 12 SAFe × 12 ekip = 144 ekip doğru kaldıraç mı?

**Hayır** (C6, C4).

**Sınır olmayanlar.**

- **Model hız limitleri bağlayıcı değil.** 144 ajan, en düşük kademenin (Start) %5–16'sını kullanır. Asıl risk aylık **harcama tavanı**: Start kademesinde 500 $. Tavana gelindiğinde bütün filo aynı anda durur.
- **Donanım.** 128 GB'lık tek sunucu yaklaşık 8–14 orta boy ajan taşır, kabaca bir ART. 144 ajan için 10–18 sunucu ve Kubernetes gerekir, ayda yaklaşık €2,6k–4,6k. Bu, token maliyetinin çok altında.

**Aşılamayan iki kısıt:**

1. **İnsan inceleme ve kabul kapasitesi.**
   - Varsayım: ekip başına günde 3–10 PR. Bu toplamda günde 432–1.440 PR eder.
   - İnceleme yükü günde 173–576 saat; bunun için 43–144 kişi gerekir.
   - Faros 2026 verisinde inceleme süresi %441, olay/PR oranı %243 arttı.
2. **Tek trunk'ın entegrasyon kapasitesi.**
   - Hedef hacim, GitHub'ın kendi monolitinin 4–12 katı.
   - Shopify'da tek kuyrukta P90 bekleme 693 dakikaydı. Kuyruk kod bölgelerine bölünce yaklaşık 41 dakikaya indi.

**Yapı kanıtı:**

- **Düz yapı çöküyor.** Hiyerarşisiz düz yapıda 20 ajanın etkin verimi 2–3 ajana düştü (Cursor).
- **İşe yarayan yapı:** planlayıcı → birbiriyle konuşmayan işçiler → yargıç.
- **Resmî öneri küçük ekip.** Claude Code agent teams belgesi 3–5 takım arkadaşı öneriyor; iç içe takım yok.
- **Sıralı işte çoklu ajan kötüleştiriyor.** Sonuç %39 ile %70 arasında düşüyor.
- **Rol simülasyonuna kanıt yok.** Scrum/SAFe rol simülasyonunun büyük ölçekte fayda sağladığına dair kanıt bulunamadı.
- **Sahada gözlenen desen.** Stripe, Spotify, Ramp ve OpenAI'da kalıcı "ajan ekibi" yok. Yapı şu: görev kuyruğu + görev başına tek seferlik izole işçi + insan onayı.

**SAFe'ten politika olarak kalanlar:**

- WIP limiti
- ART bütçesi
- İnsan demo ve kabul ritmi olarak PI kadansı
- Bağımlılık panosu

**12 ART, HRMS'in 12 alanına eşlenebilir.** Her alanda 12 sabit ekip yerine şunlar olur:

- bölümlenmiş bir iş kuyruğu,
- elastik bir işçi havuzu,
- bir ya da birkaç insan kondüktör.

**Kademeli büyüme:** 1 → 3 → 12 → 36–48 → en fazla 144. Her adım şu ölçütlerle kapılanır:

- kuyruk P90 ≤ 60 dk,
- trunk zamanın ≥ %95'inde yeşil,
- inceleme birikimi en çok bir günlük kapasite,
- kabul oranı ≥ %50,
- kabul edilen değişiklik başına maliyet artmıyor.

**Maliyet (insan hariç, token + CI + sandbox):**

| Senaryo | Aylık |
|---|---|
| Mesai saatleri | 15k–120k $ |
| 7/24 | 50k–450k $ |
| Ekip başına 5 ajanlı SAFe rol oyunu | Yalnız token 218k–1,93M $ |

Ajan-saat maliyetindeki 5–9 kat belirsizlik, bir pilotta ilk ölçülmesi gereken sayı.

---

## 8. Sezgileriniz: nerede doğru, nerede düzeltme gerekiyor?

**Doğru olanlar:**

- **"Araçlar hızla değişiyor, tak-çıkar şart."** Kanıt güçlü (§4).
- **"OpenHands yeterli olabilir de olmayabilir de."** İkisi de doğru: yürütücü katmanı için yeterli, çerçeve için değil (§3).
- **"Aperant'ın WordPress modülü yetmez."** Doğru. HRMS'in zorluğu kod miktarı değil; oracle, ayrıştırma ve entegrasyon (§5–§6).
- **"90/90'da kalmasın; gap, bilinmeyen-bilinmeyen, AC ve DoD."** Araştırmanın merkezindeki bulgu bu. Asıl iş, ajanların dokunamayacağı bir doğruluk kaynağı (oracle) kurmak (§5–§6).

**Düzeltilmesi gerekenler:**

- **"Tak-çıkar = n8n'deki fiş."** Asıl taşınabilirlik fişte değil, durumun ve sözleşmenin sizde olmasında. Düğüm-grafiği platformlarının kendisi zor değiştirilir: Flowise göç yolu sunulmadan arşivlendi (§4).
- **"12 × 12 = 144 scrum ekibi" ajan yapısı olarak.** Kanıt, ölçeği ekip sayısının değil **oracle, inceleme ve entegrasyon kapasitesinin** belirlediğini gösteriyor. 144 bir hedef değil, en fazla bir tavan (§7).

---

## 9. Doğrulanamayanlar ve sınırlar

- Araştırmacıların web arama kotaları son bölümlerde doldu; kalan doğrulamalar `gh api`, doğrudan sayfa okuma ve resmî PDF'lerle yapıldı.
- İkincil kaynaktan gelen ya da doğrulanamayan iddialar:
  - OpenAI'nin harness ve Sora yazılarının orijinalleri 403 döndü; ayrıntılar röportaj ve ayna sayfalardan.
  - Anthropic'in Nisan 2026 abonelik kısıtı ikincil kaynaktan.
  - METR'in "Mythos" %50 ufku bir sosyal medya duyurusundan.
  - Asgari ücret gelir vergisi istisnasının aylık tutarları türetildi; resmî tablo bulunamadı.
- Bulunamayanlar: 144 ekip ölçeğinde ölçülmüş bir vaka ve genel geçer bir "insan : ajan" oranı. Yayınlanmış tek oran 1 araştırmacı : 16 ajan.
