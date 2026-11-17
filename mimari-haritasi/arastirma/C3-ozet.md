# C3: Tak-çıkar gerçekte ne demek, nasıl sağlanır?

Tarih: 2026-09-27. Ayrıntılar ve tüm kaynaklar `C3-tak-cikar.json` dosyasında.

## Kısa cevap

Tak-çıkar, bir aracı başka bir araçla değiştirebilmek demek değildir. Asıl anlamı şudur: bir bileşen değiştiğinde sistemin gerçeği kaybolmaz (durum, spesifikasyon, kabul testi, bilgi) ve değişimin çalıştığı otomatik olarak kanıtlanabilir. Bunun üç koşulu var:

1. **Gerçek araçta değil, sizde durur.** İş alanının durumu kendi olay defterinizde, spec'ler, testler ve talimatlar da depoda tutulur.
2. **Araçla sistem arasında dar ve yazılı bir sözleşme vardır.** Buna port denir. Her adaptörün geçmek zorunda olduğu bir uyumluluk takımı (TCK) bulunur. Mümkün olduğunda sözleşme açık bir standarda dayanır.
3. **Geçiş yolu prova edilmiştir.** Eski ve yeni yol bir bayrakla kademeli olarak kaydırılır, geçişin bitiş tarihi bellidir ve periyodik tatbikat yapılır.

n8n örneğine dönersek: n8n'de bir düğümü değiştirmek kolaydır, çünkü durumu, sırları, yeniden denemeyi ve sürümlemeyi n8n platformu taşır. n8n'in kendisini değiştirmek de aynı sebeple zordur. Sizin çerçevenizde "n8n'in yaptığı işi", yani durumu, sözleşmeyi ve testi, siz üstlenmelisiniz.

## 1. Neden önemli: 2024–2026 değişim kanıtları

