# Senaryo Atlası

Karar arayüzü: **Plane → agentic-tdd-development → GitHub CI/CD → alpha → insan kabulü**.

Başlangıç: `senaryo-atlasi.html` dosyasını tarayıcıda aç. Tek dosyadır; JS, CSS, grafikler, senaryolar ve seçilmiş kaynaklar içindedir. CDN, model anahtarı veya çalışan fabrika gerekmez. Araştırma bağlantılarına tıklamak dışında ağ isteği üretmez.

## Kullanım

1. **Bulgudan karara:** 24 kaynaklı soruda gözlemi, yorumunu, kanıt sınırını, seçenek/bedelleri ve eksik ölçümü oku. Hiçbir seçenek senin adına seçilmez. Kendi notunu ekle; JSON ile taşı.
2. **Kanıt defteri ve Kaynaklar:** 82 özgün kaydı kanıt türüyle incele; 94 gömülü belgede başlık ve içerik ara. Markdown belgeler okuma görünümündedir.
3. **Senaryo tasarımcısı:** hazır senaryo, teknoloji rolü, insan rolü, ECA eşikleri ve kümeleri seç. Faz etiketi mevcut seçimlerini sıfırlamaz.
4. **Olay laboratuvarı:** OOM, takılma, çift görev, belirsiz etki, eski CI, insan reddi, skill ihtiyacı, bütçe, iptal veya CI olayı dene. Bu sadece deterministik tasarım simülasyonudur.
5. **Diyagramlar:** Mermaid çizimleri, yapışkan notlar ve SVG/Mermaid kaynaklarını al. D2 yalnız metin olarak dışa aktarılır; burada D2 çizicisi/derleyicisi yoktur.
6. **Rapor ve PDF:** çizimler ve yazı tipleri tamamlanınca yazdır → PDF olarak kaydet. Uzun akışlar ayrı sayfalarda okunabilir parçalara ayrılır.
7. **Karar paketini indir:** seçimler, kişisel bulgu notları, 24 karar sorusu, açık/kapalı ECA, kaynak manifesti, belirsizlikler, Mermaid/D2, 22 belge taslağı ve bu oturumda aynı kararla yapılan simülasyonlar JSON içinde bulunur. Aynı JSON yeniden yüklenebilir; karar durumu ve varsa bulgu notları geri yüklenir, dosyadaki talimatlar/kod çalıştırılmaz.

Seçimler bu tarayıcının localStorage alanında tutulur. Dosyanın yeri/tarayıcı değişirse depolama değişebilir; taşımadan önce JSON indir. Simülasyon geçmişi bu açık oturum içindir; kalıcı arşiv için paket indir. Kaynakları herkese açık yerde yayımlamadan önce yerel içeriklerini değerlendir; mevcut çıktı yerel araştırma içindir.

## Ne içerir?

- 10 örnek senaryo; Temporal, Kestra, n8n giriş, OpenHands, Codex, Hermes/OpenClaw, DBOS/goose, Jev/Laya, HRMS ve çok ekip örnekleri.
- 79 düzenlenebilir tasarım ECA kuralı; 10 olay ailesi için simülatör. Tüm ECA metinleri yürütülebilir motor kodu değildir.
- Tipli karar katmanında 12 birincil kaynak incelenmiş aday + 7 kimliği henüz doğrulanmamış isim; ayrıca mevcut PydanticAI/DSPy seçenekleri.
- 18 yerel geçmiş, 36 dünya vakası, 28 mimari inceleme = 82 özgün kayıt. **82 bağımsız olay iddiası yoktur.**
- Seçilmiş raporlar, kaynak kayıtları ve büyük haritaların indeksleri gömülüdür; tüm araştırma arşivi/PDF’leri kopyalanmamıştır.
- 12 rol kartı, skill havuzu, MCP erişim ilkeleri, tak-çıkar sözleşmeleri; CLAUDE.md oluşturulmaz.
- ECharts istatistikleri; envanter sayımıdır, araçların gerçek hata/başarı oranı değildir.

