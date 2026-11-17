# CONT-Q-S0038-7da7f8d7-A1 inceleme raporu

Kaynak: agents/17Agentic.pdf, sayfa 1, sayfa dışı metin.
Birimler: s046, s047, s048. Her birimde 500 token var. Üçü de tamamen okundu.
Görsel yok. Bu rapor yalnız metin katmanına dayanır.

## Ne bulundu

Metin, test stratejisi ve arayüz kabul notlarıdır. Kartlar hâlinde yazılmış.

1. Dört arayüz ölçütü var. Yazı okunaklı olmalı. Boşluk ve hizalama tutarlı olmalı. Gereksiz kaydırma olmamalı. WCAG kuralı arayüzü bozmamalı.
2. Altı başlıklı kontrol var. Totolojik test yasağı. Bilinen kötü sürümde kırılma kontrolü. Tek sinyale güvenmeme. Kademeli otonomi güven skoru. Niyet ile kod eşleşmesi. Ortam parmak izi ile baseline yenileme.
3. ‘Ali Bora’ etiketli beş tanım var. Ajan kodu ve testi aynı bağlamdan üretmemeli. Hedef somut ve yazılı olmalı. İlişki temelli test tanımı. Karşılaştırmalı test tanımı. Onaylı referans tanımı.
4. ‘Sea’ etiketli üç kart var. Dar kapsamlı görsel regresyon testi. Beklenen değerleri harici dosyadan çekme. Küçülen ekranda düğmelerin tıklanabilirliğini TypeScript ile doğrulama.
5. Görev sözleşmesi şablonu var. Her görevde dört alan doldurulur: beklenen sonuç, kaynak, doğrulama yöntemi, kapsam dışı alan.

## Önemli sorunlar

- Metin katmanı bozuk. Her satır iki kez var. Bazı harfler eksik. Örneğin f, h, z, j ve yüzde işareti düşmüş.
- Sayılar kayıp. Piksel, yüzde ve ay değerleri okunmuyor. Bu değerler kabul ölçütü olarak kullanılamaz.
- Dokuz cümle yarım. Başı veya sonu başka birimde. s049 ve sonrası henüz hazır değil.
- İki başlık ‘4’ numarasıyla başlıyor. Numaralar güvenilmez.
- Verifier için iki farklı tarz var. Biri kural ile ölçer. Diğeri algısal soru sorar. Hangisi ne zaman, yazılı değil.
- Etiketler kişi adı gibi görünüyor. Rol ve yetki yazmıyor. Sahip atamayın.

## Dot karşılaştırması

Kartlar Dot'un Oracle, Stryker, Playwright ve bağımsız kabul başlıklarıyla örtüşüyor. Kaynak somut mekanizma ekliyor. Örneğin güven skoru girdileri ve PR otomatik ret. Hiçbiri çalışan sistem kanıtı değil. Dot önerilerinin güncel doğrulaması yok.

## Kapasite ve kesinti

Bu konular birimlerde geçmiyor. Açık kalır.

## Önerilen deneyler

Dört deney tanımlandı. Hepsi not_run. Glyph kurtarma, sayfa dışı alanı görüntüleme, kopya oranı ölçümü, komşu birimlerle birleştirme.

## Teslim notu

Koordinatör sonuçları kaynaktan ayrıca doğrulamalı. Denetim betiği çalıştırılmadı. Görev komut çalıştırmayı yasaklıyor. Gerçek okurla denenmedi.