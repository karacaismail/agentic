# Sürekli ve derin dosya denetimi

## Güncel kullanıcı kararı

Kullanıcı, 10 Kasım 2026 tarihinde sürekli canlı denetim istedi.
30 dakikalık otomasyon silindi.
Yeni çalışma, Pane olaylarına göre ilerleyecek.
Bir iş bitince Codex sonucu inceleyecek.
Sonraki görev, bulgulara ve kalan kapsama göre yazılacak.
Aynı görev metni süreye bağlı olarak tekrar gönderilmeyecek.

Kullanıcı beş ayrı Claude hesabı kullanmak istiyor.
İki ayrı Codex hesabının girişi de doğrulandı.
İkinci Codex hesabı Chrome'daki Yonetim profilinden açıldı.
Hesaplar abonelik girişiyle kullanılacak.
Hesap sınırı dolunca uygun başka hesapla devam edilecek.
Hiçbir hesap uygun değilse çalışma kaydı korunacak.
API anahtarı veya ek ücretli kullanım açılmayacak.

## Amaç

Tüm kaynaklar tek tek ve derinlemesine incelenecek.
Kaynak kökü `/Users/w6x/Documents/otomasyon coding` konumudur.
Ana dizindeki dosyalar da kapsamdadır.
Alt klasörlerin içindeki kaynaklar da kapsamdadır.
PDF, tablo, görsel, diyagram, metin ve kod ayrı yöntemlerle incelenecek.
Dosyanın açılamaması, incelemenin tamamlandığı anlamına gelmez.

Araştırma şu soruyu yanıtlayacak:
İnsan müdahalesi olmadan, girdiden çıktıya çalışan ajan sistemi hangi parçalardan kurulabilir?

Her bölümde üç çalışma yapılacak:

1. Claude, geliştirme odaklı eleştiri yazacak.
2. Claude, henüz fark edilmemiş bilinmeyenleri araştıracak.
3. Claude, her ihtiyaç için araç veya dil modeli süreci önerecek.

Claude, bütünlüğü bozabilecek somut engeller arayacak.
Kesintiler ve zorunlu insan müdahaleleri özellikle incelenecek.
Yeni sorun bulunmazsa sorun uydurulmayacak.

## Geçmiş yazışmalar

Dot yazışmalarının kayıtları iki dosyada bulunuyor:

- `DOT-BAGLAMI.md`
- `DOT-EKLERI.md`

Bu kayıtlar, kullanıcının gönderdiği 58 ekran görüntüsünü kapsıyor.
Kullanıcı kararları ile Dot önerileri ayrı değerlendirilecek.
Dot'un araç, sürüm ve lisans iddiaları doğrulanmış sayılmayacak.
Seçilen araçların güncel iddiaları resmî kaynaklardan kontrol edilecek.

Eski belgelerde insan onayı gerektiren aşamalar bulunuyor.
Yeni müdahalesiz hedefle çelişen kararlar açıkça gösterilecek.
Araştırma, mevcut üretim ortamlarına müdahale yetkisi vermiyor.

## İş paylaşımı

Pane içinde bir Codex koordinatörü çalışacak.
Claude ajanları, birbirinden ayrılmış kaynak bölümlerini inceleyecek.
İlk aşamada iki Claude incelemeyi paralel yürütecek.
Üçüncü Claude gerektiğinde bağımsız karşı inceleme yapacak.
Kalan hesaplar, kota geçişinde kullanılabilecek.
Kapasite ve gerçek kullanım görüldükçe dağılım değiştirilebilecek.

Son kapsam, `SON-KAPSAM.md` dosyasında ayrıntılıdır.
İç boşluklar ve dış bağımlılıklar ayrı incelenecek.
Risk, sürdürülebilirlik ve bilinmeyen sorunlar için ayrı görevler verilecek.
SAFe ekibinin birden fazla Scrum ekibini yönetmesi incelenecek.
Plane görev seçimi ve güvenli Git birleştirmesi birlikte değerlendirilecek.
Kullanıcı bir hafta boyunca bilgisayara erişemeyecek.
Süreklilik, tek Codex oturumunun açık kalmasına bağlı olmayacak.
Claude'un Codex'i yeniden başlatması gerçek denemeyle doğrulanacak.

Koordinatör, her bölümü yalnız bir etkin çalışana atayacak.
Karşı inceleme, açıkça ayrı bir görev olarak kaydedilecek.
Çalışanlar kaynak dosyaları değiştirmeyecek.
Rapor numaralarını yalnız koordinatör verecek.

## Dosya ve öğe kaydı

Koordinatör bütün kaynakların envanterini çıkaracak.
Her kayıtta dosya yolu, tür, boyut ve içerik özeti bulunacak.
İçerik özeti, dosya değiştiğinde eski incelemeyi ayıracak.
Gizli çalışma kayıtları ve üretilen raporlar yeniden kaynak sayılmayacak.
Bağlantılar, kopyalar ve okunamayan biçimler ayrıca kaydedilecek.

