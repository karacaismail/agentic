# E2 — Araç haritası: Codex karşılaştırması (özet)

Tarih: 2026-09-27 · Ayrıntılı kayıt: `E2-codex-arac.json`

## Ne yapıldı

- Codex'in `arac-katalogu/` klasöründeki 271 araç/bileşen kaydı, bizim `arac-haritasi/` klasöründeki 4.382 araçla betikle eşlendi. Eşleme sırası: kanonik ad → GitHub deposu (owner/name) → resmî alan adı. Ad ya da alan adı çakışan 15 kayıt elle doğrulandı.
- Codex'in `tmp/arac-arastirmasi/` ham araştırmasından (~14 MB) nihai kataloğa girmemiş 103 anahtar (depo veya alan adı) çıkarıldı. Bunlar da bizim haritayla eşlendi.
- Yalnız bizde olmayanlar doğrulandı. Doğrulama en fazla 25 kalemlik partilerle yapıldı: `gh api` ile lisans, arşiv durumu, son itme tarihi, yıldız sayısı ve yönlendirme bakıldı; ayrıca resmî site ve belgeler kontrol edildi.
- Harita bizim şemayla yeniden üretildi. Önce değişiklik yapmadan yeniden üretim denendi; sonuç mevcut 127 dosyayla anlamsal olarak birebir aynıydı. Ardından D15 eklemeleri uygulandı. Son durumdan yapılan yeniden üretimde de 128 dosyada fark çıkmadı.

## Sayılar

- Codex kataloğundaki 271 kaydın 254'ü bizde vardı, 17'si yoktu. 17'sinin hepsi doğrulanıp eklendi.
- Ham araştırmadan 103 katalog dışı anahtar çıktı. 34'ü bizde zaten vardı, 5'i eklendi. Kalan 64 kaydın dağılımı:
  - 29'u rozet, görsel, yerel adres ya da yan hizmet,
  - 19'u belge, blog, standart veya örnek sayfası,
  - 16'sı değerlendirilip elendi.
- Araç sayısı 4.382'den 4.404'e, döngü sayısı 24'ten 25'e çıktı. Yeni döngü dosyası `donguler/D15.json`. Araçsız ihtiyaç sayısı (2) ve ihtiyaç başına medyan araç sayısı (27) değişmedi.

## Eklenen araçlar (22)

**Codex kataloğundan (17):**
- Dovetail, Matomo, Sim, LangChain (Python çekirdeği), Prompt flow
- Neo4j, Gravitee API Management, Redpanda Connect, XState, Node-RED
- Colima, Harbor Registry (CNCF), Penpot, Figma, NVDA, VoiceOver, Debezium

**Ham araştırmadan (5):**
- ACCESSIBILITY.md, accessibility-skills, LiteParse
- Portkey Models (fiyat verisi), Google Code Wiki

Her araç şu alanlarla eklendi:
- ilgili ihtiyaç kimlikleri (N-Kxx),
- yetenek sınıfları,
- `codex_kaynagi`, `dogrulama` (19 araç dogrulandi, 3 araç kismen: Dovetail, Prompt flow, Code Wiki) ve `dogrulama_notu`,
- birincil kaynak URL'leri.

Hiçbiri arşivlenmiş değil; hepsinin URL'si 200 döndü.

## Düzeltme

AR-0167 "Harbor" kaydı iki farklı ürünü birleştiriyordu: ajan değerlendirme çerçevesi (harbor-framework) ile CNCF'nin OCI kayıt defteri (goharbor). Bunun nedeni, üretim betiğindeki `norm_name` işlevinin parantez içini silmesi. Yapılanlar:
- AR-0167'den goharbor'a ait kanıt URL'si, Y-28/Y-41, üç ihtiyaç eşlemesi ve OCI sınır cümlesi çıkarıldı. Kayda `duzeltme_notu` eklendi.
- goharbor, AR-4394 numarasıyla ayrı kayıt olarak eklendi.

## Çelişkiler

- **Harbor:** Codex haklı; bizde düzeltildi.
- **AutoGen:** Codex "bakım/geçiş" diyor, bizde "arsiv-terk" yazıyor. Depo arşivli değil; bakım modunda, son itme 2026-04-15. Codex'in etiketi daha kesin. Bizim şemada "bakım" değeri olmadığı için kayıt değiştirilmedi; sınırlar metni zaten doğru.
- **goose:** Codex'in verdiği depo adresi `block/goose` eski; `aaif-goose/goose`'a yönleniyor. Bizdeki bilgi doğru.
- **Agent Router:** İki taraf da ad değişikliğinde doğru. Codex'in depo adresi (`envoyproxy/ai-gateway`) eski; `theagentrouter/agent-router`'a yönleniyor.
- **Conductor:** Ad belirsizliği var, iki taraf da doğru. Codex kaydı AR-0014 (conductor-oss) ile eşlendi.
- **Lisanslar:** Codex'in 193 lisans işaretinde çelişki yok. Tek fark yazım: "ELv2" ile "Elastic License 2.0".
- Codex'in 14 yaşam döngüsü notunun 12'si bizde zaten vardı (Presidio taşınması, FastMCP, Jira Align, Vertex adı vb.).

## Eklenmeyenler

- **48 araç seti:** Codex'in kendi kaydı da "bu bileşimde doğrulanmadı" diyor; bizim şemada set kavramı yok.
- **106 araç ailesi:** Bizdeki 67 yetenek sınıfı aynı işi görüyor.
- **827 kaynak kaydı:** Bizde bu iş `kanit_url` ve `url_kontrol` ile yapılıyor.
- **Kritik boşluklar:** İhtiyaç düzeyinde bulgular; ihtiyaç haritasının işi.
- Ham araştırmadan elenenler ve gerekçeleri kayıtta. Örnekler:
  - pydantic-ai-harness: Pydantic AI'a birleştiriliyor.
  - Chandra: model ağırlığı lisansı doğrulanamadı.
  - LobeHub, NextChat, ClickHouse ve benzerleri: ihtiyaçla bağı zayıf.

## Bizde olup Codex'te olmayan

- Codex'le eşleşmeyen 4.129 araç.
- Codex'te hiç aracı olmayan 11 yetenek sınıfı (SLO/hata bütçesi, olay sonrası öğrenme, tehdit modelleme, biçimsel doğrulama vb.).
- 388 ihtiyaca doğrudan eşleme (Codex'te 112 ihtiyaç var).
- Olgunluk, bölge/veri yerleşimi notu ve URL kontrolü alanları.
- Model, egemen/Türkiye, Asya ve akademik ekosistem döngüleri.

## Uyarılar

- `calisma-arsivi/…/arac/birlestir.py` haritayı ham döngü dosyalarından siler ve baştan üretir. Ham klasörde D15 yok; bu betik yeniden çalıştırılırsa E2 eklemeleri ve Harbor düzeltmesi kaybolur. Betik bu yüzden çalıştırılmadı.
- Aynı parantez hatası Glean kayıtlarını (Meta kod bilgisi sistemi + kurumsal arama) ve Faker kayıtlarını (Python + JS) da birleştirmiş görünüyor. Codex kapsamı dışında kaldığı için düzeltilmedi; ayrı iş olarak ele alınmalı.
- Araçlar kurulmadı. İhtiyaç eşlemeleri analist çıkarımıdır ve seçim anlamına gelmez.
