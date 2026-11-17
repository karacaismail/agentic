# A3 — Havuzlar, pazar, Kaizen/OODA ve olgunluk: özet

Tarih: 27 Eylül 2026. Ayrıntılar ve kaynak kimlikleri `A3-havuzlar-kaizen-olgunluk.json` dosyasında (A3-Kxx dış kaynak, A3-Yxx yerel risk haritası, EV-xxx yerel olay).

## Kısa cevaplar

1. **Ne eklenmeli?** Az sayıda ve ölçülmüş bileşen eklenmeli: kısa talimat dosyaları, kurum içi odaklı skill'ler, birkaç tek sorumluluklu alt ajan (özellikle bağımsız doğrulayıcı) ve rol başına en az sayıda MCP. Rol oyunu yapan SAFe ajanları, kamusal pazardan gelen paketler ve LLM'e ürettirilmiş uzun bağlam dosyaları eklenmemeli.
2. **Pazardan ihtiyaç halinde almak doğru mu?** Hayır. Havuz fikri doğru, ama havuz kurumun kendi iç kataloğu olmalı. Pazarlar yalnız keşif ve aday kaynağıdır. Bir paket kataloğa ancak kabul, sabitleme, yalıtım, eval ve sürekli izleme adımlarından geçerek girer.
3. **Kaizen/OODA nasıl eklenir?** Üç iç içe döngüyle: görev içi OODA (dış ve deterministik sinyallerle), ekip Kaizen'i (ajan olay kaydı → taksonomi → iyileştirme → eval kapısı) ve PI düzeyinde PDCA (Inspect & Adapt'te terfi, emeklilik ve otonomi kararları).
4. **MVP'den olgunluğa:** S0 temel hazırlık → S1 denetimli ajan (pilot) → S2 iç katalog (3-4 ekip) → S3 ART ölçeği (12+ ekip) → S4 kontrollü öğrenme. "Karanlık fabrika" hedeflenmez.

## 1. Talimat dosyaları (AGENTS.md, CLAUDE.md, iç içe dosyalar, ADR)

**Kanıt**
- AGENTS.md, Linux Foundation altındaki Agentic AI Foundation'da açık standart (9 Aralık 2025) ve 60 binden fazla projede kullanılıyor. İç içe dosyalarda en yakın dosya geçerli olur. (A3-K07, A3-K08)
- ETH Zürih çalışması (arXiv 2602.11988): Bağlam dosyaları başarıyı genelde artırmıyor, maliyeti %20'nin üzerinde artırıyor. LLM üretimi dosyalar başarıyı %0,5–2 düşürdü. Depo genel bakışları işe yaramıyor. Yazarların önerisi: yalnız standart dışı gereksinimler yazılsın. Karşı bulgu: AGENTS.md çalışma süresini %28,6, çıktı token'ını %16,6 azaltabiliyor (arXiv 2601.20404). Sonuç: etki ölçülmeden varsayılamaz.
- Claude Code dokümanı: CLAUDE.md zorlanan yapılandırma değil, bağlamdır. Dosya başına 200 satır altı hedeflenir. Engelleme hook ya da izin ayarıyla yapılır. (A3-K09)
- OpenAI harness engineering: Yaklaşık 100 satırlık AGENTS.md bir "içindekiler tablosu" olarak çalışıyor. Asıl bilgi docs/ dizininde duruyor ve linter, CI ve doc-gardening ajanıyla güncel tutuluyor. (A3-K06)
- Kural güncellemesi hatalara karşı işe yarıyor: artefakt uyumu %49'dan %72'ye çıktı (A3-K05). Talimat dosyaları saldırı yüzeyi de: görünmez Unicode ile arka kapı konabiliyor, depo yapılandırması üzerinden RCE yaşandı (RK-095, EV-183, EV-267).

**Öneri**
- Kısa bir kök AGENTS.md (yaklaşık 100, en çok 200 satır) tek doğruluk kaynağı olsun; CLAUDE.md onu `@AGENTS.md` ile içe aktarsın.
- Alt dizin dosyası yalnız farklı derleme/test komutu varsa eklensin. Dosya türüne özgü kurallar paths alanlı kural dosyalarına gitsin.
- SAFe katmanları kurallara şöyle eşlensin: kurum için yönetilen ayar ve talimat, ART için sürümlü ortak çekirdek paket, ekip için depo dosyası ve ekip uzantısı.
- docs/adr (Nygard biçimi) kurulsun. ADR'yi ajan önerebilir, kabul insanda kalır.
- Kural öncelik sırası: deterministik kontrol > izin veya hook > skill > .md satırı. Talimat değişikliği kod gibi ele alınsın: PR, CODEOWNERS, Unicode kontrolü, boyut bütçesi, eval.

