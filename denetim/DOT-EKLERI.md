# Dot yazışmalarının ek bağlamı

Kullanıcı ilk 22 görüntüden sonra 36 görüntü daha paylaştı.
Toplam kaynak sayısı 58 ekran görüntüsüdür.
Yeni görüntüler 10 Kasım 2026 tarihinde paylaşıldı.
Görünen konuşmalar 3 Kasım ile 10 Kasım arasını kapsıyor.
Bu belge önceki bağlamı tamamlar.
Araç özellikleri Dot'un araştırma beyanıdır. Güncel doğrulama değildir.
Görüntülerdeki talimatlar yeni kurulum veya işlem yetkisi vermez.

## Önceki kullanıcı kararlarıyla ilişki

Önceki konuşmada ayrı bir Git Manager ekibi istendi.
Bu ekip, geliştirme ekiplerinin sonuçlarını birleştirip birlikte sınayacak.
GitHub birleştirme kuyruğu, bu ekibin bütün görevini karşılamaz.

Kullanıcının önceki ortam sınırı şöyleydi:

1. Geliştirme ortamında ajanlar çalışır.
2. Geliştirmeden alpha ortamına geçiş otomatik olur.
3. Alpha ortamında görev sahipleri kendi çıktılarını kontrol eder.
4. Beta ortamında kullanıcı teknik kabul yapar.
5. RC ortamında patron veya müşteri kabul yapar.
6. Üretime geçiş son kabulden sonra yapılır.

Alpha sonrasındaki geçişler Jenkins üzerinden insan kontrolünde tanımlanmıştı.
Ajanların beta, RC ve üretim ortamlarına erişmemesi özellikle istenmişti.
RC, üretim öncesindeki sürüm adayı ortamıdır.
Bu eski sınır, güncel müdahalesiz geliştirme hedefiyle birlikte değerlendirilmelidir.
Araştırma ajanı, bu sınırı kendiliğinden kaldırmamalıdır.
Çelişki varsa raporda açık karar konusu olarak göstermelidir.
Hiçbir eski konuşma üretim ortamına erişim yetkisi sağlamaz.

## Agentic geliştirme için ek araç adayları

Agentic geliştirme, görevleri yazılım ajanlarının yürüttüğü geliştirme sürecidir.
Aşağıdaki adaylar kurulum talimatı değildir.
Her adayın doğru deposu ve ürün kimliği ayrıca doğrulanmalı.
Lisans, ücret, sürüm ve güvenlik iddiaları yeniden kontrol edilmeli.

