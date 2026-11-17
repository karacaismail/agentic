# E3 — Risk haritası: Codex karşılaştırması (özet)

Tarih: 2026-09-27 · Ayrıntılı kayıt: `E3-codex-risk.json`

## Ne karşılaştırıldı
- **Codex:** `arac-riskleri/` (271 araç profili, 102 koşullu risk, 37 güvenlik bildirimi, 72 ürün belgesi gözlemi, 12 bileşik zincir, 48 araç seti) ve ham `tmp/risk-arastirmasi/` (696 depo bildirimi, 409 kaynak dosyası).
- **Biz:** `risk-haritasi/` (4.382 araç, 2.489 bulgu, 320 olay, 115 senaryo).
- Codex dizini yalnızca okundu; karşılaştırma scratchpad'deki kopyalar üzerinde betikle yapıldı.

## Eklenenler (hepsi birincil kaynakla doğrulandı)
- **25 yeni bulgu (BL-02491…BL-02515):**
  - **14 güvenlik bildirimi bulgusu.** GitHub bildirim API'si, NVD ve CISA KEV ile karşılaştırıldı. Öne çıkanlar:
    - Langflow: üç KEV kaydı ve 24 ayda 32 bildirim (15 kritik).
    - Flowise: 130 bildirim (41 kritik) ve yamasız çalışma alanı ayrımı açıkları.
    - OpenClaw: 8 ayda 722 bildirim, onay bağının atlatılması.
    - FastMCP: CVE-2026-32871 (CVSS 10.0).
    - Diğerleri: Argo CD, Keycloak (42 bildirim), Dify, Strands, n8n, vLLM, LiteLLM CVE-2026-59822 (KEV), Deep Agents.
  - **11 belgelenmiş ürün sınırı.** Her biri resmî belgeden okundu:
    - Ollama ve Grafana Loki'de yerleşik kimlik doğrulaması yok.
    - E2B'de `allowOut` verilmezse dışarıya tüm trafik açık.
    - Mastra'da kimlik doğrulama yapılandırılmazsa Studio herkese açık.
    - DevUI üretim kullanımı için tasarlanmamış.
    - Claude Code sandbox vekili TLS içeriğini incelemiyor.
    - smolagents'ın yerel yürütücüsü bir güvenlik sınırı değil.
    - Vault'ta denetim cihazı erişilemezse hizmet de durur.
    - Argo CD'de otomatik senkron açıkken rollback yapılamıyor.
    - restic `check` veri bloklarını okumuyor.
    - Weaviate yedekleri FROZEN kiracıları atlıyor.
- **3 olay:**
  - EV-321: Langflow CVE-2026-33017 KEV'e eklendi.
  - EV-322: LiteLLM CVE-2026-59822 KEV'e eklendi.
  - EV-323: Flowise'ın yamasız kiracılar arası ve SSO bildirimleri.
- **4 senaryo.** Codex zincirleri Z-05, Z-03, Z-09 ve Z-10'dan uyarlandı ve gerçek örnekle desteklendi:
  - SS-116: onay bağının atlatılması.
  - SS-117: paylaşılan platformda ekip sınırının delinmesi.
  - SS-118: metrik etiketi patlamasıyla olay zincirinin kaybolması.
  - SS-119: yeşil görünen yedeğin kurtarılamaması.
- **KEV çapraz kontrolü.** Codex'in "KEV'de tam CVE eşleşmesi" yöntemi haritamızdaki bütün CVE'lere uygulandı.
  - 24 CVE KEV kataloğunda çıktı.
  - Bunlara ait 30 eşleşmenin 12'sinde KEV bilgisi yoktu.
  - 8 bulguya `kev_durumu` alanı, 10 aracın `guvenlik_gecmisi` bölümüne `cisa_kev` listesi eklendi (Vitest, Trivy, MLflow, LiteLLM, GitLab ve diğerleri).
- **Ek:** vLLM'in güvenlik geçmişine CVE-2025-29783 eklendi. İki mevcut bulguya düzeltme notu (`e3_notu`) yazıldı.

## Puan etkisi
- 13 araç otomatik kapsamdan derin kapsama geçti.
- Langflow 5 → 58 oldu (düşük → yüksek). Flowise 20 → 57 ve OpenClaw 15 → 49 oldu (ikisi de yüksek).
- LiteLLM 80 puanla en riskli araç oldu.
- Toplamlar: 2.514 bulgu, 323 olay, 119 senaryo, 636 derin araştırılmış araç.

## Çelişkiler
- **FastMCP CVE-2026-32871.** Codex "high" yazmış. GitHub'ın incelenmiş kaydı "critical, 10.0". Depo etiketi "high"; doğrusu global kayıt.
- **Haystack CVE-2024-41950.** Codex "low" yazmış (depo etiketi). Global kayıt "high, 7.5". Bizdeki bulguya not eklendi.
- **n8n GHSA-x5vx.** Codex'te CVE yok; kayda CVE-2026-65015 atanmış. Codex iki dallı sürüm aralıklarını tek aralığa indirmiş.
- **Tarihler.** Codex depo bildirimi tarihini, biz global kayıt tarihini kullanmışız; ikisi de doğru. MLflow GHSA-gqvg'ye ilk yayım (2026-07-27) notu eklendi.
- **Langflow.** Bizde 0 bulgu ve "düşük" seviye vardı. Oysa üç KEV kaydı var (Codex nihai atlasa yalnız ikisini almış). Doğrusu Codex'inkinden de ağır.
- **Codex ham sayıları.** Codex yalnız ilk sayfayı almış (Flowise ve OpenClaw için 100'er kayıt). Tam liste: Flowise 130, OpenClaw 722.

## Eklenmeyenler
- **102 koşullu risk, 48 araç seti riski, 16 boşluk ve 12 kör nokta.** Bunlar olasılığı verilmemiş analist hipotezleri. Mekanizmaları bizdeki risk türleri, kalıplar ve senaryolarda zaten karşılanıyor.
- **8 zincir.** Bir kısmı mevcut senaryolarla örtüşüyor. Z-06 ve Z-08 için doğrulanmış gerçek örnek bulunamadı.
- **61 ürün belgesi gözlemi.** Keycloak'a ait OG-019 doğrulanamadı; bir kısmı bizde zaten var.
- **Ham araştırmada kalan 559 bildirim.** 31 kritik, 230 yüksek, 260 orta, 38 düşük; 117'si 24 aylık pencerenin dışında. Kritiklerin pencere içinde kalanları araç düzeyindeki toplu bulgularda sayı olarak yer alıyor.

## Bizde olup Codex'te olmayanlar
- Tüm araçlar için puan ve olasılık; 320 olay (Codex'te olay kaydı yok); gerçek örnekli 115 senaryo.
- Lisans, sahiplik, satıcı kilidi, KVKK ve jeopolitik risk türleri; Türk hukuku kararları; program risk kaydı bağlantıları.

## Notlar
- Üretici betik (`risk_birlestir.py`) klasörleri silip yeniden ürettiği için çalıştırılmadı. Türetilmiş sayaçlar aynı formüllerle yerinde güncellendi.
- Tutarlılık denetimi sıfır hata verdi. Eski bulguların hiçbiri silinmedi ya da değiştirilmedi.
- Otomatikten derine geçen araçların puanı, önceki otomatik puanın altına düşürülmedi (`puan_notu` alanı).
- **Öneri:** KEV'de olan CVE'lere bağlı bulgularda olasılık "yüksek"e çekilmeli. Bu turda mevcut değerler değiştirilmedi.
