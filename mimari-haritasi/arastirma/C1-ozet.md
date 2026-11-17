# C1 – Bu döngüyü hazır uygulayan bir sistem var mı? (özet)

Tarih: 27.09.2026. Tüm puanlar, kanıtlar ve bağlantılar `C1-hazir-sistemler.json` dosyasında: 32 aday, R1–R12 matrisi. Yıldız ve son push bilgileri 27.09.2026 tarihli `gh api` çıktısından alındı. Puanlama: 0 = yok, 1 = kısmi, 2 = belgelenmiş ürün davranışı. Toplam puan R1–R11 üzerinden, en fazla 22.

## Kısa cevap

**Hayır.** Aranan döngü şu: takipçi → N izole ajan → tek entegrasyon dalında merge queue → alpha ortamına dağıtım ve doğrulama → orada insan incelemesi → issue → otomatik yeni görev → 144 ekiplik portföy. İncelenen 32 adayın hiçbiri bu döngünün tamamını belgelenmiş davranış olarak sunmuyor.

Döngünün iki halkası hiçbir üründe yok: **R7** (uzak ortama dağıtıp orayı doğrulamak) ve **R8** (dağıtılmış ortamdaki incelemeden otomatik görev üretmek). Hiçbir aday bu ikisinden 2 almadı.

En yakın adaylar:
- **GitLab Duo Agent Platform**: 17/22 puan, 6 kalemde 2.
- **Warp Factories**: 16/22 puan. Kanıtın tamamı kapalı erken erişimdeki ürün sayfası.
- **Açık kaynakta Gas Town** (14/22) ve **LangChain Open SWE** (13/22).

## (a) R1–R11'in çoğunda 2 alan var mı?