- **Model.** Anthropic'in 2025 sürümleri çoğunlukla 12–13 ayda emekliye ayrıldı: Sonnet 3.7 2025-02-19'da çıktı, 2026-02-19'da emekli oldu. Sonnet 4 ve Opus 4 2026-06-15'te emekli oldu. Taahhüt edilen bildirim süresi en az 60 gün ([Anthropic](https://platform.claude.com/docs/en/about-claude/model-deprecations)). Opus 4.7 ve sonrasında `temperature`, `top_p` ve `top_k` artık 400 hatası veriyor, yani yalnızca model adını değiştirmek yetmiyor. OpenAI'nin kaldırma sayfasında 2025'te en az 12, 2026'da en az 9 duyuru var ([OpenAI](https://developers.openai.com/api/docs/deprecations)).
- **API ve platform.** Assistants API 2026-08-26'da kapandı. Agent Builder 2025-10-06'da tanıtıldı, 2026-06-03'te kaldırma kararı açıklandı ve 2026-11-30'da kapanacak. Evals ve reusable prompts de aynı gün kaldırıldı ([OpenAI](https://developers.openai.com/api/docs/deprecations)).
- **Harness.** Terragon 2026-02-09'da kapandı. Crystal 2026-02'de kaldırıldı ([repo](https://github.com/stravu/crystal)). Vibe Kanban'ın şirketi 2026-04-10'da kapandı ([duyuru](https://www.vibekanban.com/blog/shutdown)). 3 milyon kurulumlu Roo Code 2026-05-15'te kapandı ([özet](https://www.bodegaone.ai/blog/roo-code-shutdown-alternatives)). Cody Free/Pro 2025-07-23'te sona erdi ve Copilot Workspace 2025-05-30'da kapandı. Clawdbot 4 gün içinde önce Moltbot, sonra OpenClaw adını aldı ([Wikipedia](https://en.wikipedia.org/wiki/OpenClaw)). OpenHands'in ana deposu artık "any ACP-compatible agent" çalıştıran bir Agent Canvas ([repo](https://github.com/OpenHands/OpenHands)).
- **Sağlayıcı koşulları.** Anthropic'in üçüncü taraf harness ve abonelik kuralı 6 ayda 5 kez değişti: 2026-01-09, 02-19, 04-04, 05-13 ve 06-15 ([VentureBeat](https://venturebeat.com/technology/anthropic-cracks-down-on-unauthorized-claude-usage-by-third-party-harnesses), [TechCrunch](https://techcrunch.com/2026/04/04/anthropic-says-claude-code-subscribers-will-need-to-pay-extra-for-openclaw-support/), [InfoWorld](https://www.infoworld.com/article/4171274/anthropic-puts-claude-agents-on-a-meter-across-its-subscriptions.html)). Koşul metninde "may do so without prior notice" ifadesi geçiyor ([doküman](https://code.claude.com/docs/en/legal-and-compliance)).
- **Düğüm-grafiği araçları.** Workday, Flowise'ı 2025-08'de satın aldı. Flowise'ın deposu 2026-08-13'te arşivlendi. Resmi bir göç yolu sunulmadı. Gerekçe olarak "rigid workflow low-code approach quickly hits the limit" yazıldı ([duyuru](https://github.com/FlowiseAI/Flowise/discussions/6727)). Langflow 18 ay içinde iki kez sahip değiştirdi (DataStax, ardından IBM).
- **Orkestratör.** Netflix Conductor OSS 2023-12'de terk edildi ([TechCrunch](https://techcrunch.com/2023/12/13/orkes-forks-conductor-as-netflix-abandons-the-open-source-project/)). Airflow 3 (2025-04-22) görev kodunun meta veritabanına doğrudan erişimini kaldırdı ([doküman](https://airflow.apache.org/docs/apache-airflow/stable/installation/upgrading_to_airflow3.html)).
- **Sandbox.** Gitpod 2025-09'da Ona adını aldı, OpenAI da Ona'yı 2026-06-11'de satın aldı ([Forbes](https://www.forbes.com/sites/janakirammsv/2026/06/13/openai-buys-ona-to-run-codex-agents-inside-enterprise-clouds/)). CodeSandbox'ı Together AI satın aldı (2024-12).
- **Lisans.** n8n 2022'de Sustainable Use License'a geçti. Terraform 2023'te BUSL lisansına geçti ve OpenTofu 5 ayda GA oldu. Redis 2024'te lisans değiştirdi; ardından Valkey fork'u çıktı ve 2025'te AGPL eklendi. Elastic 2021'de SSPL'e geçti, 2024'te AGPL ekledi.
- **Çerçeve.** AutoGen bakım moduna alındı, yerini Microsoft Agent Framework aldı (GA 2026-04-03). LangChain 1.0 eski işlevleri `langchain-classic`'e taşıdı.

"Araç yarı ömrü" üzerine akademik çalışma bulunamadı (doğrulanamadı). Seçim yanlılığı taşıyan bu örneklemde harness/orkestratör ömrü **8–18 ay**.

## 2. Düğüm-grafiği benzetmesinin sınırı

| Soru | Nerede yaşar? (kanıt) |
|---|---|
| Uzun bekleme | n8n'de 65 saniyeyi aşan beklemede çalışma verisi n8n'in veritabanına yazılıyor ([Wait](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.wait/)). LangGraph'ta durum checkpoint'lere LangGraph'a özgü biçimde serileştiriliyor ([doküman](https://docs.langchain.com/oss/python/langgraph/checkpointers.md)). |
| Zamanlama | n8n'in varsayılan zamanlayıcısı için doküman "Restarts lose pending runs" diyor. Dayanıklı zamanlayıcı 2.36'dan beri var ama varsayılan olarak kapalı ([doküman](https://docs.n8n.io/deploy/host-n8n/configure-n8n/durable-scheduler.md)). |
| Sürümleme ve Git | n8n'de yalnızca Business ve Enterprise planlarında var. Doküman "not full version control" ve "can't detect conflicts on workflows" diyor ([doküman](https://docs.n8n.io/administer/use-source-control-and-environments/use-git-in-n8n.md)). |
| Sırlar | n8n'de `~/.n8n` klasöründeki anahtarla şifrelenip n8n'in veritabanında duruyor ([doküman](https://docs.n8n.io/deploy/host-n8n/configure-n8n/basic-configuration/configuration-examples/set-a-custom-encryption-key.md)). |
| Test | n8n'de veri sabitleme yalnızca geliştirmede kullanılabiliyor, üretimde yok ([doküman](https://docs.n8n.io/build/work-with-data/pin-and-mock-data.md)). |
| Grafik biçimi | Her aracın kendine özgü JSON'u ya da kodu var. Langflow'da girdi veya çıktı değişince bağlantılar kopuyor ([doküman](https://docs.langflow.org/contributing-components)). Zapier dışa aktarması yalnızca Team/Enterprise planlarında ve yalnızca Zapier hesapları arasında çalışıyor. Serverless Workflow 1.0, BPMN ve Arazzo gibi tarafsız standartlara içe veya dışa aktarma bulunamadı (doğrulanamadı). |

Sonuç: düğüm değişimi adaptör değişimidir; orkestratör değişimi durum göçüdür; grafik değişimi yeniden yazımdır. Pilotta Kestra, Postgres tablosunu 15 saniyede bir yoklayan ikinci bir beyindi ve V1-4 görevi `P7D` zaman aşımıyla düştü (A0).

## 3. Değiştirilebilirliği gerçekten sağlayan ilkeler

1. **Gerçeği araç dışında tutmak (olay defteri).** OpenAI'nin Assistants göç rehberi thread'leri taşımak için "use your stored messages instead" diyor ([rehber](https://developers.openai.com/api/docs/assistants/migration)). Netflix'te durum instance-yerel tutuluyordu ve çökmede kayboluyordu ([CDF](https://cd.foundation/blog/community/2026/02/03/netflix-spinnaker/)).
2. **Port/adaptör ve ACL.** Cockburn 2005'te sistemin "equally driven by … automated test" olması gerektiğini yazdı ([Cockburn](https://alistair.cockburn.us/hexagonal-architecture)). Netflix, Temporal'a geçişi bir `CloudOperationRunner` arayüzüyle ve dinamik yapılandırmayla yaptı.
3. **Sözleşme ve TCK.** Kubernetes'in CRI arayüzü sayesinde dockershim kaldırıldığında imajlar değişmeden çalışmaya devam etti ([k8s](https://kubernetes.io/blog/2022/05/03/kubernetes-1-24-release-announcement/)). MCP'nin resmi bir [conformance](https://github.com/modelcontextprotocol/conformance) takımı var ve SDK kademelendirmesi buna bağlı. A2A için de bir [TCK](https://github.com/a2aproject/a2a-tck) var (MUST/SHOULD/MAY seviyeleri, JUnit çıktısı).
4. **Açık standartlar.** Git, OCI, OpenAPI/AsyncAPI/JSON Schema, CloudEvents (2024'te CNCF mezunu), OpenTelemetry ([GenAI kuralları "Development" durumunda](https://github.com/open-telemetry/semantic-conventions-genai)), MCP ve AGENTS.md (LF AAIF), A2A (v1.0, 2026-03), [Agent Client Protocol](https://zed.dev/blog/acp-registry), Agent Skills, SPDX ve CycloneDX, [OpenFeature](https://openfeature.dev/).
5. **Araçtan bağımsız varlıklar.** Roo Code'dan Kilo'ya geçişte modlar ve MCP otomatik taşındı. Buna karşılık "Keys don't port" ve `.roorules → AGENTS.md` dönüşümü elle yapıldı ([Kilo](https://kilo.ai/articles/roo-to-kilo-migration-guide)). Hermes'in `hermes claw migrate` komutu OpenClaw'dan belleği ve skill'leri taşıyor.
6. **Spec ve kabul testi kalıcı varlıktır.** [Spec Kit](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/) 30'dan fazla ajanla çalışıyor. Buna karşı kanıt da var: [Böckeler](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html) araçların fazla Markdown ürettiğini, ajanların spec'i yok sayabildiğini ve spec-as-source yaklaşımının MDD'ye benzediğini gösteriyor. Öneri spec-anchored yaklaşımı ve çalıştırılabilir testler.
7. **Uygunluk fonksiyonları** ([Thoughtworks](https://www.thoughtworks.com/radar/techniques/architectural-fitness-function)). OpenHands'in CI'da çalışan "Deprecation deadlines" kapısı buna bir örnek ([issue](https://github.com/OpenHands/software-agent-sdk/issues/5106)).
8. **Strangler fig ve bayrak, bitiş tarihiyle birlikte** ([Fowler](https://www.martinfowler.com/bliki/StranglerFigApplication.html)).
9. **Taşınabilir CI ve altyapı.** [Dagger](https://docs.dagger.io/) kullanılabilir. [GitHub Actions Importer](https://github.blog/enterprise-software/ci-cd/introducing-github-actions-importer/) yapıların %90'ından fazlasını çeviriyor ama sırlar, runner'lar ve izinler elle taşınıyor. OpenTofu aynı state biçimini kullanıyor.
10. **Çıkış planı ve tatbikat.** DORA md. 28, çıkış planlarının "sufficiently tested" olmasını istiyor ([EUR-Lex](https://eur-lex.europa.eu/eli/reg/2022/2554/oj/eng)).

**Karşı kanıt: soyutlamanın vergisi.** Anthropic'in OpenAI uyumluluk katmanı kendi dokümanında "not … production-ready" olarak geçiyor. Bu katmanda `strict` şema desteği ve prompt caching yok, desteklenmeyen alanların çoğu da sessizce yok sayılıyor ([doküman](https://platform.claude.com/docs/en/api/openai-sdk)). LiteLLM her sağlayıcı sürümünün arkasından koşuyor: GPT-5 çıktıktan bir gün sonra `reasoning_effort` hatası çıktı ([#13402](https://github.com/BerriAI/litellm/issues/13402)), 2026-09'da imzalı thinking bloklarının düşürüldüğü raporlandı ([#41361](https://github.com/BerriAI/litellm/issues/41361)). Anthropic, çerçevelerin "obscure the underlying prompts … harder to debug" etkisi olduğunu yazıyor ([yazı](https://www.anthropic.com/engineering/building-effective-agents)). Hohpe'nin ifadesiyle: "Avoiding one lock-in often comes at the expense of another" ([makale](https://martinfowler.com/articles/oss-lockin.html)). Bir de şu var: OpenAI'nin önerdiği ara göç hedefi olan Prompts nesnesi de sonradan kaldırıldı.

**Ne zaman soyutlamamalı:** Değişim olasılığı da maliyeti de düşük olan katmanlarda (Git, SAFe politikası, OTLP) soyutlama gereksiz. Sağlayıcıya özgü üstün yetenekler (caching, yapısal çıktı) adaptörün içinde kalmalı. İkinci bir somut uygulama yoksa port dar tutulmalı.

## 4. Kararlı ve oynak katmanlar

| Katman | Oynaklık | Standart dikiş | İçeride tutulacak | Değişim testi |
|---|---|---|---|---|
| İş girişi / tracker | Orta (Projects classic, Atlassian DC EOL) | WorkItem JSON Schema + CloudEvents | Kanonik görev modeli, ID eşlemesi | 2 hafta gölge senkron, round-trip farkı 0 |
| SAFe politikası | Düşük (6 ana sürüm/15 yıl) | Politika-kod (YAML/OPA) | Tüm kurallar | Geçen PI kararlarını yeniden oynatma |
| Orkestrasyon | Orta (Conductor, Airflow 3, Temporal API) | Kendi RunPort'u + idempotency anahtarı | Alan defteri, aktivite kodu | Kill -9 kaos testi, 20 altın görevi iki motorda koşturma |
| Ajan harness | **Yüksek** | ACP / başlıksız CLI, AGENTS.md, Skills, MCP | Görev/sonuç zarfı, harness TCK | Altın görevlerde kabul oranı, maliyet, süre toleransı |
| Model | **Yüksek** (12–13 ay) | Sağlayıcıya özgü native adaptör + OTel GenAI | Değerlendirme seti, talimat dosyaları | Emeklilikten önce A/B, kanarya |
| Araç protokolü | Orta | MCP (sabit sürüm) + conformance | Araç sunucuları, yetki | Conformance'ı CI'da koşturma |
| Sandbox | Orta-yüksek | OCI + Dev Container + WorkspacePort | İmajlar, egress, sırlar | İki arka uçta aynı sonuç ve güvenlik testi |
| Kod barındırma | Düşük (Git) / orta (özellikler) | Git + CodeHostPort | Dal ve birleşme politikası | İkinci barındırıcıya aynalama |
| CI | Orta | Depo-içi betik/Dagger, JUnit/SARIF | Betikler, kapılar | Ayda bir ikinci CI'da koşturma |
| Merge queue | Orta (bors-ng arşivlendi) | "Gerekli kontroller" sözleşmesi | Birleşme politikası, karantina | Bir hafta alternatif kuyrukla çalışma |
| Dağıtım | Düşük-orta | OCI + OpenTofu/Compose (GitOps) | Ortam tanımları, rollback | Sıfırdan yalnızca depodan kurulum |
| Önizleme | Orta | Dağıtımla aynı + Dev Container | Şablon, seed | İkinci çalışma zamanında ayağa kaldırma |
| Gözlemlenebilirlik | Düşük / orta (GenAI) | OTel/OTLP | İz kimliği şeması, maliyet | Çift dışa aktarım |
| Kabul spec'leri / oracle | **Düşük olmalı** | Markdown spec + çalıştırılabilir test | Hepsi | Testsiz spec = kırmızı, mutasyon testi |
| Bilgi / bellek | Yüksek (araç biçimleri) | AGENTS.md, ADR, Skills; indeks önbellek olarak | ADR, sözlük, skill'ler | İndeksi silip depodan yeniden kurma |
| İnsan incelemesi | Orta | PR arayüzü + Verdict olayı | Rubrik, karar şeması | İki arayüzden aynı olayların üretilmesi |
| Sağlayıcı sözleşmesi | **Yüksek** (6 ayda 5 olay) | API anahtarı + OTel maliyet | Bütçe, çıkış planı | Çeyreklik bir günlük sağlayıcı kapatma tatbikatı |

## 5. Vakalar: değişimi ne ucuzlatır?

- **Ucuz olanlar:** Docker'dan containerd'ye geçiş (CRI + OCI). AWS'de Redis'ten Valkey'e kesintisiz, yerinde yükseltme, üstelik %20–33 daha ucuz ([AWS](https://aws.amazon.com/about-aws/whats-new/2024/10/amazon-elasticache-valkey)). Terraform 1.5.x'ten OpenTofu'ya geçiş (aynı state). Her birinde protokol ya da biçim aynı kaldı.
- **Orta:** Netflix'in Temporal'a geçişi. Port ve bayrakla yapıldı, iki çeyrek sürdü ve hata oranı %4'ten %0,0001'e indi. Asıl maliyet aktiviteleri idempotent olacak şekilde yeniden yazmaktı. Roo'dan Kilo'ya geçişte açık biçimdeki her şey kolay taşındı, özel biçimdeki her şey elle taşındı.
- **Pahalı olanlar:** Assistants'tan Responses'a geçiş (durum sağlayıcıdaydı). Projects classic (otomasyonlar taşınmadı). Flowise (göç yolu yok).
- **Pilot (Kestra → Temporal):** Ders Netflix'inkiyle aynı. Alan gerçeği Postgres'te tek kaynak olarak kalmalı ve Temporal yalnızca yürütme durumunu tutmalı. Eski ve yeni yol bir port arkasında bayrakla kaydırılmalı ve geçişin bitiş tarihi olmalı. Bu yapılmazsa "iki beyin" kalıcı hale gelir.

## 6. Dikiş haritası ve kurallar

```
Tracker ─[WorkItemPort/CloudEvents]─► ALAN DEFTERİ (Postgres, append-only) ◄─[PolicyPort]─ politika-kod
                                             │ ▲ olaylar
                                  [RunPort]  ▼ │
                                 Temporal (yalnız yürütme durumu)
                                             │ aktivite
                    [AgentExecutorPort: TaskEnvelope→ResultEnvelope | ACP/CLI]
                        ├─ ModelPort (native API)  ├─ MCP araçları  └─ WorkspacePort (OCI/devcontainer)
                                             │ PR
             Git ─[CodeHostPort]─ CI (Dagger/betik, JUnit) ─ merge queue ("gerekli kontroller")
                                             │ OCI
                         Dağıtım (OpenTofu/Compose) → alpha.example.com → ReviewPort (Verdict olayı) → defter
             OTel/OTLP her adımda | Depoda kalıcı: spec, kabul testi, altın görevler, AGENTS.md, Skills, şemalar, TCK'ler
```

**Kurallar**

- **K1.** Her dış araç bir port arkasında durur. Port sözleşmesi depoda sürümlenir. TCK'den geçmeyen adaptör devreye alınmaz.
- **K2.** Alan gerçeği tek bir defterde tutulur. İki sistemin aynı alanı yazması, yani "iki beyin", CI'daki bir uygunluk fonksiyonuyla engellenir.
- **K3.** Spec'ler, kabul testleri, altın görev seti, AGENTS.md, Skills ve politika dosyaları depoda, araçtan bağımsız biçimde tutulur. Sağlayıcının nesne deposuna iş kuralı konmaz.
- **K4.** Önce açık standart kullanılır. Model tarafında en küçük ortak payda sunan bir geçit yerine sağlayıcıya özgü native adaptör yazılır.
- **K5.** Soyutlamaya yapılacak yatırım oynaklık ile değişim maliyetinin çarpımına göre belirlenir. Düşük oynaklıklı katmanlarda soyutlama eklenmez.
- **K6.** Her geçiş strangler, bayrak ve bitiş tarihiyle yapılır. Bitiş kriteri: altın görevlerde kabul oranının eşit ya da daha iyi olması.
- **K7.** Her çeyrek oynak katmanlardan biri ikincil adaptöre geçirilir ve bir gün boyunca gerçek işle çalıştırılır.
- **K8.** Harness, SDK, model ve spec sürümleri sabitlenir. Güncellemeler kanaryayla yapılır. Kaldırma tarihleri CI'da bir kapıyla izlenir.
- **K9.** CI'daki uygunluk fonksiyonları şunları denetler: çekirdek hiçbir sağlayıcı SDK'sını import etmez; her spec en az bir teste bağlıdır; bütün TCK'ler yeşildir; defter dışında alan durumu yazan kod yoktur.
- **K10.** Otomasyonda abonelik OAuth'u yerine API anahtarı kullanılır. Her sağlayıcı için ayrı bütçe tanımlanır.

**Ölçek notu.** 144 takım araçları ayrı ayrı bağlarsa entegrasyon N×M olur; standart dikişler (ACP, MCP) bunu N+M'ye indirir. TCK'ler merkezi platform ekibinde tutulmalı. 144 takımda ölçülmüş vaka bulunamadı.

**Sınırlar.** Terragon sayfası sertifika hatası verdi. OpenHands V0 tarihi ikincil kaynaktan. Ayrıntı JSON `meta.sinirlar`'da.
