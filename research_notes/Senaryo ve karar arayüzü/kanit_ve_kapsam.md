# Senaryo ve karar arayüzü: kanıt ve kapsam denetimi

27 Eylül 2026. Mevcut uygulama yalnız statik olarak okundu; uygulama, fabrika, servis veya test çalıştırılmadı. `otomasyon coding 2` salt okunur kaldı. Bu not bir uygulama geliştirme önerisidir. RDD açılımı henüz doğrulanmadığı için kullanıcıdaki `agentic-rdd-development` ifadesi korunur.

## 1. Olay → risk → ECA → kanıt zincirinde kaybolan bilgiler

**Çıkarım:** Mevcut arayüz faydalı bir tasarım kataloğu; geçmiş araştırmanın tamamını izlenebilir biçimde temsil etmiyor. Öncelik daha fazla sorun kartı üretmek değil, özgün bulgu kimliklerini ve kanıt bağlarını korumak olmalı.

**Kaynaklı bulgular:** Üretici betik, Kestra için `pilot-dersleri.json` içindeki kök nedenlerden konumsal `KP-01…KP-20` kimlikleri üretiyor. Codex derin incelemesinin tam kopyası özgün dosyayla byte düzeyinde eşit; fakat uygulamaya aktarım yalnız kimlik, başlık, önem ve kısaltılmış gereken değişikliği koruyor. Gözlemin yeri, hata zinciri, kaynaklar, uygulanma durumu, sözleşmeler ve deneyler aktarılmıyor. [Aktarım kodu](</Users/w6x/Documents/otomasyon coding/fabrika-karar-merkezi/scripts/veri-uret.mjs:159>)

Özgün [18 yerel bulgu](</Users/w6x/Documents/otomasyon coding 2/kestra-gecmis-incelemesi/bulgular>), [36 dünya vakası](</Users/w6x/Documents/otomasyon coding 2/dunya-vakalari/kumeler>) ve [28 derin bulgu](</Users/w6x/Documents/otomasyon coding 2/agentic-sistem/data/15_derin_inceleme/01_kacirilan_bulgular.json>) ayrı kaynak kümeleridir. Toplam 82 kayıt, 82 bağımsız olay demek değildir. Yerel bulguların 38 kanıt kaydı, dünya vakalarının 61 kaynak kaydı; derin incelemenin 140 kaynak kaydı, 16 sözleşmesi ve 28 `not_run` deneyi vardır. Kaynaklar kümeler arasında tekrar edebilir.

**Önerilen yorum:** Kimliği `namespace + özgün id` olarak koru; KP/D1/D2/B2/B3 özetlerini silmeden özgün kayda ilişkiyle bağla. Her kartta kanıt türü, sürüm/tarih, `observed_in`, neden güveni, kaynak işaretçisi, hata sırası ve kabul deneyi bulunmalı. Dünya vakasındaki `local_analogy_normalized` ilişkisinden ECA adayı üretilebilir; bu benzerlik tam davranış kapsamı olarak sunulmamalı. Ekteki JSON 82 özgün kaydı referanslar; dünya vakalarının ECA adayları benzerlikten türetilmiş ve semantik doğrulaması tamamlanmamış olarak işaretlidir.

**Açık sınır:** Bu tur 36 dış vakanın birincil web kaynaklarını yeniden doğrulamadı. Kaynak kataloglarının sayıları yapısal olarak kontrol edildi. Eski kayıttaki tarihsel düzeltme veya deney önerisi güncel canlı başarıya çevrilemez. PDF'lerin hash eşliği içeriğinin okunduğu anlamına gelmez.

## 2. Açık bir ECA anahtarı, uygulanmış veya doğrulanmış önlem değil

**Çıkarım:** En kritik hata, tasarım seçiminden çözüm sonucu çıkarılması. Arayüzde üç ayrı soru görünmeli: “Bu riske uygun önlem tasarlandı mı?”, “Uygulandı mı?”, “Bu sürümde kanıtlandı mı?”

**Kaynaklı bulgular:** `durumu()` ilgili kurallardan yalnız birinin açık olmasını `kapsandi` sayıyor. Sunucu seçimi tek başına `karar` sonucuna yükseliyor; PDF aynı hesabı “Sorun kapsamı” yüzdesi ve yeşil eşikle gösteriyor. [Hesap](</Users/w6x/Documents/otomasyon coding/fabrika-karar-merkezi/src/durum/hesap.ts:98>), [PDF özeti](</Users/w6x/Documents/otomasyon coding/fabrika-karar-merkezi/src/sayfalar/Rapor.tsx:65>)

Semantik bağlar da kontrol gerektiriyor. DK04 yalnız R14 RED kapısına bağlanmış; kaynak bulgu refactor, dokümantasyon ve diğer iş türleri için farklı kanıt yolları istiyor. DK02→R38 ortam eşliği bağlantısı bileşen/şema/olay sürümlerini birlikte kapatmıyor. DK08→R66 onaysız yeteneği reddediyor, fakat eksik yeteneği isteme, niteleme ve bekleyen işe dönme döngüsünü tamamlamıyor. DP11→R57 insan inceleme kapasitesi hesabı, süreçler arası atomik RAM rezervasyonunu kanıtlamıyor. DE01→R04 kimlik doğrulama bağlantısı Plane edition/sürüm zarfı uygunluğunu sağlamıyor. [Mevcut kurallar](</Users/w6x/Documents/otomasyon coding/fabrika-karar-merkezi/src/veri/kurallar.ts>), [bağlayıcı derin sözleşmeler](</Users/w6x/Documents/otomasyon coding 2/agentic-sistem/data/15_derin_inceleme/02_duzeltilmis_sozlesmeler.json>)

