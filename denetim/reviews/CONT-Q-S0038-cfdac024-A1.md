## Özet

Üç birimin 1.500 kelimesinin hepsi okundu. Index aralığı 10500 ile 11999 arasıdır.

Bu birimler için manifestte görsel dosya yok. Bu yüzden görsel doğrulama yapılmadı.

## Ne var

Parçada 5 tablo ve 4 akış şeması iç içe geçiyor:

- Benchmark tablosu: model, benchmark, puan, kaynak ve yorum.
- Araç tablosu: embedding, reranker, belge okuma ve bilgisayar kullanımı.
- OpenCode tablosu: ajan rolleri ve yerel model servisi.
- Değerlendirme tablosu: test ajanı, kontrol ajanı ve Türkçe kabul ölçütü.
- Model kartı listesi: üretici bağlantıları.
- Akışlar: OOP kararı, modül ilişkisi, görev listesi ve katman kontrolü.

## Önemli bulgular

1. Metin katmanında bazı harfler ve rakamlar kayboluyor. Benchmark puanları bu yüzden okunamıyor.
2. Kaynak puanların üretici beyanı olduğunu kendisi yazıyor. Kaynak sürüm eşitlenmeden sıralama yapılmamasını istiyor.
3. Kaynak her görevin en az 3 bağımsız denemede ölçülmesini istiyor.
4. 'max döngü' için sayı yazılmamış. Durma kuralının sınırı bilinmiyor.
5. Notlarda kişi adları var. İçerik herkese açık depoya taşınırsa bu adları çıkarın.

## Açık işler

- Puan rakamları görselden okunmalı.
- Okların yönü görselden doğrulanmalı.
- s021 ve s025 sınırındaki bağlantılar birleştirilmeli.

Bütün deneyler not_run durumundadır. Gerçek okurla denenmedi.