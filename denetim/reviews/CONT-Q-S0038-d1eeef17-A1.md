# s049, s050 ve s051 inceleme raporu

## Okuma

Üç parçanın 1500 kaydı okundu. Her parçada 500 kayıt vardı. Atlanan indeks yok. Her kaydın index, text ve bbox alanları okundu.

Görsel doğrulama yapılmadı. Manifestte overview görseli yok. Bu üç birimin görsel dosyası da yok.

## Metin katmanı sorunları

Sayfadaki metinler iki kez çıkarılmış. İkinci kopya x ve y yönünde 16 birim kaymış. Kopyalar çakışınca harfler karışıyor. Bu yüzden sayımlar yaklaşık iki kat görünür.

Bazı harfler metin katmanında yok. Örneğin 'farklı' kelimesi 'arklı' olarak geçiyor. Kişi adları bu yüzden kesin değil.

## İçerik

Kaynakta test oracle riskleri tablosu var. Tablo üç riski anlatıyor. Kaynaktan türetilen beklenen değer hiçbir şeyi kanıtlamaz. Yalnız doğru sürümde geçen test kusuru yakaladığını kanıtlamaz. Tek testin geçmesi kullanıcı akışını kanıtlamaz.

Tablo doğru örnekler de veriyor. Örneğin beklenen değer ürün kuralından gelen sabit eşik olmalı.

Büyük yazılı bir not yatay kaydırma sorununu anlatıyor. Not, sorunun mobil, tablet ve desktop ekranlarında olabileceğini söylüyor.

İkinci tablo doğrulama yöntemlerini karşılaştırıyor. Yöntemlerden biri aynı işi birkaç kez yaptırıp oylatmaktır.

## Açık karar konuları

Kaynakta 'her PR insan onayı bekler' yazıyor. Kullanıcının hedefi normal akışta insan müdahalesine gerek bırakmamaktır. Koordinatör bu çelişkiyi karar konusu olarak göstermeli.

Kaynakta görsel baseline'ların otomatik yenilendiği yazıyor. Aynı bölgede 'onay bekliyor' etiketi de geçiyor. Cümle eksik olduğu için çelişki kesin değil.

Aynı ajanın oylaması bağımsız kabul sayılmamalı. DOT-BAGLAMI.md de bu sınırı belirtiyor.

## Kalan iş

1. Bu bölgenin görselini hazırlayın ve okuyun.
2. Kopya katmanı temizleyin.
3. Eksik harflerin nedenini bulun.
4. s048 ve s052 parçalarını bu parçalarla birleştirin.
5. Hazırlanmamış 15 birimi hazırlayın.

Bütün deneyler not_run durumundadır. Bu sonuç accepted değildir. Koordinatör sonucu kaynaktan ayrıca doğrulamalıdır.

Denetim betiği çalıştırılmadı. Görev komut çalıştırmayı yasaklıyor. Metin elle denetlendi. Gerçek okurla denenmedi.