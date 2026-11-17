# C2 — OpenHands, OpenAI Symphony, Aperant ve yürütücü tak-çıkar standartları

Tarih: 2026-09-27. Ayrıntılı kanıt ve kaynak URL'leri: `C2-openhands-symphony-aperant.json`. Repo verileri `gh api` ile o gün çekildi.

---

## 1. OpenHands

**Ne yapar.** 2026-07-27'de yeniden yapılandırıldı. `OpenHands/OpenHands` reposu artık yalnızca **Agent Canvas** arayüzünü (TypeScript) barındırıyor. Çekirdek bileşenler (ajan, araçlar, konuşmalar, workspace'ler ve REST/WebSocket **Agent Server** API'si) MIT lisanslı `software-agent-sdk` reposunda. Zamanlama ve webhook işleri `automation` reposunda (beta). Eski kod arşivlenmiş `legacy` reposuna, Enterprise kodu ayrı bir repoya taşındı ([geçiş SSS](https://github.com/OpenHands/docs/issues/657)).
- **Dış orkestratörden sürülebilir.** API'de `POST /api/conversations`, `/{id}/run|pause|interrupt|fork`, `WS /sockets/events/{id}` ve warm-pool için `POST /api/init` var ([router](https://github.com/OpenHands/software-agent-sdk/blob/main/openhands-agent-server/openhands/agent_server/conversation_router.py)). Workspace tipleri: Docker, Remote Runtime API, Kubernetes (`kubernetes-sigs/agent-sandbox` + SandboxWarmPool), Apptainer ve Cloud.
- **Başka harness'leri çalıştırabilir.** `ACPAgent` şu ajanları ACP üzerinden çalıştırıyor: claude-code, codex, gemini-cli, kimi-code, pi ve opencode ([kaynak](https://github.com/OpenHands/software-agent-sdk/blob/main/openhands-sdk/openhands/sdk/settings/acp_providers.py)). Kendi yazılımıyla OpenHands hem ACP istemcisi, hem ACP ajanı (CLI ACP modu), hem de MCP istemcisi.
- **Kapasite ayarları.** Agent Server'da `max_concurrent_runs=10` varsayılan. Docker runtime'da konuşma başına 4 GB RAM, 2 CPU ve 512 PID varsayılan ([config](https://github.com/OpenHands/software-agent-sdk/blob/main/openhands-agent-server/openhands/agent_server/config.py)). Enterprise'ın resmî boyutlandırması sandbox başına **0,5 vCPU ve 4 GiB**. Tek VM'de 100 eşzamanlı sandbox'a kadar çıkılabiliyor, üstünde Kubernetes zorunlu. 500'den fazla sandbox'ta PostgreSQL ayrı altyapıya taşınmalı ([sizing](https://docs.openhands.dev/enterprise/sizing-guide)).
- **Benchmark ([OpenHands Index](https://github.com/OpenHands/openhands-index-results)):**
  - Claude Fable 5 + OpenHands: SWE-bench Verified %95,8; Commit0 %62,5 (16 depodan 10'u); Commit0 için örnek başına 12,49 $ ve ~18 dk.
  - Aynı modelle harness farkı: Opus 4.6 ile OpenHands ajanı SWE-bench'te 76,8, Commit0'da 56,2. ACP üzerinden Claude Code 74,4 ve 37,5.
  - Commit0'ın örneklemi küçük (1 depo = 6,25 puan). Ayrıca git geçmişinden kopyalama açığı yüzünden skorlar sonradan düzeltildi.

**Sizin çerçevede hangi katmana takılır.** Yürütücü çalışma zamanı ve sandbox katmanına (Agent Server + Workspace). ACP ile, içinde çalışan ajan da değiştirilebilir.

**Neyi karşılamaz.**
- Orkestratör değildir. ART ve takım düzeyinde iş ayrıştırma, bağımlılık grafiği, merge kuyruğu, DoD kapısı, alpha ortamına deploy ve "geri bildirimden yeni görev" döngüsü yok.
- Plane entegrasyonu yok. MIT otomasyon kataloğunda Jira, Linear, GitHub ve GitLab'dan PR'a giden akışlar var ([katalog](https://github.com/OpenHands/extensions/tree/main/automations/catalog)).
- Resmî karşılaştırmaya göre Agent Canvas'ta "Isolated sandboxes", "Scalable, always-on agents", çok kullanıcılı yapı ve RBAC **yok**; bunlar yalnızca Enterprise'da ([OSS ile Enterprise](https://docs.openhands.dev/enterprise/enterprise-vs-oss)).

**Riskler.**
- **Lisans.** Enterprise kodu *PolyForm Free Trial* lisanslı: "not an open source license", ticari lisans olmadan yılda 30 günle sınırlı ([LICENSE](https://github.com/OpenHands/enterprise/blob/main/LICENSE)). Jira, Jira DC, Bitbucket, Azure DevOps ve Slack'e gömülü entegrasyonlar buradaki `integrations/` dizininde.
- **Churn.**
  - Mimari 18 ayda V0 → V1 → Agent Canvas olarak değişti.
  - V0 API'leri resmî dokümantasyon hiç yazılmadan kullanımdan kaldırıldı ([#12417](https://github.com/OpenHands/OpenHands/issues/12417)).
  - `agent-canvas` ve `typescript-client` repoları birkaç ay içinde arşivlendi.
  - TUI bakım modunda (en az 2026-10-01'e kadar).
- **Ölçek hataları.**
  - Ağustos 2026: konuşmalar arası global kilit deadlock'u, LLM çağrılarının serileşmesi (sunucu fiilen tek thread'li kalıyordu) ve thread-pool tükenmesi. Yük testleri sürüm kapısına sonradan eklendi ([#4588](https://github.com/OpenHands/software-agent-sdk/issues/4588)).
  - `max_concurrent_runs` async yolda sınır uygulamıyor ([#4063](https://github.com/OpenHands/software-agent-sdk/issues/4063), açık).
  - Sandbox durdurulunca konuşma `RUNNING` durumunda takılı kalıyor ([#4893](https://github.com/OpenHands/software-agent-sdk/issues/4893), açık).
- **Güvenlik.**
  - CVE-2026-33718: git diff endpoint'inde komut enjeksiyonu. CVSS 3.1 7,6 HIGH; bazı üçüncü taraf siteler 9,9 yazıyor, yani kaynaklar çelişkili ([OSV](https://osv.dev/vulnerability/CVE-2026-33718)).
  - Sır maskeleme 13 aracın yalnızca 1'indeydi ([#4677](https://github.com/OpenHands/software-agent-sdk/issues/4677), kapandı).

---

## 2. OpenAI Symphony

**Ne yapar.** Symphony, çalıştırılacak bir üründen çok bir **spesifikasyon** (`SPEC.md`, "Draft v1", ~2.300 satır). Yanında deneysel bir Elixir referans uygulaması var. README'ye göre "low-key engineering preview for testing in trusted environments".
- **Çalışma döngüsü.** Tracker'ı belirli aralıklarla sorgular (varsayılan 30 sn). Her issue için deterministik bir workspace açar ve `codex app-server`'ı stdio üzerinden başlatır. Durumlar şöyle:
  - Claim durumları: `Unclaimed/Claimed/Running/RetryQueued/Released`.
  - Deneme aşamaları: `PreparingWorkspace … Succeeded/Failed/TimedOut/Stalled/CanceledByReconciliation`.
- **Uzlaştırma (reconciliation).** Her tick'te dispatch'ten önce çalışır. Takılma tespiti varsayılan 5 dk. Tracker'da terminal duruma geçen işin worker'ı durdurulur ve workspace'i temizlenir. Hatalı denemeler `min(10 sn·2^(n−1), 5 dk)` bekleyişle yeniden denenir.
- **WORKFLOW.md.** YAML front matter (`tracker`, `polling`, `workspace`, `hooks`, `agent`, `codex`) ile katı bir Liquid prompt şablonundan oluşur ve repoda sürümlenir. Varsayılanlar: `max_concurrent_agents=10`, `max_turns=20`. Durum bazında eşzamanlılık limiti de tanımlanabiliyor.
- **Tracker adapter sözleşmesi.** Yalnızca iki okuma işlemi zorunlu: `fetch_issues_by_states` ve `fetch_issues_by_ids`. Bilet yazma işlerini ajan, sağlayıcıya özgü araçlarla kendisi yapar. Referans uygulamada Linear, Jira Cloud, GitHub Issues, GitLab Issues ve Asana adapter'ları var (2026-07-18). **Plane yok.**
- **Uzak çalıştırma.** Ek A'daki SSH worker uzantısıyla uzak host havuzunda çalışabiliyor.

**Sizin çerçevede hangi katmana takılır.** Görev kaynağı ile orkestratör arasındaki **tasarım referansı**. Tracker soyutlaması ve durum makinesi doğrudan kopyalanabilecek kalitede.

**Neyi karşılamaz.**
- Yürütücü resmî olarak **yalnızca Codex**. Spec'e göre `codex.command` "MUST speak a compatible app-server protocol" ve protokolün şeklini Codex belirliyor.
- Claude Code, Gemini ve Pi için yalnızca topluluk çatalları var: [oh-my-symphony](https://github.com/cskwork/oh-my-symphony) 30★, [symphony-claude-code](https://github.com/Hisensen/symphony-claude-code) 1★. Olgunlukları doğrulanamadı. OpenHands adapter'ı bulunamadı.
- Spec'in kendi non-goal'ları: kalıcı veritabanı yok (yeniden başlatmada bellekteki durum kaybolur), çok kiracılı kontrol düzlemi yok, "distributed job scheduler" hedeflenmiyor, güçlü sandbox zorunlu değil. Tek süreçli bir orkestratör 144 takıma ölçeklenmez.

**Riskler.**
- **Bakım.** OpenAI Symphony'yi bağımsız bir ürün olarak sürdürmeyi planlamıyor ve referans uygulama olarak görüyor ([Help Net Security](https://www.helpnetsecurity.com/2026/04/28/openai-symphony-codex-orchestration-linear/)). Repoda issue'lar kapalı, dış katkı PR'ları kapatılıyor, commit'lerin neredeyse tamamı tek bir OpenAI geliştiricisinden. Sürümler v0.0.1–v0.0.3.
- **Doğrulanmamış verim iddiası.** "%500 daha fazla landed PR" iddiası OpenAI'ye ait ve bağımsız olarak doğrulanmadı.
- **Yüksek güven varsayımı.** Referans `WORKFLOW.md` `approval_policy: never` ve `networkAccess: true` ile çalışıyor.

---

## 3. Aperant (eski adı Auto Claude)

**Ne yapar.** Electron tabanlı bir masaüstü uygulaması (+CLI), AGPL-3.0 ve CLA ile.
- **Akış:** spec hattı → planner → coder (paralel alt ajanlar) → qa_reviewer → qa_fixer → insan incelemesi ve AI destekli semantik merge.
- **Çalışma ortamı:** git worktree izolasyonu, 12'ye kadar ajan terminali, Graphiti belleği, GitHub/GitLab/Linear entegrasyonu.
- **Kod sabitleri:** `MAX_QA_ITERATIONS=50`; 3 ardışık hatadan sonra insana eskalasyon; paralel alt görev varsayılanı 3.
- **Model katmanı:** 2.8-beta'da Claude Agent SDK'dan Vercel AI SDK'ya geçildi ve çok sağlayıcılı hale geldi.

**Sizin çerçevede hangi katmana takılır.** Tek geliştiricinin **iç döngüsü** (inner loop) için referans: faz tasarımı ve planner/coder/QA/PR-review prompt kütüphanesi. Platform bileşeni olarak uygun değil.

**Neyi karşılamaz (WordPress modülünden ERP'ye ve 144 takıma):**
- Sunucu veya daemon modu, çok kullanıcılı yapı, merkezi kuyruk ve dış API yok. Görevler arayüzden giriliyor.
- **Tek repo varsayımı var.** Çok repo desteği talebi "not_planned" olarak kapatıldı ([#1505](https://github.com/AndyMik90/Aperant/issues/1505)).
- İzolasyon yalnızca worktree ile sağlanıyor, container yok. Monorepo'da worktree başına ~1 GB `node_modules` kopyalanıyor ([#1901](https://github.com/AndyMik90/Aperant/issues/1901)).
- Plane ve Jira yok. Yayınlanmış benchmark veya ERP ölçeğinde vaka çalışması yok.

**Riskler.**
- **Bakım.** 2.x **bakım modunda**. Son kararlı sürüm v2.7.6 (2026-02-20), son beta 2026-03-23. PR'lar durduruldu. 3.0 ayrı ve görünmeyen bir repoda sıfırdan yazılıyor, çıkış tarihi yok. 2026 Mayıs–Eylül arasında 116 issue "not_planned" olarak kapatıldı.
- **Abonelik politikası.** 2.7.x Claude Pro/Max OAuth ile çalışıyor. Anthropic 2026-04-04'ten itibaren abonelik OAuth'unun üçüncü taraf ajan araçlarında kullanılmasını yasakladı (ikincil kaynaklar, ör. [VentureBeat](https://venturebeat.com/technology/anthropic-cuts-off-the-ability-to-use-claude-subscriptions-with-openclaw-and)). "Multi-Account Swapping" özelliği bu politikayla çatışma riski taşıyor.

---

## 4. Yürütücü düzeyinde tak-çıkar standartları

| Standart | Katman | Yürütücüyü orkestratörü yeniden yazmadan değiştirir mi? | Kanıt |
|---|---|---|---|
| **ACP** (Agent Client Protocol) | orkestratör/istemci ↔ kodlama ajanı | **En yakın aday.** ~37 ajan yerel destekliyor: Gemini CLI, Copilot, Cursor, Goose, OpenCode, OpenHands, Junie, Hermes Agent, OpenClaw… Claude Code ve Codex resmî adapter'la bağlanıyor. | OpenHands, altı ajanı aynı API ve aynı benchmark düzeneğiyle çalıştırıyor. Registry matrisi (35 ajan): `session/resume` 12, `session/fork` 9, `session/stop` **0** ajanda var. Protokol v1 kararlı, v2 alpha'da. |
| **MCP** | ajan ↔ araç/veri | Hayır, ama araç katmanını ajandan bağımsızlaştırır (tracker yazma, CI, deploy). | AAIF (Linux Foundation) bünyesinde. |
| **AGENTS.md** | repo içi talimatlar | Hayır, ama davranışı taşınabilir kılar. | OpenHands'teki ACP ajanları AGENTS.md'yi kendisi okuyor. AAIF bünyesinde. |
| **A2A** v1.0.1 | ajan ↔ ajan (opak servis) | Bugün pratik değil. Başlıca kodlama ajanları A2A konuşmuyor; Gemini CLI'daki a2a-server "experimental". | 2026-08'de AAIF'e katıldığı bildirildi (ikincil kaynak). |
| **Symphony WORKFLOW.md** | repo içi iş akışı politikası | Tracker katmanında evet; yürütücü katmanında hayır (Codex'e bağlı). | SPEC §5.3.6, §10 |
| **OpenHands Agent Server API** | konuşma ve sandbox | Sandbox'ı ve içteki ajanı değiştirebilir, ama API OpenHands'e özgü ve iki kez büyük değişiklik geçirdi. | V0 → V1 → Canvas |
| **Codex app-server** | Codex'i gömme | Hayır, tek satıcıya bağlı. | Symphony bu protokole bağlı. |
| **Agent Protocol** (agi-inc) | genel REST | Kullanılmamalı; son push 2025-04. | gh api |

**Çıkarım.** Kullanıcının örneğindeki (Hermes → OpenClaw) iki ajan da ACP'yi yerel olarak destekliyor. Yürütücü sınırını **ACP artı sizin ince bir "ExecutorPort" arayüzünüz** olarak tanımlarsanız, yeni bir ajan bir adapter ile takılabilir. Port kabaca şu işlemleri kapsamalı: başlat, devam et, durdur, sonuç artefaktını al (PR/test raporu), maliyet ve durum bilgisini al.

ACP'nin kapsamadığı her şey yine sizin sözleşmenizde tanımlanmalı:
- sandbox provizyonu
- kota
- durdurma ve devam ettirme için eksik yetenekler
- sonuç artefaktı

---

## 5. OpenHands yeterli mi?

**Karar: Hayır, tek başına yeterli değil. Ama "yürütücü çalışma zamanı + sandbox" katmanı için güçlü bir adaydır; orkestratörün arkasında değiştirilebilir bir bileşen olarak konumlanmalı.**

Gerekçeler (kanıtlar JSON'da):
1. **Kapsam.** OpenHands bir ajan çalışma zamanı ve kontrol merkezi; 144 takım ölçeğinde bir teslimat orkestratörü değil. ART düzeyinde iş ayrıştırma, bağımlılıklar, trunk-based merge kuyruğu, DoD kapıları, alpha deploy ve insan geri bildiriminden yeni görev üreten döngünün hiçbiri ürünün içinde yok.
2. **Lisans ve ölçek.** İzole sandbox, çok kullanıcı ve "unlimited concurrent" yalnızca ticari Enterprise'da var. MIT SDK ile kendi havuzunuzu kurmak mümkün, ama işletme yükü size kalır. Resmî oranlarla 144 eşzamanlı sandbox kabaca ~576 GiB RAM ve ~72 vCPU istek demek (kendi hesabımız) ve bu Kubernetes kademesine denk geliyor.
3. **Churn, tak-çıkar hedefiyle çelişiyor.** 12 ay içinde API katmanı iki kez kırıldı. Orkestratörünüz OpenHands'e doğrudan bağlanmamalı; aradaki ACP ve adapter katmanı bu riski yalıtır.
4. **Ölçek ve güvenlik olgunluğu.** Ağustos 2026'da hâlâ deadlock ve serileşme regresyonları vardı; eşzamanlılık limiti hatası ve takılı `RUNNING` konuşmaları açık issue olarak duruyor; CVE-2026-33718 ve sır maskeleme açığı yaşandı. Ek savunma katmanları (ağ çıkış kontrolü, sır enjeksiyonu, denetim) sizin sorumluluğunuzda.
5. **Uzun ufuklu işler için kanıt eksik.** En iyi Commit0 skoru %62,5 (n=16). ERP ölçeğinde çok özellikli teslimat için yayınlanmış kanıt yok. OpenHands'in kendi yazısı bile büyük refaktörlerin "only 80-90% automatable" olduğunu ve en zor kısmın görev ayrıştırması olduğunu söylüyor ([blog](https://www.openhands.dev/blog/automating-massive-refactors-with-parallel-agents)). Yani 90/90 sorununu araç değil süreç çözer: ayrıştırma, kabul kriteri → test eşlemesi ve boşluk analizi.

**Önerilen konumlandırma:**
- **Orkestratör:** Symphony'nin durum makinesi ve tracker sözleşmesini tasarım girdisi olarak kullanan, dayanıklı bir iş akışı motoru üzerinde çalışan kendi orkestratörünüz.
- **Tracker:** Plane için iki işlemli bir adapter.
- **Yürütücü portu:** ACP; ilk sağlayıcı OpenHands Agent Server (MIT). Claude Code, Codex, Goose ve OpenClaw aynı porttan takılabilir.
- **Araç ve politika katmanı:** araçlara MCP ile, repo kurallarına AGENTS.md ile erişim.
- **Aperant:** yalnızca prompt ve faz tasarımı için referans; lisansı AGPL olduğu için kod alırken dikkat.

**Doğrulanamayanlar:**
- OpenHands vaka çalışması sayfası (404 döndü)
- "50× verim" iddiası
- Symphony'nin "%500" iddiasının bağımsız doğrulaması
- Plane için bir Symphony/OpenHands adapter'ı
- Claude Code, Codex ve OpenHands için yerel A2A sunucusu
- Topluluk Symphony çatallarının üretim olgunluğu
