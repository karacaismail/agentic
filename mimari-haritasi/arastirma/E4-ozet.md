# E4 — Codex mimari karşılaştırması: özet

Tarih: 2026-09-27. Kapsam: Codex `agentic-sistem/` (raporlar 01–05, data/02–13, şemalar, yönergeler, roller, skill'ler, MCP, deneyler, `uygulama/`) ile bizim `mimari-haritasi/` ve (salt okunur) `agentic-fabrika/`. Codex testleri çalıştırılmadı; kanıt dosyaları çapraz denetlendi. Ayrıntı: `E4-codex-mimari.json`.

## Temel fark

Codex'in paketi büyük ölçüde **sözleşme ve tasarım**: 26 kontrol kümesi, 113 ihtiyaç eşlemesi (hepsi "mimaride ele alındı", hiçbiri "uygulandı" değil), girdi/çıktı sözleşmeleri, gözetim ve evrilebilirlik sözleşmeleri. Çalışan parçası dar bir Temporal pilotu: model, GitHub ve dağıtım faaliyetleri fikstür, adaptörler iş akışına bağlı değil. Güncel üst kararında platform seçilmemiş.

Bizde ise **çalışan bir akış** var: gerçek Temporal, Postgres, Docker sandbox ve git ile uçtan uca senaryo (Plane, GitHub ve model sahte). RED/GREEN kapıları, birleştirme kuyruğu, Rejected'da geri alma, yazar ve committer'ı koruyan hızlı ileri birleştirme, atama ve hatırlatma, OOM profil merdiveni ve çıkış vekili Codex'te yok.

## Codex'ten eklenenler

- **Bileşenler (M-B15–M-B21):** kabul ve dış etki defteri, iş akışı dışı gözlemci ve toparlanma dağıtıcısı, kaynak ölçüm sözleşmesi, yetenek sicili yaşam döngüsü ve kiralama, 9 adaptör yuvası, güvenilir ajan aracısı (sabit argv ve stdin), yayın politikası kapısı.
- **Kararlar (M-K13–M-K25):**
  - her durum alanının tek yazıcısı olması
  - niyet → makbuz → uzlaştırma zinciri (`unknown_effect`)
  - nesil ve girdi özeti
  - tipli 6 terminal sonuç
  - "canlılık ilerleme değildir" ve "exit 137 OOM değildir"
  - iş akışı dışı gözlemci
  - evrilebilirlik
  - motor kararının geri dönüş ölçütleri
  - çağrı öncesi rezervasyon
  - görev verisinin argv'ye ya da kabuğa girmemesi
  - dürüst durum kaydı
  - depo ve ortam eşlemesi
  - Plane webhook kuralı
- **Doğrulama:**
  - 28 önerilen kabul deneyi (M-D01–M-D28, hepsi çalıştırılmadı)
  - Codex'in üç kanıt grubunun ne gösterip ne göstermediği
  - test envanteri düzeltmesi: tanımlı test sayısı 61, eski kayıtta 41
- **`codex-eklemeleri.json` (yeni):** otoriteler, C01–C26 → bileşen eşlemesi, bileşen düzeyinde durum ayrımı, sözleşme özetleri, yaşam döngüsü, gözetim, havuz, yuvalar, evrilebilirlik, olgunluk eşlemesi, Codex sınırları ve bizdeki karşılıkları, doğrulanmış olgular.

## Deneyler ne gösterdi?

- **Motor takılma sondası:** Temporal'da iş akışı kodunda düz bir Python istisnası Workflow Task hatasına dönüşüyor ve iş RUNNING kalıyor. Aynı süreçteki gözlemci bunu 0,4 sn'de görüp işi sonlandırdı. Geçmiş dosyaları ve Temporal belgesi bunu doğruluyor. Gerçek ajan takılması ya da üretim yalıtımı değil.
- **Politika deneyi:** 30 sentetik test geçti ve sha256 özetleri dosyalarla eşleşti. Motor, model ya da gerçek OOM yok.
- **Pilot:** 12 birim test ve gerçek Temporal'da 9 senaryo. "Etki sonrası çökmede çift yazım yok" senaryosu geçmiş dosyasında görülüyor (enjekte çökme, 2. deneme). "Belirsiz etki" senaryosunun ön koşulu elle kurulmuş.

## Çelişkiler ve hangisi doğru

1. **Exit 137:** Codex doğru. Bizim `siniflandir()` 137'yi tek başına bellek yetmezliği sayıyor. cgroup belgesine göre kesin işaret `oom_kill` sayacı.
2. **Plane webhook sürümü:** İmza ikisinde aynı ve doğru: ham gövdenin HMAC-SHA256'sı, `X-Plane-Signature` başlığında. Plane'in açık kaynak kodu (preview dalı) v1 gövdesi gönderiyor; v2 alanları depoda yok, yalnız belgede tanımlı. Codex'in yalnız v2 kabul eden adaptörü topluluk sürümünde her olayı reddeder. Biz doğruyuz. Ek bulgu: Plane 5 ağ hatasından sonra webhook'u devre dışı bırakıyor, 5xx yanıtını yeniden denemiyor.
3. **n8n:** Çekirdek için biz doğruyuz. CVE-2026-21858 kritik (CVSS 10) ve doğrulandı; Codex'in önerdiği karşılaştırmalı arıza paketi hiç koşulmadı.
4. **Motor seçimi:** İki tarafta da canlı karşılaştırma yok. Bizim Temporal kararımız çalışan koda dayandığı için korunur; Codex'in geri dönüş ölçütleri eklendi.
5. **Error sonrası devam:** Kısmen ikisi de doğru. Girdi değiştiyse yeni nesil açılması ve eski kanıtın geçersiz sayılması kuralı eklendi.
6. **İnsan testinde sürüm kimliği:** İlke olarak Codex doğru; bizim S2 görev başına önizleme planı bunu çözüyor.
7. **Birleştirme:** Biz daha eksiksiziz. Squash'ta committer "GitHub" olur; Codex bu sorunu açık bırakıyor.
8. **Kapasite ve görev içi paralellik:** İki taraf da ölçmedi; ölçüm deneyleri eklendi.
9. **Alpha depo adı:** Codex'in "tam owner/repo gerekir" uyarısı doğru (depo adı sahip başına tekil). Bizim yapılandırmamız zaten tam eşleme kullanıyor.

## Güven sınırı karşılaştırması

- **Codex:** görev verisi yalnız stdin JSON'dan gider; sabit argv, `shell=False`, çalıştırılabilir ve çağrı manifesti özeti. Ancak aracı yalıtım sağlamıyor ve iş akışına bağlı değil.
- **Biz:** `claude -p "$(cat istem)"` kullanıyoruz. Görev metni kabuk kodu olmaz (komut ikamesi çift tırnakta yeniden yorumlanmaz) ve konteyner yalıtımı var. Ancak tek argv sınırı (~128 KiB, E2BIG) ve özetsiz ikili riski kalıyor.

## Eklenmeyenler

144 ekip, platform matrisi ve HRMS (başka çalışmaların kapsamı), 21 skill şablonu (belirtime uymuyor, etkin değil), 12 ayrı rol ajanı, görev içi paralel DAG ve n8n'i tek motor seçmek.

## agentic-fabrika için (yalnız not)

- 137 koşulunu kaldırmak
- istemi stdin'den vermek
- etki makbuz defteri kurmak
- nesil ve girdi özeti eklemek
- WFT hata alarmı ve dış gözlemci
- faaliyet yeniden deneme sınırları
- Plane aktör yetkisi ve webhook devre dışı alarmı
- yeni commit kimlik denetimi
- stdout bayt sınırı
