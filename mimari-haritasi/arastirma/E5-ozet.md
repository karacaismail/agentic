# E5: Codex araştırmasıyla karşılaştırma (özet)

Tarih: 27.09.2026. Ayrıntı ve bütün kaynaklar `E5-codex-arastirma.json` dosyasında. Codex dizinine hiçbir şey yazılmadı.

Codex'in 7 raporu, araştırma notları ve `dunya-vakalari/` paketi bizim A0–D2 dosyalarımızla karşılaştırıldı. Her kalem birincil kaynakla kontrol edildi (`gh api`, resmî doküman, şirket blogu, arXiv, NVD):

- **74 kalem eklendi:** 70'i "doğrulandı", 4'ü "kısmen".
- **14 çelişki** çözüldü.
- **67 kalem** gerekçesiyle eklenmedi.

`agentic-sistem/arastirma`, `research_notes`'un birebir kopyası; bir kez sayıldı.

## 1. Plane tabanlı sistem (A0–A3): 11 ekleme, 6 çelişki

**Eklenenler:** Plane'de kapalı webhook'un olayları kaybolur; iş listesinde `state` filtresi, PATCH'te ETag yok. Temporal'da ebeveyn başına en fazla 1.000 child. Scrum Guide: hesap verebilirlik tek kişi olan PO'da. Spotify Honk hakemi oturumların dörtte birini veto ediyor, hakemin kendisi ölçülmüyor. GitHub lockdown, Playwright origin filtresi ve Filesystem Roots yetki sınırı değil.

**Çelişkiler:**
- **Webhook tekrar denemesi ve `event_id`: biz haklıyız.** CE v1.4.2 kodunda 5xx tekrar denenmiyor, `event_id` yok. Codex dokümandaki v2'yi aktarıyor.
- **"1 GB/ajan": ikimiz de kısmen haklıyız.** Resmî değer bir taban, tavan değil.
- **In Progress tetiği: Codex haklı.** Pilotta REVIEW ve WAITING_DECISION da `started` grubunda (`bootstrap_plane.py:29`). A2'deki kural state UUID'siyle düzeltilmeli.
- **Filesystem MCP: biz haklıyız.** CVE-2025-53109 var.

## 2. Tıkanıklık ve toparlanma (A2, D1, C6): 7 ekleme