**Önerilen yorum:** Tasarım durumu `seçilmedi/seçildi`, eşleme `tam/kısmi/eksik`, uygulama `uygulanmadı/uygulanıyor/uygulandı`, doğrulama `not_run/fixture_pass/live_pass/failed/stale` olarak ayrı tutulmalı. AND gerektiren yükümlülükler tek bir açık kuralla kapanmamalı. Alternatif önlemler açık OR gruplarıyla tanımlanmalı. Hariç tutulan kaynak-metodoloji bulguları gerekçesiyle görünür kalmalı. “Kararla önlendi” yerine “Tasarıma eklendi; uygulama kanıtı yok” kullanılmalı.

**Açık sınır:** Bu arayüz fabrikayı çalıştırmıyor; uygulama/kanıt alanları boş başlamalı. Bir ECA simülasyonu yalnız beklenen kararın gösterimidir. Canlı yaptırım, rollback, idempotency veya kaynak rezervasyonu sağlandığı iddia edilemez.

## 3. Düzenlenebilir senaryo, merkezi belgeler ve taşınabilir çıktı

**Çıkarım:** ECA, preset, diagram ve belge aynı sürümlü senaryo taslağından türetilirse kullanıcı seçiminin sonuçları anlaşılır; kaynak araştırma değiştirilmeden korunur.

**Kaynaklı bulgular:** ECA paneli açık/kapalı ve hazır parametreleri değiştiriyor; olay, koşul, eylem metni veya yeni kural düzenlemiyor. Kaydedilen durum katalog digest'i içermiyor; yeni kurallar eski durum yüklenirken varsayılanlarıyla ekleniyor. [Panel](</Users/w6x/Documents/otomasyon coding/fabrika-karar-merkezi/src/bilesenler/KuralPaneli.tsx>), [durum modeli](</Users/w6x/Documents/otomasyon coding/fabrika-karar-merkezi/src/durum/depo.tsx:115>) Merkezi belgeler seçili senaryodan bağımsız sabit şablon; ADR “Görev durumunu yalnız Temporal yazar” diyor. [Şablon](</Users/w6x/Documents/otomasyon coding/fabrika-karar-merkezi/src/veri/belgeler.ts:245>) Bu, tak-çıkar tasarımındaki seçilmemiş teknolojiye yanlış zorunluluk verir.

Sorun ayrıntısı ilk 12 kaydı gösterip kalanları metinle bildiriyor; bütün kayıtlar arayüzden gezilemiyor. Kaynak ekranı HTML taşındığında göreli dosya bağlantılarının kopabileceğini kabul ediyor. PDF otomasyonu, bütün diagramlar tamamlanmadan sekiz saniyelik zaman aşımıyla yazdırabilir. Bunlar statik kod bulgusudur; PDF çıktısında fiilen eksik diagram gözlenmedi. [Sorun ekranı](</Users/w6x/Documents/otomasyon coding/fabrika-karar-merkezi/src/sayfalar/Sorunlar.tsx:92>), [kaynak ekranı](</Users/w6x/Documents/otomasyon coding/fabrika-karar-merkezi/src/sayfalar/Kaynaklar.tsx:10>), [yazdırma koşulu](</Users/w6x/Documents/otomasyon coding/fabrika-karar-merkezi/src/sayfalar/Rapor.tsx:28>)

**Önerilen yorum:** Salt okunur kaynak kural + sürümlü kullanıcı override'ı kullan. Preset değişikliğinde fark göster, özel ECA'yı sessizce silme. Senaryo şema/katalog sürümü ve digest'i, kaynak referansları, belirsiz kararlar ve seçili parametreleri JSON'a koy. Kural ekleme/düzenleme; olay türü, koşul, eylem, kapsam, neden, kaynak ve doğrulama alanlarını içersin. PDF ve merkezi belge paketi aynı taslaktan üretilsin; uygulama kanıtı bulunmayan seçimler açıkça öneri olarak yazılsın. Git yazarlığı şablonu da kullanıcının sabit politikasını kullanmalı. Diagram tamamlanmadıysa çıktı eksikliği görünür olmalı; kaynak manifesti ve özgün URL'ler taşınabilir pakete dahil edilmeli.

**Doğrulama önerisi:** Ekteki `not_run` kabul senaryoları; 82 özgün kayda erişim, kısmi eşlemelerin açık kalması, tek toggle'ın risk kapatmaması, farklı stackte Temporal sabitinin çıkmaması, JSON yeniden içe aktarım eşliği, katalog sürüm farkında onaylı göç, ECA taslak düzenleme ve PDF eksiklik bildirimi üzerinden uygulamayı sınar. Şu an bunlar başarı sonucu değildir.

Makine okunur eşlemeler ve kabul önerileri: [kanit_ve_kapsam.json](</Users/w6x/Documents/otomasyon coding/research_notes/Senaryo ve karar arayüzü/kanit_ve_kapsam.json>).
