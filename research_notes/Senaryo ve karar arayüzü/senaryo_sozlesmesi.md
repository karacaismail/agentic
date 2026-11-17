# Senaryo presetleri ve düzenlenebilir ECA sözleşmesi

27 Eylül 2026. Bu çalışma arayüz için araştırma ve sözleşme önerisidir. Fabrika kurulmadı, çalıştırılmadı veya değiştirilmedi. `otomasyon coding 2` değiştirilmedi. Aşağıdaki kombinasyonların tamamı **taslak / nitelendirme yapılmadı** durumundadır. Ayrıntılı alanlar, 12 bulgu ve 14 önerilen deney [JSON dosyasındadır](<./senaryo_sozlesmesi.json>).

Son kullanıcı açıklamasıyla **RDD → TDD**, **Jev → TypeSafe**, **Laya → NandhaKishorM/laya** olarak düzeltildi. Kimlik artık açık soru değildir. Bu iki ürünün özellik doğrulaması diğer araştırmacının kapsamındadır; kimliğin biliniyor olması bütün yeteneklerinin doğrulandığı anlamına gelmez.

## Hangi teknoloji kombinasyonları gerçekten farklı seçenekler oluşturuyor?

### Takeaway

Araçları aynı listede birbirinin yerine koymak yerine, **görev yaşam döngüsü, kodlama çalışanı, bağımsız doğrulama, dış etki yazarı ve operasyon geçidi** rollerini ayırmak gerekir. İlk karşılaştırma PS01 ile PS02 arasında, aynı kabul deneyleri üzerinden yapılabilir. Bu bir kazanan ilanı değildir.

| Preset | Yaşam döngüsü sahibi | Çalışan ve ek rol | Ne zaman anlamlı? |
| --- | --- | --- | --- |
| PS01 | Temporal | OpenHands kodlama | Uzun bekleme ve açık toparlanma sözleşmesi gereken doğrudan aday |
| PS02 | Kestra | OpenHands kodlama | Görünür YAML akışı isteniyorsa; eski pilotun doğruluğu varsayılmaz |
| PS03 | Temporal | Kestra giriş/zamanlama, OpenHands kodlama | Kestra için ayrıca somut entegrasyon ihtiyacı varsa |
| PS04 | Temporal | Hermes planlama/kodlama profilleri | Hermes çalışan yeteneklerini mevcut dış yönetim altında değerlendirmek için |
| PS05 | Temporal | OpenHands kodlama, OpenClaw operasyon geçidi | Ayrı sohbet/operasyon kanalı gerekiyorsa |
| PS06 | Hermes Kanban | Hermes çalışanları | Tek hostta düşük riskli keşif ve nitelendirme alternatifi |

Her preset ortak olarak görev kaynağı adaptörü, doğrulama koşucusu, GitHub teslim adaptörü, alpha dağıtım kimliği ve insan kabul kaydı ister. Bunlar ürün etiketine basılınca kurulmuş olmaz. Ekip ve eşzamanlı worker sayıları ölçülene kadar boş bırakılır.

### Cited Findings