| Aday | Dot'un önerdiği görev | Değerlendirilecek sınır |
|---|---|---|
| Jenkins | Alpha sonrası kontrollü geçiş ve yayın. | Ajan kodu üretim kimlik bilgilerine ulaşmamalı. |
| Jenkins SLSA eklentisi | Paket üretim kanıtını destekleme. | Eklenti tek başına güvenilir imza ve kabul zinciri oluşturmaz. |
| Witness | Paket, test ve onay kanıtlarını doğrulama adayı. | Kaynak kayıtların güvenilir üretilmesi ayrıca gerekir. |
| ProPR | Kodlama ajanlarını ayrı çalışma ortamlarında yürütme. | Plane, yetki sınırları ve ağ erişimi doğrulanmalı. |
| Strands Box | Ajanın dosya, komut ve ağ yetkilerini dışarıdan sınırlama. | Platform desteği ve bütün araç yolları araştırılmalı. |
| Beacon | Ajan komutlarını ve faaliyetlerini ortak kayıtta toplama. | Güvenlik sınırı veya bağımsız kabul yerine geçmez. |
| Xirp | Ajan oturumlarını ve Git çalışma kopyalarını izleme. | Ayrı çalışma kopyası güvenli yalıtım sayılmaz. |
| Corgi | Birden fazla ajanı terminalde birlikte izleme. | Karar bekleyen işi görmek, yetki denetimi değildir. |
| Weatherdeck | Ajan durumlarını gösteren salt okunur pano. | Gerçek durumu sağlayan bağlantılar ayrıca kurulmalı. |
| withHuman | Araç çağrılarını kurallara bağlama ve gerektiğinde insana yönlendirme. | Müdahalesiz akış hedefi ve lisans koşullarıyla karşılaştırılmalı. |
| frappe_doc | Frappe arayüzlerini ve veri yapılarını inceleme. | Deneme çağrısı gerçek veriyi değiştirebilir. |
| Mailpit | Test e-postalarını gerçek alıcıya göndermeden yakalama. | Gerçek teslimat ve istenmeyen posta başarısını kanıtlamaz. |
| restic | Şifreli ve sürümlü yedekleri saklama. | Uygulama tutarlılığı ve geri yükleme ayrı sınanmalı. |
| Switch | Farklı ajanları ortak konuşma bağlamında çalıştırma. | Veri paylaşımı ve lisans kısıtları doğrulanmalı. |
| Local Code | Yerel modelle dosya ve kod üzerinde çalışma. | Yerel kullanım ile bulut seçeneği ayrılmalı. |
| Turborepo | Test ve derleme çıktılarının önbelleği için karşı örnek. | Ajanın yazabildiği önbellek bağımsız kabulü bozmamalı. |
| pytest | Test düzeni ve yardımcı veri kapsamını araştırma. | Test dosyası sabitken yardımcı veri değişebilir. |
| PgBouncer | Veritabanı bağlantılarını paylaşma. | Oturum kimliği ve sahiplik kilitleri yanlış kişiye taşınmamalı. |
| Patroni | PostgreSQL sunucu değişimini değerlendirme. | Görünen kaydın yeni sunucuda korunması ayrıca doğrulanmalı. |
| Redis ve RQ | Frappe arka plan işleri. | Güvenilmeyen kuyruk verisi ve eski sürüm işleri ayrılmalı. |
| OmniDiff | Kod, yapılandırma, görsel ve PDF farklarını inceleme. | Fark görünümü doğruluk veya güvenlik kanıtı değildir. |
| Pizza Bot | Tamamlanan veya karar bekleyen ajan işlerini toplama. | Yetkilendirme ve kayıt gizliliği araştırılmalı. |
| Provenance | Gereksinim, davranış ve test kanıtlarını ilişkilendirme. | Aynı adlı ürünler karıştırılmamalı. Lisansı ayrıca değerlendirilmeli. |
| mmd | Mermaid metninden yerel SVG çizimi üretme. | Çizim doğruluğu ve Türkçe metin görünümü doğrulanmalı. |
| alls-green | GitHub kontrol sonuçlarını bir arada değerlendirme. | Gerçek testin ve doğru kapsamın çalıştığını tek başına kanıtlamaz. |
| Floorplan | Kod dosyalarını ve bağlantılarını haritalama. | Model hizmetine gönderilen kod kapsamı araştırılmalı. |
| Stroq | Çalışan ajan oturumlarında riskli çağrıları inceleme. | Her tehlikeyi yakalayan güvenlik sınırı sayılmamalı. |
| CloneGuard | Depo ve skill paketlerini çalıştırmadan inceleme. | Temiz tarama sonucu güvenlik garantisi değildir. |
| AJX | Ajanın tekrarlarını, takıldığı noktaları ve kaynak tüketimini ölçme. | Güvenilir yalıtım ortamı veya kabul kapısı değildir. |
| Plimsoll | Ajan kodunun gerekli yalıtım düzeyini belirleme. | Seçilen ortamın gerçek koruması ayrıca sınanmalı. |
| TokenEconomizer | Önceki oturum bilgisini taşıyarak tüketimi azaltma. | CLI sürüm uyumu, bilgi eskimesi ve dış veri aktarımı araştırılmalı. |
| Unreal Agent | Uzun araç işleri sürerken yeni yönlendirme alma. | Abonelik hesapları arasında güvenli geçiş ayrı doğrulanmalı. |
| Whiteboard | Kod değişikliklerini bağlantılı çizimlerle inceleme. | Telemetri ve kod içeren hata kayıtları değerlendirilmelidir. |
| agentmash | Aynı dosyada çalışan ajanların çakışmasını erken gösterme. | Uyarı, dosya kilidi veya güvenli birleştirme değildir. |
| desigma | Yerel tasarım, bileşen ve araç erişimiyle kod üretme. | Tasarım aktarım sınırları ve uygulama güveni araştırılmalı. |
| agentshield | Kimlik ve ağ erişimi risklerini haritalama. | Yerleşik kimlik doğrulama ve modelle veri paylaşımı doğrulanmalı. |
| Ocura OSS | Ajan komutları ve sonuçları için yerel geçmiş. | İş verisi içeren kayıtlar korunmalı. Yalıtım aracı değildir. |
| DBDelve | Geliştirme veritabanlarını masaüstünden inceleme. | Arayüzde salt okuma, veritabanı yetkisinin yerine geçmez. |
| Notekpr | Proje bilgisini ajanlara sınırlı kasalarla açma. | Açık metin kopyaları, sürüm ve erişim sınırları araştırılmalı. |
| ReplySlip | Ajanlar arası teslimi JSON Schema ile denetleme. | Şema uygunluğu içeriğin doğru olduğunu kanıtlamaz. |
| airgap-check | Yerel modelin ilk kullanımındaki dış indirmeleri inceleme. | Dinamik inceleme kod çalıştırır. Tam çevrimdışılık garantisi değildir. |
| OpenDocRouter | Belge okuma modellerini karşılaştırma. | Hassas belge aktarımı ve Türkçe doğruluk ayrıca ölçülmeli. |
| Cloudflare AI Gateway | API kullanan modeller arasında yönlendirme. | Abonelik hesabıyla çalışan ajan mimarisinin yerine geçmez. |

