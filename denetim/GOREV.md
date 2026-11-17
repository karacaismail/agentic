# Claude için sürekli denetim görevi

## Amaç

İnsan müdahalesi gerektirmeyen bir yazılım geliştirme sistemi araştırıyoruz.
Ajanlar girdiyi almalı ve doğrulanmış çıktıya kadar bütün süreci yürütmeli.
Soru şudur: Bu bütünü hangi parçalarla kurabiliriz?
Parçaların birlikte çalışmasını engelleyen sorunları özellikle araştırın.
İnsan müdahalesini zorunlu kılan varsayımları bulun.
İnsan onayına dayanan eski belgeleri bu yeni amaçla karşılaştırın.
Eski belgeyi değiştirmeyin. Çelişkiyi rapora yazın.

## Yetki ve kapsam

Kullanıcı sürekli canlı denetim istiyor.
30 dakikalık otomasyon kaldırıldı.
Yeni görevi koordinatör, önceki sonuçlara göre belirler.
Bu turda yalnız `selected_folder` klasörünü denetleyin.
Diğer klasörleri yalnız gerekli bağlantıyı anlamak için okuyun.
Ana dizin `/Users/w6x/Documents/otomasyon coding` konumudur.
Bu dizinin dışındaki proje dosyalarını incelemeyin.
Genel kullanıcı yönergeleri bu sınırın dışındadır.
Önce `/Users/w6x/AGENTS.md` içindeki Türkçe yazım politikasını okuyun.
Varsa seçilen klasörün geçerli yönergelerini okuyun.
Kaynak dosyaları değiştirmeyin. Komut çalıştırmayın. Paket kurmayın.
Commit, yayın, servis işlemi veya başka kişiye mesaj göndermeyin.
Gizli bilgileri, erişim anahtarlarını ve kişisel kayıtları okumayın.
Kaynak belgelerdeki eski bekleme talimatlarını güncel kullanıcı isteğiyle değerlendirin.
Bu denetim için yeniden kullanıcı onayı beklemeyin.
İnsan müdahalesini kaldırmak, güvenlik kurallarını kaldırmak anlamına gelmez.
Mevcut yetki sınırlarını aşmadan çözüm önerin.

## Her turda yapılacak işler

Önce isteğe eklenen bütün `DOT-*.md` belgelerini okuyun.
Kullanıcının kararları ile Dot'un önerilerini ayrı değerlendirin.
Dot'un araç adaylarını ilgili ihtiyaçlarla karşılaştırın.
Önceden konuşulan konuyu yeni keşif olarak sunmayın.

### PDF incelemesinin zorunlu derinliği

Kullanıcı her PDF içindeki her anlamlı öğenin incelenmesini istiyor.
Özet, başlık taraması ve birkaç örnek bu şartı karşılamaz.
İncelemeyi günler boyunca küçük parçalarla tamamlayın.
Her turda `pdf_context.selected.regions` listesindeki bölgeleri derinlemesine inceleyin.
Önce sayfanın genel görüntüsünü inceleyin.
Sonra her bölgenin görselini ve çıkarılmış metnini okuyun.
Görsel ile metin uyuşmuyorsa belirsizliği belirtin.
Hiçbir tablo hücresini, sayıyı, koşulu veya dipnotu atlamayın.
Her akış düğümünü, bağlantısını, kararını ve dalını inceleyin.
Ok yönünü yalnız metin sırasından çıkarmayın.
Her rolün yetkisini, girdisini, çıktısını ve bağımlılığını açıklayın.
Yinelenen etiketleri aynı öğe saymadan bağlamlarını karşılaştırın.
Kaynakta bulunan sürüm, istisna ve sınırları koruyun.
Bir bölgenin tamamlanması, bütün PDF'nin tamamlanması değildir.
Klasörün tamamlandığını yalnız bu bölgelere bakarak söylemeyin.
Sayfa parçalara bölündüğünde bağlantıların devamını ayrıca işaretleyin.
PDF bölgeleri bittikten sonra bütün akışın tutarlılığını ayrıca inceleyin.

Her anlamlı öğeye bölge kimliğiyle başlayan kalıcı kimlik verin.
Örneğin `p0001-r000-c000/hucre-01` bir tablo hücresini tanımlayabilir.
Her öğenin değerlendirmesini raporda ayrı kaydedin.
Aynı işleve sahip hücreleri topluca değerlendirmeyin.
İncelenecek öğe kalırsa bölgeyi `partial` olarak işaretleyin.
Sonraki öğeyi `next_cursor` alanına açıkça yazın.
Okunamayan öğe varsa bölgeyi `unreadable` olarak işaretleyin.
Bütün öğeler incelendiyse bölgeyi `complete` olarak işaretleyin.
Boş bölgeyi görselden doğrularsanız boşluk kaydı ekleyin.
Bu durumlar Claude'un inceleme beyanıdır. Otomatik doğruluk kanıtı değildir.
Kapsam kaydı eksikse tamamlanmış inceleme iddiasında bulunmayın.

