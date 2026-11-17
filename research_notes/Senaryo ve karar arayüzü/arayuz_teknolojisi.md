# Senaryo ve karar arayüzü: teknoloji ve çıktı kararı

Araştırma tarihi: 27 Eylül 2026. Bu not bir UI tasarım kararıdır; fabrika kurulumu veya kod değişikliği değildir. Mevcut uygulama yalnız statik olarak okundu. JSON eşinde yerel dosya SHA-256 değerleri, satır kanıtları ve çalıştırılmamış kabul deneyleri bulunur. `otomasyon coding 2` bu alt görevde değiştirilmedi.

## 1. Seçimlerden senaryo üreten arayüz için hangi UI temeli uygun?

### Takeaway

Mevcut React + Mantine + TypeScript/SCSS temelini korumak uygun. Tailwind/daisyUI geçerli alternatifler; fakat bu karar formunda değiştirmeyi gerektiren ölçülmüş bir kazanım yok. Öncelik şık yeni bileşenler değil, kullanıcının seçiminin anlamını korumak, anlaşılır etkilerini göstermek ve aynı senaryodan güvenilir çıktılar üretmek.

### Cited Findings

Mantine 8.3.18’in resmî Radio belgesi native radio sarmalayıcısını, etiketli grup kullanımını ve klavye destekli Radio.Card bileşenini açıklar. Radio.Indicator tek başına etkileşimli veya erişilebilir değildir. Bu nedenle mevcut gerçek Radio ve Checkbox kullanımı doğru yöndedir; görsel kartla değiştirilirse anlamı korunmalıdır. [Mantine 8 Radio](https://v8.mantine.dev/core/radio/)

Tailwind sunumu utility sınıflarıyla düzenler. daisyUI bu katmanın üzerinde CSS bileşen adları sunar ve kendi layout CSS’iyle de kullanılabilir. Senaryo verisi, doğrulama veya iş kurallarını bu CSS katmanları üstlenmez. [Tailwind](https://tailwindcss.com/docs/styling-with-utility-classes), [daisyUI](https://daisyui.com/docs/intro/)

Yerel `KararPaneli.tsx:16–39` tekil seçenekleri etiketliyor; soru başlığı ayrı Text, Radio.Group/Checkbox.Group bağlantısı görünmüyor. `depo.tsx:115–129` import doğrulaması yalnız üst düzey şekli kontrol ediyor. `depo.tsx:80–100` faz seçiminde kuralları tekrar atıyor, silinen kümenin aşamalarını ilk kalan kümeye aktarıyor. Bunlar uygulama kaynak gözlemleri; tarayıcıda yeniden üretilmiş hata iddiaları değildir. [Karar paneli](</Users/w6x/Documents/otomasyon coding/fabrika-karar-merkezi/src/bilesenler/KararPaneli.tsx:16>), [state ve import](</Users/w6x/Documents/otomasyon coding/fabrika-karar-merkezi/src/durum/depo.tsx:80>)

### Inferences

Önerilen akış: **Senaryonu seç → Kararları değiştir → Etkiyi ve açıkları gör → Ana akış/alt süreçte incele → JSON/PDF al.** Kullanıcıya ilk ekranda teknoloji kataloğu veya kod editörü yüklenmemeli. Derin açıklama, kaynak ve teknik ayrıntılar ilgili kararın yanında açılmalı.

- Radio: birbirini dışlayan tercih. Kararsızlık varsa açık “Henüz seçmedim” değeri bulunur.
- Checkbox: birlikte seçilebilen yetenekler. Seçenekler arası önkoşul görünür açıklanır.
- Switch: etkisi hemen anlaşılan aç/kapat ayarı. Belirsiz veya kritik mimari kararı iki değerli switch içine sıkıştırma.
- Grup sorusu programatik etiketlenir; hata/açıklama ilişkilendirilir. Klavye odağı diyagram yenilendiğinde kaybolmaz. Renk tek anlam taşıyıcısı olmaz.
- Faz değişimi veya küme silmenin etkisi görünür olur, geri alınır; “varsayılan öneri” ile “kullanıcının seçimi” ayrı saklanır.

Tek doğruluk kaynağı sürümlü senaryo JSON’dur. `schema_version`, `scenario_id`, `revision`, kaynak/katalog sürümü, kararların kimliği/değeri/kökeni, açık sorular ve kanıt referansları taşır. Her görünüm bu snapshot’tan türetilir. Seçili bir kontrolün durumu ile gerçekten uygulandığı ve test edildiği durum ayrı eksenlerdir. Bir kutuyu işaretlemek `passed` üretmez. İçe aktarma tam şema, enum, referans ve boyut denetimiyle atomik yapılır; bozuk JSON mevcut senaryoyu değiştirmez. localStorage kolaylıktır; taşınabilir ve yeniden içe alınabilir JSON asıl kullanıcı çıktısıdır.

### Gaps

Ekran okuyucu/klavye testi bu tur yapılmadı. Mevcut state katmanının yalnız incelenen yerleri için gözlem yapıldı; tüm uygulamaya erişilebilirlik veya veri güvenliği sertifikası verilmedi. UI teknolojilerinin performans ve paket boyutu karşılaştırılmadı. Bu tur yalnız araştırma notları yazıldı.

## 2. Diyagram motoru Mermaid mi D2 mi; ECharts nerede kullanılmalı?

### Takeaway

Mermaid mevcut akış, durum ve sıra diyagramlarının varsayılan çizicisi olarak uygun. ECharts yalnız nicel karşılaştırma ve dağılım görünümlerinde kullanılmalı. D2, aynı senaryo modelini tüketebilen koşullu bir alternatif çizici olabilir; sırf daha yeni veya farklı diye tüm arayüzün temeli yapılmamalı.

### Cited Findings

Mermaid `accTitle`/`accDescr` ile SVG’ye başlık/açıklama ekler; bu tek başına düğümler arasında klavye gezinmesi sağlamaz. `strict` güvenlik seviyesi HTML’yi kodlar ve click davranışını kapatır. Etkileşim için güvenliği gevşetmek yerine diyagramın yanında normal bağlantı ve metinli aşama listesi sunulabilir. [Mermaid erişilebilirliği](https://mermaid.js.org/config/accessibility), [güvenlik seviyesi](https://mermaid.js.org/config/schema-docs/config-properties-securitylevel.html)

D2 resmî FAQ, WebAssembly/D2.js ile tarayıcıda çalışabildiğini doğrular; aynı sayfa binlerce düğümde test edilmediğini belirtir. D2 CLI’nin varsayılan çıktısı SVG’dir. Resmî export belgesine göre PDF, PNG çıktılarının PDF sayfalarına yerleştirilmesiyle üretilir; bunu otomatik vektör PDF üstünlüğü saymak yanlış olur. SVG’de font/CSS davranışı görüntüleyiciye göre değişebilir. [D2 FAQ](https://d2lang.com/tour/faq/), [D2 export](https://www.d2lang.com/tour/exports/)

ECharts iki çiziciyi destekler. SVG yakınlaştırmada keskin kalır; çok elemanlı grafiklerde Canvas daha uygun olabilir. Yerel `EGrafik.tsx:5–23` SVGRenderer, ResizeObserver ve açıklamalı img rolü kullanıyor. Karşılaştırmanın verisi ayrıca tablo olarak erişilebilir olmalı. [ECharts renderer karşılaştırması](https://echarts.apache.org/handbook/en/best-practices/canvas-vs-svg/), [yerel grafik](</Users/w6x/Documents/otomasyon coding/fabrika-karar-merkezi/src/grafik/EGrafik.tsx:5>)

### Inferences

Tak-çıkar sınırı çizici adaptöründe kurulmalı: `scenario snapshot → graph model → renderer → SVG + erişilebilir metin + render status`. D2/Mermaid metni kanonik karar verisinin yerini almamalı. Böylece çizici değiştiğinde kullanıcının karar dosyası, kaynak bağları ve navigasyonu korunur.

Özet görünüm yalnız ana sınırları gösterir; detay görünümü seçilen süreç, hata yolu veya sorumluluk alanına iner. Aynı kimlik tablodan diyagrama ve kaynak ayrıntısına gider. 12×12 ekip tahayyülü yüzlerce kutuyu tek sayfaya sıkıştırma gerekçesi değildir; organizasyon sayısı ile görsel küme sayısı farklıdır. D2 adaylığı ancak aynı temsili senaryolarda okunabilirlik, kenar/düğüm bütünlüğü, çizim zamanı, bellek ve offline dosya testi daha iyi sonuç verirse ilerler.

Mevcut singlefile build yapılandırması bir paketleme niyetidir; çevrimdışı çalışma kanıtı değildir. Tek HTML tesliminde bütün JavaScript, CSS, font ve gerekiyorsa WASM/worker bağımlılıkları paketlenmeli; haricî CDN/fetch gereksinimi gerçek ağ kapatma testiyle yakalanmalıdır. [Yerel build ayarı](</Users/w6x/Documents/otomasyon coding/fabrika-karar-merkezi/vite.config.ts:5>)

### Gaps

D2.js’in gerçek paket/worker/WASM gömme ayrıntısı bu dar turda incelenmedi; tarayıcı desteği tek dosya `file://` uyumluluğunu kanıtlamaz. D2 veya Mermaid karşılaştırma deneyi yapılmadı. Mermaid’nin güncel doküman sayfası yereldeki 11.17.2’den üst sürümü gösteriyor; ayrıntılar sabit yerel sürümle test edilmeli. D2’nin CLI PDF açıklaması, tarayıcıdan inline SVG yazdırmanın da raster olmak zorunda olduğu anlamına gelmez.

## 3. Tek HTML’den eksiksiz ve okunabilir PDF nasıl üretilebilir?

### Takeaway

Ekranın anlık görüntüsünü basmak yerine, seçilen senaryonun sabit snapshot’ından ayrı bir rapor DOM’u üretmek gerekir. Mevcut uygulamada bu ayrı rapor sayfası var; güçlendirilmesi gereken nokta hazırlık koşulu ve çıktı doğrulamasıdır. “8 saniye geçti” bir PDF tamamlanma kriteri olamaz.

### Cited Findings

Yerel rapor çizilen diyagram ID sayısını izliyor; buna rağmen 8 saniye sonra print çağıran yedek yol var. Manuel PDF düğmesi doğrudan `window.print()` çağırıyor. Çizim bileşeninin hata yolu önceki SVG’yi temizlemiyor veya eski sürüm diye damgalamıyor. Bunlar eksik veya eski görsel basılması için somut risk yollarıdır; henüz yeniden üretilmediler. [Rapor hazırlığı](</Users/w6x/Documents/otomasyon coding/fabrika-karar-merkezi/src/sayfalar/Rapor.tsx:23>), [manuel export](</Users/w6x/Documents/otomasyon coding/fabrika-karar-merkezi/src/sayfalar/Rapor.tsx:54>), [render hata yolu](</Users/w6x/Documents/otomasyon coding/fabrika-karar-merkezi/src/diyagram/MermaidGorunum.tsx:13>)

CSS print medyası ve `@page` ekranla basılı sayfanın farklı düzenlenmesini sağlar; print olayları UI’yi hazırlamak için kullanılabilir. Playwright `page.pdf()` print CSS kullanır, sayfa ölçüsü/arka plan/tagged/outline seçenekleri sunar. Bunlar otomatik kabul testinin araçlarıdır; PDF içeriğinin doğru olduğunu kendiliğinden kanıtlamaz. [MDN printing](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Media_queries/Printing), [Playwright PDF](https://playwright.dev/docs/api/class-page#page-pdf)

Yerel CSS `break-inside: avoid`, `overflow: visible`, `max-height:250mm` kullanıyor. Sayfadan uzun bir diyagramın okunabilirliği bu kurallarla garanti edilemez. [Print CSS](</Users/w6x/Documents/otomasyon coding/fabrika-karar-merkezi/src/stiller/genel.scss:104>)

### Inferences

Önerilen PDF sözleşmesi: Senaryo digest’i sabitlenir; tüm beklenen diyagramlar aynı digest için başarıyla üretilir; fontlar/görseller ve print ölçülerindeki yerleşim hazır olur; animasyon durur; hata varsa kullanıcıya ilgili diyagram gösterilir. Zaman aşımı, eksik PDF’yi başarı diye sunmak yerine açık hazırlama hatası verir. Export sırasında değişen seçim yeni bir snapshot oluşturur, eski callback yeni raporu hazır yapmaz.

Rapor, ekranın açık sekmelerinden bağımsız olarak seçilen bütün bölümleri render eder. SVG `viewBox`, ok uçları, yapışkan notlar ve uzun Türkçe etiketler incelenir. Çok uzun akış ana akış ve alt süreç sayfalarına bölünür; gerekirse yatay sayfa ve ayrı SVG eki sunulur. `htmlLabels`/foreignObject bağımlılığı baskı dönüştürücüsünde sorun gösterirse ayrı saf SVG text profili denenir; bu çözüm peşinen başarılı sayılmaz. Font tercihi çevrimdışı ve Türkçe glifleri kapsamalı; PDF’de metin çıkarımı ve görsel kontrol birlikte yapılmalıdır.

İlk gerçek kabul turu şu kanıtları üretmeli; hepsinin mevcut durumu **not_run**:

1. Yalnız klavye ve VoiceOver ile seçim, açıklar, rapor; etiket/grup bağlamı ve odak korunması.
2. JSON round-trip aynı normalize digest; yanlış enum/id/sürüm/boyut içe alması mevcut state’i korur.
3. Geciktirilmiş/bozuk çizim ve çizim sırasında senaryo değişimi; erken veya karışık sürümlü PDF engellenir.
4. Gerçek PDF kaydı; bütün sayfaları raster önizlemede inceleme ve metin/ID sayımıyla bölüm atlanmadığını kontrol etme. Gizli sekme, uzun tablo, ok ucu, Türkçe font ve taşma örnekleri kullanılır.
5. Ağ kapalı `file://` çalışma, JSON/SVG/PDF yolları; dış istek olmaması. Mac Safari ve Chromium yazdırması ayrı kontrol edilir.
6. Tüm kontroller seçili fakat testler `not_run` iken “riskler çözüldü / fabrika hazır” çıktısı üretilmemesi. Seçim kapsamı ve doğrulanmış çalışma ayrı kalır.

### Gaps

Tarayıcı açılmadı, uygulama build edilmedi, PDF oluşturulmadı ve hiçbir kabul deneyi koşulmadı. `tagged` PDF seçeneği yardımcı olabilir fakat gerçek ekran okuyucu ve okuma sırası denetiminin yerini tutmaz. Tam erişilebilir PDF veya bütün tarayıcılarda piksel eşitliği bu araştırmada vaat edilmiyor. Çalışma yalnız karar notu ve onun JSON kaydıdır.
