# Karar modeli adayları — kimlik, rol ve sınır

27 Eylül 2026 · Sınırlı ek araştırma. Kullanıcı düzeltmesi: **RDD değil TDD**. Jev = **TypeSafe Jev**, Laya = **NandhaKishorM/laya**. Eş JSON: `decision-models.json`.

## 1. Hangi adayın kimliği ve rolü doğrulanabildi?

### Takeaway

12 ana adayın birincil kaynağı doğrulandı; 7 ad kimliği belirsiz olarak korundu. Kaynak teyidi, modelin yerelde başarıyla çalıştığı veya üretime uygun olduğu anlamına gelmez. Adaylar aynı ürün ailesinden değildir.

### Cited Findings

| Aday ve birincil kaynak | Aile | Sistemde aday rolü | Belirleyici sınır |
|---|---|---|---|
| [Jev (TypeSafe)](https://docs.typesafe.ai/introduction) | hosted_typed_decision_model | Dar semantik sorular, rota/sınıf/skor; kodlayan ajan veya kalıcı orkestratör değil. | Şema uyumu semantik doğruluk değildir. |
| [Laya](https://github.com/NandhaKishorM/laya) | encoder_typed_decision_engine | Yerel typed kararlar; dil/checkpoint yönlendirmesi. | Kısa Latin yazılı metinde dil yanlış yönlenebilir; Türkçe iş yükü ayrıca sınanmalı. |
| [Von](https://github.com/wfzyx/von) | encoder_typed_decision_engine | Yerel süreç/HTTP üzerinden typed karar servisi. | Uyum ve calibration guarantee ifadeleri yayıncı iddiasıdır; gerçek eşdeğerlik, Türkçe doğruluğu ve kalibrasyon bu tur sınanmadı. |
| [Kev](https://github.com/jaredpalmer/kev) | fine_tuned_typed_decision_model_family | Yerelde çalıştırılabilen ve alan verisiyle eğitilebilen typed model ailesi. | Alan dışı/Türkçe veri için sonuç garanti değil; aynı API kalite eşdeğerliği değildir. |
| [Decider](https://github.com/Mapika/decider) | fine_tuned_typed_decision_model_family | Tek geçişte seçenek dağılımı veren, yerel eğitim/sunum ailesi. | README İngilizce sınırlaması, çok adımlı aritmetik, zor örneklerde yanlış yüksek güven, seçenek adlandırma ve uzun JSON dizisi sorunlarını açıklar. |
| [AnyJev](https://github.com/nokia-applied-research/AnyJev) | decision_readout_and_calibration_adapter | Mevcut açık modele typed karar arayüzü/okuma ve isteğe bağlı kalibrasyon veya head ekleme. | No training başlığı tüm modlarda verisiz olduğu anlamına gelmez; L1 kalibrasyon ve L2 head etiket ister. |
| [SemIf (SemIf-OpenJev)](https://github.com/TheoLeeCJ/SemIf-OpenJev) | decision_readout_and_calibration_adapter | Açık model logitslerinden runtime kriterlerine göre olasılıklı karar; ortak state yeniden kullanımı. | Olasılıklar verilen seçeneklere koşulludur; iş yükünde etiketli kalibrasyon gerekir. |
| [Bespoke Nimble](https://github.com/bespokelabsai/nimble) | fine_tuned_typed_decision_model_and_recipe | Karar modeliyle birlikte veri kürasyonu/eğitim/değerlendirme tarifi. | Yayıncı erken proje ve pürüzler uyarısı yapıyor; fabrika olgunluğu kanıtı yok. |
| [GLiNER2.5-Decide](https://huggingface.co/fastino/GLiNER2.5-Decide) | encoder_schema_defined_classifier | İstek anında etiket kümesiyle tekli/çoklu sınıflandırma ve dar operasyonel karar. | Bu tam checkpoint İngilizce; multilingual kardeş modeli ayrı kimliktir. Türkçe başarısı varsayılamaz. |
| [SetFit](https://huggingface.co/docs/setfit/main/index) | few_shot_classifier_training_framework | Az etiketli veriden alan sınıflandırıcısı eğitmek. | Hazır evrensel Jev muadili model/API değildir. |
| [FastFit](https://github.com/IBM/fastfit) | few_shot_classifier_training_framework | Çok sınıflı metin işlerinde az örnekli sınıflandırıcı eğitmek. | Dinamik Choice/Score/Noul API’siyle aynı ürün sınıfı değildir. |
| [ModernBERT](https://huggingface.co/answerdotai/ModernBERT-base) | encoder_backbone_model_family | Sınıflandırma, retrieval veya karar katmanı için temel encoder. | Hazır karar API’si veya orkestratör değil; görev başlığı/eğitim/kalibrasyon gerekir. |

### Inferences

Arayüzde önce ihtiyaç rolü seçilmeli: **hazır karar motoru**, **mevcut modele karar okuma katmanı**, **özel sınıflandırıcı eğitme**, **encoder tabanı**. Sonra o rolün adayları karşılaştırılmalı. Tek radio grubunda ModernBERT, SetFit ve Jev’i doğrudan eşdeğer görmek yanlıştır. Aynı sistemde farklı iş yükleri farklı araç kullanabilir.

### Gaps

Rizzo Flow, NanoJev, Open-Jev, JevK5, AgentJev, OpenThai-SystemOne ve Jev-Style kesin sahip/depo/model eşleşmesi yapılmadan `unverified_identity` tutuldu. GLiNER kartında JevK5 adının geçmesi bunun TypeSafe Jev olduğu anlamına gelmez. SemIf-OpenJev ile “Open-Jev” kullanıcı adayı da kendiliğinden birleştirilmedi. Kaynak kodu çalıştırma, lisansların bütün sürümlerde çapraz denetimi ve yerel benchmark yapılmadı.

## 2. Somut sınırlar ve önceki yorumları düzelten kanıtlar neler?

### Takeaway

Typed çıktı doğru yargı garantisi değildir. Bu modeller kararın biçimini sınırlayabilir; oracle problemini, görev tamamlanma ispatını veya bütün ürün kabulünü tek başına çözmez.

### Cited Findings

TypeSafe kendi belgesinde Jev’in kodlayan ajanın LLM’si yerine geçmediğini söyler. Ayrıca 1.13 için sayı/tarih hesabı, dolaylı/olumsuz ifade, adversarial state, ilgisiz bağlam ve bağımsız soruların tutarsızlığı sınırlarını kaydeder. Choice/Score confidence ise cevap dağılımının bir istatistiğidir; ayrı bir doğruluk ispatı değildir. [Kodlama ajanı sınırı](https://docs.typesafe.ai/introduction/coding-agents), [1.13 zayıflıkları](https://docs.typesafe.ai/model-jaggedness/jev-1.13), [confidence](https://docs.typesafe.ai/confidence)

AnyJev’in “no training” tanımı tüm yolların verisiz olduğu anlamına gelmez: bazı düzeyleri kalibrasyon veya closed-form head için etiket kullanır. SemIf olasılıklarının verilen seçeneklere koşullu olduğunu ve iş yükünde kalibre edilmesini belirtir. [AnyJev](https://github.com/nokia-applied-research/AnyJev), [SemIf](https://github.com/TheoLeeCJ/SemIf-OpenJev)

Laya README’si kısa Latin metinde dil rotası ve uzun bağlam kısıtlarını, ayrıca CUDA OOM/fallback ve eşzamanlı tampon düzeltmelerini açıklar. Decider’ın sınır bölümü zor örneklerde kalibrasyon, kural ifadesi ve uzun JSON dizisi sorunlarını; schema cache’in doğruluk maliyetini bildirir. Nimble’ın temperature güncellemesi aynı seçili cevabı korurken Noul/Score değerlerini değiştirebilir. [Laya](https://github.com/NandhaKishorM/laya), [Decider](https://github.com/Mapika/decider), [Nimble](https://github.com/bespokelabsai/nimble)

### Inferences

Kontrol katmanı yetki, hesap, kuyruk, bütçe, state geçişi ve yan etkiyi sahiplenmeli. Model dar semantik soruya aday yargı verir. Örneğin “hangi hata kategorisi?” sınıflandırılabilir; “bordro aritmetiği doğru mu?” için deterministik hesap ve bağımsız oracle gerekir. “Tamamlandı” sınıflandırması eksik AC/DoD, başarısız test veya açık ürün yükümlülüğünü kapatamaz. Belirsizlikte ek kanıt/ikinci değerlendirme sınırlandırılır; çözülemeyen sonuç açık kalır. Kullanıcının yalnız girdi ve çıktı görme hedefi sürekli gizli insan triage işine çevrilmemeli.

### Gaps

Kaynakların garanti, production-ready ve drop-in ifadeleri bağımsız doğrulanmış olarak aktarılmadı. Jev 1.13 sınırları adı belirtilmiş sürüme aittir; gelecek sürümlere değişmez hüküm değildir. 128 GB sistem belleği tek başına model kapasitesi/ajan sayısı belirlemez; checkpoint, quantization, backend, context, batch ve GPU ayrıca ölçülmeli.

## 3. Seçenekleri nasıl değerlendirelim ve hangi iddiaları açık bırakalım?

### Takeaway

Şimdi seçim yapmaya yetecek ortak bir yerel karşılaştırma yok. Adaylar kaynak teyitli seçenek olarak kaydedildi; performans sıralaması hesaplanmadı ve hiçbir model kurulmadı.

### Cited Findings

Kev README’si kendi Jev karşılaştırmasının kontrollü mimari karşılaştırma olmadığını kabul eder. SemIf de sistem karşılaştırmalarında model ailesi, quantization ve runtime farklarını ayırır. FastFit ve SetFit ise sınıflandırıcı eğitim çerçeveleridir; onların az örnekli görev başarımı bütün ajan fabrikası başarımına dönüşmez. [Kev](https://github.com/jaredpalmer/kev), [SemIf](https://github.com/TheoLeeCJ/SemIf-OpenJev), [FastFit](https://github.com/IBM/fastfit), [SetFit](https://huggingface.co/docs/setfit/main/index)

### Inferences

Kullanıcının paylaştığı sayısal benchmarklar alıntı iddiası olarak kalmalı. Yayıncı ölçümleri de donanım, sürüm, veri, oracle, dil, soru sayısı, input uzunluğu, kalibrasyon ayrımı ve hata tanımı eşleşmeden tek lig tablosuna dönüştürülmemeli.

İlk değerlendirme paketi Türkçe/karışık dil; eksik doğru seçenek; seçenek sırası ve adı; çifte olumsuzluk; prompt injection; uzun state kesilmesi; model/sıcaklık değişiminde eşik kayması; OOM/timeout; sahte “tamamlandı” kararını kapsamalı. Her adayda `seçildi`, `kaynak teyitli`, `yerelde sınanmadı` ve `kullanımda` ayrı statüler olur. JSON’daki yedi negatif kabul deneyinin tamamı **not_run**.

### Gaps

Bu tur benchmark yeniden üretmedi, canlı API çağırmadı, model indirmedi ve kod değiştirmedi. Yalnız araştırma JSON’u ve bu not yazıldı. Belirsiz adlar katalogdan silinmedi; doğrulanmış özellik veya rol atanmadan korundu.