Seçili önlem → uygulanmış önlem → doğrulanmış sonuç farklıdır. Bu projede **fabrika kurulmadı ve gerçek adaptör uygunluğu test edilmedi**. Eski katalog hükümleri tarihî kaynak olarak korunur; güncel ürün tavsiyesi değildir. Yeni araç değerlendirmeleri birincil kaynak iddialarıdır; bağımsız hız/kalibrasyon benchmarkı yapılmadı.

## JSON dosya haritası

`data/map.json` kümelenmiş senaryo, ECA, karar adayı, ajan/skill/MCP, belge, sözleşme ve özgün kanıt JSON’larının tek indeksidir. `npm run export:data` bu snapshotları günceller. Başlangıçtaki araştırma arşivleri değişmez.

## Derin inceleme

`docs/KANIT-VE-KARAR-INCELEMESI.md` 24 karar sorusunu ve bu turdaki kaynak kontrollerini toplar; HTML kaynak kütüphanesinde de okunur. `data/analysis/` altında karar soruları, 82 kayıt için tür fihristi ve özgün dosya/dış kaynak tekrar okumaları bulunur. 5 özgün yerel aralık ve 3 dış kaynak tekrar okundu; canlı sistem deneyi yapılmadı. Senaryo varsayılanları kullanıcı onayı sayılmaz.

## Teknik seçim

React + Mantine / TypeScript / SCSS / ECharts SVG / Mermaid / Vite singlefile. Mevcut kullanılabilir arayüzden izole kopya alındı; kontrol, kanıt, senaryo ve çıktı davranışları düzeltildi. Mantine erişilebilir form kontrolleri ve bileşenleri sağlar. D2 alternatif kaynak ihracıdır; tarayıcı çizim altyapısı olarak eklenmedi.

## Geliştirme

```sh
npm ci --ignore-scripts --no-audit --no-fund
npm run denetle
npm run build
```

Build, kardeş araştırma klasörlerini ve `otomasyon coding 2` içindeki belirtilmiş veri dosyalarını **yalnız okur**, bu uygulamanın üretilen JSON’larına yazar. Taşınabilir geliştirme için `npm run build:offline` mevcut gömülü snapshotları kullanır. `npm run dev:offline -- --host 127.0.0.1` yalnız UI geliştirme sunucusudur.

Kaynak yenileme: `scripts/veri-uret.mjs`, `scripts/kanit-uret.py`. Bunlar fabrika betikleri değildir. Kütüphaneler package-lock ile sabittir. Git commit veya dağıtım yapılmadı.

## Sınırlar ve doğrulama

- `audit/contracts-results.json`: durum şeması, parametreler, öncelik, olumsuz olaylar ve ihracat testleri.
- `audit/ui-results.json`: gerçek Chrome ile çevrimdışı/masaüstü/mobil, senaryolar, import/export, SVG/PDF hazırlığı.
- `audit/evidence-ux-results.json`: bulgu kaynak bütünlüğü, seçim yapılmamış başlangıç, not taşıma, kanıt türleri, Markdown, mobil ve çevrimdışı kullanım.
- `audit/protected-check.json`: başlangıç SHA-256 kaydıyla korunan kaynak dosyalarının karşılaştırması.
- `output/pdf/ornek-karar-raporu.pdf`: varsayılan senaryonun örnek PDF’i. Senin daha sonraki seçimlerini içermez.

Bu çalışma `coding/fabrika-karar-merkezi`, `coding/agentic-fabrika` ve **`coding 2` içine yazmaz**. Hash karşılaştırmasında `coding 2` ve fabrika kodu değişmedi. Ayrı `fabrika-karar-merkezi` arayüzünde başlangıç kopyasına göre başka değişiklikler görüldü; bunlar korunur, bu uygulama tarafından geri alınmaz. Ayrıntı `audit/protected-check.json`. Bu uygulamanın tek yazma alanı `coding/senaryo-atlasi`; araştırma notları `coding/research_notes/Senaryo ve karar arayüzü`, raporu `coding/reports/Senaryo ve karar arayüzü.md` altında.
