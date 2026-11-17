# Konuşma özeti: ne soruldu, ne üretildi, ne eksik, asıl sorun ne

Tarih: 27.09.2026. Kapsam: `/Users/w6x/Documents/otomasyon coding` üzerinde tek Claude oturumu. Konuşma bağlam dolduğu için birkaç kez özetlendi. İlk bölümler o özetlerden, sonrakiler doğrudan konuşmadan alındı. Dosyaların yeri: `00-harita.json`.

---

## 1. Kısa özet

Konuşma iki ürünle başladı: markasız bir ihtiyaç haritası ve ona bağlı araç ve risk haritaları. Ardından iş Kestra pilotunun yerine geçecek bir yazılım fabrikasına döndü (`agentic-fabrika`). Fabrika gerçek bileşenlerle yazıldı, ama yalnız sahte Plane/GitHub/model ile test edildi.

Sonra araştırma dönemi geldi:

- hazır projeler, vakalar, ön-ölüm (B1–B3)
- hazır sistemler, tak-çıkar, büyük yapım vakaları, HRMS/oracle, 144 ekip ölçeği (C1–C6)
- dünyadaki orkestratör ve ajan platformu hataları (D1–D2)

En son, aynı soruların sorulduğu Codex'in çalışma dizini karşılaştırıldı ve eksiklerimiz tamamlandı (E1–E6).

Araştırmalar sırasında üç kez kapsam dışına çıktım: istenmeden kod değiştirdim, istenmeden prototip denetledim, istenmeden dosya ekledim. Bir kez de İngilizce yazdım. Bunlar kullanıcıyı haklı olarak kızdırdı ve genel kurala dönüştü (bkz. `SOHBETTE-KALAN-BULGULAR.md` §1).

---

## 2. Sorduğunuz sorular (kronolojik)

