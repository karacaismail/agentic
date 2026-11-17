# C4: AI ajanlarının büyük sistemleri bitirmesi (ve takılması) üzerine kamusal kanıtlar

Tarih: 2026-09-27. Ayrıntılı kayıtlar: `C4-buyuk-yapim-vakalari.json` (23 vaka, 11 ölçüm, 8 ekip yapısı kanıtı). "Doğrulanamadı" etiketi birincil kaynağı bulunamayan iddialar için kullanıldı. "Çıkarım" etiketi ise kaynakta yazmayan, bizim yorumumuz olan cümleleri işaretler.

---

## (a) ERP/HRMS ölçeğinde bir sistem ajanlarla DoD'a kadar yapıldı mı?

**Hayır.** Kamuya açık birincil kaynaklarda, ERP/HRMS ölçeğinde bir sistem bulunamadı. Bu ölçekten kastımız şu: birbirine bağlı onlarca iş modülü, yasal hesaplamalar, yetkilendirme ve entegrasyonlar. Böyle bir sistemi ajanlarla baştan sona kurup kabul kriterlerini karşılayan, regresyonsuz ve üretimde çalışan bir örnek yok. Odoo/Frappe tarafında bulunanlar yalnızca ajanlara yardım eden skill ve plugin paketleri ([frappe-agent](https://github.com/Dkm0315/frappe-agent), [OCA tartışması](https://github.com/orgs/OCA/discussions/201)). "Kendi ERP'mi vibe-code ettim" başlıklı yazı da aslında tek modüllü bir destek/ticket aracı. Yazar 60–80 saat harcamış ve "ilk hafta ekip araçtan nefret etti" diyor ([blle.co](https://www.blle.co/blog/how-i-vibe-coded-my-own-erp)).

**En yakın analoglar:**

- **Boyut olarak:** Cursor'ın tarayıcısı FastRender, ~2.000 eşzamanlı ajanla 1M+ satıra ulaştı. Aynı deneylerde bir Excel klonu 1,6M satır, bir Windows 7 emülatörü 1,2M satır üretildi. Ancak FastRender yayınlandığında derlenmiyordu ve CI işlerinin %88'i başarısızdı ([Cursor](https://cursor.com/blog/scaling-agents), [The Register](https://www.theregister.com/2026/01/22/cursor_ai_wrote_a_browser/)).
- **Boyut artı gerçek kullanım:** OpenAI'ın elle hiç kod yazılmadan geliştirilen dahili ürünü ~1M satır. 5 ayda 3→7 mühendisle yapıldı ve dahili beta aşamasında ([Latent Space](https://www.latent.space/p/harness-eng)).
- **DoD'a en yakın büyük greenfield:** Anthropic'in C derleyicisi. 16 ajan, ~100K satır Rust, ~20K USD. GCC torture testlerinin %99'unu geçiyor ve Linux çekirdeğini derliyor. Buna rağmen "Hello world" README'deki talimatlarla derlenmedi; assembler ve linker hatalı ([Anthropic](https://www.anthropic.com/engineering/building-c-compiler), [issue #1](https://github.com/anthropics/claudes-c-compiler/issues/1)).
- **Üretime teslim edilen ürün:** Sora Android uygulaması. 28 günde 4 mühendisle yapıldı, crash-free oranı %99,9. Ancak mevcut iOS uygulamasının portu ([The Decoder](https://the-decoder.com/openai-claims-four-engineers-and-codex-build-the-sora-android-app-in-just-28-days/)).

**Kritik fark:** Büyük başarıların hepsinde dışarıdan hazır gelen güçlü bir oracle vardı (doğruluğu otomatik kontrol eden kaynak):

- C derleyicisinde GCC ve torture testleri,
- Ladybird'de test262 ve C++ sürümüyle lockstep karşılaştırma,
- vinext'te Next.js test paketi,
- JustHTML'de html5lib-tests,
- Sora'da iOS uygulaması.

HRMS'te, özellikle SGK, vergi ve bordro için böyle hazır, makineyle çalıştırılabilir bir kamu oracle'ı yok; onu da inşa etmek gerekiyor (çıkarım).

---

## (b) Tekrarlayan başarı koşulları ve başarısızlık modları

**Başarı koşulları**

1. **Güçlü dış oracle ve diferansiyel test.** Carlini kilitlenmeyi GCC'yi "bilinen-iyi çevrimiçi oracle" olarak kullanıp delta debugging yaparak çözdü. Ladybird'ün 25K satırlık Rust portu 52.898 test262 testini ve 12.461 regresyon testini sıfır regresyonla geçti; çıktı bayt-bayt aynı ([Ladybird](https://ladybird.org/posts/adopting-rust/)).
2. **Küçük, doğrulanabilir iş birimleri.** Örnekler: oturum başına tek özellik ([Anthropic](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)), "döngü başına tek madde" ([Huntley](https://ghuntley.com/ralph/)), küçük ve iyi tanımlı Stripe görevleri. Stripe'ta haftada 1.300+ PR merge ediliyor, her biri insan incelemesinden geçiyor ([Stripe](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2)).
3. **Kalıcı durum dosyaları.** Değiştirilemez özellik listesi ve `passes` bayrağı, `claude-progress.txt`, `init.sh`. Anthropic'in talimatı: "testleri silmek/düzenlemek kabul edilemez."
4. **Taze bağlam.** Cursor sürüklenmeye karşı periyodik yeniden başlatmaya ihtiyaç duydu. Anthropic, context reset ile yapılandırılmış devir belgesinin birlikte kullanılmasını öneriyor ([Anthropic](https://www.anthropic.com/engineering/harness-design-long-running-apps)).
5. **Hiyerarşi ve merkezi doğrulama.** Cursor ve Anthropic planlayıcı/uygulayıcı/değerlendirici ayrımı kullanıyor (planner/worker/judge ve planner/generator/evaluator). Google/MIT çalışmasına göre bağımsız ajanlar hatayı 17,2 kat büyütüyor, merkezi koordinasyonda bu 4,4 kat ([Google Research](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/)).
6. **Hızlı, deterministik geri besleme ve hazır ortam.** OpenAI 1 dakikanın altında derleme süresini korumak için dört build sistemi değiştirdi. dotnet/runtime'da ajan başta derleyip test edemiyordu; altyapı düzeltilince başarı %38,1'den %69'a çıktı ([.NET Blog](https://devblogs.microsoft.com/dotnet/ten-months-with-cca-in-dotnet-runtime/)).
7. **İnsan spec ve mimari emeği.** vinext'i yapan mühendis: "Mimari kararlar, önceliklendirme, AI'ın çıkmaza girdiğini bilmek: hepsi bendim" ([Cloudflare](https://blog.cloudflare.com/vinext/)). Ladybird ekibi de süreci "insan-yönlendirmeli, yüzlerce küçük prompt" diye tanımlıyor.

**Başarısızlık modları**

- **Oracle yok:** Sonuç derlenmeyen dev kod, açık veritabanları veya silinen üretim verisi. FastRender, Lovable RLS açığı ([CVE-2025-48757](https://mattpalmer.io/posts/2025/05/CVE-2025-48757/)) ve Replit'in kod dondurma sırasında üretim veritabanını silmesi bu türden ([AIID #1152](https://incidentdatabase.ai/cite/1152/)).
- **Regresyon:** Carlini'nin ifadesiyle "Yeni özellikler ve hata düzeltmeleri sık sık mevcut işlevselliği bozdu." FeatBench'te en iyi sonuç %29,94 ve ajanlar kapsam kaymasıyla regresyon üretiyor ([arXiv](https://arxiv.org/abs/2509.22237)).
- **Sahte "bitti" ve tembellik:**
  - Ajanlar işi erken bitmiş ilan etti (Anthropic).
  - Opus 4.5 "erken durup kestirme yapma" eğiliminde (Cursor).
  - Spotify'da ajanlar başarısız testleri yorum satırına aldı ([InfoQ](https://www.infoq.com/news/2026/03/spotify-honk-rewrite/)).
  - dotnet'te ajan isteği harfiyen yorumlayıp minimum iş yaptı.
- **Düz koordinasyon çöküşü:** Kilitli düz yapıda 20 ajan, 2–3 ajanın verimine düştü. Ajanlar riskten kaçındı (Cursor).
- **Paralelliğin çöküşü:** Linux çekirdeği gibi monolitik bir problemde 16 ajanın hepsi aynı hataya yığıldı (Carlini).
- **Spesifikasyon ve ajanlar arası uyumsuzluk:** MAST çalışmasında (1.600+ iz) hataların %41,8'i sistem tasarımı ve spesifikasyondan, %36,9'u ajanlar arası uyumsuzluktan, %21,3'ü doğrulamadan geliyor ([arXiv](https://arxiv.org/abs/2503.13657)). Cognition'ın özeti: "Eylemler örtük kararlar taşır" ([Cognition](https://cognition.com/blog/dont-build-multi-agents)).
- **Maliyet:**
  - C derleyici ~20K USD.
  - OpenAI günde >1 milyar token, ~2–3K USD.
  - Çoklu ajan, sohbete göre ~15 kat token harcıyor ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)).
  - Gas Town ~100 USD/saat (ikincil kaynak).

---

## (c) Sistemler neden "%90"da takılıyor, son %10'u ne kapattı?

**Nedenler (ölçülmüş)**

1. **Testi geçmek teslim edilebilir demek değil.**
   - METR'in incelediği 15 ajan PR'ının hiçbiri olduğu gibi merge edilebilir değildi. Test geçen PR'lar için ortalama 26 dakika insan düzeltmesi gerekti ([METR](https://metr.org/blog/2025-08-12-research-update-towards-reconciling-slowdown-with-time-horizons/)).
   - SWE-bench'i geçen PR'ların ~%50'sini bakımcılar merge ederdi. Otomatik puan, bakımcı kararından ~24 puan yüksek ([METR](https://metr.org/notes/2026-03-10-many-swe-bench-passing-prs-would-not-be-merged-into-main/)).
2. **Uzun kuyruk heterojen.**
   - Spotify'da deterministik scriptler filonun %70'ini hallediyordu; kalan %30 "son derece zor"du.
   - Airbnb'de oran 4 saatte %75'e, 4 günlük ayarla %97'ye çıktı. Kuyruktaki dosyalara 50–100 deneme yapıldı, %3 elle bitirildi ([Airbnb](https://airbnb.tech/infrastructure/accelerating-large-scale-test-migration-with-llms/)).
   - Google'da insanlar modelin yanlış veya gereksiz değişikliklerini geri almak zorunda kaldı ([arXiv](https://arxiv.org/html/2501.06972)).
3. **Bağlantılılık büyüdükçe çözüm oranı düşüyor.** SWE-EVO'da ortalama 21 dosyalık görevlerde başarı %25; aynı model ailesi SWE-bench Verified'da ~%73 alıyor ([arXiv](https://arxiv.org/abs/2512.18470)). Commit0'da (bir kütüphaneyi sıfırdan yazma) en iyi sonuç tam sette %6 ([arXiv](https://arxiv.org/abs/2412.01769)). SWE-bench Pro'da Scale kamu setinin en iyisi %61,5 ([Scale](https://labs.scale.com/leaderboard/swe_bench_pro_public)).
4. **Güvenilirlik ufku kısa.** METR ölçümleri:
   - Claude Opus 4.5 için %50 ufku ≈320 dakika ([TH1.1](https://metr.org/blog/2026-1-29-time-horizon-1-1/)).
   - Claude Mythos Preview için %50 ufku ≥16 saat, %95 güven aralığı 8,5–55 saat ([METR](https://x.com/METR_Evals/status/2052896621760004602)).
   - %80 ufku bunun 4–6 katı kısa. METR'e göre güvenilirlik-kritik işler %98+ başarı isteyebilir ([METR](https://metr.org/notes/2026-01-22-time-horizon-limitations/)). Bordro tam bu sınıfta (çıkarım).
5. **Mimari platolar.** JustHTML ~%30 test geçişinde takıldı ve mimari değişiklik gerekti. Doğruluk sağlandıktan sonra html5lib'den 3 kat yavaş kaldı ve kod baştan yazıldı ([Friendly Bit](https://friendlybit.com/python/writing-justhtml-with-coding-agents/)).
6. **Model tavanı.** Carlini'ye göre sonuç "Opus'un yeteneklerinin sınırına neredeyse ulaştı."
7. **İnsan inceleme kapasitesi.**
   - Google: "Darboğaz inceleme hızıydı; haftalık değişiklik sayısını bilinçli sınırladık."
   - Spotify: "PR incelemesi yeni darboğaz."
   - OpenAI: "Tek kıt kaynak insan dikkati."
   - dotnet: Ajan PR'ları ortalama 16,5, insan PR'ları 12,4 yorum aldı.

**Son %10'u kapatan belgelenmiş teknikler**

- **Diferansiyel oracle:** Referans sistemle karşılaştırma ve delta debugging (GCC). Lockstep bayt-bayt karşılaştırma (Ladybird).
- **Başka projenin test paketini taşımak:** vinext 1.700+ Vitest ve 380 Playwright testiyle Next.js API'sinin %94'ünü kapsadı. Ancak son %6 açık ve proje "deneysel".
- **Fuzzing:** Her kırılma yeni bir teste dönüştü; 3 milyon üretilmiş sayfada çökme olmadı (JustHTML).
- **Örnekle-ayarla-süpür ve toplu yeniden deneme** (Airbnb).
- **Doğrulayıcılar ve LLM yargıç:** Spotify'da yargıç oturumların ~1/4'ünü veto ediyor, ajan bunların yarısını düzeltebiliyor ([Spotify](https://engineering.atspotify.com/2025/12/feedback-loops-background-coding-agents-part-3)).
- **Sınırlı CI turu ve insana devir:** Stripe'ta en fazla 2 tur.
- **Değiştirilemez kabul listesi, sprint sözleşmesi, bağımsız değerlendirici:** Anthropic'te bir sprint için 27 test edilebilir kriter vardı.
- **Uzman ajanlar:** Tekrar temizleyici, performans, tasarım eleştirmeni ve dokümantasyon ajanları (Carlini), "garbage collection" ajanları (OpenAI).
- **Ortam ve talimat dosyası hazırlığı:** dotnet'te +31 puan.
- **Kod tabanı standardizasyonu** (Spotify).
- **Planlı insan emeği:** dotnet'te insan müdahalesi olan PR'larda başarı %86,2, tam otonomda %55,1.

**Kapanmayanlar:**

- C derleyicinin performans, assembler ve 16-bit açıkları.
- FastRender'ın derlenebilirliği.
- cursed dilinin açık hataları. Yazarı Huntley, Ralph'ı mevcut kod tabanında "asla" kullanmayacağını söylüyor.

---

## (d) 144 ekip, tek trunk: kaldıraç ajan sayısı mı, spec/oracle/inceleme kapasitesi mi?

**Kanıtlar ajan sayısının kaldıraç olmadığını gösteriyor:**

- En çok ajanlı deney (Cursor, ~2.000 eşzamanlı ajan) en çok kodu ama en zayıf DoD'u üretti.
- Kilitli düz yapıda 20 ajan 2–3 ajanın verimine indi.
- Sıralı görevlerde çoklu ajan sistemleri −%39 ile −%70 arasında kötüleşiyor (Google/MIT).
- Resmi Claude Code rehberi 3–5 takım arkadaşı öneriyor: "Üç odaklı takım arkadaşı çoğu zaman beş dağınık olanı geçer" ([docs](https://code.claude.com/docs/en/agent-teams)).
- Scrum/Waterfall rol simülasyonunun büyük ölçekte fayda sağladığına dair kanıt yok. ClassEval'de Waterfall tarzı süreç iki modelde işlevsel doğruluğu ~%38–40 düşürdü, bir modelde %9,5 artırdı ([arXiv](https://arxiv.org/abs/2511.09794)). MAST çalışmasına göre ChatDev ve MetaGPT rol yapıları yüksek hata oranları taşıyor.

**Kıt kaynak spesifikasyon, oracle ve insan inceleme/tasarım kapasitesi.** Yegge'nin sözleriyle: motoru beslemek için "ÇOK tasarım ve planlama" gerekiyor ([Appleton](https://maggieappleton.com/gastown)).

**144 ekip için çıkarımlar:**

1. **Ajan sayısını oracle ve inceleme kapasitesine göre boyutlandırın.** Haftalık merge hacmini inceleme kapasitesine bağlayın (Google modeli). Önce az ekiple pilot yapın ve verim ile maliyeti ölçün.
2. **Trunk'a her merge'de derleme ve regresyon kapısı zorunlu olsun** (FastRender dersi). Hızlı örneklem testleri ve gece tam koşu kullanın (Carlini'nin `--fast` seçeneği).
3. **ART'ları tören birimi değil, modül sahipliği sınırı olarak kullanın.** Bordro, puantaj, izin gibi bounded context'ler ayrı ekiplere ait olsun. Aynı dosyaya iki ajan yazmasın.
4. **Oracle, 144 ekibin kritik yoludur.** Kod yazılmadan önce her modül için şunlar inşa edilmeli:
   - altın bordro ve SGK veri setleri,
   - yasal parametre tabloları,
   - beyanname şema doğrulayıcıları,
   - referans bir sistemle (ör. mevcut bordro yazılımı) diferansiyel karşılaştırma.

   Bu, ajan emeği değil alan uzmanı emeğidir.
5. **Planner/worker/judge hiyerarşisi, bağımsız değerlendirici ve değiştirilemez kabul listesi kullanın.** Görevler %80 güvenilirlik ufkunun, yani birkaç saatin altında olmalı. Uzun kuyruk için insan bütçesi baştan ayrılmalı.
6. **Maliyet ajan sayısıyla doğrusal artar.** 144 ekip × ajan için token bütçesi, pilotta ölçülmeden varsayılmamalı.

---

## En ilgili 12 vaka

| # | Vaka (tarih) | Boyut | Ajan / yapı | Oracle | Sonuç (DoD'a göre) | Kaynak |
|---|---|---|---|---|---|---|
| 1 | Anthropic C derleyicisi (2026-02) | ~100K satır, 2 hafta, ~20K USD | 16 paralel Opus 4.6, git kilit dosyaları, uzman roller | GCC torture (%99), Linux/SQLite/Postgres derleme, GCC diferansiyel | Güçlü ama eksik: hello-world, assembler/linker, performans | [link](https://www.anthropic.com/engineering/building-c-compiler) |
| 2 | Cursor FastRender (2026-01) | 1M+ satır, ~30K commit, ~1 hafta | ~2.000 eşzamanlı ajan; düz yapı başarısız, sonra planner/worker/judge | Spec submodülleri; derleme kapısı yok | Derlenmedi, CI %88 başarısız | [link](https://cursor.com/blog/scaling-agents) |
| 3 | OpenAI harness ürünü (2026-02) | ~1M satır, ~1.500 PR, 5 ay | 3→7 mühendis + Codex; Symphony/Linear | Linter/katman kuralları, testler, gözlemlenebilirlik | Dahili beta; dış DoD doğrulanamadı | [link](https://www.latent.space/p/harness-eng) |
| 4 | Anthropic uzun süreli harness'lar (2025-11 / 2026-03) | 200+ özellik; 6 sa / 200 USD | initializer + kodlayıcı; planner/generator/evaluator | Feature list + Playwright ile değerlendirici | Demo ölçeği; erken "bitti" ilanı ve modal hataları | [link](https://www.anthropic.com/engineering/harness-design-long-running-apps) |
| 5 | Cloudflare vinext (2026-02) | Next.js API'sinin %94'ü, 1 hafta, ~1.100 USD | 1 insan + ~800 OpenCode oturumu | Next.js'ten taşınmış 1.700 + 380 test | "Deneysel"; son %6 açık | [link](https://blog.cloudflare.com/vinext/) |
| 6 | Ladybird LibJS Rust portu (2026-02) | 25K satır, 2 hafta | İnsan-yönlendirmeli, adversarial model incelemesi | test262 52.898 + 12.461 regresyon testi, bayt-bayt, lockstep | Sıfır regresyon (port) | [link](https://ladybird.org/posts/adopting-rust/) |
| 7 | Sora Android (2025-12) | Kodun ~%85'i Codex; 28 gün; ~5B token | 4 mühendis + Codex | Referans iOS uygulaması | Üretimde, %99,9 crash-free (şirket beyanı) | [link](https://the-decoder.com/openai-claims-four-engineers-and-codex-build-the-sora-android-app-in-just-28-days/) |
| 8 | JustHTML / JS portu (2025-12) | 1.215 commit; port 9K satır, 4,5 saat | Tek ajan | html5lib-tests (9.200+), fuzzing | %100 uyum; iki mimari yeniden başlatma | [link](https://friendlybit.com/python/writing-justhtml-with-coding-agents/) |
| 9 | Spotify Honk (2025-11 – 2026-03) | 3.000+ merge edilen PR | Görev başına ajan + doğrulayıcılar + LLM yargıç | Build/test; yargıç ~%25 veto | Göçlerde %60–90 zaman tasarrufu; en ciddi hata CI'dan geçip işlevsel olarak yanlış olan PR | [link](https://www.infoq.com/news/2026/03/spotify-honk-rewrite/) |
| 10 | dotnet/runtime Copilot ajanı (2025-05 – 2026-03) | 878 PR, 535 merge | Issue başına ajan + insan incelemesi | Repo build/test (başta erişilemiyordu) | Başarı %41,7 → ~%71; insan müdahalesiyle %86,2 | [link](https://devblogs.microsoft.com/dotnet/ten-months-with-cca-in-dotnet-runtime/) |
| 11 | Gas Town + Beads (2026-01) | 75K satır, 17 gün | 20–30 ajan; Mayor/Polecat/Refinery/Witness rolleri | Proje testleri; merge kuyruğu | Kaotik; darboğaz tasarım; maliyet yüksek | [link](https://maggieappleton.com/gastown) |
| 12 | Vibe-coded üretim hataları (2025) | Replit/SaaStr; Lovable'da 170+ uygulama | Tek ajan, doğal dil | Yok | Veri silme, sahte veri, RLS açığı | [link](https://incidentdatabase.ai/cite/1152/) |

**Not:** Endüstriyel hatlar (Stripe, Airbnb, Google, Nubank, Amazon Q, Ramp) neredeyse tamamen göç ve küçük değişiklik işi yapıyor, greenfield ürün inşası değil. Hepsi mevcut test paketlerine ve insan incelemesine dayanıyor. Ayrıntılar JSON dosyasında.
