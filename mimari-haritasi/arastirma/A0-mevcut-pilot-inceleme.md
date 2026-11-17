# A0 — Mevcut "yazılım fabrikası" pilotunun teknik incelemesi

İnceleme tarihi: 27 Eylül 2026. Kök dizin: `/Users/w6x/Developer/software-factory` (aşağıda `SF/`).
Yöntem: salt okuma. Dosya okuma, `git log/show/diff --stat/status`, `docker ps`, `docker inspect`, `docker logs --tail 200`, `ps`. Hiçbir dosya, servis ya da veritabanı değiştirilmedi. `.env`, `config/connections.local.json`, `state/credentials.json`, `state/provider-auth/`, `state/agent-auth.json` ve `state/owner-access.key` açılmadı. Veritabanına doğrudan sorgu atılmadı. Canlı iş sayıları, servisin kendi yazdığı salt okunur anlık görüntüden (`SF/state/public/status.json`, 27.09 06:57 UTC) ve rapor dosyalarından okundu.

Kanıt yolları `dosya:satır` biçimindedir. Sayılar ölçümdür. Yorum olan yerler **Yorum** diye işaretlidir.

---

## 0. Özet: tek paragrafta teşhis

Pilot 11 Eylül'de bir kez uçtan uca çalıştı. 1 görev yaklaşık 26 dakikada, 10 Codex çağrısıyla Plane READY'den yerel prod'a gitti. Bu koşu da iki elle yapılan kurulum onarımı içeriyordu (`SF/docs/PILOT-RESULT.md:5,24-34`). Sonraki 7 günde (12–18 Eylül) sistem 11 modülden 98 modüle (27.294 satır) ve 92 tabloya büyüdü. Kapsam 9 takımlı SAFe/ART, uzman havuzu, ECA kural motoru, Kaizen/CAPA, çoklu sağlayıcı havuzu ve adaptör doğrulamasını kapsayacak kadar genişledi. İlk gerçek ürün görevi (73 bileşenli Ant Design karşılığı UI kütüphanesi, V1-4) 456 ajan çağrısı ve 7,0 M çıktı tokenı harcadı. 73 paketin tamamı yerel teslim dalına birleşti. Ancak kök görev hiçbir zaman kabulü geçmedi: `AC-REQUEST: NOT_TESTED`. Görev 46 kez RUNNING→ERROR'a düştü, en son 7 gün boyunca kimse ilerletmediği için Kestra `LoopUntil P7D` zaman aşımıyla `KESTRA_FAILED` oldu.

Ölçülen başarı:
- Kök görev: 4. Otonom, müdahalesiz yayın: **0/4**.
- Müdahaleyle RELEASED: 1/4.