| # | Soru / istek (özet) | Karşılığında üretilen |
|---|---|---|
| S1 | Ana amaç altında kümelenmiş, markasız ihtiyaç haritası JSON'u; bilinmeyen-bilinmeyen, gap ve çember analizi | `ihtiyac-haritasi/` |
| S2 | HTML görselleştirme | `ihtiyac-haritasi/gorsel/` + yayınlanan sayfa |
| S3 | Araç haritası: 12+ araştırma döngüsü, küme JSON'ları + tek harita JSON'u | `arac-haritasi/` |
| S4 | Risk haritası | `risk-haritasi/` |
| S5 | "Bu proje sence ne için?" | Sohbette cevap. Kullanıcı düzeltti (S6). |
| S6 | Düzeltilmiş amaç: "insanların ve yapay zekâ ajanlarının birlikte, birden fazla ekip üzerinden güvenilir yazılım üretebildiği bir çalışma sistemi kurmak… eksik varsa tamamla, ara bul ekle" | Haritalar genişletildi ve doğrulandı |
| S7 | Pano PDF'leri: Plane'de In Progress → ajanlar → GitHub alpha → alpha.* → insan testi; 12+ scrum/SAFe; Hetzner 128 GB. İstenenler: mermaid/echarts, hangi skills/agents/MCP/kaizen, havuz/market, olgunluk planı, orkestrasyon, kapasite, "artık bana şu sistemi kur" | `agentic-fabrika/` (kod, belgeler, şablonlar, e2e), `mimari-haritasi/` (A0–A3), yayınlanan "Agentic Fabrika" sayfası |
| S8 | "Emin misin? Tekrar incele": Kestra'da ajan duruyordu, 1 GB yetmedi, alt ajan/worktree, n8n mı, küme mi | Fabrikaya çözücü, kaynak profili, hatırlatma/SAFe yükseltmesi eklendi; MIMARI §2a |
| S9 | Hazır projeler ve vakalar var mı? Oracle, 1 GB gibi sorunlar; "problemleri öngörelim" | B1, B2, B3. **İstenmeden** fabrika kodu B3 bulgularına göre değiştirildi. |
| S10 | "Ben sadece araştırma istedim, otomasyon mu kuruyorsun?" | Kod değişikliği durduruldu. Tut/geri al kararı sorulamadı, açık. |
| S11 | Asıl kastedilen "hazır proje": {görev girdisi → ajan süreci → GitHub → uzak sunucu}, Plane → {OpenHands 1…12}, trunk alpha, insan incelemesi → issue → yeni görev. Araçlar örnek. OpenHands/Symphony yeter mi? 12 SAFe × 12 ekip. Hedef: HRMS'i ERP modülü olarak DoD'ye kadar bitirmek. "Yeniden araştır." | C1, C2, C4, C5, C6 (+ istenmeyen C0 sentezi) |
| S12 | "Tak-çıkar yalnız model/API değişimi değil, sistem adapte olabilmeli" (n8n benzetmesine takılma uyarısı) | C3 |
| S13 | "Sadece güçlü bir araştırma yapacaksın" | Kod ve kurulum yapılmadığı teyit edildi |
| S14 | CronHR prototipinin denetlenmesine itiraz ("sanane") | Prototip denetimi sentezden çıkarıldı |
| S15 | "Projemi kirletme, token'ımı harcama; genel kural" | Hafızaya kural yazıldı |
| S16 | Kestra/OpenHands/Temporal vb. kullanan dünyadaki ekiplerin hataları (+ 15 araç listesi) | D1, D2 |
| S17 | Araştırma ve günlerin çalışması `otomasyon coding` altına alınsın; yan sohbet "D1/D2 yarım" dedi | D1/D2'nin tam olduğu doğrulandı; `calisma-arsivi/` |
| S18 | "İngilizce konuşma" | Hafızaya kural yazıldı |
| S19 | Codex'in (`otomasyon coding 2`) bulgularından alınacakları al, eksiklerimizi tamamla, belgelere ekle; Codex dizinini bozma | E1–E6 ve haritalara eklemeler |
| S20 | "Eksikler var, daha derin analiz et" | Kaçırılanlar bulundu: uygulama kanıtları, 52 deney, PDF gereksinimleri, ham araştırma. Kapsam genişletildi. |
| S21 | Bu özet, harita, sohbette kalanlar, asıl sorun, devir-teslim sözleşmesi | `devir-teslim/` |
| S22 | (Sonraki oturum) "Bu HTML'i neyle kuralım?": ECharts istatistikleri, Mermaid/D2 diyagramları, teknoloji kümeli örnek senaryolar, ECA kurallarıyla seçilebilir ve değiştirilebilir senaryolar, PDF, yapışkan notlar, skill/MCP/ajan/.md rehberi, merkezi gezinme. Codex dizini salt okunur analiz edildi. | `fabrika-karar-merkezi/` |
| S23 | “UX estetiğini geliştir; dökümanları daha derin analiz et; kesin bulgular ve somut ifadeler; kararları ben vereceğim” + “bitince localhost çalıştır” | 3.434 kaynaklı bulgu tabanı, nötr karar dili, karşılaştırma tablosu, yenilenen arayüz, localhost |
| S24 | “earendil-works/pi var mı? projede, ekle.” + “sonra bu projeyi GitHub Pages'te agenticlaude repo adıyla yayınla.” | Pi araç ve risk haritalarına (AR-4405, D16, 10 bulgu) ve karar merkezine eklendi; https://karacaismail.github.io/agenticlaude/ |
| S25 | “Sonra UX estetiğini geliştir ve GitHub Pages'i güncelle.” | İkinci arayüz turu (senaryo kartları, karar dizini, gruplu sorunlar, lejant, telefon düzeltmeleri); yayın güncellendi |
| S26 | “Postman, Hoppscotch gibi araçlardan başka neler var? Hangi süreçlere eklenmeli? Mevcut mu? Ekle.” | 19 yeni API aracı (D17), 18 bulgu, iki yeni karar; yayın güncellendi |

---

## 3. Aslında ne istiyorsunuz? (sözlerinizden çıkarım)

1. **Çalışan ve güvenilir bir çalışma sistemi.** İnsanlar ve ajanlar birden fazla ekipte birlikte güvenilir yazılım üretmeli. Ölçüt somut: HRMS'i bir ERP modülü olarak DoD'ye kadar bitirebilmek. Bu, testler %90'da takılmadan, gap ve bilinmeyen-bilinmeyen analiziyle, kabul kriterleri karşılanarak olmalı.
2. **Sonuç.** "Aylardır sonuç alamıyorum." Kanıtlanmış bir uçtan uca çalışma istiyorsunuz; iddia değil.
3. **Uyarlanabilirlik.** Araçlar hızla değişiyor. Sistem, parçaları (orkestratör, ajan çalışma zamanı, görev kaynağı…) değişince çökmemeli.
4. **Doğrulanmış, derin araştırma.** Yeni kaynak getirmeli; iddiayı kaynakla göstermeli, uydurmamalı.
5. **Dediğinizin yapılması.** Fazlasının değil. Türkçe; token'lar boşa gitmemeli; projeye istenmemiş dosya konmamalı.
6. **Yönetebileceğiniz bir sistem.** "Ben developer değilim, vibecoder'ım" dediniz. Kararların size açık seçeneklerle getirilmesi gerekiyor; teknik ayrıntıya gömülmemesi gerekiyor.

---

## 4. Neyi veremedim ya da veremiyorum?

- **Gerçekten çalışan bir fabrika yok.**
  - `agentic-fabrika` hiç gerçek Plane, GitHub, model ve alpha sunucusuyla çalıştırılmadı.
  - Testler ve uçtan uca senaryo sahte dış servislerle geçiyor.
  - Hetzner'e kurulum yapılmadı. Tek bir gerçek görev bile baştan sona geçmedi.