PDF incelemesi sayfa ve okunabilir bölge düzeyinde ilerleyecek.
Büyük diyagramlar, örtüşen görsel parçalara ayrılacak.
Claude, görseli ve çıkarılmış metni birlikte inceleyecek.
Metin çıkarımı tek başına görsel inceleme sayılmayacak.

Her anlamlı öğeye ayrı kimlik verilecek.
Tablo hücreleri, kararlar, koşullar ve istisnalar kaydedilecek.
Akış kutuları ile kutuları bağlayan çizgiler ayrı incelenecek.
Her öğenin sayfası ve bölgesi belirtilecek.
Bağlantı başka bölgede sürüyorsa devam noktası kaydedilecek.
Sayfalar bitince bütün iş akışı yeniden birleştirilecek.
Kaynaklar arasındaki çelişkiler ayrıca incelenecek.

Durumlar açık tutulacak:

- `bekliyor`
- `inceleniyor`
- `kısmi`
- `okunamadı`
- `incelemeye_hazır`
- `doğrulandı`
- `düzeltme_gerekiyor`

Claude'un beyanı doğrudan `doğrulandı` durumuna dönüşmeyecek.
Codex, iddiaları kaynak konumlarıyla karşılaştıracak.
Eksik kalan öğeler ve akış bağlantıları yeniden atanacak.
Tüm dosya bitmeden dosya tamamlandı sayılmayacak.

## Sonuçların kabulü

Codex şu ayrımları koruyacak:

- Kaynakta açıkça bulunan bilgi.
- Kaynaktan çıkarılan yorum.
- Önerilen çözüm.
- Henüz çalıştırılmamış deney.
- Henüz doğrulanmamış uygulama davranışı.

Bir belgede bulunamayan kural, bütün arşivde yok sayılmayacak.
Yazılı tasarım, çalışan uygulama kanıtı olarak sunulmayacak.
Her önemli bulguya kaynak konumu eklenecek.
Her öneride girdi, çıktı, sorumlu parça ve kalan eksiklik açıklanacak.
Her bilinmeyen için onu ortaya çıkaracak gözlem veya deney tanımlanacak.
Kaynak projelerde deney çalıştırılmayacak.

Raporlar ana dizinde `103.md` ile devam edecek.
Mevcut `101.md` ve `102.md` korunacak.
`101.md` ön incelemedir.
`102.md`, tek PDF'nin yalnız üç bölgesini kapsıyor.
Bu raporlar bütün klasörün tamamlandığını göstermiyor.

## Canlı ilerleme ve hesap geçişi

Koordinatör, Pane'in olay bekleme aracını kullanacak.
Rapor, bekleme, hata veya kapanma olayı yeni değerlendirme başlatacak.
Koordinatör aynı işi ikinci kez başlatmadan etkin çalışmaları kontrol edecek.
Kullanıcının durdurduğu ajan kendiliğinden yeniden başlatılmayacak.

Kota hatası, genel teknik hatadan ayrılacak.
Koordinatör eski çalışanın gerçekten durduğunu doğrulayacak.
Doğrulanmış bulgular ve kalan öğeler bir devir dosyasına yazılacak.
Yeni hesap, bu devir dosyasından yeni çalışma başlatacak.
Hesap değişimi, eski konuşmanın eksiksiz taşındığı anlamına gelmeyecek.
Doğrulanmamış bölüm, yeni hesapta tamamlanmış sayılmayacak.

Bir hesap sınıra ulaşınca bekleme zamanı kaydedilecek.
Uygun hesap yoksa sistem yoğun yeniden deneme yapmayacak.
Hesapların açılması, kota geçişinin sınandığı anlamına gelmez.
Kota geçişi için kontrollü doğrulama sonucu ayrıca kaydedilecek.

Mac veya Pane kapanırsa yerel çalışma kesilebilir.
Yeniden açılınca koordinatör kalıcı kayıtları uzlaştıracak.
Bu sınır, kesintisiz çalışma garantisi olarak gizlenmeyecek.

## Güncel kurulum

Pane sürümü `2.4.216` olarak gözlendi.
Claude Code sürümü `2.1.295` olarak gözlendi.
Güncel Pane komutu `/Users/w6x/.pane/bin/runpane` konumundadır.
Hesap kaydı `/Users/w6x/.config/claude-denetim/accounts.json` dosyasındadır.
Bu kayıt parola veya oturum anahtarı içermez.

Pane oturumu:
`__orchestration_session_63eaa959-f979-4db8-b2a9-a092df8c103c__`

Çalışanların Pane kimliği:
`e6237362-e3c5-4616-ad8b-725d0616b8af`

Yeni canlı çalışma kayıtları `.claude-denetim/live` altında tutulacak.
Eski `run.py` artık zamanlayıcı tarafından çağrılmıyor.
Eski betik, yeni canlı sistemle eşzamanlı başlatılmayacak.

Gerçek okurla denenmedi.