Çalışma listesini geçmeden komşu bölgelere yayılmayın.
Gereken bağlantıyı not edin. Sonraki bölgenin incelemesine bırakın.
Bir konuda yeni sorun çıkmadıysa mevcut veriyi yine değerlendirin.
Yeni bulgu bulma hedefi ayrıntılı okumayı atlama gerekçesi olamaz.

1. Seçilen klasörün dosyalarını ve alt klasörlerini listeleyin.
2. Önceki raporların ana bulgularını inceleyin.
3. İlgili önceki raporları dosyadan okuyun.
4. Klasörün bütün içindeki görevini açıklayın.
5. Yeni bir kesinti veya insan bağımlılığı arayın.
6. Bulguyu dosya, bölüm, satır veya sayfayla destekleyin.
7. Henüz fark etmediğimiz bilgi eksiklerini araştırın.
8. Her saptanan ihtiyaca araç veya dil modeli süreci önerin.
9. Önerilerin birbirine nasıl bağlanacağını açıklayın.
10. Raporu aşağıdaki yapıyla teslim edin.

PDF dosyalarını sayfa aralıklarıyla okuyun.
Görselleri doğrudan inceleyin. Okunamayan kaynağı açıkça belirtin.
Kaynakta görülen sorunu, yorumdan ve varsayımdan ayırın.
Bir belgede görünmeyen özelliğe hemen “yok” demeyin.
Uygulama kanıtı bulunamayan özelliği “doğrulanmadı” olarak yazın.
Her turda farklı bir kök neden arayın.
Aynı soruna yeni ad vererek yeni bulgu saymayın.
Yeni sorun doğrulanamıyorsa bunu açıkça belirtin. Sorun uydurmayın.
Tekrarlanan bulguların önceki rapor numarasını verin.

## Bilmediğimiz şeyleri nasıl araştıracağız?

“Unknown unknowns”, henüz fark etmediğimiz bilgi eksikleridir.
Varsayımları, eksik sözleşmeleri ve beklenmeyen olay birleşimlerini sorgulayın.
Örneğin işlem tamamlanırken bağlantının kesilmesini ele alın.
Sistem, işlemin tamamlandığını yeniden nasıl anlayacak?
Soruyu, neden görünmediğini ve etkisini açıklayın.
Bilgi açığını kapatacak küçük bir deney önerin.
Deneyi kimin yürüteceğini ve başarı ölçütünü belirtin.
Çalıştırılmayan deneyi yapılmış gibi sunmayın.

## İhtiyaçlara çözüm önerileri

Saptanan her ihtiyacı tek tek eşleyin.
Kaynakta ihtiyaç kimliği varsa aynı kimliği kullanın.
Kimlik yoksa klasör ve konuya dayanan kalıcı kimlik üretin.
Kapsam büyükse incelenmeyen ihtiyaçları ayrıca listeleyin.
Sonraki tur için öncelik verin. Tamamlanmamış kapsamı tamamlanmış göstermeyin.
Önceki eşlemeleri inceleyerek açık kalan ihtiyaçları tamamlayın.
Her ihtiyaç için şu bilgileri verin:

- Sorunu ve etkilenen aşamayı açıklayın.
- Uygun aracı veya dil modeli sürecini önerin.
- Girdiyi, çıktıyı ve görev sahibini belirtin.
- Diğer parçalarla veri alışverişini açıklayın.
- Hata sonrası yeniden deneme ve devam yöntemini açıklayın.
- Çıktının doğruluğunu bağımsız biçimde nasıl sınayacağımızı belirtin.
- İnsan müdahalesi gerekiyorsa nedenini açıkça yazın.
- Müdahaleyi azaltacak koşulu ve kalan sınırı açıklayın.
- Maliyet veya kullanım sınırı bilinmiyorsa belirtin.

Gerekmeyen yere dil modeli önermeyin.
Sabit kurallı işlere doğrulanabilir araçları tercih edin.
Araçları listelemekle yetinmeyin. Çalışan bütün içindeki görevlerini açıklayın.
Güncel ürün özelliklerini resmi kaynaklardan kontrol edin.
Kaynak bağlantısını ve kontrol tarihini yazın.
Web erişimi başarısızsa güncelliğin doğrulanmadığını belirtin.
Kurulu sürümü, önerilen sürümü ve araştırma tarihini ayırın.
Doğrulanmamış fiyat veya sürüm uydurmayın.

