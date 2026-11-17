# C6 — 144 ajan ekibi, tek trunk: sınırlar, darboğazlar, maliyet (Özet)

**Tarih:** 27 Eylül 2026 · **Ayrıntılı veri ve tüm URL'ler:** `C6-olcek-144-ekip.json`
Aksi belirtilmedikçe tüm kaynaklara 2026-09-27'de erişildi. **tahmin** = kaynaklı sayılardan türetilmiş (aritmetik gösteriliyor). **doğrulanamadı** = birincil kaynak bulunamadı.

---

## 1. Karar

**144 kalıcı "ajan scrum ekibi" doğru kaldıraç değil.**

Model hız limitleri, sandbox yoğunluğu ve GitHub API para ve mühendislikle aşılabiliyor. Aşılamayan iki kısıt: **insan review/kabul kapasitesi** ve **tek trunk'ın entegrasyon kapasitesi** (merge queue, kırık trunk).

Önerilen birim: HRMS modül sınırlarına göre **bölünmüş iş kuyrukları**, görev başına **tek seferlik izole işçi**, deterministik doğrulama (CI + oracle) ve insan onay kapısı.

Eşzamanlı işçi sayısı sabit tutulmamalı. Şu formülle dinamik belirlenmeli: `min(insan review kapasitesi, merge kuyruğu kapasitesi, bütçe)`. 144 sayısı bir hedef değil, en fazla bir tavan olmalı.

SAFe **politika** olarak değerli, **rol-oyunu** olarak değil. Değerli kalan parçalar: WIP limiti, ART bütçesi, PI kadansı ve bağımlılık panosu (bkz. §5).

---

## 2. Ana sayılar

### Model sağlayıcı

