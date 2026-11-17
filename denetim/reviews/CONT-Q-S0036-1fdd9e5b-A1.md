## CONT-Q-S0036-1fdd9e5b-A1 özeti

Üç metin birimini okudum: s004, s005 ve s006. Her birimde 500 kayıt var. 1500 kaydın hepsini indeks, metin ve bbox alanlarıyla okudum.

Görsel okunmadı. Manifestte bu birimler için görsel dosya yok. Bu yüzden kutu, renk ve ok ilişkileri doğrulanmadı.

### Ne anlatıyor?

Sayfa bir TDD ve ajan iş akışını anlatıyor. Görevler Plane'den alınıyor. Test Ajanı önce testi yazıyor. Kodlama Ajanı kodu yazıyor. Kontrol Ajanı bağımsız inceleme yapıyor. PASS veya FAIL sonucunu bağımsız runner veriyor.

### Önemli bulgular

1. Metin katmanı z, j ve ç harflerini kaybediyor. Bu yüzden olumsuzluk ekleri siliniyor. Örneğin 'gevşetemez' yerine 'gevşeteme' yazıyor. Bu metinler görsel olarak doğrulanmadan kabul edilmemeli.
2. İki lejantta yeşil rengin anlamı farklı. Birinde yeşil Kontrol Ajanıdır. Diğerinde yeşil insanın devreye girdiği yerdir.
3. Sayısal sınır yalnız bir yerde açık: en çok 2 test düzeltmesi. Diğer deneme ve döngü sayıları görünmüyor.
4. Duruş kuralları var. Ama dönüşü kimin başlatacağı bu parçalarda yazmıyor.
5. Kaynak bütün testlerin DEV ortamında çalıştığını söylüyor. Dot ise alpha ortamında test yapıldığını varsayıyor.

### Kalan iş

- 41 indeks okunamıyor.
- Görsel doğrulama yapılmadı.
- Komşu birimlerle bağlantılar birleştirilmedi.
- Dosyanın 66 biriminden yalnız 9'u hazır.

Bütün deneyler not_run durumunda. Bu sonuç kabul edilmiş değildir. Koordinatör kaynaktan ayrıca doğrulamalı.