Sınırda tek aday var: GitLab Duo Agent Platform. 11 kalemin 6'sında 2 alıyor (R2, R3, R4, R5, R6, R9). Ancak bu 2'lerin yarısı ajan platformundan gelmiyor, GitLab'ın DevOps platformundan geliyor:
- merge trains ([belge](https://docs.gitlab.com/ci/pipelines/merge_trains/))
- grup/alt grup/epik hiyerarşisi ([GitLab](https://about.gitlab.com/blog/gitlab-for-agile-portfolio-planning-project-management/))
- self-managed ve çevrimdışı kurulum ([belge](https://docs.gitlab.com/administration/gitlab_duo_self_hosted/offline_deployment/))

Önemli bir kısıt var: akış tetikleyicileri yalnız insan eylemiyle çalışıyor. Belge bunu şöyle söylüyor: "a service account user, or another flow, cannot activate a trigger" ([tetikleyiciler](https://docs.gitlab.com/user/duo_agent_platform/triggers/)). Yani bir botun veya inceleme ajanının açtığı issue ajanı kendiliğinden başlatamaz. Dağıtılmış uygulamadan MR'a geri bildirim toplayan Visual Review Tools da 17.0'da kaldırıldı ([issue](https://gitlab.com/gitlab-org/gitlab/-/issues/387751)).

## En yakın adaylar

| # | Aday | Toplam | 2 alan kalemler | Kritik eksik |
|---|---|---|---|---|
| 1 | [GitLab Duo Agent Platform](https://docs.gitlab.com/user/duo_agent_platform/) | 17 | R2 R3 R4 R5 R6 R9 | Tetikleyici yalnız GitLab'da ve yalnız insan eylemiyle; R7, R8, R10 kısmi; ticari lisans |
| 2 | [Warp Factories](https://www.warp.dev/factories) | 16 | R1 R2 R3 R5 R10 | Kapalı erken erişim, tescilli, bağımsız kanıt yok; merge queue ve portföy yok |
| 3 | [Gas Town + Beads](https://github.com/gastownhall/gastown) | 14 | R3 R4 R6 R11 | Tek makine, bus factor ≈ 1 (steveyegge 4.831 commit). Bir ajan admin yetkisiyle CI'ı atlatıp birleştirdi ([#4442](https://github.com/gastownhall/gastown/issues/4442)) |
| 4 | [LangChain Open SWE](https://github.com/langchain-ai/open-swe) | 13 | R2 R4 R5 R11 | Tek harness (Deep Agents); README "stability… not guaranteed" diyor |
| 5 | [GitHub Copilot cloud agent + Agent HQ](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent) | 12 | R2 R5 | SaaS; görev başına tek PR, 59 dakika sınırı; Jira/Linear'dan yalnız "doğrudan PR" |
| 6 | [GitHub Agentic Workflows (gh-aw)](https://github.com/github/gh-aw) | 12 | R2 R3 R5 | 0.x sürüm; güvenlik açığı nedeniyle sürüm aralığı geri çekildi |
| 7 | [Atlassian Agents in Jira + Rovo Dev](https://www.atlassian.com/blog/announcements/ai-agents-in-jira) | 11 | R3 R5 R9 | Yalnız Cloud ([Rovo Dev](https://www.atlassian.com/software/rovo-dev)) |
| 8 | [Cursor Cloud Agents](https://cursor.com/docs/cloud-agent) | 11 | R2 R5 | Self-host yalnız worker düzeyinde; ajan döngüsü Cursor bulutunda ([belge](https://cursor.com/docs/cloud-agent/self-hosted/pool)) |
| 9 | [OpenHands](https://github.com/OpenHands/OpenHands) | 10 | R2 R3 | Ölçek, RBAC ve bütçe Enterprise'da; lisans PolyForm Free Trial ([enterprise](https://github.com/OpenHands/enterprise)) |
| 10 | [OpenAI Symphony](https://github.com/openai/symphony) | 9 | R1 R4 | Yalnız Codex; kalıcı veritabanı yok ([SPEC](https://github.com/openai/symphony/blob/main/SPEC.md)) |

Diğerleri 3–10 puan aldı: Coder, Ona, Devin, Agent Orchestrator, Kiro, Codex, Cyrus, Claude ailesi, Temporal, Factory, Aperant, Sculptor, Plane, Linear, Vibe Kanban, Tembo, CrewAI/AutoGen/MAF, Jules, Kilo, Amp, Antigravity, MetaGPT/ChatDev. Ayrıntılar JSON'da.

## (b) Hangi sistem hangi katmana fiş olur?

| Katman | Fiş olarak alınabilecekler | Not |
|---|---|---|
| Görev kaynağı / insan arayüzü | Plane Agent Run ([Beta](https://developers.plane.so/dev-tools/agents/overview)), Linear AgentSession ([belge](https://linear.app/developers/agents)), Jira, GitHub Issues, GitLab work items | Ortak `TaskSource` sözleşmesi için Symphony'nin "portable read kernel" tanımı iyi başlangıç ([SPEC](https://github.com/openai/symphony/blob/main/SPEC.md)). Plane'de 5 dakika güncellenmeyen çalışma "stale" oluyor; heartbeat şart. |
| Dağıtıcı / orkestratör | Temporal ([depo](https://github.com/temporalio/temporal)), LangGraph (Open SWE), OpenHands automation ([Beta](https://github.com/OpenHands/automation)), MAF iş akışları ([depo](https://github.com/microsoft/agent-framework)) | 144 ekip için kota, WIP ve öncelik yönetimi hiçbir üründe yok. Bu kısım çerçevenin kendi kodu olmalı; motor değiştirilebilir kalmalı. |
| Yürütücü (harness) | Claude Code / Agent SDK, Codex app-server ([belge](https://developers.openai.com/codex/app-server)), OpenHands Agent Server ([SDK](https://github.com/OpenHands/software-agent-sdk)), droid exec ([belge](https://docs.factory.ai/droid-exec/overview)); yönetilenler: Copilot, Devin, Cursor, Jules, Kiro, Claude Managed Agents | 2026'da en hızlı değişen katman. Harness süreç/HTTP/ACP sınırıyla soyutlanmalı. |
| Sandbox | Coder workspaces ([belge](https://coder.com/docs/ai-coder/agents)), OpenHands Docker/K8s, Claude Managed Agents self-hosted sandbox ([belge](https://platform.claude.com/docs/en/managed-agents/overview)), E2B ([depo](https://github.com/e2b-dev/E2B)), container-use ([depo](https://github.com/dagger/container-use)), Actions/GitLab runner | Daytona'nın açık deposu Haziran 2026'dan beri bakımsız ([depo](https://github.com/daytonaio/daytona)). Tembo'ya göre ciddi ekipler derleme için 32 GB, bazıları test ve tip denetimi için 128 GB RAM istiyor ([blog](https://www.tembo.io/blog/goodbye-background-agents)). |
| VCS + CI + merge | GitHub merge queue ([belge](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue)), GitLab merge trains, gh-aw (CI içinde ajan adımları), Open SWE `/baby-sit` | Merge queue ajanda değil VCS'de zorunlu olmalı. Gas Town'daki admin bypass olayı bunun gerekçesi. |
| Dağıtım + doğrulama | GitHub Actions environments, GitLab Review Apps ([arşiv belge](https://archives.docs.gitlab.com/16.7/ee/ci/review_apps/index.html)) | Hiçbir aday alpha ortamını doğrulamıyor. Doğrulama en fazla sandbox içinde tarayıcı/video ile yapılıyor ([Cursor](https://cursor.com/docs/cloud-agent), [Devin](https://docs.devin.ai/work-with-devin/testing-and-recordings.md)). **En büyük boşluk.** |
| İnceleme → görev | Issue ataması (GitHub, GitLab, Linear, Plane) | Ölçekte darboğaz insan incelemesi. Warp'ın panosunda en büyük kuyruk "Awaiting maintainer" (1.816) ([build.warp.dev](https://build.warp.dev)). dotnet/runtime'da PR'ların %67,9'u birleşti ([.NET blog](https://devblogs.microsoft.com/dotnet/ten-months-with-cca-in-dotnet-runtime/)). |
| Kalite / oracle | Claude Code hook'ları (TaskCompleted exit 2) ([belge](https://code.claude.com/docs/en/agent-teams)), gh-aw safe-outputs, Kiro spec akışı, Sculptor "önce başarısız test" ([depo](https://github.com/imbue-ai/sculptor)) | Korunan test, DoD kanıtı ve gap analizi hiçbir üründe hazır değil. |
| Portföy | Jira, GitLab grupları/epikleri, Plane | Takipçiler portföyü tutuyor, ama ART düzeyinde ajan kotası uygulamıyor. |

## (c) ERP/HRMS büyüklüğünde teslim kanıtı var mı?

**Bulunamadı.** Mevzuat içeren (bordro, SGK, vergi) ve DoD'ye kadar götürülmüş, bu büyüklükte kamuya açık bir ajan teslimatı bulamadım. Satır sayısı olarak büyük üretimler var:

- **OpenAI.** 3–7 mühendis ~5 ayda ~1 milyon satır ve ~1.500 PR üretti, "no manually-written code" kuralıyla. Ürün bir iç beta. Yazarlar yaklaşımın genellenemeyebileceğini söylüyor ([ayna](https://jaytaylor.com/notes/node/1770842156000.html)).
- **Anthropic.** 16 paralel ajan 2 haftada, ~20.000 $ ile 100.000 satırlık bir C derleyicisi yazdı. Derleyici Linux 6.9'u derliyor. Başarının anahtarı GCC'nin "known-good oracle" olarak kullanılması ([Anthropic](https://www.anthropic.com/engineering/building-c-compiler)).
- **Cursor.** Yüzlerce ajanla 1,2 milyon satırlık bir Windows 7 emülatörü ve 1,6 milyon satırlık bir Excel yazıldı. Ama "Twenty agents would slow down to the effective throughput of two or three" notu da var ([Cursor](https://cursor.com/blog/scaling-agents)).
- **Hedefin ölçeği.** frappe/hrms deposunda ~2,3 MB Python ve ~0,74 MB JS/Vue var, 11.173 commit ile. Üstelik Frappe/ERPNext altyapısı ve Türkiye yerelleştirmesi bu sayılara dahil değil ([depo](https://github.com/frappe/hrms)).

Sonuç: satır sayısı artık tek başına engel değil; asıl engel oracle. Derleyici için hazır bir oracle vardı. HRMS için mevzuat tabloları, altın bordro vakaları ve korunan kabul testleri önce üretilmek zorunda. "90/90'da tıkanma" riski buradan geliyor.

## (d) Hüküm

1. **Hazır çerçeve yok. Hazır fişler var.** Doğru yol ince ama sahibi belli bir çerçeve yazmak. Çerçevenin içeriği: sözleşmeler, durum makinesi, kota/WIP, kalite kapıları, dağıtım doğrulama, geri bildirim yönlendirme. Her katmanda hazır ürünler fiş olarak takılır.
2. **Tak-çıkar zorunlu.** Son 12 ayda bu katmanlarda ciddi kapanış ve geri çekilmeler yaşandı:
   - Roo Code kapandı ([depo](https://github.com/RooCodeInc/Roo-Code)).
   - Vibe Kanban kapandı ([duyuru](https://www.vibekanban.com/blog/shutdown)).
   - Terragon kapandı ([duyuru](https://docs.terragonlabs.com/docs/resources/shutdown)).
   - Coder Tasks ve AgentAPI geri çekildi ([Coder](https://coder.com/docs/@v2.36.0/ai-coder/tasks), [AgentAPI](https://github.com/coder/agentapi)).
   - OpenHands deposu baştan yapılandırıldı ([FAQ](https://github.com/OpenHands/OpenHands/issues/14841)).
   - AutoGen bakım moduna geçti ([depo](https://github.com/microsoft/autogen)).
   - Daytona'nın açık deposu bakımsız kaldı ([depo](https://github.com/daytonaio/daytona)).
   - Agent Orchestrator'da GitLab/Linear desteği düştü ([belge](https://github.com/Untrivial-ai/agent-orchestrator/blob/main/frontend/src/docs/content/plugins/trackers/index.mdx)).
   - Kilo Code satın alındı ([duyuru](https://www.businesswire.com/news/home/20260715437804/en/Anaconda-Acquires-Kilo-Code-to-Power-the-Trillion-Token-Enterprise)).
3. **"OpenHands yeterli olabilir" sezgisi yürütücü katmanında doğru, çerçevenin tamamı için yanlış.**
   - Güçlü yanlar: MIT lisanslı SDK ve Agent Server, Docker/K8s çalışma alanları ve ACP ile Claude Code/Codex/Gemini sürebilmesi ([legacy README](https://github.com/OpenHands/legacy)).
   - Eksik olanlar: takipçi adaptör sözleşmesi, merge queue, dağıtım doğrulama, oracle ve portföy.
   - Lisans: "sınırsız paralel konuşma", RBAC ve bütçe PolyForm Free Trial lisanslı Enterprise'da; kullanım yılda 30 günle sınırlı ([enterprise](https://github.com/OpenHands/enterprise)).
   - Mimari: "Plane → openhands 1…12" şeması, OpenHands'i çerçeve değil **executor havuzunun bir tipi** olarak okursa doğru olur.
4. **Aperant gözlemi doğru.** Aperant tek makinede en fazla 12 terminal çalıştırıyor, Claude Pro/Max OAuth kullanıyor ve kendi QA döngüsüyle main'e AI ile merge yapıyor. 2.x sürümü bakım modunda ([depo](https://github.com/AndyMik90/Aperant)). ERP ölçeği için bir kanıt değil.
5. **Yüzeysel benzetmeden kaçın.** MetaGPT/ChatDev ve Claude Code agent teams "rol = ajan" kurgusu kuruyor, ama teslimat altyapısı sağlamıyor. Agent teams'in kendi sınırları var: oturum başına tek takım, iç içe takım yok, oturum devamında takım arkadaşları geri gelmiyor ([belge](https://code.claude.com/docs/en/agent-teams)). SAFe hiyerarşisi takipçide kalmalı. Ajanlar iş öğesi başına izole yürütücü olmalı.
6. **Önerilen ilk adımlar.**
   - Symphony SPEC, Linear AgentSession ve Plane Agent Run'dan tek bir TaskSource/Dispatcher sözleşmesi türetmek.
   - Executor arayüzünü en az iki harness ile kanıtlamak.
   - Merge queue'yu VCS'de zorunlu kılmak.
   - R7/R8 katmanını kendin tasarlamak: alpha'ya dağıtım, smoke/E2E testleri ve bulgunun issue'ya çevrilmesi.
   - HRMS için önce oracle üretimini planlamak.

**Sınırlamalar.** Oturumun web arama kotası araştırmanın son bölümünde doldu. Sonraki doğrulamalar bilinen URL'ler ve `gh api` ile yapıldı. Agents in Jira'nın GA tarihi yeniden doğrulanamadı. Kapalı ürünlerin (Warp Factories, Ona, Factory, Cursor) puanları resmî sayfalara dayanıyor; bağımsız kanıt çoğunda yok.