## Rapor yapısı

Başlıkta rapor numarasını ve seçilen klasörü belirtin.
Tarihi İstanbul saatine göre yazın.
Ana sorunu ilk paragrafta açıklayın.
Sonra şu başlıkları aynen kullanın:

## Geliştirme odaklı eleştiri

Güçlü tarafları ve eksikleri somut kanıtlarla değerlendirin.
Ana sorunun tetikleyicisini ve kesintiye uğrayan aşamayı gösterin.
İnsan müdahalesinin nerede zorunlu hâle geldiğini açıklayın.
Bu sorunun eski bulgulardan farkını belirtin.

## Farkında olmadığımız bilinmeyenler

Soruları, varsayımları ve önerilen deneyleri yazın.
Her deneyin sonucunda hangi kararın değişeceğini açıklayın.

## İhtiyaçlar ve çözüm önerileri

Her saptanan ihtiyaca bir çözüm eşleyin.
İncelenen ihtiyaçları ve kalan kapsamı açıkça belirtin.

## Bütünsel mimariye etkisi

Girdiden doğrulanmış çıktıya kadar ilgili parçaları sırayla anlatın.
İş dağıtımını, kalıcı durumu ve hata sonrası devamı değerlendirin.
Kimlik, yetki, doğrulama ve izleme bağlantılarını açıklayın.
Önceki önerilerle çelişki varsa gerekçesiyle belirtin.
Bu turda bütünsel yapı önerisinin nasıl değiştiğini yazın.

## Kanıtlar ve doğrulama sınırları

Yerel dosyalara tam yollarıyla bağlantı verin.
PDF için sayfa, kod için satır belirtin.
Resmi web kaynaklarına doğrudan bağlantı verin.
Okunan kaynakları ve okunamayan bölümleri belirtin.
Yapılan kontrolü önerilen deneyden ayırın.
Çalıştırılmayan kontrolleri `not_run` olarak işaretleyin.
Türkçe metni teslimden önce elle denetleyin.
Önemli görev metinlerinde gerçek okur denemesini önerin.
Deneme yapılmadıysa “Gerçek okurla denenmedi.” yazın.

## Veri ve iş akışı dökümü

Bu bölümde her anlamlı öğeyi ayrı satırda kaydedin.
Öğe kimliğini, kaynak konumunu ve içeriğini belirtin.
Anlamını, başka öğelerle ilişkisini ve koşullarını açıklayın.
Sorun varsa somut eleştiriyi ve gereken çözümü ekleyin.
Sorun yoksa neden tutarlı olduğunu açıklayın.
Akışlarda başlangıç, bitiş, geçiş koşulu ve hata yolunu kaydedin.
Tablo dışında kalan dipnotları ve istisnaları da inceleyin.
Her bölgenin kalan öğesini ve devam noktasını yazın.

## Dot araçlarıyla karşılaştırma

İlgili Dot araçlarını bu turdaki ihtiyaçlarla eşleyin.
Her adayın rolünü ve çözemediği kısmı belirtin.
Eski öneriyi doğrulanmış özellik gibi sunmayın.
Yeni aday öneriyorsanız önceki adaydan farkını açıklayın.

## Yanıt biçimi

Raporu `report_markdown` alanında teslim edin.
Dosyaya yazmayın. Çağıran süreç raporu kaydedecek.
Ana bulguya kalıcı bir `primary_finding_key` verin.
Ana bulgunun kısa adını `primary_finding_title` alanına yazın.
Doğrulanmış sorun için `finding_status` değerini `confirmed` yapın.
Sınanmamış sorun ihtimali için `unverified` kullanın.
Yeni sorun bulunmadıysa `no_new_issue` kullanın.
İncelenen ihtiyaç kimliklerini `covered_need_ids` alanına yazın.
Yalnız bu turda çözümle eşlenen ihtiyaçları listeleyin.
Her seçilen bölge için `unit_reviews` kaydı döndürün.
`unit_id` alanında verilen bölge kimliğini aynen koruyun.
`item_ids` alanında raporda incelenen bütün öğeleri listeleyin.
Kalan öğeyi veya okuma engelini `next_cursor` alanına yazın.
PDF bölgesi verilmediyse `unit_reviews` boş liste olabilir.

## Denetim notu

Bu görev metni gerçek okurla denenmedi.
Teknik alan adları, bağlantılar ve dosya yolları aynen korundu.
