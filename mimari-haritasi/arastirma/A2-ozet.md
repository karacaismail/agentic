# A2 — Platform ve Kapasite Araştırması (Özet)

**Tarih:** 27 Eylül 2026
**Ayrıntılı veri:** `A2-platform-ve-kapasite.json` (674 benzersiz kaynak URL'si; her alt bulguda `kaynak` alanı var)
**Etiketler:**
- **doğrulanamadı:** birincil kaynak bulunamadı.
- **tahmin:** kaynaklı sayılardan türetilmiş; dayanağı JSON'daki `sentez` ve `gorev_basi_butce_tahmini` bölümlerinde yazılı.

---

## En önemli 12 bulgu

1. **"Bir Claude ajanı 1 GB RAM ayırıyor" iddiası yanlış yorumlanmış.**
   - Anthropic'in hosting dokümanı "1 GiB RAM, 5 GiB disk, 1 CPU / ajan" değerini yeni açılmış bir oturum için *başlangıç noktası* olarak veriyor ve bunun **"a floor, not the ceiling"** olduğunu açıkça yazıyor.
   - Ajan belleği önceden ayırmaz. Bellek, oturum uzunluğu ve araç kullanımıyla büyür.
   - Küçük headless oturumda ölçülen tepe RSS yaklaşık **0,5 GB**. Hatalı ya da patolojik durumlarda süreç başına **6–15 GB** raporlanmış.
   - Kaynaklar: [hosting](https://code.claude.com/docs/en/agent-sdk/hosting), [#79196](https://github.com/anthropics/claude-code/issues/79196)
2. **Görev başına bütçeyi ajan CLI belirlemiyor; build, test, LSP ve tarayıcı belirliyor** (tahmin).
   - hafif: 4 GB / 1–2 vCPU
   - orta: 8 GB / 4 vCPU
   - ağır (Next.js build ve Playwright): 16 GB / 6–8 vCPU
3. **Plane CE webhook'u v1 biçiminde geliyor.** developers.plane.so'da anlatılan "v2" (`workitem.created`, `previous_attributes`) CE kodunda yok.
   - "In Progress"e geçiş şu koşulla yakalanır: `event=issue`, `action=updated`, `activity.field ∈ {state, state_id}` ve `data.state.group == "started"`.
   - İmza `X-Plane-Signature` başlığında gelir; ham gövdenin öneksiz HMAC-SHA256 hex değeridir.
4. **Plane webhook teslimi güvenilir değil.**
   - Yalnızca ağ hatası ve timeout'ta tekrar deniyor; 5xx yanıtında tekrar denemiyor.
   - Denemeler tükenince webhook kendini otomatik olarak devre dışı bırakıyor.
   - Silme, toplu işlem ve otomatik kapatma için webhook gönderilmiyor.
   - Sonuç: webhook'un yanında REST API ile periyodik uzlaştırma (reconciliation) şart.
5. **Plane CE'de olmayan özellikler:** özel alanlar (work item types, custom properties), şablonlar, workflows, custom automations, intake formları. Hepsi Pro, Business veya Enterprise'da.
   - CE'de temel Intake var; durum grupları ve özel durumlar da var.
6. **Temporal: tek düğüm ve PostgreSQL yeterli, Elasticsearch zorunlu değil.** Yine de şunlara dikkat:
   - `numHistoryShards` Docker varsayılanında **4**. İlk açılıştan önce **512** yapılmalı; sonradan değiştirilemez.
   - Sınırlar: event geçmişi **51.200 event / 50 MB**, payload **2 MB**, gRPC mesajı **4 MB**.
   - Worker Versioning v1.31 ile GA oldu. External Storage (resmi claim-check) hâlâ Public Preview.
7. **Abonelikle otomasyon riskli.**
   - Agent SDK ile yapılan ürünler **API anahtarı** kullanmalı.
   - Pro/Max limitleri "ordinary, individual usage" varsayıyor.
   - `claude -p` ve Agent SDK kullanımı şu an abonelik limitinden düşüyor. Ayrı bir SDK kredisi planı 15 Haziran 2026'da durduruldu.
   - Sunucu filosu için API anahtarı ve Build ya da Scale tier gerekiyor.
8. **Anthropic API tier adları değişti:** Start, Build, Scale, Custom.
   - Start tier'ın aylık harcama tavanı **$500**. Bu, sürekli çalışan bir filo için bağlayıcı.
   - RPM ve ITPM sınırları (Start'ta Sonnet 5 ve Opus 5.5 için 1.000 RPM, 2M ITPM, 400k OTPM) büyük olasılıkla bağlayıcı değil. Cache okumaları ITPM'e sayılmıyor.
9. **Sandbox seçenekleri:**
   - En pratik katman: rootless ya da sertleştirilmiş Docker, üstüne gVisor (`runsc`).
   - En güçlü sınır: Firecracker tabanlı E2B Embed. Ancak E2B bunu "evaluation" (değerlendirme) paketi olarak konumluyor, üretim için değil.
   - **Daytona açık kaynak sürümü Haziran 2026'dan beri bakımsız.**
   - gVisor için yeni kritik CVE: CVE-2026-96812 (25 Eylül 2026).
10. **GitHub:**
    - Self-hosted runner ücreti ($0,002/dk) **ertelendi**; şu an self-hosted kullanım ücretsiz.
    - Merge queue kişisel hesaplardaki ya da Team planındaki private repolarda **yok**.
    - Otomasyon için GitHub App kullanılmalı. Installation token'ı 1 saat geçerli ve repo bazında daraltılabilir.
11. **Önizleme ortamı araçlarının güvenlik geçmişi ağır.**
    - Coolify: 70 advisory, 21'i kritik.
    - Dokploy: 60 advisory, 34'ü kritik.
    - Eski Hetzner DNS API'si 27 Mayıs 2026'da kaldırıldı. DNS-01 artık Cloud API token'ıyla yapılıyor.
12. **Asıl darboğaz insan incelemesi** (tahmin).
    - 128 GB'lık bir sunucu aynı anda yaklaşık 12 orta profilli görev çalıştırabilir.
    - Buna karşılık bir kişi haftada ortalama 3,2 saatte yaklaşık 4 değişiklik inceliyor (Google).
    - Ajan PR'larının kabul oranı %35–64 (AIDev).

---

## 1. Plane Community Edition

| Konu | Bulgu | Kaynak |
|---|---|---|
| Sürüm | **v1.4.2** (23 Ağustos 2026), AGPL-3.0. `plane-ce` Helm chart hâlâ 1.4.1 gösteriyor. | [release](https://github.com/makeplane/plane/releases/tag/v1.4.2) |
| Webhook olayları (CE) | project, issue, cycle, module, issue_comment. Yük alanları: `event`, `action`, `webhook_id`, `workspace_id`, `workspace_slug`, `data`, `activity{field, old_value, new_value, actor}`. | [webhook_task.py](https://github.com/makeplane/plane/blob/5f7d92784c403f76284f0f16718f320221dc7fec/apps/api/plane/bgtasks/webhook_task.py) |
| Durum değişikliği | Değişen her alan için **ayrı** bir teslimat gönderiliyor. `old_value`/`new_value` yalnızca state UUID'si. `data.state.group` yeni grubu doğrudan veriyor. | aynı dosya, satır 478–521 |
| İmza | `X-Plane-Signature` = HMAC-SHA256(secret, ham gövde) hex. Ayrıca `X-Plane-Delivery` ve `X-Plane-Event` başlıkları var. | aynı dosya |
| Retry | Celery `max_retries=5`, `retry_backoff=600`. Yalnızca `RequestException` durumunda tekrar deniyor; 5xx'te denemiyor. Denemeler tükenince webhook devre dışı kalıyor. | aynı dosya |
| REST API | `/api/v1/`, başlık `X-Api-Key`. Varsayılan **60 istek/dk/token** (`API_KEY_RATE_LIMIT` ile değiştirilebilir). Yanıtta `X-RateLimit-Remaining` ve `X-RateLimit-Reset` var. Token **kullanıcıya bağlı**, workspace'e değil; kullanıcının rolleriyle yetkilendiriliyor. `issues/` ve `work-items/` yolları birlikte çalışıyor. | JSON → `plane.rest_api` |
| Durum grupları | backlog, unstarted, started, completed, cancelled, triage. Grupların altında özel durumlar tanımlanabiliyor. Tespitte **grup** kullanılmalı, isim değil. | [state.py](https://github.com/makeplane/plane/blob/5f7d92784c403f76284f0f16718f320221dc7fec/apps/api/plane/db/models/state.py#L14-L97) |
| CE'de olmayanlar | Work item types ve custom properties, şablonlar, epics, time tracking, PQL, workflows ve approvals, custom automations, Intake Forms/Email, SAML/OIDC. | [plane.so/pricing](https://plane.so/pricing), JSON → `plane.ce_de_olmayanlar` |
| MCP server | `makeplane/plane-mcp-server` v0.3.3 (MIT). CE ile **stdio ve kişisel erişim token'ı** kullanılıyor; CE'de OAuth uygulaması yok. | JSON → `plane.mcp_server` |
| Gereksinim | En az 2 CPU ve 4 GB RAM; production için 8 GB öneriliyor. | [overview](https://developers.plane.so/self-hosting/methods/overview) |

**Mimari sonucu.** Görev şablonu ve kabul kriteri alanları CE'de özel alan olarak tutulamaz. Bu bilgiler açıklama içinde yapılandırılmış blok olarak ya da etiketlerle taşınmalı. Yeterli olmazsa ücretli plan değerlendirilmeli.

## 2. Temporal (self-host)

| Konu | Bulgu | Kaynak |
|---|---|---|
| Sürüm | Server **v1.32.0** (11 Eylül 2026; Standalone Activities GA). Python SDK **1.33.0**. | [release](https://github.com/temporalio/temporal/releases/tag/v1.32.0) |
| Dağıtım | `temporalio/docker-compose` **arşivlendi**; yerine samples-server/compose geldi (yalnızca geliştirme için). Helm chart 1.7.0 artık veritabanı alt-chart'ı kurmuyor. `temporal-server start` tek süreçte 4 servisi başlatıyor. | [deployment](https://docs.temporal.io/self-hosted-guide/deployment) |
| Görünürlük | PostgreSQL 12+ ile SQL visibility yeterli, Elasticsearch **zorunlu değil**. SQL'de namespace başına özel Search Attribute kotası düşük: Keyword 10, diğer tipler 3. | [visibility](https://docs.temporal.io/self-hosted-guide/visibility) |
| Kaynak gereksinimi | Resmi CPU/RAM rakamı **doğrulanamadı**; Helm'de `resources: {}` boş. Shard önerileri: küçük production için 512, 500 shard başına 1 History süreci. | [temporal-server](https://docs.temporal.io/temporal-service/temporal-server#history-shard) |
| Limitler (v1.32 kodu) | Event sayısı: hata 51.200, uyarı 10.240, Continue-As-New önerisi 4.096. Boyut: hata 50 MB, uyarı 10 MB, CAN önerisi 4 MB. Blob: hata 2 MB, uyarı 512 KB (dokümanda 256 KB). Bekleyen activity, child ve signal sınırı 2.000. | [constants.go](https://github.com/temporalio/temporal/blob/v1.32.0/common/dynamicconfig/constants.go) |
| Örüntüler | Continue-As-New (`workflow.info().is_continue_as_new_suggested()`), External Storage ile S3 claim-check (Public Preview), ajan loglarını ve diff'leri dış depoda tutup history'ye yalnızca referans yazmak. | [continue-as-new](https://docs.temporal.io/develop/python/workflows/continue-as-new) |
| Worker tuning | Python varsayılanları: 100 slot, 5 poller, 1.000 cache. Resource-based tuner `WorkerTuner.create_resource_based()` ile kuruluyor (`ResourceBasedTuner` adında bir sınıf yok). Docs çoğu iş yükü için sabit slot öneriyor. | [worker-tuning-reference](https://docs.temporal.io/develop/worker-tuning-reference) |
| Ölçekleme | Worker'lar stateless; aynı kuyruğu istenen sayıda host dinleyebilir. Varsayılan 4 partition. Sandbox yakınlığı için host'a özel task queue kullanılabilir. | [workers](https://docs.temporal.io/workers) |
| Worker Versioning | v1.31.0'da **GA**; Pinned veya Auto-Upgrade seçenekleri var. Eski API'ler v1.33'te kaldırılacak. | [v1.31.0](https://github.com/temporalio/temporal/releases/tag/v1.31.0) |
| Uzun activity (Python) | `start_to_close_timeout` her zaman verilmeli, ayrıca `heartbeat_timeout` ve sık `activity.heartbeat(details)`. Retry'da `heartbeat_details` ile kalınan yerden devam ediliyor. İptal heartbeat üzerinden iletiliyor. Saatlerce süren alt süreç + heartbeat deseni resmi bir tarif değil (tahmin). | [detecting-activity-failures](https://docs.temporal.io/encyclopedia/detecting-activity-failures) |

## 3. Claude Agent SDK ve Claude Code headless

**Süreç modeli.** Bir oturum tek bir `claude` alt sürecine karşılık gelir; N eşzamanlı oturum N süreç demektir. CLI artık Bun tabanlı native bir binary, dolayısıyla Node heap sınırı onu yönetmiyor. Kaynak: [hosting](https://code.claude.com/docs/en/agent-sdk/hosting).

**Resmi rakamlar:**
- Makine için "4 GB+ RAM".
- Ajan başına 1 GiB, 5 GiB disk, 1 CPU (taban).
- Self-hosted environments: oturum başına 4 GiB bellek, 2–4 CPU.
- Secure-deployment örneği: `--memory 2g --cpus 2 --pids-limit 100`.
- Oturum heap'i 2,5 GB'ı geçince uyarı.
- Host başına formül: (RAM − ek yük) / oturum başına tepe RSS.

**Raporlanmış bellek sorunları** (tam liste JSON → `ajan_calisma_zamani.bellek_raporlari`):
- Büyük transcript ile `--resume`: dosya boyutunun 9–14 katı, 16 GB host'ta OOM.
- Uzun Bash beklerken sızıntı: 10–15 GB.
- Subagent ve MCP fan-out: 70 süreç toplam ~43 GB.
- Sandbox'lı her Bash çağrısı: +1,0–1,6 GB ve ~8–10 sn tek çekirdek (açık).
- Gömülü grep regex patlaması: 6,6 GB (2.1.235'te "fail fast" düzeltmesi).
- Çoğu issue "stale" ya da "not planned" olarak kapatılmış; düzeltilip düzeltilmedikleri **doğrulanamadı**.

**Eşzamanlılık.**
- Eşzamanlı oturumlarda `~/.claude.json` bozulma raporları var; düzeltme 2.1.259'da geldi.
- Oturum başına ayrı `CLAUDE_CONFIG_DIR`, `setting_sources=[]`, `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` ve ayrı `cwd` önerilir.

**Kullanım koşulları.**
- "Anthropic does not allow third party developers to offer claude.ai login or rate limits for their products, including agents built on the Claude Agent SDK."
- Consumer Terms, otomatik erişimi "API key ile ya da açıkça izin verilen durumlar dışında" yasaklıyor.
- `claude setup-token` bir yıllık OAuth token'ı üretir; kişisel CI için belgelenmiş durumda.
- Paylaşılan üretim otomasyonu için **API anahtarı** kullanılmalı.
- Kaynaklar: [legal-and-compliance](https://code.claude.com/docs/en/legal-and-compliance), [consumer-terms](https://www.anthropic.com/legal/consumer-terms)

**Oran sınırları.**
- Tier'lar: Start, Build, Scale, Custom. Aylık tavanlar: $500, $1.000, $200.000.
- Model başına RPM, ITPM ve OTPM ayrı kovalardan sayılıyor.
- Kaynak: [rate-limits](https://platform.claude.com/docs/en/api/rate-limits)

**Kontrol yüzeyi.**
- İzin modları: default, acceptEdits, plan, auto, dontAsk, bypassPermissions. `-p` varsayılan olarak Manual modda başlıyor.
- Deny kuralları her modda geçerli.
- 30'dan fazla hook olayı var (PreToolUse, PostToolUse, Stop, SessionEnd…).
- Çıktı: `--output-format json|stream-json`. Sonuçta `total_cost_usd` (istemci tarafı *tahmin*, fatura değil), `usage`, `num_turns`, `duration_ms`, `session_id` alanları var.
- Sınır bayrakları: `--max-turns`, `--max-budget-usd`.
- OpenTelemetry dışa aktarımı destekleniyor.

## 4. Sandbox izolasyonu

| Seçenek | Durum ve not | Kaynak |
|---|---|---|
| Docker (runc), rootless veya sertleştirilmiş | En ucuz taban: boş konteyner başına ~4 MB. runc kaçış CVE'leri düzenli çıkıyor (CVE-2024-21626, Kasım 2025 üçlüsü). Güvenilmeyen kod için tek başına zayıf. | JSON → `sandbox[0]` |
| gVisor (runsc) | Düşük sürtünme. Ek yük: boş sandbox 23,7 MB, Node uygulaması 124 MB (runc'ta 76,7 MB). I/O ağırlıklı işler yavaşlıyor. Ölçümler eski ptrace platformundan. Yeni CVE-2026-96812 (CUSE ile host root). | [performance](https://gvisor.dev/docs/architecture_guide/performance/), [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-96812) |
| Firecracker | VMM ek yükü ≤ 5 MiB, açılış ≤ 125 ms. Tek başına bir orkestratör değil. | [SPECIFICATION](https://github.com/firecracker-microvm/firecracker/blob/main/SPECIFICATION.md) |
| E2B Embed | Tek bir KVM host'ta Docker Compose ile çalışıyor; 12 GiB öneriliyor. "Evaluation" paketi. Port 5008 kimlik doğrulamasız, firewall arkasına alınmalı. | [embed README](https://github.com/e2b-dev/runtime/blob/main/embed/compose/README.md) |
| Kata Containers | Güçlü izolasyon, ama Docker yolu deprecated. 2026'da çok sayıda advisory çıktı. | JSON |
| Daytona OSS | **Bakımsız** (Haziran 2026). Sandbox'lar privileged konteyner olarak çalışıyor. Önerilmez. | [repo](https://github.com/daytonaio/daytona) |
| microsandbox | libkrun microVM, beta (v0.7.3). Yakın tarihte host'a dosya yazma açığı çıktı. | JSON |
| Sysbox | Kasım 2025 runc yamalarını ancak Haziran 2026'da yayımladı (~7 ay gecikme). | JSON |
| Anthropic sandbox-runtime ve devcontainer firewall | İkinci katman olarak kullanılmalı: egress allowlist ve kimlik bilgisi maskeleme. | JSON |

**Ağ ve sırlar.**
- Egress, host'ta ya da ayrı bir proxy'de allowlist ile kısıtlanmalı; konteyner içinde değil, çünkü ajan NET_ADMIN'e erişememeli.
- Kimlik bilgileri proxy tarafından enjekte edilmeli (hosting dokümanının önerisi).
- Kısa ömürlü GitHub App token'ı, repo kapsamıyla daraltılmış olarak kullanılmalı.
- `ANTHROPIC_BASE_URL` ile anahtar konteyner dışında tutulabilir.
- Ayrıntı: JSON → `sandbox_ag_ve_sir`.

## 5. Kaynak tüketimi (gerçek sayılar)

- **Node varsayılan heap:** 64-bit'te en fazla 2 GB. Fiziksel bellek 15 GB veya üstündeyse 4 GB. Cgroup sınırı hesaba katılıyor. Sonuç: 8 GB'lık konteynerde build için `--max-old-space-size` vermek gerekir. [environment.cc](https://github.com/nodejs/node/blob/main/src/api/environment.cc)
- **Next.js build:** Turbopack fixture'ında 1,15–1,31 GB RSS. Büyük projelerde 4 GB heap yetmiyor, 6–8 GB ile geçiyor. [PR 98522](https://github.com/vercel/next.js/pull/98522)
- **tsc (TS7):**
  - vscode reposu: 4,2 GB
  - bluesky: 1,3 GB
  - TS7 varsayılan olarak 4 checker kullanıyor.
  - Kaynak: [TS 7.0](https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/)
- **tsserver:** VS Code varsayılan tavanı 3.072 MB.
- **pytest-xdist:** bellek worker sayısıyla katlanıyor; tipik değer **doğrulanamadı**. Pyright için tipik değer de **doğrulanamadı**.
- **Chromium ve Playwright:** tarayıcı başına tipik bellek **doğrulanamadı**. Docker'da `--ipc=host` öneriliyor; `/dev/shm` varsayılanı 64 MiB. [playwright docker](https://playwright.dev/docs/docker)
- **Görev bütçeleri** (tahmin, dayanaklar JSON → `gorev_basi_butce_tahmini`):

| Profil | RAM (cgroup sınırı) | CPU |
|---|---|---|
| Hafif | 4 GB | 1–2 vCPU |
| Orta | 8 GB | 4 vCPU |
| Ağır | 16 GB | 6–8 vCPU |

## 6. GitHub

- **Self-hosted runner güvenliği.**
  - Public repoda neredeyse hiç kullanılmamalı.
  - Ephemeral runner (`--ephemeral`) ya da JIT runner kullanılmalı (en fazla 1 job).
  - ARC Kubernetes gerektiriyor. Kubernetes olmadan `actions/scaleset` public preview'da; Docker örneği "production için değil" olarak işaretli.
  - Runner'ın her yeni sürümü 30 gün içinde kurulmak zorunda.
  - 2026 değişiklikleri:
    - `actions/checkout` v7 fork PR kodunu varsayılan olarak checkout etmiyor.
    - Public repolarda `pull_request_target` engeli 2 Kasım 2026'da zorunlu hale geliyor.
    - Workflow execution protections 17 Eylül 2026'da GA oldu.
- **Merge queue:** yalnızca organizasyona ait public repolarda ya da GitHub Enterprise Cloud'daki private repolarda var. Workflow'larda `merge_group` tetikleyicisi zorunlu.
- **Actions ücretleri.**
  - 1 Ocak 2026'da hosted runner fiyatları düştü: Linux 2 çekirdek $0,006/dk.
  - 1 Mart 2026'da başlaması planlanan self-hosted **$0,002/dk ücreti ertelendi**; iptal edilmedi.
  - Güncel doküman: "free for self-hosted runners". [billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions), [changelog](https://github.blog/changelog/2025-12-16-coming-soon-simpler-pricing-and-a-better-experience-for-github-actions)
- **Kimlik.**
  - GitHub App öneriliyor. Installation token'ı 1 saat geçerli, `repositories` parametresiyle daraltılabiliyor.
  - Hız sınırı 5.000/saat'ten başlıyor, en fazla 12.500'e çıkıyor.
  - Checks API yalnızca App'lere açık; `.github/workflows` dosyalarını değiştirmek için ayrı `workflows` izni gerekiyor.
  - `GITHUB_TOKEN` ile açılan PR'larda CI onay bekliyor.
- **Rulesets:** private repolarda Pro, Team ya da Enterprise Cloud gerekiyor. PR yazarı kendi PR'ını onaylayamaz. GitHub App onayının zorunlu incelemeye sayılıp sayılmadığı **doğrulanamadı**.

## 7. Önizleme ve alpha ortamları, Hetzner

- **TLS.**
  - Let's Encrypt wildcard sertifikası yalnızca **DNS-01** ile alınabiliyor.
  - PR başına ayrı sertifika almak, kayıtlı alan adı başına 7 günde 50 sertifika sınırına takılır. Bu yüzden `*.alpha.<alanadi>` için tek bir wildcard sertifika önerilir.
- **Hetzner DNS.**
  - Eski dns.hetzner.com ve API'si **27 Mayıs 2026'da kaldırıldı**.
  - Yeni DNS, Cloud API üzerinde (`/v1/zones`) ve proje kapsamlı token istiyor.
  - Araç tarafı: lego sağlayıcı adı hâlâ `hetzner` ama değişken artık `HETZNER_API_TOKEN` (v4.27+).
  - Caddy için `caddy-dns/hetzner/v2` modülüyle `xcaddy` build gerekiyor.
- **PaaS araçları:**

| Araç | PR önizleme | Güvenlik geçmişi |
|---|---|---|
| Coolify v4.3.23 | Var | 70 advisory, 21 kritik |
| Dokploy v0.30.7 | Var | 60 advisory, 34 kritik |
| Kamal v2.12 | Yok | Kayıtlı CVE yok |
| CapRover v1.15.4 | Yok | Kayıtlı CVE yok |

  - Dokploy CVE-2025-53825 (9,8): public repoda fork PR açan herkes önizleme sırlarını sızdırabiliyordu.
  - Önerilen yol (tahmin): önizlemeler için Traefik ve Docker label'larıyla kendi yönlendirmemizi kurmak ve PaaS yönetim panelini internete açmamak.
- **Hetzner fiyatları** (15 Haziran 2026 zammından sonra; KDV hariç, IPv4 dahil). Kaynak: [fiyat verisi](https://www.hetzner.com/_resources/app/data/app/live_data_prices.json), [duyuru](https://www.hetzner.com/pressroom/standardization-and-price-adjustment-of-our-server-products/)

| Model | CPU | RAM | Aylık | Kurulum |
|---|---|---|---|---|
| AX102-1 | Ryzen 9 7950X3D, 16C/32T | 128 GB (ECC değil) | €259 | €129 |
| AX162-1 | EPYC 9454P, 48C/96T | 128 GB ECC | €614 | €304 |
| AX162-2 | EPYC 9454P, 48C/96T | 256 GB ECC | €844 | €419 |
| AX162-3 | EPYC 9454P, 48C/96T | 512 GB ECC | €1.599 | €799 |

  - Server Auction'da 128 GB sunucular €107'den, 256 GB sunucular €108'den başlıyor (anlık kesit, eski nesil donanım).

## 8. Kapasite kanıtları ve sentez

**Kanıtlar:**
- **Claude Code maliyeti:** aktif geliştirici günü başına ortalama ~$13, aylık $150–250; kullanıcıların %90'ında günlük $30'un altında. Agent teams yaklaşık 7 kat token harcıyor. [costs](https://code.claude.com/docs/en/costs)
- **Tur süresi:** medyan ~45 sn. %99,9'luk dilim Ocak 2026'da 45 dakikanın üstünde. [measuring-agent-autonomy](https://www.anthropic.com/research/measuring-agent-autonomy)
- **SWE-bench Verified (mini-SWE-agent):** Opus 4.5 için instance başına $0,75, Opus 4.6 için $0,55. Duvar saati süresi yayımlanmamış (**doğrulanamadı**). [swebench.com](https://www.swebench.com/)
- **GitHub Copilot coding agent:** oturum sınırı 59 dakika. AIDev verisine göre Copilot PR'larının yarısı 12,8 dakikada hazır.
- **Ajan PR kabul oranları:** Codex %64, Devin %49, Copilot %35. [arXiv 2507.15003](https://arxiv.org/abs/2507.15003)
- **İnceleme kapasitesi:**
  - Google: medyan inceleme süresi 4 saatin altında, medyan değişiklik 24 satır, haftada ~4 inceleme ve ortalama 3,2 saat. [ICSE-SEIP 2018](https://sback.it/publications/icse2018seip.pdf)
  - SmartBear/Cisco: tek seferde 200–400 LOC, saatte 500 LOC'nin altında (üretici raporu).
- **METR:**
  - 2025 RCT: deneyimli geliştiriciler yapay zekâyla %19 daha yavaş çalıştı.
  - 2026 güncellemesi farklı sonuçlar veriyor.
- **DORA 2024:** yapay zekâ benimsenmesi arttıkça teslimat istikrarı %7,2 düştü.

**Sentez** (tahmin; ayrıntı JSON → `sentez.kapasite_modeli_tahmin`):
- **Host rezervi:** yaklaşık 24–32 GB. Bunun içinde işletim sistemi, Docker ve cache için 8–16 GB, Plane için 8 GB, Temporal ve PostgreSQL için 4–8 GB var. Temporal rakamı yer tutucu; pilotta ölçülmeli.
- **128 GB host:** aynı anda ~12 orta profilli görev.
  - AX102'de (32 iş parçacığı) CPU daha önce darboğaz olur.
  - AX162'de (96 iş parçacığı) RAM darboğaz olur.
- **256 GB host:** ~28 orta profilli görev.
- **512 GB host:** ~60 görev RAM'e sığar, ama CPU (96 iş parçacığı) 2,5 kat aşılır.
- **Bağlayıcı olan donanım değil**, şunlar:
  - İnsan inceleme ve kabul testi kapasitesi.
  - API harcama tavanı. Start tier'ın $500'ı yetmez; kaba hesapla günde 20 görev yaklaşık $880/ay eder.

## Doğrulanamayanlar ve açık riskler

- **Temporal:**
  - Server için resmi CPU/RAM rakamı yok.
  - Blob uyarı eşiği docs'ta 256 KB, kodda 512 KB.
  - Python'da heartbeat olmadan iptal desteği belirsiz.
- **Plane:**
  - Eski `issues/` yollarının ne zaman kaldırılacağı belli değil.
  - İmza doğrulaması canlı ortamda test edilmedi.
  - MCP araçlarının CE'deki uyumluluğu belirsiz.
- **Claude Code:** bellek sorunlarının çoğu "stale" olarak kapatıldı; LSP ve MCP alt süreçlerinin tipik belleği bilinmiyor; Pro/Max için mutlak limitler yayımlanmıyor.
- **Tarayıcı, pytest, pyright:** tipik bellek değeri için birincil kaynak yok.
- **GitHub:** GitHub App onayının zorunlu incelemeye sayılıp sayılmadığı belirsiz; Team planında org-level rulesets konusunda docs çelişkili.
- **Hetzner:** KDV dahil fiyatlar Almanya'nın %19 oranıyla hesaplandı; `-1-Ltd` modellerinin satışta olup olmadığı belirsiz.
