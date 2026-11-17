# CONT-Q-S0039-cab00bb5-A1 incelemesi

## Kapsam

Üç metin birimi okundu: s043, s044 ve s045.
Okunan aralık 21000 ile 22499 arasıdır. Toplam 1500 öğe okundu.
Atlanan öğe yok.
Manifestte bu birimler için görsel yok. Görsel doğrulama yapılmadı.

## Kaynakta ne var

Bu bölüm ajanlı test ve doğrulama ilkelerini anlatan kartlar içeriyor.
Kartların çoğunda "Neden" ve "Örnek" alt başlığı var.
Okunan kart konuları şunlardır:

1. Doğrulayıcı ajan, cevabı bilinen bir sınavla düzenli ölçülür.
2. Doğrulayıcı onay vermeden önce karşı gerekçe üretip çürütür.
3. Gereksinim ile kod yorumu arasındaki benzerlik düşerse alarm verilir.
4. Kusurlu baseline kaydedilirse kusur kalıcı doğru sayılır.
5. Ajan ölçümü gevşetemez. maxDiffPixels artışı ayrı onay ister.
6. Kırmızı takım ajanı Builder kodunu görmeden gereksinimi kırmaya çalışır.
7. Test ve beklenti dosyası değişikliği ayrı risk sınıfıdır.
8. İnsan onayı dört sabit noktaya konur.
9. Headless tarayıcı gerçek cihazın yerini tutmaz.
10. LLM hafızası doğru sonuç kaynağı sayılmaz.
11. Tek PASS sonucu yerine çok boyutlu kanıt raporu verilir.

Sağ sütunlarda tarayıcıya özgü teknik öneriler var.
Örneğin safe-area, dvh, font-display ve dokunma gecikmesi anlatılıyor.
Sol sütunlarda elle yazılmış izlenimi veren arayüz kontrol notları var.

## Önemli bulgular

1. Metin katmanında harf ve rakam kaybı var. Bu yüzden eşik sayıları okunamıyor. Örneğin "5 ms" değeri güvenilir değil.
2. Her metin iki kez geçiyor. Sayım yapılırken kopyalar birleştirilmeli.
3. Kaynak insan onay noktaları öneriyor. Güncel hedef ise normal akışta insan müdahalesi bırakmamak. Bu bir karar konusudur.
4. Onaycı, süre ve dönüş kuralı kaynakta yazılmamış.
5. Gerçek cihaz kapasitesi ve sahibi tanımlı değil.
6. Bu konuların çoğu Dot bağlamında önceden konuşuldu. Kaynak yeni somut örnekler ekliyor.

## Açık işler

- Kartların başlık başları s042 içinde olabilir.
- Birçok örnek cümlesi s046 içinde sürüyor.
- Manifestte s046 yok. Sonraki birimler hazırlanmamış.

## Deneyler

Altı sınırlı deney önerildi. Hepsi not_run durumundadır.

## Denetim notu

Denetim betiği çalıştırılmadı. Bu görevde komut çalıştırmak yasak. Metin elle denetlendi.
Kaynak alıntıları özgün sözdizimiyle korundu.
Gerçek okurla denenmedi.