Kestra durumsuz bir zamanlayıcı değildir. Resmî alt akış belgesi retry ve restart kapsamlarını açıkça ayırır; task-level retry tamamlanmış çocuk adımları tekrar çalıştırabilir. PS02'de iş yaşam döngüsünün sahibi Kestra olabilir. PS03'te ise Kestra kendi execution kaydını korurken canonical görev geçişlerini Temporal yönetir. “Kestra durum tutmaz” metni bu nedenle değiştirilmelidir. [Kestra alt akış semantiği](https://kestra.io/docs/how-to-guides/subflow-executions)

Temporal replay deterministik komut sırası ister ve çalışan workflow kodu değişirken sürümleme düşünülmelidir. Bu garanti PR'ın doğru olduğunu veya bir harici işlemin yalnız bir kez gerçekleştiğini tek başına kanıtlamaz. [Temporal Workflow Definition](https://docs.temporal.io/workflow-definition)

OpenHands SDK, Python ve REST üzerinden kodlama ajanı oluşturma yüzeyi sunar; konuşma durumunu kaydetme ve devam ettirme de belgelenmiştir. Bunun yanında Git/deploy etkilerinin tekilleştirilmesi, kabul oracle'ı ve alpha kimlik zinciri bizim sözleşmemizde kalır. Konuşma arşivinin hassas içerik taşıyabileceği gözetilmelidir. [OpenHands SDK](https://docs.openhands.dev/sdk), [Persistence](https://docs.openhands.dev/sdk/guides/convo-persistence)

Hermes Kanban için “dayanıklılık yok” demek doğru değildir: kalıcı pano, crash reclaim ve iterasyon sınırları vardır. Resmî sınır tek hosttur; ortak panoyu iki hostta çalıştırmak desteklenmez. İterasyon sınırı, bütün görev ağacının para ve aktif süre kotasının kanıtı olarak alınmamalıdır. [Hermes Kanban](https://hermes-agent.nousresearch.com/docs/user-guide/features/kanban)

OpenClaw alt ajanları destekler; buna karşılık gateway karşılıklı güvensiz kullanıcıları izole eden bir çok kiracılı güvenlik sınırı değildir. PS05 bu yüzden onu dar yetkili operasyon rolünde ele alır. Bu bir ürünün bütün kullanımlarını reddetme kararı değildir. [Alt ajanlar](https://docs.openclaw.ai/tools/subagents), [Güven modeli](https://docs.openclaw.ai/gateway/security)

### Inferences

Bütün ara durumları tek motora zorla taşımak gerekmez. Tek sahiplik, **bir iş alanının geçişini kimin yetkili olarak yazdığı** meselesidir: worker kendi oturumunu, CI kendi koşusunu, deploy adaptörü kendi receipt'ini tutabilir. Bunların hiçbiri tek başına görevi “insan kabul etti” durumuna çeviremez.

“Tak-çıkar”ın anlamı yeni ürünün schema, dış etki, iptal, güven sınırı, checkpoint ve kanıt sözleşmelerini karşılamasıdır. Çalışan işler eski adaptörde bitirilebilir; yeni işe yeni adaptör atanabilir. Ara durum göçü ayrı nitelendirme ister. Her motorun checkpoint'ini diğerinin okuyabildiği varsayılmaz.

Scrum/SAFe rol isimleri öncelik ve bağımlılık yönetimi için yararlı olabilir; 12 ekip oluşturmak 12 güvenilir paralel çalışma hattının oluştuğu anlamına gelmez. RAM, CPU, disk, model kotası, build/browser yükü ve insan kabul kuyruğu birlikte ölçülür.

### Gaps

Kurulu ürün sürümleri, gerçek GitHub planı/rulesetleri, Plane API sürümü, runner kaynak profili ve adaptörlerin yetenek uygunluğu bu araştırmada doğrulanmadı. Presetlerden hiçbiri canlı E2E kanıtı taşımaz. Önceki pilotu ne otomatik aklama ne de ürünü toptan eleme gerekçesi olarak kullandım.

## Düzenlenebilir ECA ve olay simülasyonu nasıl yanıltmadan çalışmalı?

### Takeaway

Arayüz bir **plan tasarım aracı** olmalı. Kullanıcı kuralı kapatabilmeli; sonuç ve risk görünür kalmalı. Anahtarın açık olması riskin çözüldüğü anlamına gelmemeli. “Planlandı”, “simülasyonda geçti”, “belirtilen ortamda nitelendirildi” ve “canlı koşuda gözlendi” ayrı durumlar olmalı.

### Cited Findings

Mevcut [hesap.ts](</Users/w6x/Documents/otomasyon coding/fabrika-karar-merkezi/src/durum/hesap.ts:102>), ilişkili kurallardan herhangi biri açık olduğunda sorunu `kapsandi` sayıyor. Bu, birden çok zorunlu kontrolü veya uygulama kanıtını değerlendirmiyor. [tipler.ts](</Users/w6x/Documents/otomasyon coding/fabrika-karar-merkezi/src/veri/tipler.ts:16>) ECA'yı olay/koşul/eylem metni olarak tutuyor.

[JSON export](</Users/w6x/Documents/otomasyon coding/fabrika-karar-merkezi/src/sayfalar/Tasarimci.tsx:82>) yalnız seçim durumunu kaydediyor. PDF raporunda kapalı kurallar ve uyarılar zaten var; eksik olan JSON'un da bağımsız okunabilir risk, kaynak ve kanıt manifestini taşımasıdır. [Faz değişimi](</Users/w6x/Documents/otomasyon coding/fabrika-karar-merkezi/src/durum/depo.tsx:80>) kullanıcı anahtarlarını yeniden atıyor; [küme silme](</Users/w6x/Documents/otomasyon coding/fabrika-karar-merkezi/src/durum/depo.tsx:94>) aşamaları ilk kalan kümeye aktarıyor. Bunlar sessiz mimari değişiklik üretebilir.

CloudEvents'in `source + id` ikilisi olay tekrarını tanımlamak için uygun bir zarf sağlar. İş etkisi kimliği bunun yerine geçmez; PR açma veya dağıtım gibi etkiler ayrı tekilleştirme anahtarı ister. [CloudEvents v1.0.2](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md)

### Inferences

Önerilen ECA sözleşmesi şu sırayı izler:

1. Schema ve referans kontrolü; sonra kimlik, yetki, kişisel Git politikası ve görev nesli.
2. Terminal/iptal/fencing; ardından belirsiz dış etki uzlaşması ve global görev bütçesi.
3. Normal ilerleme; en son bildirim ve görünüm güncellemesi.

Koşullar güvenli bir AST ile `all/any/not/eq/in/lt/lte/gt/gte/exists` işlemlerinden oluşmalı. Rastgele JavaScript, shell ve ağ isteği çalıştırılmamalı. Veri eksikse sonuç `unknown` olur; yan etkili izin için sessizce doğru kabul edilmez.

Aynı etki için deny/hold allowdan önce gelir. Sayısal öncelik yetki sınırlarını geçersiz kılamaz. Aynı görev sürümü için iki uyumsuz geçiş varsa `unresolved_conflict` gösterilir. Bağımlılık döngüsü hatadır. Rule dependency grafiği ile task dependency grafiği ayrı tutulur.

Dış etki sözleşmesi `intent → dispatch → receipt/unknown → read-only reconcile` olmalı. Zaman aşımı “işlem olmadı” kanıtı değildir. İptal edilen eski worker sonuçları yeni görev nesline yazamamalı.

Simülasyon tamamen yerel ve yan etkisiz olmalı. İz; girdi/politika digest'i, sanal saat, eşleşen ve bastırılan kurallar, veri kaynağı, çatışma, önerilen eylem ve kalan riski içermeli. JSON'da 14 **not_run** örnek var: tekrarlı webhook, kaybolan PR yanıtı, heartbeat varken ilerlememe, OOM kanıtı olmadan exit137, host doluyken doğrulanmış OOM, eski worker yazımı, skipped CI, yanlış alpha SHA, kapalı güvenlik kapısı, market paketi yetki büyütmesi, çakışma, bağımlılık döngüsü, bilinmeyen yetenek ve eski dağıtım kabulü.

Export `planning_only`, `deployable:false` taşımalı. Kapalı kapı `draft_unsafe` üretir; kullanıcı tercihi sessiz düzeltilmez. Yeteneği bilinmeyen araç veya eksik binding `draft_incomplete` olarak görünür. Bu sınıflar kurulum onayı değildir. Faz/preset değişiminde varsayılanlar ile kullanıcı override'ları ayrı tutulmalı; etki farkı gösterilmelidir.

### Gaps

Önerilen AST ve kural listesi tam bir motor uygulaması değildir. JSON'daki kurallar kavramsal örneklerdir; tam izin kümesi ve derleyici yapılmış sayılmaz. Simülasyon sonuçları henüz yoktur. Bütün güvenlik kapıları açık olsa bile “güvenli sistem kuruldu” sonucu çıkarılamaz.

## Skill, ajan, MCP havuzları ve repo belgeleri nasıl nitelendirilmeli?

### Takeaway

Havuzlar mantıklıdır; dış market doğrudan çalışma zamanı yetki dağıtıcısı yapılmamalıdır. **Büyük katalog, küçük göreve uygun seçim, sürüm/digest ile nitelendirme ve süreli görev yetkisi** birlikte kullanılmalıdır. Skill üretimi ile onaylama iki ayrı işlemdir.

### Cited Findings

Agent Skills standardı içerik paketinin biçimini tanımlar. `allowed-tools` deneysel olduğundan her çalıştırıcıda aynı izin sınırını uyguladığı varsayılamaz. Bu standart evrensel “20 skill'i geçme” kuralı koymaz. [Agent Skills Specification](https://agentskills.io/specification)

MCP güvenlik belgesi token passthrough'u yasaklar, session kimliğini authentication yerine kullanmayı reddeder ve yerel server/OAuth keşfi risklerini açıklar. “MCP bağlandı” bu nedenle yetkinin doğru sınırlandığı anlamına gelmez. [MCP Security Best Practices](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices)

Mevcut [CODEOWNERS açıklaması](</Users/w6x/Documents/otomasyon coding/fabrika-karar-merkezi/src/veri/belgeler.ts:360>) zorunlu onayın kendiliğinden uygulandığı izlenimi veriyor. GitHub belgesi bu zorunluluğu branch protection/ruleset ile ilişkilendiriyor; dosya tek başına yeterli değil. [GitHub Code Owners](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)

### Inferences

Paket yolu: keşif → karantina → kaynak/bağımlılık incelemesi → önceden yazılmış kabul ölçütü → sandbox testi → bağımsız regresyon → iç katalog onayı → görev kapsamlı yetki → gözlem → iptal/emeklilik. Ajan yeni skill önerebilir; kendi üretimini tek başına yetkilendirip canlıya alamaz. Kaizen/OODA çıktısı da önce eval ve öneri olur.

Manifest; ürün kimliği, URL, lisans, sürüm, digest, runtime uyumu, veri sınıfı, gereken araç/ağ/dosya yetkileri, test veri seti ve nitelendirme sonucunu tutmalı. Aktif koşu sabit sürümü kullanmalı. Revocation yeni çağrıları ve çocuk yetkilerini etkileyebilmeli.

Başlangıçta sözleşme/AC yorumlama, planlama, TDD-red doğrulama, kod değişikliği, bağımsız kabul, hata tanısı, dış etki uzlaşması ve alpha kanıt paketi yetenekleri yeterli bir çekirdek oluşturur. Migration, güvenlik, erişilebilirlik, yük testi, bordro oracle'ı ve incident-to-eval ihtiyaca göre eklenir. Bunların 10 veya 18 ayrı dosya olması zorunlu değildir.

MCP için server kimliği ve tool schema digest'i kadar principal, project/repo, görev nesli, tool adı, resource scope, egress, süre ve iptal bilgisi gerekir. HTTP yetkilendirmesi ile stdio süreç yetkisi ayrı incelenir. Child ajan parent yetkisinden geniş scope alamamalı. Gerekli enforcement credential, gateway ve sandbox tarafında yapılmalı.

Repo belgesi olarak AGENTS.md kısa indeks olabilir; CLAUDE.md ancak kullanılan runtime için gerekiyorsa canonical kaynaklara yönlendiren uyumluluk dosyası olur. Form/AC, mimari-yetki, ADR, makine sözleşmeleri, doğrulama/oracle, runbook, güvenlik-veri ve katalog nitelendirme içeriği gerekir. Aynı içerik mevcut belgede varsa dosya sayısı büyütülmez. Kimlik kuralı her yeni Git author ve committer için geçerlidir; Mac guardının uzak workerı koruduğu varsayılmaz.

### Gaps

Paketlerin hangi runtime'da nasıl yüklendiği, `allowed-tools` desteği, credential kapsamı ve gerçek repo kuralları nitelendirme bekler. Skill sayısı, farklı model seçimi veya ekip adı başarı garantisi değildir. Yalnız görevi ve ölçümü belli deney sonuçları uygunluk kararı verebilir.

