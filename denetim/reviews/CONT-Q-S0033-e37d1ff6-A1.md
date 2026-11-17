## CONT-Q-S0033-e37d1ff6-A1

Bu inceleme sayfa 1'in üç metin parçasını kapsar. Parçalar `words[27000..28500)` aralığındadır.

- s055 ve s056 tam okundu. Her kayıtta index, text ve bbox okundu.
- s057 kısmi okundu. 28209-28499 arasında yalnız text alanı okundu.
- Bu birimler için görsel dosyası yok. Görsel doğrulama yapılmadı.

### İçerik

Parçalar numaralı ajan test kurallarını içerir:

- Test değişikliklerinin ayrı risk sınıfı
- 11. kural: insan onayının yeri
- 12. kural: gerçek cihaz
- 13. kural: metrik doğruluğu ve billing servisi
- 14. kural: çok boyutlu rapor
- Kodu görmeyen kırıcı ajan rolü

Ayrıca mobil uygulama kartları vardır. Konuları safe-area, 100vh, klavye, font metrikleri, dokunma gecikmesi ve touch-action'dır. Sol sütunda gözden geçiren kişilerin yorumları vardır.

### Ana sorunlar

1. Metin katmanında harf ve rakam kaybı var. Sayılar görselle doğrulanmadan kullanılmamalı.
2. Her satır iki kez geçiyor.
3. Kart, ok ve tablo ilişkileri görsel olmadan kurulamadı.
4. Dış bağımlılıkların sahibi ve kesinti kuralı kaynakta yok.

### Açık işler

- s057'de 291 öğenin bbox alanı okunmadı.
- s054 ve s058 ile bağlantılar açık.
- Görsel bölge hazırlanmadı.
- Dot karşılaştırması yapılmadı.
- Üç deney not_run durumunda.