- **Ölçüm yok.** Şunlar ölçülmedi: ajan-saat maliyeti (C6'da 5–9 kat belirsiz), kabul oranı, birleştirme kuyruğu gecikmesi, inceleme süresi.
- **HRMS oracle'ı yok.** Uzman imzalı altın bordro/SGK test setleri üretilmedi. Bu işi yapay zekâ tek başına yapamaz; mali müşavir ve İK hukukçusu gerekir (C5).
- **Kabul deneyleri çalıştırılmadı.**
  - `mimari-haritasi/dogrulama.json`'da 28 deney var.
  - `E5`'te Codex'ten gelen 52 deney var.
  - Hiçbiri çalıştırılmadı.
- **Hazır bir çözüm devredemedim, çünkü yok.** 32 adayın hiçbiri döngünün tamamını yapmıyor (C1).
- **Tak-çıkar yalnız tasarım olarak var.** Tasarım hazır (C3 dikiş haritası). Kodda "her araç bir sözleşmenin arkasında + uyumluluk testi" biçiminde uygulanmadı.
- **Tek bir doğruluk kaynağı yok.**
  - Codex'in bulguları bizim dosyalara eklendi.
  - Ama iki ayrı çalışma dizini ve iki ayrı "gerçek" hâlâ yan yana duruyor. Codex şu an bizim bulgularımızla kendi tarafını güncelliyor.
- **Yayınlanan iki sayfa eski** (00-harita.json → yayinlanan_sayfalar).
- **Bekleyen kararlar:**
  - S9'daki istenmemiş kod değişiklikleri tutulsun mu, geri alınsın mı?
  - `C0-sentez.md` silinsin mi?
- **Süreç hataları:** kapsam dışı işler (S10, S14, S15) ve dil hatası (S18).

---

## 5. İstemediğiniz ama ihtiyaç duyduğunuz şeyler

1. **Tek doğruluk kaynağı ve karar günlüğü.** Claude, Codex ve yan sohbetler aynı soruya paralel ve farklı sonuçlar üretiyor. Hangi dosyanın geçerli olduğu, hangi kararın alındığı tek yerde tutulmalı.
2. **Sürüm kontrolü ve yedek.** `otomasyon coding` bir git deposu değil. Yanlış bir betik (bkz. `SOHBETTE-KALAN-BULGULAR.md` §5) haritaları geri dönüşsüz ezebilir. Geçici klasör yeniden başlatmada silinir.
3. **Küçük ama gerçek bir pilot planı.** Tek ekip, tek proje, 10 düşük riskli görev. Gerçek Plane, GitHub, model ve alpha kullanılmalı. Geçiş kapıları ölçülmeli (C6 §6'daki kademeler).
4. **Alan uzmanı zamanı.** HRMS için mali müşavir ve İK hukukçusu altın veri setini imzalamadan "bitti" denemez.
5. **İnsan kapasitesi planı.** Asıl darboğaz inceleme ve kabul yapacak insanlar. 144 ekip ölçeğinde bu 43–144 kişi eder (C6).
6. **Hesap ve ayar işleri.** Bunlar yalnız sizin yapabileceğiniz işler:
   - API katmanı: Start kademesinin 500 $/ay tavanı pilotta bile yetmez.
   - GitHub organizasyonu, App ve ruleset.
   - Plane durumları, `ajan` etiketi ve webhook izinli IP'leri.
   - alpha DNS'i ve sunucusu.
7. **İnsanın rolüne dair karar.** Pano notunda "insan yalnız girdi ve çıktıyı görür" yazıyor; proje amacında insan eş üretici. Bu çelişki (C-040 / D-024) kararınızı bekliyor.

---

## 6. Çözmemiz gereken asıl sorun

**Asıl sorun araç seçmek değil.** Kestra yerine Temporal, OpenHands mı Symphony mi gibi seçimler kolay değişen katmanlar (C3).

Çözülmesi gereken üç sorun var. Aynı zincirin halkaları.

1. **"Bitti"nin ajanların kandıramayacağı bir tanımı yok (oracle).**
   - Büyük otonom yapımların başarılı olduğu her vakada hazır bir dış doğruluk kaynağı vardı: GCC, test262, bir referans uygulama (C4).
   - HRMS, özellikle Türk bordrosu, SGK ve beyanname için böyle bir kaynak yok. Önce inşa edilmesi gerekiyor.
   - Kaynak yokken ajanlar yeşil test üretir ama iş yanlış olur. Testi geçen PR'ların yaklaşık yarısı birleştirilemez (B2, C4).
2. **İnsan inceleme ve kabul kapasitesi, ve insana düşen işin sahipsiz kalması.**
   - Önceki pilotta bir görev, bir insan eylemini beklerken 7 gün sonra zaman aşımına düştü (E6).
   - Ölçeği ajan sayısı değil, inceleme ve birleştirme kapasitesi belirliyor (C6).
3. **Durumun ve sözleşmelerin tek sahibi yok.**
   - Pilottaki "iki beyin" (Kestra bir tabloyu yoklarken işi elle yazılmış Python yapıyordu) bunun örneği.
   - Dış etkilerin (push, PR, yorum, deploy) belirsiz sonuçları da aynı sorun. Codex'in pilotu bunu "etki defteri ve unknown_effect" ile ele aldı (E4). Dünyadaki hataların büyük sınıfı da bu (D1).

Üst düzeyde tek cümle: **aylardır sonuç alınamamasının nedeni, işin gerçek ortamda tek bir görevle baştan sona kanıtlanmadan genişletilmesi.** Bir tarafta paralel araçlar ve paralel belgeler, öbür tarafta kanıtsız "hazır" iddiaları var.

**İlk çözülecek şey:** tek bir gerçek görevin döngünün tamamından geçmesi. Döngü şu: form → Plane → ajan → PR/CI → alpha → insan kabulü. Görev gerçek entegrasyonlarla, insanın sahip olduğu bir kabul oracle'ıyla ve ölçülerek geçmeli. Ölçek bundan sonra, ölçülen kapılarla açılır.

---

## 7. Açık kararlar (kullanıcı)

1. S9'da istenmeden yapılan `agentic-fabrika` değişiklikleri tutulsun mu, geri alınsın mı?
2. `mimari-haritasi/arastirma/C0-sentez.md` kalsın mı?
3. Birleştirme yöntemi (AK-42). Seçenekler:
   - Hızlı ileri gönderim: yazar ve committer korunur, fabrika App'ine ruleset bypass gerekir.
   - GitHub squash: committer "GitHub" olur ve kişisel git politikasına aykırıdır.
4. İnsanın rolü: yalnız girdi/çıktı mı, eş üretici mi? (C-040 / D-024)
5. HRMS için çerçeve seçimi: Frappe üzerine Türkiye uygulaması, Odoo EE, ya da sıfırdan (C5).
6. KEV listesindeki 12 bulguda olasılık "yüksek"e çekilsin mi? (E3)
7. Yayınlanan iki sayfa güncellensin mi?

---

## 8. Ek: sonraki oturum (27.09.2026)

- Kullanıcı `agentic-fabrika` için: "fabrika kod değişiklikleri senin işin değil, buranın konusu değil; orası kalsın, bu başka proje. Biz yeni fabrika kuracağız." §7'deki 1. karar böylece kapandı: değişiklikler olduğu gibi kalır, o klasöre dokunulmaz.
- Yeni fabrikanın tasarım merkezi kuruldu: `fabrika-karar-merkezi/fabrika-karar-merkezi.html` (ayrıntı `00-harita.json`).
- "Laya" adlı araç kaynaklarda ve 127 araçlık katalogda bulunamadı; Jev senaryosunda uygulama kümesinin teknolojisi seçilebilir bırakıldı.
- S23 (27.09.2026): Kullanıcı karar vermek istediğini, benden karar değil bulgu beklediğini söyledi. Karar merkezine araştırma dosyalarından 3.434 kaynaklı bulgu eklendi; öneri, sentez ve hüküm metinleri ayıklandı (ayrıntı `00-harita.json` → `fabrika-karar-merkezi/` → `S23_eki`). Kararlar nötr dille yeniden yazıldı. Yerel sunucu: `http://127.0.0.1:8765/fabrika-karar-merkezi/fabrika-karar-merkezi.html`.
- S24 (28.09.2026): Pi projede yoktu (Earendil'den yalnız Absurd ve Gondolin vardı). Birincil kaynaklarla araştırılıp araç haritasına AR-4405 (D16), risk haritasına 10 bulguyla eklendi; 'Kodlama çalıştırıcısı' kararında seçenek oldu. Karar merkezi https://karacaismail.github.io/agenticlaude/ adresinde yayında (ayrıntı `00-harita.json` → `S24_eki`).
- S25 (28.09.2026): İkinci arayüz turu yapıldı ve https://karacaismail.github.io/agenticlaude/ güncellendi (ayrıntı `00-harita.json` → `S25_eki`).
- S26 (28.09.2026): API istemcisi ve API testi araçları tarandı; eksik 19 araç haritalara eklendi, Hoppscotch, Bruno ve Hurl derin araştırıldı. Karar merkezinde 'API testleri' ve 'API istemcisi (insan)' kararları açıldı (ayrıntı `00-harita.json` → `S26_eki`).