Kök nedenler:
- dayanıklı iş akışı ilkelerinin (lease, heartbeat, outbox, retry, bekleme, devam) Python + Postgres ile elle yeniden yazılması ve Kestra'nın yalnız 15 saniyelik bir yoklayıcı olarak kullanılması;
- canlı sistemin sürüm kontrolü olmadan yamalanması (60 aktivasyon manifesti, 98 modülün 87'si git dışında);
- kapsam patlaması;
- anlamsal kabul/oracle eksikliği;
- Mac uykusu;
- sağlayıcı kapasitesi darboğazı;
- bütçe sınırlarının "adaptive" modda uyarıya çevrilmesi.

---

## 1. Gerçekte kurulu mimari

### 1.1 Bileşenler (çalışan)

| Katman | Gerçek bileşen | Kanıt |
|---|---|---|
| Görev girişi | Plane CE 1.4.2 (web, space, admin, live, api, worker, beat, proxy), valkey, RabbitMQ 3.13.6, MinIO, ayrı plane-db. Adres: `127.0.0.1:8088` | `SF/compose.yaml:57-464`, `docker ps` |
| Orkestrasyon yüzeyi | Kestra 2.0.1 (binary; OCI etiketi `nightly`, digest `sha256:948dae5a…`), 6 GiB / 4 CPU limit, `127.0.0.1:8080` | `SF/README.md:72`, `SF/compose.yaml:485-494`, `docker inspect` |
| Kontrol veritabanı | Ayrı Postgres `factory` şeması, `127.0.0.1:54329`. **92 tablo**, 10+ plpgsql fonksiyonu | `SF/scripts/*.sql`, `factory_*.py` içindeki `CREATE TABLE` sayımı |
| Kontrol düzlemi | Host'ta, launchd ile başlayan Python süpervizörü `factory_service.py` (3 saniyelik döngü) ve ayrı süreçler: `factory_autonomy_service.py --management/--background/--reporting`, `factory_blockage_worker.py --background`, `factory_storybook_live.py`, `caffeinate -dis` | `SF/factory_service.py:12-95`, `ps` (PID 37797, 8 gün 14 saattir çalışıyor) |
| Süpervizör içi iş parçacıkları | Kestra kontrol dağıtıcısı (250 ms SQL yoklama), ECA motoru (1 s), katalog | `SF/factory_service.py:22-29`, `docs/audits/2026-09-14-reliability-efficiency/infrastructure.md:110` |
| Aşama işçileri | `factory_worker.py` alt süreçleri. Sayıyı `worker_launch_budget` belirler (`max_slots=8`) | `SF/factory_service.py:75-78`, `SF/config/scheduler.json` |
| Ajan sandbox'ı | Her rol çağrısı ayrı `docker run` ile açılır (Colima `factory` profili): read-only rootfs, `--cap-drop ALL`, `no-new-privileges`, `--pids-limit 256`, `--memory 2g --cpus 2`, yalnız worktree mount'u, docker.sock yok. İmaj `factory-agent:sdk-20260913` | `SF/factory_agent_runtime.py:44-68`, `SF/config/agent-image.json` |
| Ajan CLI/SDK | Claude Agent SDK 0.3.270 (Claude Code 2.1.267), Codex SDK 0.154.0 (Codex CLI 0.153.4), OpenCode 1.18.30 (yalnız protokol testi) | `SF/config/agent-image.json`, `SF/runtime/sdk/claude.mjs`, `SF/runtime/sdk/codex.mjs` |
| Kestra eklentisi | Özel Java eklentisi `io.kestra.plugin.fabrika.Control` (Control/ControlClient/JdbcGateway, 298 satır + 186 satır test). Postgres `control_requests` komut kuyruğuna yazar ve 500 ms aralıkla sonucu yoklar | `SF/plugins/kestra-control/src/main/java/io/kestra/plugin/fabrika/*.java`, `SF/scripts/kestra-control.sql:1-60` |
| Ürün ortamları | `factory-v1test-{alpha,beta,rc,prod}` (8111–8114, aynı imaj `032677633fd5`); `factory-product-d1636cfab714-{alpha,beta,rc}` (8200–8202, imaj `ce673a4c40ed`) | `docker ps`, `SF/VALIDATION-V5.md:12`, `SF/VALIDATION-V8.md:54` |
| Storybook | `factory_storybook_live.py` ile 6017'de önizleme (launchd `lab.atonota.storybook-live`) | `SF/docs/handoffs/2026-09-15-claude/DEVIR-RAPORU.md:33-37` |
| GitHub | `atonota/v1test`. Host'taki `gh` CLI ile push, PR, CI yoklama (10 sn aralık, 600 sn) ve `--match-head-commit` ile merge | `SF/factory_worker.py:626-664` |

### 1.2 Uçtan uca akış (tasarlanan ve kodda olan)

```
Plane READY (30 sn yoklama, factory_core.intake)
  → factory.jobs (QUEUED) → dispatch → Kestra factory.delivery yürütmesi
  → her aşama için: [Kestra JDBC Query: factory.enqueue(stage)]
                    → [Kestra LoopUntil: 15 sn'de bir stages tablosunu yokla, en fazla P7D]
                    → [If PASS devam / değilse Fail]
     Aşamaları asıl yürüten: host'taki factory_worker.py süreci (lease + heartbeat)
  plan → test_red → code_green → review → readiness → github → build
       → alpha → beta → rc → (Plane REVIEW) → Kestra Pause 24h (Resume = onay) → prod
  hata → errors: factory.fail_execution → outbox → Plane ERROR
```

Kanıt: `SF/flows/delivery.yaml:15-17` (concurrency 5, QUEUE), `:18-66` (enqueue/LoopUntil/If kalıbı), `:579-584` (tek native `Pause`, 24 saat sonra CANCEL), `:653-667` (hata yolu); `SF/VALIDATION-V6.md:65` (aşama sırası); `SF/factory_worker.py:730` (RC'de Plane REVIEW).

Kestra flow'larında kullanılan görev tipleri (21 flow, 1.641 satır):

| Görev tipi | Adet |
|---|---:|
| `jdbc.postgresql.Query` | 29 |
| `fabrika.Control` | 18 |
| `Log` | 12 |
| `LoopUntil` | 11 |
| `If` | 11 |
| `Fail` | 11 |
| `Schedule` (`fabrika_art_senkron`, her 2 dakikada bir) | 1 |
| `Pause` | 1 |

Kestra'nın `retry` ilkesi yalnız `control-status.yaml`'da bir kez geçiyor. Kaynak: `grep` sayımı, `SF/flows/*.yaml`. **Yorum:** Kestra bir iş akışı motoru gibi değil, Postgres'teki durum tablosunun 15 saniyelik yoklayıcısı ve form ekranı gibi kullanılıyor. Dayanıklılık semantiğinin tamamı Python ve SQL'de.

### 1.3 Orkestrasyon ve eşzamanlılık mekanizmaları (elle yazılmış)

| Mekanizma | Kanıt |
|---|---|
| Aşama lease'i: 120 sn TTL, 15 sn heartbeat iş parçacığı | `SF/factory_scheduler.py:22,324-342`, `SF/factory_worker.py:755-793` |
| Paket lease'i: 600 sn TTL, 60/90 sn yenileme | `SF/factory_work_packages.py:120-152`, `SF/factory_delivery_coordinator.py:12,385` |
| Yayın lease'i (repo başına sıralama) | `SF/factory_scheduler.py:341,364` |
| Outbox'lar: `outbox` (Plane durumu), `autonomy_report_outbox`, `autonomy_kestra_report_outbox`, `rule_event_outbox` | `SF/scripts/schema.sql:28-30`, `SF/factory_plane_dialogue.py:22-37` |
| Kurtarma kuyruğu `recovery_queue`, `RECOVERY_RETRY_BOUND` | `SF/flows/delivery.yaml:45-55`, `DEVIR-RAPORU.md:77` |
| Komut kuyruğu `control_requests` (Kestra formu → Java eklentisi → Postgres → Python) | `SF/VALIDATION-V7.md:27`, `SF/scripts/kestra-control.sql` |
| Kod tabanında geçme sayısı: "lease" 786, "retry" 172, "outbox" 101, "recovery_queue" 32 | `grep -o` sayımı (`factory_*.py`, `scripts/*.sql`) |

### 1.4 Ajan CLI'larının çağrılması

- **Claude:** `runtime/sdk/claude.mjs` içinde Agent SDK `query()` kullanılıyor. Ayarlar: `permissionMode:'bypassPermissions'`, `persistSession:false`, `continue:false`, araç beyaz/kara listesi ve `PreToolUse` kancası (`SF/runtime/sdk/claude.mjs:72-87`). Her çağrı yeni bir oturumdur; oturum devamı yoktur.
- **Codex:** `startThread({sandboxMode:'danger-full-access', approvalPolicy:'never', webSearchMode:'disabled'})`. İç sandbox kapalı, sınırı Docker çiziyor (`SF/runtime/sdk/codex.mjs:72-76`, `SF/KAIZEN.md:17`).
- **Hesap havuzu:** `provider_accounts` ve `provider_sessions` tabloları. Kimlik dizini konteynere RW bağlanıyor (refresh için): `SF/factory_agent_runtime.py:51-59`. Altyapı denetimi bunu açık risk olarak işaretliyor: `infrastructure.md:134`.
- **Rol → sağlayıcı dağılımı:** PO, SM/Coordinator, SDET ve Platform/Release Codex'te; diğer teknik roller Claude'da (`DEVIR-RAPORU.md:20`). 24 saatlik örnekte Claude coder 29 çağrı, Codex PO 13, SM 9, reviewer 11 (`docs/audits/2026-09-14-reliability-efficiency/economics.md:7-13`).

### 1.5 GitHub entegrasyonu

- PR'ı ve CI'ı gerçekten çalıştırılan işler: PR #1 (pilot), #2 (V5), #3 (V8) (`SF/projects/v1test` git log).
- CI şablonu: `SF/projects/v1test/.github/workflows/ci.yml`. SHA ile sabitlenmiş action'lar; pytest, 3 tarayıcıda Playwright + axe, Storybook build.
- V1-4 UI kütüphanesi GitHub'a hiç PR olarak gitmedi. Yerel `factory/30bc1cb8…/g5` dalında `main`'e göre **251 commit, 1.346 dosya, +116.987 satır** bekliyor (`git diff --stat main …/g5`).

---

## 2. Gerçekten çalıştığı kanıtlanmış olanlar

### 2.1 Görev bazında sonuçlar (`SF/state/public/status.json`, 27.09.2026)

| Görev | Durum | Çağrı | Önbelleksiz girdi | Çıktı | Süre | Not |
|---|---|---:|---:|---:|---|---|
| e108c171: ilk pilot | **RELEASED/prod** | 10 | 179.908 | 21.018 | ~26 dk (22:52→23:18 TRT) | 2 elle kurulum onarımı. "Müdahalesiz bitmiş deney olarak sunulmamalı" (`PILOT-RESULT.md:34`) |
| cd2d3525: V4/V5 adaptif UI | ERROR (`ERROR_REPAIR_LIMIT`) | 10 | 226.471 | 8.503 | ~8 saat | Ürün, operatör tarafından elle yayınlandı. Otomatik görev ERROR kaldı (`VALIDATION-V5.md:16-18`) |
| 364c693e: V8 generic Python app | ERROR/rc | 5 | 61.694 | 3.670 | 3 nesil | RC'ye kadar tüm aşamalar PASS, PR #3 birleşti. Evaluator kimliği değişince eski RC kanıtı geçersizleşti ve prod'a geçilmedi (`VALIDATION-V8.md:52-64`) |
| 30bc1cb8: V1-4 UI kütüphanesi (73 bileşen) | **ERROR (`KESTRA_FAILED`)** / review | **456** (kök sayaç çocukları da içerir) | **24.097.677** | **6.997.704** | 12.09 22:43 UTC → 25.09 (13 gün) | 73 paket yerel dalda MERGED; `AC-REQUEST: NOT_TESTED`; 93 çağrının kullanımı bilinmiyor |
| 9 çocuk takım işi (team-1…9) | "RUNNING/code_green" | 21–60 (toplam 391) | 1,36–3,67 M | 0,44–1,13 M | son güncelleme 16–18.09 | Hiçbir `factory_worker.py` süreci çalışmıyor (`ps`). Durum 9+ gündür bayat |

- Kök sayacın çocukları da içerdiğinin kanıtı: `SF/factory_core.py:327` (`UPDATE … agent_calls+1 WHERE id=ANY(child, root)`) ve `SF/factory_budget_roots.py:44`.
- **Tüm zamanlar toplamı (kökler):** 481 çağrı, ≈24,57 M önbelleksiz girdi, ≈7,03 M çıktı tokenı. 93 çağrının kullanımı bilinmiyor.
- **V1-4 toplam girdi:** 419.985.626 token. Bunun 395.887.949'u önbellekten geldi (`evidence/autonomy-reports/30bc1cb8…/v3494-3a1e42b3577fb3e2.md`, son satırlar).
- **Para/kredi maliyeti:** hiçbir yerde ölçülmedi. "CLI hesap kredisi ölçülemiyor" (`status.json.credit_note`, `README.md:35`).

### 2.2 Ölçülmüş başarı oranı

- Kök görev: 4. Otonom, müdahalesiz prod: **0**. Müdahaleyle RELEASED: **1**. RC'ye ulaşan: **3** (pilot, V5, V8).
- V1-4 kök görevinin durum geçişleri (3.494 rapor sürümünün zaman sırasıyla): RUNNING→ERROR **46 kez**, ERROR→RUNNING/QUEUED **47 kez** (`evidence/autonomy-reports/30bc1cb8…`, `ls -tr` ile `sed -n 5p` taraması).
- Aynı iş için 198 olay kaydı (incident) açıldı. 326 kayıtta gerekçe `SUPERSEDED_BY_CONTROLLER_CORRECTION` (aynı rapor dosyası).
- Paket düzeyinde: 102 teslim satırı. 79 MERGED, 22 SUPERSEDED (geri çağırma: 8 "merged-candidate regression", 6 "final type check failed", 3+2 diğer), 1 LOCAL (FOUNDATION) (aynı rapor, satır 23-171).

### 2.3 Ölçülmüş kaynak kullanımı

| Ölçüm | Değer | Kanıt |
|---|---|---|
| Host | Apple M5 Max, 18 CPU, 128 GiB RAM | `infrastructure.md:19` |
| Colima `factory` VM | 10 CPU, 24 GiB (docker: `MemTotal=25.145.901.056`), 100 GiB disk | `infrastructure.md:20`, `docker info` |
| **Coder ajan konteyneri (gerçek)** | **208,5 MiB ve 205,8 MiB** (limit 2 GiB) | `infrastructure.md:26` |
| **Tarayıcı testi konteyneri** | **710,5 MiB / 1 GiB, %93,9 CPU (≈1 çekirdek)** | `infrastructure.md:25` |
| Kestra | 2,93 GiB / 6 GiB, %4,1 CPU | `infrastructure.md:23` |
| Plane Celery worker | 805,8 MiB / 2 GiB | `infrastructure.md:24` |
| factory Postgres | 154 MiB, **%19,9 CPU** (yoklama baskısı) | `infrastructure.md:27` |
| Konteynerlerin toplamı (tek örnek) | ≈6,2 GiB | `infrastructure.md:21` |
| macOS VM süreci RSS | ≈20,18 GiB | `infrastructure.md:22` |
| Swap (kümülatif) | 9,79 GiB | `infrastructure.md:29` |
| Eski pilot ortamları (7 konteyner) | ≈170 MiB toplam | `RAPOR.md` §9 madde 5 |
| Fabrika konteynerlerinin **limit** toplamı | 23,75 GiB (altyapı 20,75 + ürün 3,0). VM kapasitesinin (≈23,4 GiB) tamamı | `docker inspect` toplamı (bugün) |
| Aynı VM'deki diğer yükler (bugün) | 46 çalışan konteyner. Penpot, Postiz (Temporal + Elasticsearch dahil), open-notebook vb. aynı `colima-factory` bağlamında | `docker ps`, `docker info` |
| Host süpervizör süreçleri | `factory_service` ≈133 MiB RSS, diğerleri 15–90 MiB | `ps` (bugün) |
| Disk | `evidence/` 2,4 GiB. Bunun 306 MiB'ı tek görevin 3.935 rapor dosyası (her biri ≈108 KB) | `du -sh` |
| Asılı konteyner | `happy_banach`: `claude auth login` 14.09'dan beri (12+ gün) çalışıyor, 1 GiB limitli, `claude-tertiary` bağlantı dizini bağlı | `docker inspect happy_banach` |

**Eşzamanlılık (ölçülen ve yapılandırılan):**
- Pilot profili "1 proje / aynı anda 1 görev" (`PILOT-RESULT.md:36`). V8'de 2 slot (`README.md:31`, `REMAINING-BLOCKERS-V8.md:11`).
- 14.09 ölçümünde 6 çocuk takım vardı; aktif model çağrısı yalnız **2** idi (`RAPOR.md:51-52`).
- 15.09 sahip kararıyla `max_slots=8` ve hesap başına 4 Claude çağrısı ayarlandı. Notta "altı coder çağrısı reviewer/koordinasyon çağrılarını aç bıraktı (PROVIDER_CAPACITY_UNAVAILABLE)" yazıyor (`SF/config/scheduler.json:7`, `SF/config/provider-concurrency.json:3`). Kestra delivery `concurrency.limit: 5` (`SF/flows/delivery.yaml:15`).
- **Yorum:** Belge (2), flow (5) ve scheduler (8) birbirinden kopmuş durumda.
- **Yorum:** Ajan başına gerçek RAM ≈210 MiB (coder) + ≈710 MiB (tarayıcı turu). Darboğaz bellek değil, sağlayıcı kapasitesi, lease ve durum makinesi hataları.

**Zaman verimliliği:**
- V1-4, 5. nesil: 9 sa 43 dk duvar saatinde tamamlanan çağrıların toplam süresi yaklaşık **101 dk** (`docs/SAATLIK-ILERLEME-2026-09-14.md:73`).
- 24 saatlik örnek: 62 çağrı, ≈257 dk (paralel süreler toplanmış) (`economics.md:13`).

---

## 3. Karmaşıklık ölçüsü

### 3.1 Boyut

| Ölçü | Değer | Kanıt |
|---|---:|---|
| `factory_*.py` modülü | **98** (+ `factoryctl.py`) | `ls` |
| Satır | **27.294** (1,81 MB; 1.432 `def`; 200 karakterden uzun 345 satır) | `wc -l`, `wc -c`, `grep` |
| Test dosyası / test fonksiyonu / satır | 215 `test_*.py` / **1.797** `def test_` / 29.895 satır (1,80 MB) | `ls tests`, `grep` |
| Test/kod oranı | **1,10** (satır), 0,99 (byte) | hesap |
| Postgres tablosu | **92** | `CREATE TABLE` sayımı |
| Kestra flow'u | 22 dosya, 1.641 satır (`delivery.yaml` 667 satır) | `wc -l flows/*.yaml` |
| SQL betikleri | 904 satır | `cat scripts/*.sql` |
| Java eklentisi | 298 satır kod + 186 satır test (65 davranış kontrolü) | `SF/plugins/kestra-control`, `VALIDATION-V7.md:64` |
| Skill | 18 `SKILL.md`, toplam 189 satır | `wc -l skills/*/SKILL.md` |
| Belge | `docs/` 4.976 satır + kök `.md` 565 satır. Denetim klasörü ≈350 KB | `wc -l` |
| Rol kataloğu | 9 takım şablonu, 10 uzman, 3 runtime profili, 7 alias, 16 skill eşlemesi | `SF/config/engineering-organization.json` |
| Canlıya yama | **60** `activation-manifest*.json`, **62** `deploy*.py` betiği (`experiments/` altında). Yalnız foundation-repair turunda "step10a…10ar" | `find experiments evidence` |

Büyüme hızı:
- 11.09 commit'inde 11 modül vardı (`git ls-files 'factory_*.py'`). 18.09'da 98 modüle çıktı. Yaklaşık 7 günde 87 yeni modül, ≈25 bin satır.
- Git'te yalnız **3 commit** var. Yalnız **70 dosya** izleniyor. 98 modülün **87'si**, testlerin tamamı, 21 flow ve 18 skill izlenmiyor. `git status`: 27 değişiklik, 3 silme, 428 izlenmeyen girdi (10.281 dosya, 9.782'si `experiments/`).

### 3.2 Kavram tekrarı: arıza, kurtarma ve onarım

Kullanıcının saydığı örtüşen kavramlar (blockage, recovery, repair, self_repair, runtime_repair, foundation_repair, correction, resume, retry, recall) **17 modül, 4.530 satır** tutuyor:

| Kavram | Modül (satır) |
|---|---|
| blockage | `factory_blockages` (97), `_blockage_activation` (426), `_blockage_checkpoint` (103), `_blockage_repair` (192), `_blockage_resume` (159), `_blockage_store` (179), `_blockage_worker` (558) |
| repair | `factory_self_repair` (307), `_runtime_repair` (522), `_foundation_repair` (623) |
| recovery / recall | `factory_recovery` (202), `_package_recall` (367) |
| correction | `factory_controller_correction` (259), `_autonomy_corrections` (176) |
| resume / retry | `factory_job_resume` (122), `_oracle_resume` (149), `_component_retry` (89) |

Gözlem ve yönetim döngüleri (`management_watch`, `family_watch`, `maintenance`, `support_runtime`, `kestra_control`, `autonomy_runtime`) de eklenince arıza/kurtarma alanı **24 modül, 6.566 satır**. Bu, kod tabanının **%24'ü**. Diğer alanlar:

| Alan | Modül | Satır |
|---|---:|---:|
| Teslim/scheduler | 17 | 6.506 |
| Planlama/organizasyon | 18 | 3.653 |
| Yönetişim/kural | 18 | 4.028 |
| TDD/test | 12 | 3.767 |

Gruplama `python` betiğiyle dosya adına göre yapıldı.

Aynı sorun için birden çok kayıt tipi var: `blockage_cases`, `incidents`, `recovery_queue`, `support_requests`, `maintenance_requests`, `foundation_defects`, `package_recalls`, `runtime_handoffs`. Tablo listesi `CREATE TABLE` sayımından alındı. Devir raporu sorunu şöyle özetliyor: "Kayıt SENT, çağrı COMPLETED veya handoff COMPLETE tek başına onarım/ürün başarısı değildir" (`DEVIR-RAPORU.md:107`).

### 3.3 Kestra'nın yetmediği yerde yazılan özel çözümler

1. **Java eklentisi ve Postgres komut kuyruğu.** Yönetim formlarının Python işlevlerine ulaşması için yazıldı (`VALIDATION-V7.md:27-29`, `README.md:54`).
2. **Dashboard 405.** Kestra OSS'de özel dashboard kaydı `POST /dashboards` → HTTP 405. `flows/control-dashboard.yaml` etkin olmayan taslak (`README.md:54`, `VALIDATION-V6.md:81`). Önce 8090 portunda ayrı bir web paneli yazıldı, sonra kaldırıldı (`VALIDATION-V7.md:31`).
3. **Aşama yürütme.** Kestra görevleri işi kendileri yapmıyor. `LoopUntil` ile 15 sn'de bir Postgres yoklanıyor (`delivery.yaml:32-43`). 250 ms'lik kontrol dağıtıcısı ve 1 s'lik ECA döngüsü ayrı (`infrastructure.md:110`).
4. **Lease/heartbeat/uyku dayanıklılığı.** Tamamen özel kod (`experiments/sleep-tolerant-leases-20260915/README.md:38-60`).
5. **Rapor teslimi.** Ayrı `fabrika_teslimat_raporu` flow'u ve iki outbox var (`SF/factory_autonomy_reporting.py:16-77`).

---

## 4. Sonuç alınamamasının kök nedenleri (kanıtlı)

### KN-1: Dayanıklı iş akışı ilkeleri elle yeniden yazıldı, orkestratör yalnız yoklayıcı

- Kestra'da 11 `LoopUntil`, 29 JDBC sorgusu, yalnız 1 `Pause` ve delivery'de 0 `retry` var (`SF/flows/*.yaml`). Lease, heartbeat, outbox, kurtarma kuyruğu, idempotency ve "devam" semantiği Python + SQL'de (§1.3).
- Canlı hatalar büyük ölçüde bu katmanda doğdu:
  - `SCHEDULER_LEASE_LOST`, `PACKAGE_LEASE_LOST` ve UNKNOWN zombi slotlar, tüm kapasiteyi tuttu (`DEVIR-RAPORU.md:47-57,79-89`).
  - Başarılı paket yenilemede yarış oluştu; "iş kaybı sahte idi" (`sleep-tolerant-leases/README.md:23-28`).
  - `observe()` her döngüde `IDEMPOTENCY_CONFLICT` ile çöktü: 1.275 satır `BlockageStoreError` (`sleep-tolerant-leases/README.md:29-32`).
  - `logs/autonomy.log` içinde 7 `DeadlockDetected` (`jobs` satırı kilitleri) ve 569 `recovery_dispatch_pending: StopJob` var.
  - V1-4'ün son hatası `KESTRA_FAILED`: iş 18/19.09'da RUNNING'e geçti, 25.09 19:14'te 7 günlük `LoopUntil maxDuration: P7D` doldu (rapor sürümlerinin zaman damgaları; `delivery.yaml:43`).
- **Etki:** Mühendislik zamanının çoğu ürün yerine kontrol düzlemi hatalarına gitti. "Çalışmanın ağırlığı, 73 bileşenin toplu geliştirmesinden çok otomasyonun karşılaştığı engelleri gidermeye kaydı" (`SAATLIK-ILERLEME-2026-09-14.md:5`).

### KN-2: Canlı sistem sürüm kontrolü olmadan yamalandı; düzeltmeleri fabrika değil GUI oturumları yaptı

- Git'te 3 commit var ve son commit 12.09 tarihli. 98 modülün 87'si izlenmiyor (§3.1).
- Canlıya 60 aktivasyon manifesti ve 62 deploy betiği uygulandı (§3.1).
- "Kök nedeni inceleyen ve düzeltmeyi yapan: bu Codex GUI oturumu ve onun paralel alt agent'ları" (`SAAS-UI-FIRST-DELIVERY-REPORT.md:24`). "Bu onarımları GUI'deki sistem geliştirme çalışması … yaptı. Sistemin hepsini kendiliğinden onardığı söylenemez" (`SAATLIK-ILERLEME-2026-09-14.md:42`).
- Denetim de aynı noktayı P0 sayıyor: "Güncel sistemi yeniden kurma ve geri alma kanıtı eksik" (`RAPOR.md:138-142`); "`git HEAD` tek başına çalışan controller sürümünü temsil etmiyor" (`DEVIR-RAPORU.md:115`).
- **Etki:** Her yeniden başlatmada "hangi kod çalışıyor?" belirsizliği oluşuyor ve geri alma mümkün değil. Otonomi iddiası ölçülemiyor. Ek olarak her kontrolcü değişikliği evaluator kimliğini değiştirip eski kanıtları geçersiz kılıyor (`VALIDATION-V8.md:64`, `CORRECTION_SOURCE_CHANGED` hataları 18.09).

### KN-3: Kapsam aynı anda her şeyi kurmaya çalıştı

- İhtiyaç listesinde **16 ihtiyaç** var (N01–N16) (`IHTIYACLAR-VE-GAP-ANALIZI-2026-09-12.md:11-28`).
- Hedef senaryo "5 proje × 5 modül × 9 rol = 225 mantıksal sorumluluk" (`AI-CREDIT-OPTIMIZATION-ACTION-PLAN.md:9`).
- Tek pilot çalıştıktan sonraki 7 günde şunlar eklendi: 9 takımlı SAFe/ART, 10 uzman, ECA motoru, Kaizen/CAPA/optimizer, adaptör niteleme, çoklu sağlayıcı havuzu, dört katmanlı kural çözümleme, Storybook canlı yayın (§1, §3).
- İlk gerçek ürün görevi "bütün Ant Design karşılıklarını içeren … kütüphane; hedef MVP değil", yani 73 paket (`SAAS-UI-FIRST-DELIVERY-REPORT.md:7`, `:54`).
- **Etki:** Temel akış (1 görev → prod) sağlamlaşmadan paralel ekip, uzman ve kural katmanları eklendi. Her katman yeni arıza sınıfı getirdi (§3.2).

### KN-4: Kabul ve oracle problemi. Doğrulanmış paketler ürün kabulüne dönüşmedi

- V1-4'te 456 çağrı ve 73 MERGED paketten sonra kabul durumu: "`AC-REQUEST | NOT_TESTED | review`" (son rapor, satır 7-9).
- Genel `AC-REQUEST` yedeği ayrıntılı kabul sağlamıyor: "Kanıt dosyasının varlığı, gereksinimin semantik olarak tam karşılandığını tek başına kanıtlamaz" (`VALIDATION-V6.md:24`, `AGENT-ANALIZI-VE-IS-AKISI-V2.md:102`).
- V8'in ilk koşusu, kabul kriterleri aşamalara yanlış bağlandığı için FAIL oldu (`VALIDATION-V8.md:40`).
- UI-09 paketi 14 kez `PACKAGE_REVIEW_FAILED` aldı, çünkü paket için tanımlı bir probe yoktu (`foundation-repair-20260915/README.md` bulgu 4).
- 22 paket SUPERSEDED oldu ve geri çağrıldı (birleşik aday regresyonu, tip kontrolü) (§2.2).
- Başarılı `expect.poll` testi altyapı hatası diye sınıflandırıldı (`RAPOR.md:106-110`).
- Teşhis ajanı olay dosyasını okuyamadı ama çıktısı SUCCESS sayıldı (`DEVIR-RAPORU.md:93-101`).
- Kök görev 18.09'da `WAITING_DECISION / CHANGE_REQUIRED` durumuna düştü (rapor zaman damgası 09-18T19:37).
- **Etki:** Tamamlanma ölçüsü belirsiz olduğu için sistem "bitti" diyemiyor. Paket düzeyinde yeşil sonuç, ürün düzeyinde kabul üretmiyor.

### KN-5: Sağlayıcı ve hesap kapasitesi darboğazı; bakım bütçesi onarımı aç bıraktı

- Pilot ve V5–V8 boyunca üretimde doğrulanmış tek hesap vardı, bir Codex hesabı: "tek bağlı Codex hesabı iki bağımsız hesap sayılmaz" (`README.md:31,60`, `VALIDATION-V8.md:82`). 15.09'da 2 Claude + 2 Codex hesabı vardı; kota dışarıdan doğrulanmadı (`DEVIR-RAPORU.md:59`).
- `logs/blockages.log` içindeki kayıtlar:
  - **330** `PROVIDER_CAPACITY_UNAVAILABLE`;
  - **56** `MAINTENANCE_DAILY_BUDGET` (44 + 12 `StopJob`);
  - **405** `diagnostician-assigned` kontrol noktası (aynı vakaya tekrar tekrar teşhisçi atanması).
- Bakımda günlük 4 çağrı kod sabiti var. Başlamamış rezervasyon da bu sayıya dahil ediliyor (`RAPOR.md:116`).
- "Six coder calls were starving reviewer/coordination calls" (`config/provider-concurrency.json:3`).
- 93 çağrının kullanımı bilinmiyor (`USAGE_UNKNOWN`). Bu durum bir dönem yeni çağrıları kilitledi (`SAAS-UI-FIRST-DELIVERY-REPORT.md:83-85`).
- **Etki:** Coder çağrıları kapasiteyi tüketirken teşhis, onarım ve inceleme bekledi. Arızalar kapanmadı.

### KN-6: Mac uykusu üretimi ve lease'leri kırıyor

- "Mac kapalı/uykudayken üretim devam etmez" (`README.md:74`, `WORKFLOW-V4.md:55`).
- `pmset` günlüğü ile kanıt: "Scheduler lease kaybı = Mac'in kapak kapalı uykusu … her uyku girişi iki ekibin son heartbeat'iyle saniyesi saniyesine eşleşiyor … `caffeinate -i` kapak kapanmasını engellemez" (`experiments/sleep-tolerant-leases-20260915/README.md:9-17`).
- Zombi slotlar `max_slots=2` kapasitenin tamamını tuttu; Team 3/7/9 hiç başlamadı (`:18-22`).
- Bugün çalışan `caffeinate -dis` süreci (PID 62256) kapak kapalı uykuyu engellemiyor.
- **Etki:** Gece ve uzun süreli üretim kesiliyor. Uyanışta sahiplik hataları, kurtarma döngüleri ve bekleme zaman aşımları (KN-1) tetikleniyor.

### KN-7: Bütçe ve tekrar sınırları "adaptive" modda uyarıya dönüştü; yakınsama olmadan harcama sürdü

- `config/policy.json:26-27`: `"execution_mode": "adaptive"`, `"hard_limits": []`.
- `factory_execution_policy.py:30-58`: limit aşılınca `StopJob` yerine yalnız `warn()` çalışıyor. `attempts()` sonsuz sayaç (`itertools.count()`) döndürüyor.
- Onay kaydı: `docs/ADAPTIVE-EXECUTION-2026-09-13.md:7,13`.
- V1-4'te politika eşiği ile gerçekleşen:

| Ölçü | Politika eşiği | Gerçekleşen | Kat |
|---|---:|---:|---:|
| Görev başına çağrı | 12 | 456 | 38 |
| Önbelleksiz girdi | 250 bin | 24,1 M | 96 |
| Çıktı | 50 bin | 7,0 M | 140 |

- Aynı dönemde 46 ERROR ve 47 yeniden başlatma yaşandı (§2.2).
- **Etki:** Sınırlar sorunu erken yüzeye çıkarmak yerine harcamayı büyüttü. İlerleme ölçüsü "gerçek test/tamamlanma kaydı" olduğu için döngüler paket düzeyinde yeşil üretti, ürün düzeyinde kabul üretmedi.

### KN-8: Eşzamanlılık artışı çıktıya dönüşmedi; durum doğruluğu zayıf

- Yapılandırma 1 → 2 → 5/8 slota çıktı (§2.3). Kanıtlanmış verim artışı yok. Denetimin kabul deneyi (1→2→3 paket canary) hiç koşulmadı (`infrastructure.md:106`).
- Bugün 9 çocuk iş "RUNNING/code_green" görünüyor ama son güncellemeleri 16–18.09 ve hiçbir `factory_worker.py` süreci yok (`status.json`, `ps`).
- Rapor döngüsü tek görev için 3.935 dosya (306 MiB) üretti ve hâlâ yazıyor (son dosya 27.09 10:02).
- Plane 429 sınırına takıldı: "Seven workers verify the same contract; Plane's per-minute limit answers 429" (`SF/factory_core.py:63`).
- **Etki:** Kullanıcı, işin ilerleyip ilerlemediğini arayüzden güvenilir biçimde göremiyor (bkz. `IHTIYACLAR…:26` N14).

### KN-9: Çağrılar arası bağlam ve oturum devamı yok; aynı iş tekrar keşfediliyor

- `persistSession:false, continue:false` (Claude). Codex her çağrıda `startThread` açıyor (`runtime/sdk/claude.mjs:75`, `runtime/sdk/codex.mjs:73`, `economics.md:25`).
- V1-4 girdisinin %94'ü önbellekten geldi (395,9 M / 420 M), yani çok büyük tekrar bağlam taşındı (son rapor).
- **Etki:** Maliyet büyük. Onarım çağrıları önceki muhakemeyi yeniden kuruyor.

**Ek gözlem (sürece ilişkin, kök neden değil):** Ürün reposundaki 259 commit `Factory Bot <factory@localhost>` kimliğiyle, fabrika reposundaki 2 commit de aynı kimlikle atılmış. Kullanıcının kişisel git politikası (author = karacaismail) bu sistemde uygulanmıyor. Yeni sistem bunu baştan çözmeli.

---

## 5. Yeni sisteme taşınmaya değer, kanıtlanmış parçalar

| Parça | Yol | Neden (kanıt) |
|---|---|---|
| Sürümlü kabul sözleşmesi ve aşamaya bağlı koşullar (gelecek aşama PENDING, eski kanıt reddi) | `SF/factory_readiness.py`, `SF/factory_phase_contracts.py`, `SF/docs/ADR-009-TEST-ORACLES.md` | V8'de yanlış bağlanmış kabul yakalandı, düzeltildi ve RC'ye kadar geçti (`VALIDATION-V8.md:40-52`). Model olarak taşınmalı, kod olarak değil |
| Korumalı test ve evaluator kilidi (coder test değiştiremez; asgari test sayısı; altyapı hatası RED sayılmaz) | `SF/config/evaluator-lock.json`, `SF/README.md:58`, `SF/KAIZEN.md:13,21-27` | Pilotta 133 testin 93'ü davranış nedeniyle RED oldu, sonra GREEN; bağımsız inceleme gerçek hata buldu (`PILOT-RESULT.md:14`) |
| Atomik bütçe sayaçları ve kök bütçeye yayılım (**sert limitle**) | `SF/factory_core.py:295-328`, `SF/factory_budget_roots.py` | Eşzamanlı rezervasyon ve yeniden çalıştırmada sayaç koruması testle doğrulandı (`PILOT-RESULT.md:18`, `VALIDATION-V6.md:42`) |
| Plane durum sözlüğü ve outbox ile durum senkronu | `SF/scripts/bootstrap_plane.py:29`, `SF/scripts/governance.sql:97,109`, `SF/factory_core.py:171-294` (`sync_outbox`) | 4 görevde tutarlı çalıştı; RELEASED/ERROR/REVIEW geçişleri gerçekleşti |
| Plane giriş sözleşmesi (açıklamada ```` ```fabrika ```` JSON bloğu, `FABRIKA:` satırı, `fabrika:app=` etiketleri) ve yorum tabanlı soru/rapor işaretleri | `SF/factory_plane_intake.py:11,20-36`, `SF/factory_plane_dialogue.py:22-37` | Deterministik hedef çözümü; eksik bilgi soruya dönüşüyor, ERROR'a değil (`docs/AUTONOMY-INTAKE-PACKAGES-PARALLEL.md:9-11`) |
| Skills klasörü (kısa ve öz) | `SF/skills/*/SKILL.md` (18 dosya, 189 satır) | Rol bağlamını küçük tutuyor. Özellikle `acceptance-contract`, `tdd-refactor`, `test-oracle`, `evidence-review` |
| CI şablonu | `SF/projects/v1test/.github/workflows/ci.yml` | SHA sabitli action'lar; pytest + 3 tarayıcıda Playwright/axe + Storybook; PR #1/#2/#3 başarılı CI |
| Ajan sandbox parametreleri | `SF/factory_agent_runtime.py:44-68` | Read-only rootfs, cap-drop, pids, worktree-only, docker.sock yok. Coder başına ölçülen ≈210 MiB (`infrastructure.md:26`) |
| SDK adaptörleri ve dürüst kullanım muhasebesi (bilinmeyen = UNKNOWN, sıfır değil) | `SF/runtime/sdk/claude.mjs`, `SF/runtime/sdk/codex.mjs`, `SF/factory_provider_pool.py:421` | Token ölçümü önbellek ayrımıyla güvenilir; eksik kullanım gizlenmiyor |
| GitHub birleştirme koruması ve tek imajla terfi (alpha→beta→rc→prod manifestleri) | `SF/factory_worker.py:626-712`, `SF/state/delivery-repo` | Dört ortamda aynı imaj SHA'sı doğrulandı (`PILOT-RESULT.md:12`, `VALIDATION-V5.md:12`); `--match-head-commit` ve base değişince yeniden inceleme |
| Hata sınıflandırma sözlüğü ve durma sebepleri (`same_error_limit`, `ERROR_NO_PROGRESS`, `STALE_DECISION` vb.) | `SF/factory_core.py:347-360` (`record_failure`), `SF/factory_governance.py:232` | Aynı hatanın tekrarı yakalanıyor. Ürün hatası ve altyapı hatası ayrılıyor |
| Tarayıcı kapısı dersleri (poll semantiği, network none, production build kanıtı) | `SF/runtime/browser/*`, `SF/factory_tdd_browser.py`, `RAPOR.md:106-110` | Kod değil ders olarak taşınmalı: yanlış altyapı sınıflandırmasının maliyeti ölçüldü |
| Mevcut denetim belgeleri (sorun envanteri) | `SF/docs/audits/2026-09-14-reliability-efficiency/`, `SF/docs/handoffs/2026-09-15-claude/DEVIR-RAPORU.md` | Hata senaryoları ve kabul deneyleri yeni sistemin test listesi olarak kullanılabilir |

**Taşınmaması önerilenler (Yorum):**
- 17 modüllük blockage/repair/recovery/correction ailesi;
- elle yazılmış lease, heartbeat ve outbox katmanı (dayanıklı iş akışı motorunun işi);
- Java eklentisi ve komut kuyruğu;
- ECA motoru;
- 9 takımlı ART/SAFe organizasyon katmanı;
- adaptive "uyarı" bütçe modu.

---

## 6. Kullanıcının Plane durum akışı

**Tanımlı durumlar** (`SF/scripts/bootstrap_plane.py:29`, sıra = sequence):

| Durum | Plane grubu | Renk | Fabrikadaki anlamı ve kimin koyduğu |
|---|---|---|---|
| BACKLOG | backlog (varsayılan) | #64748b | Taslak. Kestra `fabrika_gorev` formu önce BACKLOG açar (`SF/factory_control.py:101-102`) |
| READY | unstarted | #3b82f6 | **Tetik.** Kullanıcı taşır; fabrika 30 sn'de bir yalnız READY'yi okur (`SF/factory_core.py:118`, `README.md:17,23`) |
| IN_PROGRESS | started | #8b5cf6 | Kabul edilen iş. Outbox ile yazılır (`SF/factory_autonomy_service.py:78`, `SF/factory_controller_correction.py:251`) |
| REVIEW | started | #f59e0b | RC hazır. Kestra `release_approval` 24 saat bekler, onay yoksa CANCEL (`SF/factory_worker.py:730`, `SF/flows/delivery.yaml:579-584`) |
| WAITING_DECISION | started | #f59e0b | Kapsam veya kabul çelişkisi; beklerken AI çağrısı yapılmaz (`README.md:9`, `SF/scripts/governance.sql:94`) |
| ERROR | cancelled | #ef4444 | Terminal. READY'ye geri almak sayaçları sıfırlamaz (`README.md:23`, `SF/scripts/governance.sql:97`) |
| RELEASED | completed | #22c55e | Prod yayını (`SF/scripts/governance.sql:109`, `SF/scripts/schema.sql:71`) |

**Özel alanlar ve şablonlar:**
- Plane CE'de özel alan (custom property) **kullanılmıyor**.
- Meta veri üç yoldan taşınıyor:
  1. açıklamada ```` ```fabrika {…}``` ```` JSON bloğu;
  2. `FABRIKA: {…}` satırı;
  3. `fabrika:app=…`, `fabrika:module=…`, `fabrika:target=…`, `fabrika:release=…` etiketleri.
- İzinli alanlar: `app`, `module`, `target`, `release_target`, `requirements` (`SF/factory_plane_intake.py:11,20-36`).
- Kabul kriteri, açıklamanın serbest metni olarak alınıyor. Ayrı kriter yoksa tamamı `AC-REQUEST` diye tek madde sayılıyor (`AGENT-ANALIZI-VE-IS-AKISI-V2.md:102`).
- Sorular ve raporlar Plane **yorumu** olarak yazılıyor. Her yorumda `<code>FABRIKA:<QUESTION|REPORT>:<issue>:<digest16></code>` işareti ve `<pre>` gövdesi var (en fazla 100 bin karakter). Cevaplar yetkili kullanıcı kimliğiyle yorumlardan okunuyor (`SF/factory_plane_dialogue.py:19-27,167-180`).
- Takım alt işleri Plane'de alt görev olarak **açılmıyor**; yalnız fabrika veritabanında duruyor (`autonomy_delivery_children`). Plane'de görünen tek kayıt kök görev.
- Workspace `fabrika`, proje "Fabrika Durum ve Görev Panosu" (anahtar `v1test`), repo `atonota/v1test`, yerel portlar alpha 8111, beta 8112, rc 8113, prod 8114 (`SF/scripts/bootstrap_plane.py:35`, `status.json.projects`).
