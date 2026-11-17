# A1 Özeti: Kurumlar ajan tabanlı kodlamayı gerçekte nasıl kuruyor?

Tarih: 2026-09-27. Ayrıntılar ve tüm kaynaklar: `A1-kurum-ornekleri.json` (21 örnek, 26 akademik bulgu, 14 orkestrasyon bulgusu).

## Ana sonuç

Üretimde ölçülmüş sonuç yayımlayan kurumların hiçbiri "CEO/PM/QA ajanı" gibi rol yapan bir şirket simülasyonu kullanmıyor. Ortak mimari şu: **tek yazıcı ajan + deterministik iskelet + görev başına izole sandbox + sola kaydırılmış doğrulama + zorunlu insan PR kapısı**. Ek ajanlar kullanıldığında kod yazmıyor, yalnızca denetliyor (hakem, reviewer).

## Ölçülmüş sonuçlar (birincil kaynak)

| Kurum | Sonuç |
|---|---|
| Stripe Minions | Haftada 1.300'den fazla merge edilen, insan kodu içermeyen PR; en fazla 2 CI turu |
| Ramp Inspect | Frontend ve backend repolarında merge edilen PR'ların ~%30'u, birkaç ayda |
| Spotify Honk | 1.500'den fazla merge PR; göçlerde %60-90 zaman tasarrufu; LLM hakem oturumların ~1/4'ünü veto ediyor |
| OpenAI harness | 5 ayda ~1M satır, ~1.500 PR, mühendis başına günde 3,5 PR |
| Devin | PR merge oranı 18 ayda %34'ten %67'ye |
| Google iç göçler | Değişikliklerin %80'i tamamen AI; toplam süre ~%50 azaldı; darboğaz review |
| Airbnb | 3.500 test dosyası: tahmin 1,5 yıl, gerçekleşen 6 hafta (deterministik pipeline) |

## Akademik kanıt (kısa)

- **MAST:** 7 çoklu ajan çerçevesinde %41-86,7 başarısızlık; kazanımlar tek ajana göre çoğu zaman minimal (arXiv 2503.13657).
- **Scaling Agent Systems:** Sıralı görevlerde çoklu ajan tek ajana göre %70'e kadar kötü; merkezî doğrulaması olmayan mimariler hatayı yayıyor (arXiv 2512.08296).
- **Gerçek PR'lar:** 33 bin ajan PR'ında merge oranı %71,5. Ajana göre %43 ile %83 arasında değişiyor; performans ve bug fix işlerinde en düşük (arXiv 2601.15195).
- **Oracle problemi:** Testi geçen SWE-bench PR'larının kabaca yarısını bakımcılar merge etmiyor (METR 2026). Gereksinim ve arayüz verilmezse SWE-Bench Pro'da başarı üçte birine iniyor (%25,9 → %8,4).
- **Bağlam dosyaları:** AGENTS.md başarıyı genel olarak artırmıyor, maliyeti %20'den fazla artırıyor (arXiv 2602.11988).

## Ortak örüntüler

1. Tek yazıcı ajanı deterministik bir blueprint ya da durum makinesi içinde çalıştır (Stripe, Shopify Roast, Airbnb, Symphony).
2. Her görev için izole, önceden ısıtılmış, internet ve üretim erişimi olmayan bir sandbox aç (Stripe ~10 sn, Ramp Modal, Copilot Actions).
3. Hızlı yerel lint/verifier çalıştır, CI tur sayısını sınırla, sonra işi insana devret (Stripe, Spotify).
4. Tetiklemeyi tracker'dan yap ve el değiştirmeyi ticket durumlarıyla yönet: Todo → In Progress → Human Review → Merging/Rework (Symphony).
5. Ajana insanlarla aynı kuralları ver. Kural dosyası kısa olsun (~100 satır) ve bilgi repodaki dokümanlarda dursun. Araç seti küçük ve küratörlü olsun (OpenAI, Stripe).
6. Ajanın PR'ı için insan review'u zorunlu olsun; ajanı çalıştıran kişi onaylayamasın (Copilot, Stripe).
7. Bağımsız hakem/reviewer ajan kullan; bu ajan kod yazmasın (Spotify, Cognition, Uber, LinkedIn).

## Kaçınılacaklar

Rol simülasyonu yapan çoklu ajan sistemleri ve paralel yazan ajan sürüleri; "testler geçti, iş bitti" varsayımı; ajanın testleri veya CI'ı değiştirebilmesi ve sınırsız retry; dev AGENTS.md ile sınırsız araç erişimi; belirsiz ticket'la otonom başlatma; review kapasitesini aşan PR üretimi; izin verici bir sandbox ve ajana verilen ham kimlik bilgileri.

## Orkestrasyon

- **Temporal**, görev içi dayanıklı ajan yürütmesine uyuyor. Workflow deterministik kalıyor; LLM ve araç çağrıları Activity olarak çalışıyor.
  - OpenAI Agents SDK entegrasyonu 2026-03-23'te GA oldu. Replit Agent Temporal üzerinde çalışıyor.
  - İnsan onayı Signal ya da Update ile veriliyor. Bekleme sırasında compute tüketilmiyor.
- **Temporal sınırları:** Olay geçmişi en fazla 51.200 olay veya 50 MB. Payload en fazla 2 MB, tek işlem 4 MB. Çözümler:
  - uzun oturumlarda Continue-As-New,
  - büyük çıktılar için External Storage/claim check (eşik 256 KiB).
- **Kestra ve Airflow** deklaratif DAG, zamanlama ve veri pipeline'ı içindir. İkisinde de insan onayı var: Kestra'da Pause görevi, Airflow 3.1+ sürümünde HITL operatörleri. Ancak LLM'in bir sonraki adımı çalışma zamanında seçmesi, statik DAG modeline doğal olarak oturmuyor (çıkarım).
- **Symphony** bunun daha hafif alternatifi. Kalıcı DB tutmuyor; tracker'ı ve workspace'leri doğruluk kaynağı olarak kullanıyor. Yeniden başlatmada retry zamanlayıcıları kayboluyor.

## Bu projeye çıkarımlar (yorum, kaynak iddiası değil)

- Plane'de Todo'dan In Progress'e geçişin tetikleyici olması, Symphony'nin durum makinesiyle birebir örtüşüyor. "Human Review" ve "Rework" durumlarını Plane'de açıkça tanımlayın.
- SAFe katmanı insan planlaması olarak kalmalı; ajanlara rol olarak bölünmemeli. Paralellik görevler arasında kurulmalı, görevin içinde değil.
- Formdaki giriş kalitesi başarıyı doğrudan belirliyor. Gereksinim, arayüz ve kabul testleri zorunlu alan olmalı.
- Oracle problemi için test geçişine güvenmek yetmez. Mutasyon güdümlü testler (Meta ACH), ajanın dokunamadığı insan kabul testleri ve LLM hakem birlikte kullanılmalı.

## Doğrulama notları

- openai.com ve coinbase.com 403 verdi. OpenAI içeriği bir ayna kopyadan doğrulandı.
- Coinbase Forge'un "%5 PR" ve "150 saat → 15 saat" iddiaları doğrulanamadı.
- Uber Minion ayrıntıları ücretli içerikte olduğu için doğrulanamadı.
- LinkedIn kod review rakamları ikincil kaynaktan (InfoQ).
- Temporal'ın "Codex Temporal üzerinde" iddiası satıcı beyanı.