- **Temporal Python:** Workflow kodundaki sıradan hata Workflow Task'ı süresiz tekrarlatıyor. Activity retry'ı varsayılan olarak sınırsız.
- **n8n (D1'de hiç yoktu):** Global timeout varsayılan olarak kapalı, ilerleme kaydı tutulmuyor. Poll tetikleyicileri kararsız, aynı poll iki kez çalışabiliyor.
- **Kestra:** Flow düzeyinde timeout yok; yerine MAX_DURATION SLA kullanılıyor.
- **Exit 137:** Yalnız SIGKILL demek. OOM'un kanıtı `memory.events:oom_kill`.
- **Cursor, Şubat 2026:** Darboğazlar fazla rollü yürütücü, en yavaş işçi ve merkezi entegratör. RAM sınırlanınca sıcak nokta diske kaydı.
- **Cursor, Temmuz 2026:** Aynı görevde yeni harness %73–85, eski harness %11–77 geçti. Eskisi 70.000'den fazla çatışma üretti.

## 3. Projeler ve vakalar (B1–B3): 9 ekleme, 1 çelişki

**Eklenenler:**
- **Ramp Sheets:** İlk haftada 40 hata yakalandı; uyarı gürültüsü de oluştu.
- **Spotify, Haziran 2026:** PR sayısı %76 arttı, 2,5 milyon otomatik PR birleşti.
- **Open SWE:** Self-host lisans anahtarı istiyor; varsayılan `noop` auth API'yi açık bırakıyor.
- **Tekil issue'lar:** OpenHands #2482, Codex #18881, Symphony #64, Vibe Kanban #1718.
- **UTBoost:** 345 hatalı patch "geçti" sayılmıştı.
- **SWE-bench Verified denetimi (kısmen):** 138 görevin %59,4'ü kusurlu; birincil sayfa 403 döndü.

**Çelişki:** İlk pilot adayı Codex'te OpenHands, bizde Symphony. İkimiz de kısmen haklıyız. Codex, OpenHands'teki CVE-2026-33718'i (CVSS 7,6) hesaba katmıyor. Ölçülü bir pilotla karar verilmeli.

## 4. Çok katmanlı fabrika (C0–C6): 8 ekleme, 1 çelişki

**Eklenenler:**
- **Paperclip (88,5k yıldız):** Serbest metinle "blocked" yazılamıyor; bekleyen işin yönlendirilebilir bir sahibi olmak zorunda.
- **Warren:** "Run başarılı" ile "birleşti" ayrı durumlar.
- **Overstory:** Depo arşivlendi.
- **Uber:** PR'ların %70'inden fazlası ajan işi; oturum maliyeti %52 düştü.
- **Shopify:** Oturum harness'ten ayrı tutuluyor; birleşen her 8 PR'dan 1'i ajanla ortak yazılmış.
- **Atlassian:** Closer, değişikliğin dağıtılan build'de olduğunu doğruluyor.
- **Kueue:** Adil kabul (fair sharing) mekanizması.
- **Frappe:** Bank Entry ödeme demek değil, ters göç yok, `set_value` doğrulamaları atlıyor.

**Çelişki:** C1'de Paperclip ve Warren yok, Codex'te GitLab Duo yok. Paperclip ve Warren R1–R12 ile puanlanmalı. Codex'in HRMS analizinde Türkiye mevzuatı yok, bu yüzden C5 ile sayısal çelişki çıkmadı.

## 5. Evrilebilir fabrika (C3, A3): 5 ekleme, 2 çelişki

**Eklenenler:** SRE kanarya kuralları, ACL ve Strangler Fig'in bedeli, gölge karşılaştırmada yan etki yasağı.

**Çelişkiler:**
- **C3 K6 bitiş ölçütü: Codex haklı.** Mutlak SLO eşiği ve en az bir tam iş birimi süresi gerekiyor.
- **Tatbikatta dış etki: ikimiz de kısmen haklıyız.** Dış etkiyi yalnız tek yürütücü üretmeli.

Codex'in "motor değiştirmenin 5 yolu" önerisi bulgu değil tasarım olduğu için eklenmedi.

## 6. İhtiyaç tamamlama (birebir karşılığımız yok): 15 ekleme, 2 çelişki

**Eklenenler:** NIST AI RMF, Vaccaro 2024 (insan+AI en iyi tekil taraftan kötü, g=−0,23), RFC 9110/8693/7009, Google SRE (katmanlı tekrar 64 kat yük), W3C PROV-DM, NIST SP 800-34, MT-Bench, τ-bench, MemoryAgentBench.

**Çelişkiler:**
- **METR:** B2 ve A3 2025'teki %19 yavaşlamayı 2026 güncellemesi olmadan kullanıyor. Güncellemeye göre hızlanma muhtemel, ama kanıt zayıf.
- **LLM yargıç kendini kayırması:** A3'e Panickssery 2024 atfı eklenmeli.

## 7. Gerçek dünya hataları (D1, D2, B2) ve `dunya-vakalari`: 19 ekleme

Codex'in 36 vakasının dayandığı 61 kaynağın yalnız 8'i bizde vardı.

**Eklenenler:**
- **OpenHands:** Döngü algılaması uzun süreci öldürüyordu. Sert kesilmede callback gitmiyor. Benchmark'ta OOM oldu.
- **Factory:** 3 açık issue.
- **Devin:** Testte UI yerine JavaScript ile kestirme yapıyor.
- **Ruflo:** Worktree fan-out'u ortak kotayı tüketiyor.
- **Who&When:** Otomatik teşhis sorumlu ajanı %53,5, hatanın başladığı adımı %14,2 doğrulukla buluyor.
- **Kestra #16198:** SLA'nın öldürdüğü task, worker JVM'ini çökme döngüsüne sokuyor.
- **Trigger.dev'in iki olay raporu:** etcd quorum kaybı; ClickHouse belleği ~180 GiB.
- **Windmill:** 4 GiB `rlimit_as` sınırı Claude CLI'yi çökertiyor.

**Kabul deneyleri:** 52 deneyin hepsi çalıştırılmamış. Her biri vakası, yerel bulgusu ve bizdeki karşılığıyla ayrı listelendi. Bizde böyle bir deney kataloğu yok.

**Yerel bulgular (K01–K18) ve A0:** 7'si uyumlu, 6'sı kısmen uyumlu, 5'i A0'da yok; çelişen yok. A0'da olmayanlar E6'da doğrulandı. MAST'ta Codex'in 1.642 iz sayısı bizim "1.600+" ifademizle uyumlu.

## Codex'in bizim çalışmamıza itirazları

`Claude bulgularıyla kapsam tamamlama` klasörü başta boştu, 15:40'ta doldu.

- **CA-14 doğrulandı:** D1'de #1894 dört kez geçiyor. "100+ kayıt" benzersiz olay sayısı değil.
- **CA-10 ve CA-11 kısmen haklı:** C6'daki insan sayıları senaryo; olay defteri motorun iç durumunu yeniden yazmamalı.

## Düzeltme önerileri

- **A2:** Tetik state UUID'sine bağlanmalı.
- **B2 ve A3:** METR 2026 notu eklenmeli.
- **C3 K6:** Mutlak SLO eşiği eklenmeli.
- **C1:** Paperclip ve Warren puanlanmalı.
- **D1:** Kayıtlar kanonik URL ile tekilleştirilmeli.