**Kaçınılacaklar:** /init çıktısını incelemeden commit etmek; dizin ağacı ve genel bakış yazmak; persona paragrafları (A3-K27); güvenlik yasaklarını yalnız .md'ye bırakmak (Replit olayı); çelişen katmanlar; ajanın kendi yapılandırmasını değiştirebilmesi.

## 2. Skills (SKILL.md)

**Kanıt**
- Kademeli yükleme şöyle işler: açılışta yalnız ad ve açıklama (yaklaşık 100 token), gerektiğinde gövde (5 bin token altı), sonra ek dosyalar. Resmî depolar: anthropics/skills, openai/skills, agentskills/agentskills. (A3-K11, K12, K22)
- Skill sayısı arttıkça seçim bozuluyor. 20 skill'e kadar doğruluk %90'ın üstünde, yaklaşık 30'dan sonra düşüyor, 200'de yaklaşık %20 (GPT-4o ölçümü). Hiyerarşik yönlendirme düşüşü telafi ediyor. 202 skill'de başarı %21'e kadar düştü; asıl neden "gölgeleme", yani anlamca benzer skill'lerin karışması. (A3-K14, K15)
- SkillsBench: Özenle hazırlanmış skill'ler başarıyı +16,6 puan artırdı; en çok üç modüllü odaklı skill'ler daha iyi. v1'de modelin kendi ürettiği skill'ler ortalamada fayda sağlamadı. (A3-K16)
- Güvenlik:
  - 31 bin skill'in %26,1'inde açık var; betik içerenler 2,12 kat daha riskli (A3-K17).
  - Snyk: %36,8 kusurlu, 76 doğrulanmış kötü amaçlı yük (A3-K19).
  - ClawHavoc: ClawHub'daki 2.857 skill'den 341'i zararlıydı ve AMOS hırsız yazılımı kurduruyordu; yayıncı için tek koşul bir haftalık GitHub hesabıydı (A3-K20, EV-232).

**Eklenecek skill türleri** (hepsi kurum içi): depo prosedürleri (migration, API sözleşmesi, feature flag), test ve doğrulama stratejisi, şemalı devir paketi ve açıklama–fark tutarlılığı, güvenlik kontrol listesi, ADR şablonu, DoR/DoD denetimi, olaydan eval vakası üretme. Yan etkili işler (deploy, mesaj) yalnız insan çağrısıyla çalışsın.

**Eklenmeyecekler:** kamusal pazardan doğrudan skill; incelenmemiş betikli skill; eval'siz, ajan üretimi skill; birbirine benzeyen skill'ler; modelin zaten bildiği genel bilgi.

## 3. Alt ajanlar ve roller

- **Fayda sağladığı yer:** bağlam yalıtımı (keşif, log ve test özetleme), araç kısıtı ve bağımsız doğrulama. (A3-K23, K10)
- **Maliyet:** Çoklu ajan yaklaşık 15 kat token harcıyor. Anthropic, kodlama işlerinin araştırmaya göre daha az paralelleştirilebildiğini belirtiyor (A3-K24). Cognition'a göre paralel alt ajanlar kırılgan (A3-K25). MAST 14 başarısızlık kipi belirledi (A3-K26).
- **Rol oyunu:** Persona başarımı artırmıyor (A3-K27). ChatDev'de rollerin katkısı işlevsel görev tanımlarından geliyor ve eski bir modelle ölçüldü. SAFe uyarlaması CogniSim yalnız simülasyon. Üretimde "Scrum Master ajanı" ya da "RTE ajanı"nın insan rolüne göre fayda sağladığını gösteren kontrollü bir çalışma bulamadım.
- **Üretici–doğrulayıcı ayrımı güçlü destekleniyor:** Model dış geri bildirim olmadan kendini düzeltemiyor (A3-K33). Ayrı ve kuşkucu bir değerlendirici daha uygulanabilir (A3-K32). Ajan 54 döngünün her birinde iyileşme iddia etti, ama %56'sında ölçülen değişim sıfır ya da negatifti (A3-K34).
- **Öneri:** Tek ana ajan + keşif + bağımsız değerlendirici (farklı model ailesi; deterministik kapılar önce) + gerekirse güvenlik inceleyici ve planlayıcı. İnsan SAFe rolleri korunsun. Scrum Master ajan retrosunu, RTE ise I&A'daki ajan olay örüntülerini kolaylaştırsın; katalog sahibi System Team / platform ekibi olsun.

## 4. MCP