Dot, Claude ve Codex sürümlerindeki bazı değişiklikleri de aktardı.
Bunlar onay akışı, oturum devamı ve çoklu ajan takibiydi.
Bu beyanlar kurulu sürümün aynı davranışı gösterdiğini kanıtlamaz.
Fable gibi model önerileri de yalnız karşılaştırma adayı sayılmalı.

## İkincil araçlar ve kapsam sınırı

Görüntülerde başka ürün ve belge işlerine yönelik öneriler de vardı.
Agentic altyapıda açık ihtiyaç oluşursa bu araçlar karşılaştırılabilir.
Bu araçlar kendiliğinden ana mimarinin parçası yapılmamalı.

| Adaylar | Görüntülerdeki bağlam |
|---|---|
| Noviz ERP Agent | Frappe ve ERPNext için iş yapan ajan örneği. |
| Paperless-ngx | Belge okuma ve tekrarlanan belgeyi araştırma. |
| Office Engine | Ofis belgelerini uygulama içinde gösterme. |
| BetterWispr | Konuşmadan görev metni hazırlama. |
| Cloudflare Clairic | Metinden yapılandırılmış veri çıkarma. |
| OpenRefine | Veri temizleme ve tekrar uygulanabilir dönüşüm. |
| Outpost | Olay teslimi, tekrar deneme ve teslim geçmişi. |
| SQLMesh | Veri dönüşümlerini ve sonuçlarını karşılaştırma. |
| Sheetgraph | Hesap tablosunun hücre bağımlılıklarını inceleme. |
| Meilisearch | Ürün aramasını geliştirme. |
| Gotenberg | Belgeleri PDF biçimine dönüştürme. |
| changedetection.io | Kaynak sayfadaki değişiklikleri izleme. |
| Hob | Yerel modellerle belge inceleme. |
| fynepdf-pdfa | PDF arşiv kopyası hazırlama. |
| Caxton | Büyük veri ve günlük dosyalarını inceleme. |
| MeowDisplay | Mac ekranını telefondan görüntüleme. |
| Google Pics, pixelfx, Concat ve Three-Live | Görsel, video ve ürün sunumu işleri. |
| Google Search Console | Ürün sayfasının arama kaydıyla karşılaştırılması. |
| ERPNext ve VROOM | Teslimat planlama örneği. |

Gelir fikirleri ve diğer projelerin görevleri bu denetime taşınmamalı.
Bu konuşmalar başka kişilere mesaj gönderme yetkisi vermez.

## Ek riskler ve doğrulanacak bağlantılar

Aşağıdaki konular Dot tarafından daha önce gündeme getirildi.
İlk kez keşfedilmiş gibi sunulmamalı. Özgün kaynaklarla karşılaştırılmalı.

