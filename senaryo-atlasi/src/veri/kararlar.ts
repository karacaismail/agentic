import { KARAR_ADAYLARI } from './karar-adaylari';
import type { Karar } from './tipler';

// Senaryo kararları. Her seçenek diyagramdaki teknoloji etiketlerini ve uyarıları değiştirir.
export const KARARLAR: Karar[] = [
  {
    id: 'tetik', baslik: 'Tetik', soru: 'Görev fabrikaya nasıl açılır?', tur: 'radyo', varsayilan: 'durum',
    kaynak: ['Pano A1', 'İlk kapı panosu', 'AK-45', 'E5'],
    secenekler: [
      { deger: 'durum', etiket: 'In Progress + "ajan" etiketi', aciklama: 'Geliştirici işi "devam ediyor"a taşır; yalnız etiketli işler alınır. Durum grup adıyla değil, durum kimliğiyle eşlenir.' },
      { deger: 'startask', etiket: '/startask yorumu', aciklama: 'Geliştirici görev yorumuna komut yazar; yinelenen komut yeni koşu açmaz.' },
      { deger: 'agentready', etiket: 'Ayrı "Agent Ready" durumu', aciklama: 'İnsanın elle yürüttüğü In Progress işlerle hiç karışmaz.' },
    ],
  },
  {
    id: 'durumSahibi', baslik: 'Durum sahibi (orkestratör)', soru: 'Görevin durumunu, bütçesini ve beklemelerini kim tutar?', tur: 'radyo', varsayilan: 'temporal',
    kaynak: ['Pano: tek durum sahibi', 'Kullanıcı kataloğu', 'D1', 'KP-01'],
    secenekler: [
      { deger: 'temporal', etiket: 'Temporal', aciklama: "Kalıcı iş akışı geçmişi ve yeniden oynatma. Görev bütçesi, ilerleme ve dış etki sözleşmelerini uygulama tanımlar." },
      { deger: 'dbos', etiket: 'DBOS', aciklama: "Veritabanı destekli dayanıklı yürütme adayı. Teslim garantileri adaptör deneyiyle sınanmalı." },
      { deger: 'restate', etiket: 'Restate', aciklama: "Dayanıklı yürütme adayı. Dış sistem etkilerinin idempotency ve uzlaştırması ayrıca tasarlanır." },
      { deger: 'kestra', etiket: 'Kestra', aciklama: "Akış ve yürütme yönetimi adayı; önceki pilotun hataları bu yeni tasarımın kabul deneylerine taşınır.", uyari: "Ürün seçimi geçmişteki durma, bütçe veya çift sahip problemini kendiliğinden çözmez." },
      { deger: 'hermesKanban', etiket: 'Hermes Kanban (tek makine)', aciklama: "Kalıcı görev kuyruğu ve çalışma toparlama yetenekleri var.", uyari: "Bu senaryonun bütçe, nesil, izolasyon ve çok makine sözleşmeleri ayrıca sınanmalı." },
      { deger: 'n8n', etiket: 'n8n', aciklama: "Görsel akış ve entegrasyon adayı.", uyari: "Uzun süren ajan görevlerinde ilerleme, iptal, yeniden başlama ve dış etki davranışı doğrulanmalı." },
    ],
  },
  {
    id: 'ajan', baslik: 'Kodlama çalıştırıcısı', soru: 'RED ve GREEN adımlarını hangi ajan çalıştırıcısı yapar?', tur: 'radyo', varsayilan: 'claude',
    kaynak: ['Kullanıcı kataloğu', 'Risk haritası', 'C2'],
    secenekler: [
      { deger: 'claude', etiket: 'Claude Code', aciklama: 'Katalog: birincil kodlama ve araştırma çalışanı.' },
      { deger: 'codex', etiket: 'Codex CLI', aciklama: 'Katalog: bağımsız QA ve yedek ajan için önerilir.' },
      { deger: 'openhands', etiket: 'OpenHands', aciklama: "Kodlama çalışanı adayı; başsız görev, sandbox ve sonuç sözleşmesi adaptörün sorumluluğunda.", uyari: "Ajanın sonuç beyanı bağımsız CI ve kabul kanıtının yerine geçmez." },
      { deger: 'hermes', etiket: 'Hermes Agent', aciklama: "Ajan ve operasyon çalışanı adayı.", uyari: "Kabiliyet ve skill sürümleri sabitlenmeli; görev sınırları test edilmeli." },
      { deger: 'goose', etiket: 'goose', aciklama: 'Katalog: aday; başsız hat entegrasyonu pilotta sınanmalı.' },
      { deger: 'openclaw', etiket: 'OpenClaw', aciklama: "Alternatif ajan/araç yürütme adayı.", uyari: "Görev sınırı, yetkiler, sırlar ve beceri yükleme davranışı izole ortamda nitelendirilmeli." },
    ],
  },
  {
    id: 'qa', baslik: 'Bağımsız QA', soru: 'QA hangi çalıştırıcıyla yapılır? Bağımsızlık; ayrı kanıt, korunan test ve yetki ayrımı gerektirir.', tur: 'radyo', varsayilan: 'codex',
    kaynak: ['Pano C', 'A3', 'B2 S14'],
    secenekler: [
      { deger: 'codex', etiket: 'Codex CLI (OpenAI)' },
      { deger: 'claude', etiket: 'Claude Code (Anthropic)' },
      { deger: 'openhands', etiket: 'OpenHands + açık model', aciklama: "Kodlama çalışanı adayı; başsız görev, sandbox ve sonuç sözleşmesi adaptörün sorumluluğunda.", uyari: "Ajanın sonuç beyanı bağımsız CI ve kabul kanıtının yerine geçmez." },
      { deger: 'yok', etiket: 'QA yok', uyari: 'Kodlayıcının "geçti" beyanı kanıt olarak kalır; test kandırma yakalanmaz (B2 S01).' },
    ],
  },
  {
    id: 'kararModeli', baslik: 'Tipli karar ajanları', soru: 'DoR, yönlendirici, olgunluk ve risk ön sınıfı kararlarını ne verir?', tur: 'radyo', varsayilan: 'pydantic',
    kaynak: ['Kullanıcı kimlik açıklaması', 'karar-modelleri.json / birincil kaynaklar'],
    secenekler: [
      {deger:'pydantic',etiket:'PydanticAI + mevcut model',aciklama:'Şemalı model çıktısı adayı; karar doğruluğu ayrı sınanır.'},
      {deger:'dspy',etiket:'DSPy ile sınıflandırıcı',aciklama:'Etiketli örneklerle optimizasyon ve bağımsız test gerekir.'},
      ...KARAR_ADAYLARI,
    ],
  },
  {
    id: 'birlestirme', baslik: 'Birleştirme yöntemi', soru: 'Kod ana dala nasıl girer?', tur: 'radyo', varsayilan: 'ff',
    kaynak: ['AK-42', 'Kişisel git politikası'],
    secenekler: [
      { deger: 'ff', etiket: 'Kimliği koruyan seri bütünleştirme', aciklama: "Yazar ve committer korunmasını hedefler. Dal koruması, seri bütünleştirme ve gerekli kontroller birlikte sınanmalı." },
      { deger: 'squash', etiket: 'GitHub squash', uyari: 'Committer "GitHub" olur; kişisel git politikana aykırı.' },
      { deger: 'merge', etiket: 'GitHub merge commit', uyari: 'Birleştirme commit\'ini GitHub yazar; committer "GitHub" olur.' },
    ],
  },
  {
    id: 'insanRolu', baslik: 'İnsanın rolü', soru: 'İnsan sistemin neresinde?', tur: 'radyo', varsayilan: 'girdiCikti',
    kaynak: ['Proje amacı', 'İhtiyaç haritası C-040 / D-024'],
    secenekler: [
      { deger: 'esUretici', etiket: 'Eş üretici', aciklama: 'İnsan girdiyi yazar, yüksek riskte planı onaylar, çıktıyı kanıtla kabul eder.' },
      { deger: 'girdiCikti', etiket: 'Yalnız girdi ve çıktı', aciklama: "İnsan görevi ve kabul ölçülerini girer, alpha çıktısını inceler. Çözülemeyen belirsizlik görünür bir sonuç olarak döner." },
    ],
  },
  {
    id: 'oracle', baslik: 'Kabul oracle\'ı', soru: '"Doğru" kararını ne verir?', tur: 'radyo', varsayilan: 'resmi',
    kaynak: ['C4', 'C5', 'Pano bulguları'],
    secenekler: [
      { deger: 'uzman', etiket: 'Uzman imzalı altın veri seti', aciklama: "Alan uzmanıyla doğrulanmış örnekler ve sürümlü iş kuralları; HRMS/bordro için bağımsız doğruluk kaynağı." },
      { deger: 'resmi', etiket: 'Resmî örnekler + property/metamorfik testler', aciklama: 'Resmî örneklerden altın testler; iki bağımsız hesaplama.' },
      { deger: 'acTest', etiket: 'Yalnız AC → test eşlemesi', aciklama: "Kabul ölçütü ile test eşlemesi.", uyari: "Testin geçmesi ürünün doğru veya kapsamın eksiksiz olduğunu tek başına göstermez." },
    ],
  },
  {
    id: 'sandbox', baslik: 'Sandbox', soru: 'Ajan nerede çalışır?', tur: 'radyo', varsayilan: 'docker',
    kaynak: ['Kullanıcı kataloğu', 'E3', 'AK-36'],
    secenekler: [
      { deger: 'docker', etiket: 'Konteyner + çıkış vekili (Mac: Colima)', aciklama: 'Görev başına geçici konteyner; ağ yalnız izin listesiyle.' },
      { deger: 'worktree', etiket: 'git worktree + devcontainer', aciklama: 'Katalog: önerilen "izole dev alanı". İptalde konteyner öldürülmeli.' },
      { deger: 'e2b', etiket: 'E2B (bulut)', aciklama: "Bulut sandbox adayı.", uyari: "Ağ çıkışı, sırlar, veri bölgesi ve maliyet politikası açıkça tanımlanmalı." },
      { deger: 'daytona', etiket: 'Daytona', aciklama: "İzole geliştirme ortamı adayı.", uyari: "Seçilen sürümün bakım, lisans, izolasyon ve veri çıkışı özellikleri yeniden doğrulanmalı." },
    ],
  },
  {
    id: 'calismaYeri', baslik: 'Çalışma yeri', soru: 'Gelecekteki fabrika nerede koşacak?', tur: 'radyo', varsayilan: 'sunucu',
    kaynak: ['KP-06', 'C6'],
    secenekler: [
      { deger: 'sunucu', etiket: 'Hetzner sunucu (Ubuntu + Docker Engine)', aciklama: "128 GB RAM bilinen girdidir; eşzamanlı ajan sayısı CPU, I/O, build ve model limitleri ölçülmeden belirlenmez." },
      { deger: 'mac', etiket: 'Mac + Colima (yalnız deneme)', uyari: 'Mac uykusu kiralamaları ve gece üretimini kırdı (KP-06).' },
    ],
  },
  {
    id: 'model', baslik: 'Model erişimi', soru: 'Ajanlar modele nasıl erişir?', tur: 'radyo', varsayilan: 'apiBuild',
    kaynak: ['C6'],
    secenekler: [
      { deger: 'apiBuild', etiket: 'API · ölçülecek kota profili' },
      { deger: 'apiStart', etiket: 'API · kısıtlı kota profili', aciklama: "Kısıtlı kota profili.", uyari: "Sağlayıcının güncel istek, token ve harcama limitleri girilmeden filo kapasitesi bilinmez." },
      { deger: 'abonelik', etiket: 'Abonelik (Pro/Max)', aciklama: "Abonelik temelli erişim seçeneği.", uyari: "Hesabın otomasyon izinleri ve koşulları sağlayıcıya göre doğrulanmalı; kota varsayılmamalı." },
    ],
  },
  {
    id: 'bildirimAraci', baslik: 'Bildirim aracı', soru: 'Hatırlatma ve yükseltmeleri kim gönderir?', tur: 'radyo', varsayilan: 'orkestrator',
    kaynak: ['Pano: n8n yalnız yapıştırıcı', 'Hermes değerlendirmesi'],
    secenekler: [
      { deger: 'orkestrator', etiket: 'Orkestratör aktivitesi (doğrudan)' },
      { deger: 'n8n', etiket: 'n8n (yapıştırıcı)', aciklama: "Görsel akış ve entegrasyon adayı.", uyari: "Uzun süren ajan görevlerinde ilerleme, iptal, yeniden başlama ve dış etki davranışı doğrulanmalı." },
      { deger: 'hermes', etiket: 'Hermes Agent (operasyon ajanı)', aciklama: "Ajan ve operasyon çalışanı adayı.", uyari: "Kabiliyet ve skill sürümleri sabitlenmeli; görev sınırları test edilmeli." },
    ],
  },
  {
    id: 'bildirim', baslik: 'Bildirim kanalları', soru: 'İnsan nereden haber alır?', tur: 'kutu', varsayilan: ['plane', 'slack'],
    kaynak: ['KP-15', 'AK-53'],
    secenekler: [
      { deger: 'plane', etiket: 'Plane yorumu' },
      { deger: 'slack', etiket: 'Slack' },
      { deger: 'telegram', etiket: 'Telegram' },
      { deger: 'eposta', etiket: 'E-posta' },
    ],
  },
  {
    id: 'ortamlar', baslik: 'Yayın ortamları', soru: 'Aynı imaj hangi ortamlardan geçer?', tur: 'kutu', varsayilan: ['alpha'],
    kaynak: ['Pano E', 'A0'],
    secenekler: [
      { deger: 'alpha', etiket: 'alpha' },
      { deger: 'beta', etiket: 'beta' },
      { deger: 'rc', etiket: 'RC' },
      { deger: 'prod', etiket: 'prod' },
    ],
  },
  {
    id: 'gorunum', baslik: 'Diyagram görünümü', soru: 'Akış nasıl gruplansın?', tur: 'radyo', varsayilan: 'bolum',
    kaynak: [],
    secenekler: [
      { deger: 'kume', etiket: 'Teknoloji kümeleri', aciklama: 'Her kümenin kendi teknolojisi; küme bitince sıradakine geçilir.' },
      { deger: 'bolum', etiket: 'Dört ana bölüm', aciklama: 'Plane → agentic-tdd-development → GitHub CI/CD → alpha.' },
      { deger: 'kumesiz', etiket: 'Kümesiz (tek akış)' },
    ],
  },
];

export const kararBul = (id: string) => KARARLAR.find((k) => k.id === id)!;
export const secenekEtiket = (kararId: string, deger: string) =>
  kararBul(kararId).secenekler.find((s) => s.deger === deger)?.etiket ?? deger;
