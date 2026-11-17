# E6: Codex Kestra geçmişi ile A0 pilot incelemesinin karşılaştırması

Codex'in `kestra-gecmis-incelemesi/` paketini A0 incelememizle karşılaştırdık. Codex'in atıf yaptığı her kanıt satırını eski fabrikada ve Claude transkriptlerinde okuduk, log sayımlarını yeniden yaptık. Hiçbir kaynak dosya değiştirilmedi.

## Kısa sonuç

İki inceleme birbirini tamamlıyor. Biz mimariye, ölçeğe, maliyete ve nihai sonuca baktık. Codex 11–18 Eylül'ü olay olay izleyip denetleyicinin nerede kırıldığını gösteriyor. Codex'te olup bizde olmayan, kanıtla doğrulanmış **11 ders** `pilot-dersleri.json` → `kok_nedenler` listesine eklendi. 10'u tam doğrulandı, 1'i zaman eşleşmesine dayandığı için "kısmen".

## Eklenen dersler

1. **1 GiB tarayıcı test konteyneri OOM verdi.** 51 testte exit 137 görüldü. 2 GiB ile aynı aday 3/3 geçti; tepe 887–942 MiB, test başına ~6 MiB birikim. 150 testten sonra 2 GiB de yetmiyor. Testler 50'lik gruplara bölündü, ama gruplar sırayla koşuyor ve VM ~%19 CPU'da.
2. **Boşta sınırı uzun testi öldürdü.** 600 sn'lik sınır, 70 dakikalık entegrasyon testini takılma sandı; iş üç kez öldürüldü, kurtarma kapandı.
3. **Alt dize ile sınıflandırma döngü üretti.** "CAPACITY" eşleşmesi bağlam taşmasını kapasite beklemesi sandı: 4.762 CLAIM, 1 model çağrısı, 13 saat durma. Durum 1.008.940 byte'a, build kanıtı 100.248 karaktere ulaşıp sınırları aştı.
4. **Sahipsiz bekleme.** Onarım talebini okuyan yürütücü yoktu. Takımlar birleşmişken kök iş çocuklarını bekledi. Dokuz durmanın hepsi kullanıcı "bitti mi?" diye sorunca bulundu. Sonradan eklenen izleyici yalnız gözlüyor.
5. **Çağrının bitmesi başarı sayıldı.** Teşhis ajanı dosyayı okuyamadığı hâlde sonuç SUCCESS oldu. "Bitmek üzere" mesajını 13 saatlik durma izledi.
6. **İnsan onayı beklemesinin son tarihi yoktu (kısmen).** 18.09 16:14 UTC'de teslim GREEN oldu, sonra pano insan eylemi bekledi. İş tam 7 gün sonra (25.09 16:14:41 UTC) `P7D` ile KESTRA_FAILED oldu; arada rapor yok.
7. **Bağımlılık ve entegrasyon modellenmedi.** Bayat ortak temel, birleşmiş 73 paketin hepsini "stale" gösterdi.
8. **Canlı onarım başka kapıyı bozdu.** 10ao→10ap regresyonu 10 dakikada çıktı; 10aq ve 10as de aynı türden.
9. **Kapasite yanlış ölçüldü.** Yanlış rolden okununca kök iş 5 saat kabul edilmedi. Claim transaction'ı içinden ikinci bağlantıyla okununca işçi kendini kilitledi. Tek reviewer rotası kuyruğu tıkadı.
10. **Hatalar yanlış sahibe gitti.** Ortam, test yazarı, ürün ve sağlayıcı hataları ayrılmadı. Plane her 3 sn'de sorgulandı; 502 "unknown" sayıldı.
11. **Kurulum önceden sınanmadı.** Caddy'de `acme_ca` sözdizimi hatası, Kestra eklenti dizininde izin hatası vardı. İkisi de Kestra çekirdek hatası değil.

## Özel sorular

- **1 GB:** Olay gerçek, ama sınır test konteynerinindi. Host RAM darboğaz değildi.
- **7 günlük zaman aşımı:** Yalnız bizde vardı. Codex'in açık sorusu U01'i (iş sonra kabul edildi mi?) yanıtlıyor: hayır, kabul ve PR yok.
- **Bayat RUNNING:** 9 çocuk iş RUNNING görünüyor, ama Codex'e göre takımlar 18.09'da birleşmişti. İşler takılı değil; durum kaydı bayat.
- **"İki beyin":** Bizde var, Codex'te yok; Codex "motoru değiştirmek tek başına çözmez" diyor. Çelişmiyorlar: dayanıklı bir motor elle yazılmış lease/heartbeat/retry katmanını kaldırır, ama kabul, sahiplik, sözleşme ve bağlam sorunlarını çözmez.
- **Kapasite hataları:** Sayılar aynı (330 / 56). Codex alt dize sınıflandırması ve yanlış rol ölçümü mekanizmalarını ekliyor.
- **Lease ve uyku:** Bizde zaten vardı. Codex'in eki: 13.09'daki 227 sn'lik uyku ve olayın Mac'e özgü olduğu notu.

## Çelişkiler

- **BlockageStoreError:** Biz README'den 1.275 aldık; dosyada bugün 1.385 satır var. Hepsi 3 gözlem kimliğinden geliyor, yani 1.385 ayrı olay değil.
- **"Darboğaz bellek değil":** Bizim ifademiz fazla geniş; konteyner başına sınır gerçek bir tıkanmaydı.
- Diğerleri vurgu farkı; ayrıntılar JSON'da.

## Bizde olup Codex'te olmayanlar

Kestra'nın yalnız 15 sn'de bir yoklaması, git dışında kalan 87/98 modül, 11'den 98 modüle büyüme, 12'lik bütçeye karşı 456 çağrı, müdahalesiz prod sayısının 0 olması, ölçülmüş kaynak kullanımı ve taşınacak parçalar listesi.

## Eklenmeyenler

Bizde zaten bulunanlar eklenmedi: uyku, paket yarışı, idempotency hatası, Plane 429 ve log sayımları. Kullanıcı promptları da eklenmedi; ders değil, gereksinim bağlamı.

Ayrıntılar: `E6-codex-kestra-gecmisi.json`.