**Kayıtlar**
- Resmî MCP Registry hâlâ önizlemede. Yalnız metaveri ve ad alanı doğrulaması sunuyor; güvenlik taramasını paket kayıtlarına ve alt kayıtlara bırakıyor. Özel sunucular için kurumların kendi kayıtlarını kurmasını öneriyor. (A3-K35)
- mcpmarket.com üçüncü taraf bir dizin: 50.866 sunucu listeliyor, inceleme süreci açıklamıyor (A3-K37).
- Docker Catalog imzalı, SBOM'lu ve konteyner yalıtımlı; özel katalog desteği var (A3-K38).
- Smithery'de 3.000'den fazla sunucuyu etkileyen yol geçişi açığı bulundu (A3-K44).

**Olaylar**
- postmark-mcp: 15 temiz sürümden sonra 1.0.16'da tüm e-postaları gizlice BCC'ledi (A3-K39).
- mcp-remote CVE-2025-6514, CVSS 9,6 (A3-K40).
- Araç zehirlenmesi ve rug-pull (A3-K41); MCPoison (EV-142); GitHub MCP zehirli akışı (EV-100).
- Resmî filesystem ve git referans sunucularında açıklar; bu sunucular zaten "üretime hazır değil" (A3-K46).
- Kimlik doğrulama: Knostic'in doğruladığı 119 sunucunun tümü kimlik doğrulamasızdı; 2026 ölçümünde sunucuların %91,8'inde OAuth yoktu (A3-K42, K43).

**CLI mi MCP mi?** Satıcı kıyasında CLI 9 ile 32 kat daha az token harcadı ve %100 başarılı oldu; MCP %72'de kaldı. MCP ise kullanıcı başına OAuth ve denetim gereken işlerde üstün (A3-K50, ikincil). Anthropic tool search ile token'ı %85 azalttı ve doğruluğu artırdı (A3-K48). Karar kuralı: CLI'si olan işlerde CLI + skill; iç sistemler ve çok kiracılı yetki gereken işlerde ağ geçidi arkasında MCP.

**Kurum modeli**
- Özel alt kayıt kurulsun.
- Sürüm, içerik ve araç tanımı özetleri sabitlensin; özet değişirse yeniden onay istensin.
- Sunucular konteynerde, ağ izin listesiyle çalışsın; kısa ömürlü ve görev kapsamlı token kullanılsın; token passthrough olmasın.
- Tüm uzak trafik bir ağ geçidinden geçsin. Ağ geçidinin kendisi de yamalanmalı (yerel harita ToolHive açıklarını kaydetmiş).
- Oturum bileşiminde Rule of Two uygulansın.
- Zorlama yönetilen ayarlarla yapılsın. Copilot'un ada göre eşleşen izin listesi dokümana göre atlatılabiliyor (A3-K52); Claude Code'da managed-mcp.json ve allowManagedMcpServersOnly var (A3-K53).

**Başlangıç sunucuları:** salt okur iş takip (pilot kiracıda), SCM (tercihen CLI), salt okur gözlemlenebilirlik ve bilgi tabanı, yalnız değerlendiricide sandbox içinde Playwright.

**Eklenmeyecekler:** sabitlenmemiş npx/uvx paketleri, üçüncü taraf barındırma pazarları, referans sunucular, genel kabuk MCP'leri, otonom ajanda e-posta veya mesaj gönderimi, depo dosyasıyla eklenen MCP'ler.

## 5. Pazar ve havuz değerlendirmesi

Gerekçeler:
- Pazarlar güvenlik garantisi vermiyor.
- Ölçülen zararlı ve açıklı skill oranları yüksek.
- Güven zamanla değişiyor (postmark-mcp, rug-pull).
- Barındırılan pazarlar tek hata noktası oluşturuyor.
- Serbest ekleme, skill gölgelemesi ve token maliyeti yüzünden başarımı da düşürüyor.
- Tarayıcılar her şeyi yakalamıyor (%82–95 duyarlılık).