Anthropic kademeleri (Opus 5.5 ve Sonnet 5 için ayrı kovalar) ([rate-limits](https://platform.claude.com/docs/en/api/rate-limits)):

| Kademe | RPM | ITPM | OTPM | Aylık harcama tavanı |
|---|---|---|---|---|
| Start | 1.000 | 2M | 400k | $500 |
| Build | 5.000 | 5M | 1M | $1.000 |
| Scale | 10.000 | 10M | 2M | $200.000 |

- Custom kademede tavan yok.
- Tavanda istekler **ay sonuna kadar** 429 döner (retry-after yok). Önbellek okumaları ITPM'e sayılmaz.

OpenAI tarafı ([rate-limits](https://developers.openai.com/api/docs/guides/rate-limits), [GPT-6 Sol](https://developers.openai.com/api/docs/models/gpt-6-sol)):

- Tier 5: $200.000/ay limit.
- GPT-6 Sol, Tier 5'te 15.000 RPM ve 40M TPM.
- Önbellekli token'ların TPM'e sayılıp sayılmadığı dokümanda yok: doğrulanamadı.

**Ajan başına tüketim** ([C derleyicisi, 2026-02-05](https://www.anthropic.com/engineering/building-c-compiler)):

- Vaka: 16 ajan, 2 hafta, $20.000, 2 milyar giriş ve 140 milyon çıkış token'ı.
- Ajan-saat: 16 × 336 saat = 5.376.
- Ajan-saat başına: **~372k giriş, ~26k çıkış token'ı, ~$3,72** (tahmin).

**144 ajanın hız limitine etkisi** (tahmin, önbellek isabeti %90 varsayımıyla):

- Önbelleksiz giriş: 144 × 372k / 60 × 0,1 ≈ **89k ITPM**.
- Çıkış: ≈ **62,5k OTPM**.
- Bu, Start kademesinin %5–16'sı. Yani hız limiti bağlayıcı değil.
- Asıl riskler:
  - aylık harcama tavanı,
  - aynı anda başlatmada tetiklenen "acceleration limits".

### Kod barındırma ve CI

GitHub API limitleri ([REST](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api)):

- GitHub App: 5.000–12.500 istek/saat; Enterprise Cloud'da 15.000/saat.
- İkincil sınır: **içerik oluşturan istek 80/dk ve 500/saat**. Bu limitin kimlik başına mı uygulandığı dokümanda açık değil: doğrulanamadı.

GitHub Actions ([limits](https://docs.github.com/en/actions/reference/limits)):

- Eşzamanlı iş: Team planında 60, Enterprise'da 500.
- Linux 2-core runner $0,006/dk ([fiyat](https://docs.github.com/en/billing/reference/actions-runner-pricing)).
- Self-hosted runner için duyurulan $0,002/dk ücret **ertelendi** ([GitHub](https://github.com/resources/insights/2026-pricing-changes-for-github-actions)).

Merge queue ([doküman](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue)):

- Build concurrency ve grup boyutu 1–100 arasında.
- Yerleşik "bölümlenmiş kuyruk" özelliği dokümanda yok.

### Tek trunk'ta kanıt

- **GitHub'ın kendi monoliti:** 500+ mühendis ayda 2.500 PR birleştiriyor, iş günü başına ≈115 ([GitHub, 2024-03-06](https://github.blog/engineering/engineering-principles/how-github-uses-merge-queue-to-ship-hundreds-of-changes-every-day/)).
- **Shopify:**
  - 1.000+ geliştirici, günde ~400 commit, 8'li batch ([2019](https://shopify.engineering/successfully-merging-work-1000-developers)).
  - Tek kuyrukta P90 bekleme **693 dk** idi. Kuyruk kod bölgelerine bölündükten sonra P90 **~41 dk**, P50 ~26 dk ([Graphite](https://graphite.com/customer/shopify-merge-queu)).
- **Uber:**
  - Günde ~1.000 değişiklik.
  - SubmitQueue öncesinde iOS ana dalı zamanın yalnızca **%52**'sinde yeşildi.
  - 16 eşzamanlı değişiklikte sorun çıkma olasılığı **%40** ([EuroSys'19 özeti](https://blog.acolyer.org/2019/04/18/keeping-master-green-at-scale/)).
- **Google** ([SWE Book, bölüm 23](https://abseil.io/resources/swe-book/html/ch23.html)): günde 50.000+ değişiklik, 4 milyar+ test. Seri kuyruk yok: iyimser presubmit, birleştirme sonrası batch test, otomatik geri alma. Presubmit'i geçenlerin "95%+"'ı kalan testleri de geçiyor (≈%5'e kadar sonradan kırılma).

### Hesaplama ve sandbox

**Mevcut sunucu** ([AX102](https://www.hetzner.com/dedicated-rootserver/ax102/), [canlı fiyat](https://www.hetzner.com/_resources/app/data/app/live_data_prices.json)):

- 16 çekirdek / 32 iş parçacığı, 128 GB RAM.
- **€257,30/ay** ve €129 kurulum.

**Ajan başına kaynak** ([Agent SDK hosting](https://code.claude.com/docs/en/agent-sdk/hosting)):

- 1 GiB RAM / 1 CPU yalnızca bir başlangıç noktası: "a floor, not the ceiling".
- Aynı doküman: token maliyeti, altyapı maliyetini "an order of magnitude or more" aşar.

**Tek sunucuya kaç orta boy görev sığar** (tahmin; orta görev = 8 GB / 4 vCPU, sistem için 16–24 GB ayrılmış):

- RAM'e göre 13–14 görev.
- CPU'ya göre 8–16 görev.
- Sonuç: **~8–14 eşzamanlı ajan**, yani kabaca 1 ART.
- 144 ajan için **10–18 sunucu** gerekir: **€2.573–€4.631/ay**.

**Sandbox seçenekleri** (4 vCPU / 8 GB ile karşılaştırma):

- E2B $0,331/saat; Pro'da en fazla 100 eşzamanlı, Enterprise en az $3.000/ay ([fiyat](https://e2b.dev/pricing)). Modal ~$0,476 ([fiyat](https://modal.com/pricing)), Northflank ~$0,133 ([fiyat](https://northflank.com/pricing)).
- Firecracker <125 ms açılış, <5 MiB ek yük ([site](https://firecracker-microvm.github.io/)). kubernetes-sigs/agent-sandbox v1beta1, gVisor/Kata, warm pool ([repo](https://github.com/kubernetes-sigs/agent-sandbox)).
- Daytona "no longer maintained" ([repo](https://github.com/daytonaio/daytona)): self-host için elenir.

---

## 3. İlk 5 darboğaz

1. **İnsan review ve kabul kapasitesi — gerçek darboğaz.**
   - Hesap (tahmin): günde 432–1.440 PR (ekip başına 3–10) × 200 LOC ÷ 500 LOC/saat ([SmartBear/Cisco](https://smartbear.com/learn/code-review/best-practices-for-peer-code-review/)) = **173–576 review saati/gün**.
   - Günde 4 saat odaklı review ile bu **43–144 kişi** eder.
   - Faros 2026, 22.000 geliştirici ([kaynak](https://www.faros.ai/blog/ai-acceleration-whiplash-takeaways)): review süresi **+%441,5**, review'suz birleşme **+%31,3**, olay/PR **+%242,7**, geliştirici başına hata **+%54**.
   - OpenAI: "our bottleneck became human QA capacity" ([ayna](https://jaytaylor.com/notes/node/1770842156000.html)). Stripe: "developer attention" en kısıtlı kaynak ([Minions](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents)).
   - Tester başına kabul testi kapasitesi: doğrulanamadı.

2. **Tek trunk'ta merge kuyruğu ve kırık trunk.**
   - 432–1.440 PR/gün, GitHub monolitinin 4–12 katı.
   - Uber ve Google verileri: eşzamanlılık arttıkça kırılma olasılığı hızla büyüyor.
   - Tek global kuyruk, Shopify'daki 693 dk'lık P90 riskini taşır.

3. **Paylaşılan tek alpha ortamı ve şema/veri çakışması.**
   - Uber'in gerekçeleri: staging "flaky" ve "limits how many developers can test at once" ([SLATE](https://www.uber.com/us/en/blog/simplifying-developer-testing-through-slate/)).
   - Lyft'in gerekçesi: "an unstable new feature could cause problems for the entire staging environment" ([InfoQ](https://www.infoq.com/news/2022/03/scaling-testing-acceptance-lyft/)).
   - İki şirket de kişi başına tam ortam yerine **istek/tenant izolasyonuna** geçti.
   - GitLab'ın migration kuralları ([rehber](https://docs.gitlab.com/development/migration_style_guide/)):
     - her sürüm için ayrı dosya,
     - migration süresi ≤3 dk,
     - her migration geri alınabilir.

4. **Maliyet ve harcama tavanı (tek hata noktası).** 7/24'te token **$43,6k–$385,7k/ay**; üst uç Scale tavanını ($200k) aşar ve tavanda tüm filo aynı anda durur.

5. **Hesaplama ve GitHub API/CI limitleri.** 144 ajana 10–18 sunucu ve K8s gerekir (ARC zaten "a Kubernetes operator", [doküman](https://docs.github.com/en/actions/concepts/runners/actions-runner-controller)). CI'da 8 saatlik pencerede ortalama 86–288 eşzamanlı iş gerekir; Team planının 60 limiti yetmez. İçerik oluşturma sınırı 500/saat. Çözülebilir, ama 1–4'ten sonra anlamlı.

---

## 4. Maliyet aralığı (insan maliyeti hariç)

**Varsayımlar:**

- 1 ekip = 1 eşzamanlı işçi.
- Token profili C derleyicisi vakasından alındı.
- Girişin %90'ı önbellekten okunuyor, %10'u 5 dakikalık önbelleğe yazılıyor.
- Liste fiyatı kullanıldı; indirim yok ([pricing](https://platform.claude.com/docs/en/about-claude/pricing)).

**Ajan-saat başına token maliyeti:**

| Senaryo | Hesap | Sonuç |
|---|---|---|
| Düşük (Sonnet 5) | 0,9×372k×$0,20 + 0,1×372k×$2,50 + 26k×$10 (milyon token başına) | **≈ $0,42** |
| Orta (Opus 5.5) | 0,9×372k×$0,20 + 0,1×372k×$5 + 26k×$20 | **≈ $0,77** |
| Yüksek (gözlenen) | $20.000 ÷ 5.376 | **≈ $3,72** |

Yüksek senaryo için not: C derleyicisi vakasında yayınlanan token sayıları $20k'yı liste fiyatıyla açıklamıyor. Tüm giriş tam fiyattan sayılsa bile toplam $13.500 çıkıyor. Aradaki farkın nedeni doğrulanamadı.

**Aylık toplam:**

| Profil | Ajan-saat/ay | Token | CI (hosted) | Sandbox | Toplam (kaba) |
|---|---|---|---|---|---|
| Mesai: 144×8 sa×22 gün | 25.344 | $10,7k–$94,3k | $5,5k–$18,2k | €2,6k–4,6k (self-host) / $8,4k (E2B) | **$15k–$120k** |
| 7/24: 144×24×30 | 103.680 | $43,6k–$385,7k | $7,5k–$24,9k | €2,6k–4,6k / $34,3k | **$50k–$450k** |
| SAFe rol-oyunu (ekip × 5 ajan, 7/24) | 518.400 | $218k–$1,93M | — | — | Custom kademe şart |

- CI satırı self-hosted runner ile $0 olur; donanım sandbox satırında sayılı.
- CI hesabı: PR başına 96 iş-dakikası × $0,006.
- **PR başına token maliyeti** (mesai profili): 2,67 ajan-saat/PR'dan $0,6–$9,9.
  - Kabul oranı %20–60 ise ([Faros](https://www.faros.ai/blog/ai-acceleration-whiplash-takeaways)), kabul edilen değişiklik başına maliyet bunun 1,7–5 katı.
  - Buna karşılık PR başına insan review süresi en az 0,4 saat. Kabul edilen değişiklik başına maliyette **insan zamanı baskın kalem**. Bu bir yargı; ücret düzeyine bağlı.
- Pilot notu: tek ajan 7/24 çalışırsa orta senaryoda ~$554/ay harcar. Bu, Start kademesinin $500 tavanını pilotta bile aşar.

---

## 5. Yapı: kanıt ne diyor?

**Cursor** ([2026-01-14](https://cursor.com/blog/scaling-agents)):

- Düz öz-koordinasyonda kilitli 20 ajanın etkin verimi **2–3 ajan** düzeyine düştü.
- İşe yarayan yapı: hiyerarşik planlayıcı, **birbiriyle konuşmayan** işçiler, yargıç ajan ve periyodik taze başlangıç.
- Ayrı bir "integrator" rolü "created more bottlenecks than it solved".

**Anthropic** ([multi-agent](https://www.anthropic.com/engineering/multi-agent-research-system), [agent teams](https://code.claude.com/docs/en/agent-teams)):

- Çok-ajanlı sistemler sohbete göre yaklaşık **15 kat** token harcıyor.
- Kodlama, gerçekten paralelleşebilen işin az olduğu bir alan.
- Agent teams dokümanı: "Start with 3-5 teammates"; iç içe ekip yok; plan modunda ~7 kat token.

**Akademik kanıt:**

- MAST ([arXiv 2503.13657](https://arxiv.org/abs/2503.13657)): 14 hata modu, bunların bir sınıfı "inter-agent misalignment".
- Scaling Agent Systems ([arXiv 2512.08296](https://arxiv.org/abs/2512.08296)): tek ajana göre sonuç, ayrıştırılabilir işte **+%80,8**, sıralı planlamada **−%70** arasında değişiyor.

**Conway** ([1968](https://www.melconway.com/Home/Committees_Paper.html)): 144 ekip, 144 parçalı mimariye iter; önce modül sınırları, sonra kuyruklar. İletişim kanalı n(n−1)/2: 144 ekipte **10.296**; iletişim yalnız sözleşme, kuyruk ve panodan akmalı.

**Sahada gözlenen desen** (Stripe, Ramp, Spotify, OpenAI): kalıcı "ekip" yok. Görev kuyruğu, tek seferlik izole işçi (Stripe devbox'ı 10 sn'de hazır, en fazla 2 CI turu) ve insan onayı var. Genel bir "N ajan / 1 insan" oranı için birincil kaynak yok (doğrulanamadı). Açık olan tek oran **1 araştırmacı : 16 ajan** (yeşil alan, insan review'u yok).

**SAFe'ten politika olarak kalacaklar:**

- **WIP limiti:** modül kuyruğu başına işçi ve açık PR tavanı. Little yasasıyla review kapasitesinden türetilir.
- **ART bütçesi:** 12 alan için 12 workspace; her birine aylık harcama ve RPM/ITPM/OTPM limiti. Dokümanda destekleniyor.
- **PI kadansı (8–12 hafta):** insan tarafındaki demo, kabul ve sınır revizyonu ritmi.
- **Bağımlılık panosu:** modüller arası sözleşme ve şema değişiklikleri.
- **12 ART:** HRMS'in 12 alanına (bounded context) eşlenebilir. Ama her alanda 12 sabit ekip yerine **bir bölümlenmiş kuyruk, elastik bir işçi havuzu ve 1–N insan kondüktör** olmalı.

---

## 6. Kademeli plan ve kapı metrikleri

| Kademe | Eşzamanlı işçi | Altyapı | Geçiş kapısı (öneri) |
|---|---|---|---|
| 0 | 1 (1 modül) | Mevcut sunucu, LLM gateway, Build/Scale kademesi | ≥30 kabul edilen PR; kabul oranı ≥%50; PR başına CI turu medyanı ≤2 (Stripe); ajan-saat başına gerçek $ ölçülmüş |
| 1 | 3 (3 modül) | Merge queue; migration politikası | Alpha zamanın ≥%95'inde yeşil; kırık trunk MTTR ≤60 dk; kuyruk P90 ≤60 dk (Shopify ~41) |
| 2 | 12 (~1 ART) | Tek sunucunun tavanı; bölümlenmiş kuyruk; tenant izolasyonu; ART workspace bütçesi | Review kuyruğu ≤1 günlük insan kapasitesi; kaçan hata/PR artmıyor; 4–12 reviewer ayrılmış |
| 3 | 36–48 | Çok düğümlü K8s, agent-sandbox, ARC, GitHub proxy, Custom kademe | Tüm kapılar 2 hafta boyunca tutuyor; ~11–48 reviewer; kabul edilen değişiklik başına maliyet düşüyor veya sabit |
| 4 | ≤144 (tavan) | 10–18 düğüm ve ayrı CI/alpha düğümleri | Yalnızca 43–144 FTE review/kabul kapasitesi varsa **ve** marjinal işçi hâlâ kabul edilen değişiklik üretiyorsa |

Her kademede izlenecekler: merge kuyruğu P50/P90, kırık trunk oranı ve MTTR, review birikimi (bekleyen PR yaşı), kabul edilen değişiklik başına maliyet, kaçan hata (alpha bug / kabul edilen PR), PR başına CI turu, 429 oranı.

Eşikler **politika önerisidir**. Çapaları kanıt veriyor (Shopify, Uber, Stripe, Faros); kesin değerler Kademe 0–1'de kalibre edilmeli.

---

## 7. Açık sorular

Ajan-saat başına gerçek maliyet (5–9 kat belirsizlik; ilk ölçülecek şey), GitHub 500/saat sınırının kapsamı, OpenAI TPM'e önbellekli token dahil mi, tester başına günlük kabul testi kapasitesi. OpenAI harness orijinali 403 döndü; alıntılar ayna ve InfoQ'dan.
