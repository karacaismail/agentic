# E1 — İhtiyaç haritası karşılaştırması (özet)

Tarih: 2026-09-27 · Ayrıntılı kayıt: `E1-codex-ihtiyac.json`

## Ne karşılaştırıldı

- İkinci bağımsız ihtiyaç atlası (`otomasyon coding 2/ihtiyac-kumeleri/`): 113 ihtiyaç ve 16 küme. Ayrıca T01–T22 kabul güçlendirmesi, 28 boşluk, 16 keşif yüzeyi, 32 soru, 13 çelişki ve 31 dış kaynak.
- Aynı atlasın mimari araştırma notu (`pdf_requirements.json/.md`) ve iki pano PDF'i. PDF'ler görüntüye çevrilip okundu; SHA-256 değerleri eşleşti.
- Ara çıkarım klasörleri (`tmp/ihtiyac-analizi`, `tmp/ihtiyac-tamamlama`, `tmp/pdfs`). Bunlar scratchpad'deki bir betikle salt okunur tarandı.

İkinci atlas dizininde hiçbir şey çalıştırılmadı ve hiçbir dosya değiştirilmedi. `claude-karsilastirma/` klasörü kapsam dışı tutuldu.

## Sonuç: haritamız 388 → 395 ihtiyaç

İkinci atlasın ihtiyaçlarının büyük çoğunluğunun bizde karşılığı vardı. Asıl fark kabul anlamında çıktı: atlas, "neyin başarı sayılmayacağını" gösteren karşı örneklerle daha keskin tanımlar veriyor. Bu tanımlar birincil kaynaklarla doğrulandı ve eklendi.

**Yeni ihtiyaçlar (7):**
- N-K05-031: Kabul kanıtının geçerlilik bağlamı. Model, kural, yetki veya dış koşul değişince kanıt yeniden açılır; kod değişmedi diye kabul sürmez.
- N-K14-010: Bilgi düzeltmesi türevlere (özet, bellek, karar) yayılır; eski yedekten geçersiz bilginin geri dönmesi engellenir.
- N-K18-014: Adına işlem yapılan taraf ile yürütücü ayrılır. Yetki iptali kuyruktaki, süren ve alt ajana devredilmiş işlere yayılır.
- N-K16-010: Bileşen değişiminde ve devreden çıkarmada iş anlamı taşınır; taşınamayan kısım açıkça kayda geçer.
- N-K23-016: Değerlendirme örneklerinin kökeni, kullanım geçmişi ve sızıntı sınırı.
- N-K23-017: İyileşme iddiaları yanlısız ölçülür: seçilim, bırakılan işler ve paralel çalışmada çift sayım hesaba katılır, nedensellik etiketlenir.
- N-K04-014: Arayüz ve hata yönetimi için yasak kalıp kataloğu ve mevcut ihlal tabanı. Bu kayıt ara dosya taramasında bulundu; kaynak panoda vardı ama iki haritada da ihtiyaç olarak yoktu.

**Mevcut 25 ihtiyaca kabul ölçütü eklendi** (yalnız ekleme). Başlıcaları:
- Kontrol hizmeti yanıt vermezse "geçti" sayılmaz; "kabul edildi" yanıtı "tamamlandı" demek değildir.
- Süresiz bekleme görünür kılınır; kurtarma sonrası uzlaştırma yapılır; yalnız en iyi deneme raporlanmaz.
- Etkilenen tarafın itirazı "testler geçti" diye kapatılmaz; sessizlik onay, bağlam aktarımı yetki aktarımı sayılmaz.
- Panodan: reddedilenler arşivi, durum değişikliğiyle başlatma, insan testi kapsamı (pozitif/negatif, kullanıcı yolculuğu, rastgele etkileşim, veritabanına yansıma), ilerlemesizlik tespiti, hatadan iyileştirme, rol eşlemesi.

**Analizlere eklenenler:**
- 8 bilinmeyen (U-070–U-077): değerlendirme kirlenmesi, ortak yanlış anlam, çoklu arıza, geri almanın sahte güveni, dolaylı yetki yükselmesi, risk puanının kör noktası, temsil edilmeyen taraf, bellekte gecikmiş bozulma.
- 3 boşluk (G-036–G-038).
- 6 açık soru (Q-071–Q-076).
- 2 çelişki (C-040, C-041).

Çember, boşluk küme özeti, ölçek senaryoları ve indeks istatistikleri güncellendi. Görselleştirme yeniden üretildi.

**Kaynaklar:** Doğrulanmış 15 dış kaynak (S-374–S-388: standartlar, rehberler, çalışmalar) ile S-095 (ikinci atlas) ve S-096–S-097 (iki pano) eklendi. İçe aktarılan her kayıt köken ve doğrulama alanı taşır; analiz çıkarımına dayananlar `kismen` işaretli.

## Çelişkiler ve hangisi doğru

1. **İnsanın rolü.** Mimari not insanı yalnız girdi ve çıktıda konumluyor. Bizim harita ve pano ise ara müdahaleyi ve eş üretimi içeriyor. Kararı kullanıcı verecek (D-024). Önerilen uzlaşma: düşük riskli işte girdi–çıktı modu, yüksek riskli ya da belirsiz işte ara insan katkısı.
2. **"Bitti" ile insan testinin sırası.** Panoda iş önce "bitti" oluyor, insan testi sonra geliyor. Teknik tamamlanma ile insan kabulü ayrı durumlar olmalı; pano sırası düzeltilmeli.
3. **Ajan yürütme ihtiyaçlarının zorunluluğu.** İkinci atlas bunları "koşullu" sayıyor. Bizim "zorunlu" yorumumuz doğru; ikinci atlasın kendi yetenek dosyası da bunu çekirdek sayıyor.
4. **Risk olasılık puanı.** İkinci atlas puan vermiyor, bizim kayıt geçici puanlı. Etiketli olduğu sürece bizimki kabul edilebilir; ortalama puanın yarattığı risk U-075 olarak eklendi.
5. **İlk testin her zaman kırmızı olması.** Gerçek bir çelişki değil. Bizim iş türüne göre ayrımımız ikinci atlasın kaygısını karşılıyor.

## Bizde olup ikinci atlasta olmayanlar

- Ekip çalışma sistemi, sosyo-teknik yapı ve çalışan hakları (K30–K32).
- İnsan–ajan iş birliği ayrıntısı (K27–K29).
- Güvenilirlik mühendisliği (K33), güvenli tasarım (K34), mimari uygunluk (K35).
- Model, lisans ve hukuk (K09, K22); bütçe ve sayaçlar (K20).
- Ölçek senaryoları, hazırlık kapıları, bekleyen kararlar, risk kaydı, varsayımlar, 69 bilinmeyen ve 273 dış kaynak.

## Eklenmeyenler

- Sentetik örnek iş sözleşmeleri ve paket durum kayıtları.
- Bizde karşılığı zaten bulunan ihtiyaç, soru, boşluk ve çelişkiler.
- Mimari nottaki altyapı/araç beyanları ve girdi/çıktı sözleşmesi alanları (mimari düzey, marka içeriyor).
- Pano metnindeki ihlal sayıları (başka sütunlarla iç içe; doğrulanamadı).

## Düzeltmeler

- İndeksteki S kimlik aralığı eskimişti ("S-101..S-179"); güncellendi.
- Köken alanlarının yazılabilmesi için şemaya dört opsiyonel alan eklendi.
- Marka taraması yapıldı: ihtiyaç metinlerinde ürün adı yok.