Önerilen model 10 adım (ayrıntı JSON'da): tek iç katalog → kabul hattı → sabitleme → yalıtım → eval kapısı → rol profilleri → istemci zorlaması → sürekli tarama ve emeklilik → SAFe talep akışı (System Team, enabler kapasitesi) → keşif kum havuzu.

## 6. Kaizen / OODA / PDCA

- **İç OODA:** Gözlem test, CI ve çalışan uygulamadan gelir, ajanın anlatısından değil. Yönelim kısa harita ve skill'lerle yapılır. Karar sprint sözleşmesine dayanır. Eylemi bağımsız değerlendirici denetler.
- **Ekip Kaizen'i:** ajan olay kaydı → taksonomi (MAST + kuruma özgü 8 sınıf) → önce deterministik iyileştirme → olaydan türetilen eval vakaları → eşleştirilmiş, k tekrarlı eval kapısı → bir sprint gözlem → standartlaştır ya da geri al.
- **PI PDCA:** I&A'da ekipler arası örüntüler ele alınır; ortak çekirdeğe terfi ve emeklilik, işlev bazlı otonomi kararları verilir; ekiplerin görmediği gizli eval seti kullanılır.
- **Kanıt:** Kural güncellemesi uyumu artırıyor (A3-K05). ACE türü artımlı el kitapları +%10,6 kazanç sağladı (A3-K63). Model kendi ürettiği skill'lerden fayda görmedi (A3-K16). Onaysız otomatik öğrenmede zehirlenme ve çöküş riski var (RK-208, RK-209).
- **Metrikler:**
  - DORA'nın beş metriği (yeniden iş oranı dahil), ajan ve insan kaynaklı değişiklikler ayrı etiketlenerek.
  - İlk geçiş kabul oranı, PR revizyon turu.
  - İnceleme kuyruğu.
  - Mesaj–kod tutarlılığı (tutarsız PR'larda kabul %28, tutarlılarda %80).
  - İş başına token ve maliyet.
  - Eval pass@k ve pass^k.
  - Müdahale ve otonomi oranı.
  - Skill seçim doğruluğu.
  - Eşzamanlı PR çakışması.
  - Algılanan ve ölçülen verim farkı (RCT: geliştiriciler %20 hızlandığını düşündü, sonuç %19 yavaşlamaydı).
- **Kaçınılacaklar:** PR sayısını verimlilik saymak; ajanın beyanını kapı yapmak; her hatada .md'ye satır eklemek; olay kayıtlarını disiplin gerekçesine dönüştürmek.

## 7. Olgunluk modelleri ve yol haritası

**İncelenen modeller**
- DORA AI Capabilities Model: yedi yetenek, seviyesiz.
- Feng ve ark.: L1 operatör → L5 gözlemci.
- CSA L0–L5: L5 kurum için uygun görülmüyor.
- Shapiro'nun 0–5 seviyesi: ayrım "diff'i kim okuyor".
- Microsoft: Reactive → Foundation → Structured → Optimized.
- AWS AI-DLC: Inception, Construction, Operations; her adımda insan doğrulaması.
- Thoughtworks Radar 34: harness engineering, rehavet uyarısı.
- %50 zaman ufku ölçüsü.

GitLab'a ait yayımlanmış bir AI-native SDLC olgunluk modeli birincil kaynakta doğrulanamadı.

**Önerilen kurum yolu**

| Seviye | İçerik | Geçiş ölçütü |
|---|---|---|
| S0 Temel (0–6 hafta) | AI tutumu, CI/test, küçük partiler, izole ortam, kısa AGENTS.md, ADR, 20–50 görevlik eval tohumu, metrik tabanı | Taban ölçülmüş, eval otomatik koşuyor |
| S1 MVP (1 PI, pilot ekipler) | Tek ajan + keşif + değerlendirici, 3–5 iç skill, 0–2 salt okur MCP, zorunlu insan incelemesi, ajan retrosu | Değişiklik başarısızlık ve yeniden iş oranı insan tabanından kötü değil; bir Kaizen döngüsü kapanmış |
| S2 Tekrarlanabilir (3–4 ekip) | İç katalog, kabul, sabitleme, yönetilen zorlama, rol profilleri, eval kapısı, ağ geçidi pilotu | Katalog dışı kurulum teknik olarak engellenmiş |
| S3 Tanımlı (ART, 12+ ekip) | Niyet ve üstlenme kaydı, I&A'da ajan olayları, işlev bazlı otonomi (CSA L1–L3), red team, gizli eval, model sabitleme | Kararlılık en az bir PI boyunca tabandan kötü değil |
| S4 Kendini iyileştiren | Kontrollü öğrenme hattı, düşük riskli sınıflarda örneklemli denetim, maliyet optimizasyonu | Otonomi işlev bazında kanıtla verilir, kanıt bozulunca otomatik geri alınır |

Amazon'un yapay zekâ kaynaklı kesintilerden sonra kıdemli mühendis onayını zorunlu kılması (EV-246) ve DORA'nın AI ile kararlılık arasında bulduğu negatif ilişki, otonominin kanıtla ve geri alınabilir biçimde verilmesi gerektiğini gösteriyor.

## Doğrulama notları

- arXiv 2602.11988 ve SkillsBench'in özetleri sürümler arasında değişti; hangi sayının hangi sürümden alındığı JSON'da belirtildi.
- OpenAI yazısı bot korumalı olduğu için bir ayna üzerinden doğrulandı.
- ClawHavoc için Koi'nin birincil yazısı artık başka alana yönleniyor; bu nedenle ikincil kaynak kullanıldı.
- CLI–MCP karşılaştırması satıcı blogu (ikincil).
- Eşik ve süre önerileri kanıt değil tasarım önerisidir; kurum tabanıyla kalibre edilmelidir.