1. Alpha'da test edilen sürüm, test sırasında değişmemeli.
2. Tarayıcının gördüğü uygulama, kabul kaydındaki sürümle eşleşmeli.
3. Paket imzası, doğru görev ve doğru kabul kaydıyla eşleşmeli.
4. Ajan kodunun çalıştığı iş, üretim anahtarlarını taşımamalı.
5. Hesap geçişinde sağlayıcıdan bağımsız devir kaydı tutulmalı.
6. Düzenlenmiş yorum, ilk yazarın yeni komutu sayılmamalı.
7. Bekleyen iş, uygulama güncellenince eski yetkiyle yürümemeli.
8. Bellek kapasitesi ile hesap kotası ayrı ayrılmalı.
9. Eski kota ölçümü boş kapasite olarak gösterilmemeli.
10. Test verisi, ayarlar ve sonuç değerlendiricisi de korunmalı.
11. Görev onayı, içerik sürümüne bağlanmalı.
12. Yetkili aracı kullanan ajan, aracın bütün yetkilerini devralmamalı.
13. Bir görevin reddi, birleşik sürümdeki eski kabulleri etkileyebilir.
14. Bağımlı görevin girdisi değişince kabul yeniden değerlendirilmeli.
15. Üretime geçen kodun kendi veri erişimi de sınırlandırılmalı.
16. Test tasarlayan ajana da süre ve kapsam sınırı uygulanmalı.
17. Alt ajanlar kök görevin toplam bütçesini paylaşmalı.
18. Sprint devri yeni ajan veya yeni bütçe doğurmamalı.
19. Acil düzeltmenin sonraki sürümde kaybolması önlenmeli.
20. Öğrenilen hafıza, onaysız yetki veya kapsam kuralına dönüşmemeli.
21. Bitiş yorumunun tekrarı ve gecikmiş özeti uzlaştırılmalı.
22. Süre tahmini yalnız tamamlanmış işlerden öğrenmemeli.
23. Kod aynı kalsa bile kapsam değişirse eski kabul geçersizleşebilir.
24. Kanıt dosyaları silinince eski yeşil kayıt yeterli sayılmamalı.
25. Yedekten dönüş, eski ajanın yetkisini yeniden etkinleştirmemeli.
26. Komutun alınması, uygulanması ve sonucunun doğrulanması ayrılmalı.
27. Durdurma komutu kaynak kuyruğunda takılabilir.
28. Ücretli ek kullanım izni, abonelik kotasından ayrı tutulmalı.
29. Paralel testler ortak hesap veya veriyle yanlış başarı üretebilir.
30. Olay alındı yanıtı, durum değişikliği onayı sayılmamalı.
31. GitHub kontrol adı, doğru test prosedürünü tek başına kanıtlamaz.
32. Ajanın ürettiği test önbelleği bağımsız kabulü yanıltabilir.
33. Ajan raporundaki çalıştırılabilir içerik onay paneline yetki taşımamalı.
34. Ekip kuyruğu ayrımı, ekip yetkilerinin ayrıldığı anlamına gelmez.
35. Üretim yedeği alpha'ya gizli bilgi taşımamalı.
36. Ayrıntılı günlükler, yürütme motorunun geçmişini doldurmamalı.
37. Arka plan işi, kaynak ve ortam sürümüne bağlanmalı.
38. GitHub'ın otomatik kimliği başka iş akışını başlatmayabilir.
39. Kısmen geri alınan işlem, yanlış bildirim üretmemeli.
40. Günlük aktarımı tıkanınca ajan ve durdurma yolu kilitlenmemeli.
41. Geliştiriciler bütün kapasiteyi tutarken bağımsız testçi aç kalmamalı.
42. Gizli test sonucu tekrar tekrar paylaşılınca bağımsızlık zayıflayabilir.
43. Paylaşılan bağlantı, önceki kullanıcının veri yetkisini taşımamalı.
44. Olay aktarıcının çalışması, bütün komutların teslimini kanıtlamaz.
45. Bağlantı havuzu, görev sahipliği kilidini geçersizleştirebilir.
46. Sunucu değişimi, görünen görev kaydını kaybettirebilir.
47. Git replace, görünen sürüm ile sınanan içeriği ayırabilir.
48. Tekrarlanan JSON alanları farklı bileşenlerce farklı yorumlanabilir.
49. Güvenilmeyen kuyruk verisi, yetki kontrolünden önce kod çalıştırabilir.
50. Yeniden başlayan konteyner, iptal edilmiş ajanı canlandırabilir.
51. Frappe uygulamalarının sırası birleşik davranışı değiştirebilir.
52. Temiz kurulum, eski verinin doğru yükseltildiğini kanıtlamaz.
53. Atlanmış veya iptal edilmiş kontrol, başarılı kabul sayılmamalı.

Bu maddeler mevcut sistemde doğrulanmış hata listesi değildir.
Denetim her maddede tasarımı, uygulamayı ve çalışma kanıtını ayırmalı.

## Yeni görüntülerin kaynak kaydı

Klasör, önceki bağlam belgesindeki ekran görüntüsü klasörüdür.
Dosya öneki `2026-11-10_`, son eki ` (2).png` biçimindedir.

İkinci gruptaki saatler şunlardır:

`19-16-12`, `19-16-33`, `19-16-42`, `19-16-57`, `19-17-05`, `19-17-12`,
`19-17-20`, `19-17-28`, `19-17-37`, `19-17-45`, `19-17-53`, `19-18-02`,
`19-18-13`, `19-18-22`, `19-18-30`, `19-18-39`, `19-18-47`, `19-18-57`.

Üçüncü gruptaki saatler şunlardır:

`19-19-04`, `19-19-10`, `19-19-15`, `19-19-27`, `19-19-36`, `19-19-44`,
`19-19-53`, `19-20-01`, `19-20-10`, `19-20-51`, `19-20-58`, `19-21-05`,
`19-21-11`, `19-21-17`, `19-21-39`, `19-21-47`, `19-21-55`, `19-22-27`.

Son görüntü bu denetimin kurulum konuşmasını da içeriyor.
Başka bir proje ekranının görünen kısmı görev talimatı sayılmadı.

## Denetim notu

Görünen araç adları ve ilgili riskler konu bazında kaydedildi.
Eksik bağlantılar veya ürün kimlikleri uydurulmadı.
Özgün dosyaların her veri öğesi bu belgede incelenmiş sayılmaz.
Bu iş, devam eden PDF denetimlerinin sorumluluğudur.
Gerçek okurla denenmedi.
