import type { AsamaId, EcaKural, Senaryo, Sorun, SorunKaynak, YapiskanNot } from '../veri/tipler';
import { KURALLAR } from '../veri/kurallar';
import { KARARLAR, secenekEtiket } from '../veri/kararlar';
import { AKIS_SIRASI } from '../veri/asamalar';
import { senaryoBul } from '../veri/senaryolar';
import { SORUNLAR, KARARLA_ONLENEN, KURAL_GEREKMEZ } from '../veri/sorunlar';
import { TEMEL_NOTLAR } from '../veri/notlar';
import { KARAR_TEKNOLOJI, SABIT_YIGIN, type Teknoloji } from '../veri/teknolojiler';
import veri from '../veri/uretilen.json';
import { senaryodanDurum, type Durum } from './depo';

export type UyariSeviye = 'kritik' | 'uyari' | 'bilgi';
export interface Uyari { seviye: UyariSeviye; metin: string; kaynak?: string }

export interface KullanilanTeknoloji extends Teknoloji {
  riskPuani?: number;
  riskSeviye?: string;
  hukum?: string;
}

export interface Kapsam {
  toplam: number;
  kapsanan: number;
  acikSorunlar: Sorun[];
  kaynakBazli: Record<SorunKaynak, { toplam: number; kapsanan: number }>;
  sorunKurallari: Map<string, string[]>;
  durumu: (sorunId: string) => 'kapsandi' | 'acik' | 'karar' | 'gerekmez';
}

// Sorun → onu önleyen kurallar (ters dizin), bir kez hesaplanır.
const TERS_DIZIN = (() => {
  const m = new Map<string, string[]>();
  for (const k of KURALLAR) for (const s of k.onler) m.set(s, [...(m.get(s) ?? []), k.id]);
  return m;
})();

const katalogHukum = new Map(veri.katalog.araclar.map((a) => [a.ad, a.hukum]));
const riskBilgisi = veri.risk.araclar as Record<string, { puan: number; seviye: string }>;

export function degerMetni(k: EcaKural, kontrolId: string, v: unknown): string {
  const c = k.kontroller?.find((x) => x.id === kontrolId);
  if (!c) return String(v);
  if (c.tur === 'kutu') {
    const secili = (v as string[]) ?? [];
    return secili.length ? c.secenekler.filter((s) => secili.includes(s.deger)).map((s) => s.etiket).join(', ') : '(hiçbiri)';
  }
  if (c.tur === 'radyo') return c.secenekler.find((s) => s.deger === v)?.etiket ?? String(v);
  return String(v);
}

export function kuralMetni(k: EcaKural, degerler: Record<string, unknown>, alan: 'olay' | 'kosul' | 'eylem'): string {
  return k[alan].replace(/\{(\w+)\}/g, (_, id) => degerMetni(k, id, degerler[id]));
}

export interface Turetilen {
  senaryo: Senaryo;
  aktif: (id: string) => boolean;
  deger: (kuralId: string, kontrol: string) => unknown;
  metin: (k: EcaKural, alan: 'olay' | 'kosul' | 'eylem') => string;
  aktifKurallar: EcaKural[];
  kapaliKurallar: EcaKural[];
  fazUstu: EcaKural[];
  kapsam: Kapsam;
  uyarilar: Uyari[];
  gorunum: 'kume' | 'bolum' | 'kumesiz';
  kumeOf: (a: AsamaId) => string | undefined;
  asamaTeknoloji: (a: AsamaId) => string;
  karar: (id: string) => string;
  kararlarListe: string[];
  teknolojiler: KullanilanTeknoloji[];
  notlar: YapiskanNot[];
  degisenKararlar: string[];
  degisenKurallar: string[];
}

const CALISTIRICI_SAGLAYICI: Record<string, string> = { claude: 'anthropic', codex: 'openai', openhands: 'acik', hermes: 'acik', goose: 'acik', openclaw: 'acik' };
const ORKESTRATORLER = ['kestra', 'temporal', 'dbos', 'restate', 'n8n', 'hermes kanban', 'windmill', 'airflow', 'prefect'];

export function turet(d: Durum): Turetilen {
  const senaryo = senaryoBul(d.senaryoId);
  const aktif = (id: string) => !!d.kurallar[id]?.acik;
  const deger = (kuralId: string, kontrol: string) => d.kurallar[kuralId]?.degerler[kontrol];
  const metin = (k: EcaKural, alan: 'olay' | 'kosul' | 'eylem') => kuralMetni(k, d.kurallar[k.id]?.degerler ?? {}, alan);
  const aktifKurallar = KURALLAR.filter((k) => aktif(k.id));
  const kapaliKurallar = KURALLAR.filter((k) => !aktif(k.id));
  const fazUstu = aktifKurallar.filter((k) => k.faz > d.hedefFaz);
  const karar = (id: string) => {
    const v = d.kararlar[id];
    return Array.isArray(v) ? v.join(',') : String(v ?? '');
  };
  const kararEtiket = (id: string) => secenekEtiket(id, karar(id));

  // ---- Önlem planı bağlantısı ----
  const kaynaklar: SorunKaynak[] = ['kestra', 'd1', 'd2', 'd2d', 'b2', 'b3', 'codex'];
  const kaynakBazli = Object.fromEntries(kaynaklar.map((k) => [k, { toplam: 0, kapsanan: 0 }])) as Kapsam['kaynakBazli'];
  const acikSorunlar: Sorun[] = [];
  let toplam = 0; let kapsanan = 0;
  const durumu = (sid: string): 'kapsandi' | 'acik' | 'karar' | 'gerekmez' => {
    if (KURAL_GEREKMEZ[sid]) return 'gerekmez';
    const kk = KARARLA_ONLENEN[sid];
    if (kk) return karar(kk.karar) === kk.deger ? 'karar' : 'acik';
    const ids = TERS_DIZIN.get(sid) ?? [];
    return ids.length > 0 && ids.every(aktif) ? 'kapsandi' : 'acik';
  };
  for (const s of SORUNLAR) {
    const du = durumu(s.id);
    if (du === 'gerekmez') continue;
    toplam++; kaynakBazli[s.kaynak].toplam++;
    if (du === 'acik') acikSorunlar.push(s); else { kapsanan++; kaynakBazli[s.kaynak].kapsanan++; }
  }
  const kapsam: Kapsam = { toplam, kapsanan, acikSorunlar, kaynakBazli, sorunKurallari: TERS_DIZIN, durumu };

  // ---- Görünüm ve kümeler ----
  let gorunum = karar('gorunum') as Turetilen['gorunum'];
  if (gorunum === 'kume' && d.kumeler.length === 0) gorunum = 'bolum';
  const kumeOf = (a: AsamaId) => d.asamaKume[a] || undefined;

  // ---- Aşama teknoloji etiketleri ----
  const ajanAd = kararEtiket('ajan');
  const qaAd = karar('qa') === 'yok' ? 'QA yok' : kararEtiket('qa').replace(/ \(.*\)$/, '');
  const sandboxAd = kararEtiket('sandbox');
  const sahip = kararEtiket('durumSahibi');
  const ortamlar = (d.kararlar.ortamlar as string[]) ?? ['alpha'];
  const kanallar = ((d.kararlar.bildirim as string[]) ?? []).map((v) => secenekEtiket('bildirim', v));
  const asamaTeknoloji = (a: AsamaId): string => {
    switch (a) {
      case 'GIR': return `Plane · karar ajanı: ${KARAR_TEKNOLOJI['kararModeli:' + karar('kararModeli')]?.ad ?? ''}`;
      case 'TET': return `${kararEtiket('tetik')} → ${sahip}`;
      case 'ARS': return `${ajanAd} (salt okunur)${aktif('R10') ? ' + Context7' : ''}`;
      case 'HAR': return aktif('R11') ? 'kod grafiği + topolojik sıralama' : 'Faz 2\'de açılır';
      case 'PLN': return `${ajanAd} planlar · hakem: ${aktif('R13') ? qaAd : 'yok'}`;
      case 'RED': case 'GRN': return `${ajanAd} · ${sandboxAd}`;
      case 'KAP': return 'GitHub Actions';
      case 'QA': return karar('qa') === 'yok' ? 'bağımsız QA yok' : `${qaAd}${aktif('R27') ? ' + mutasyon' : ''}`;
      case 'RSK': return `policy.yaml${aktif('R30') ? ' + OpenFGA' : ''}${aktif('R29') ? (karar('insanRolu')==='girdiCikti'?' · girdi yetkisi / blokaj çıktısı':' · yüksek risk onayı') : ''}`;
      case 'MQ': return `merge queue · ${kararEtiket('birlestirme')}`;
      case 'DEP': return ortamlar.length > 1 ? `alpha.example.com → ${ortamlar.filter((o) => o !== 'alpha').join(' → ')}` : 'alpha.example.com';
      case 'HT': return `insan · ${kanallar.join(', ') || 'bildirim yok'}`;
      case 'KAB': return 'Done / Rejected';
      default: return '';
    }
  };

  // ---- Kullanılan teknolojiler ----
  const listeler: Teknoloji[] = [];
  for (const kid of ['durumSahibi', 'ajan', 'qa', 'kararModeli', 'sandbox', 'bildirimAraci']) {
    const t = KARAR_TEKNOLOJI[`${kid}:${karar(kid)}`];
    if (t) listeler.push(t);
  }
  for (const t of SABIT_YIGIN) if (!t.kural || aktif(t.kural)) listeler.push(t);
  if (gorunum === 'kume') for (const k of d.kumeler) {
    const var_ = listeler.some((t) => k.teknoloji.toLowerCase().includes(t.ad.toLowerCase()) || t.ad.toLowerCase().includes(k.teknoloji.toLowerCase()));
    if (!var_) {
      const kat = veri.katalog.araclar.find((a) => a.ad.toLocaleLowerCase('tr-TR') === k.teknoloji.trim().toLocaleLowerCase('tr-TR'));
      listeler.push({ ad: k.teknoloji, rol: `Küme: ${k.ad}`, katalog: kat?.ad, risk: kat?.risk?.id });
    }
  }
  const birlesik = new Map<string, KullanilanTeknoloji>();
  for (const t of listeler) {
    const eski = birlesik.get(t.ad);
    if (eski) { if (!eski.rol.includes(t.rol)) eski.rol += ` · ${t.rol}`; continue; }
    const katRisk = t.katalog ? veri.katalog.araclar.find((a) => a.ad === t.katalog)?.risk : undefined;
    const r = t.risk ? (riskBilgisi[t.risk] ?? (katRisk ? { puan: katRisk.puan, seviye: katRisk.seviye } : undefined)) : undefined;
    birlesik.set(t.ad, { ...t, riskPuani: r?.puan, riskSeviye: r?.seviye, hukum: t.katalog ? katalogHukum.get(t.katalog) : undefined });
  }
  const teknolojiler = [...birlesik.values()];

  // ---- Uyarılar ----
  const uyarilar: Uyari[] = [{ seviye: 'bilgi', metin: 'Bu bir tasarım kaydıdır. Seçili önlem, uygulanmış veya doğrulanmış çözüm değildir; gerçek sistem doğrulaması yapılmadı.' }];
  if (aktif('R01') && !(deger('R01','alanlar') as string[])?.includes('ac')) uyarilar.push({seviye:'kritik',metin:'R01: kabul kriteri zorunlu girdiler arasında değil.'});
  if (aktif('R21') && !(deger('R21','kapilar') as string[])?.length) uyarilar.push({seviye:'kritik',metin:'R21 açık fakat hiçbir CI kapısı seçilmemiş.'});
  if (karar('gorunum') === 'kume' && AKIS_SIRASI.some(a => !d.asamaKume[a])) uyarilar.push({seviye:'uyari',metin:'Bazı aşamaların kümesi atanmamış. Küme silindiğinde otomatik yeni sahip verilmez.'});
  if (!ortamlar.includes('alpha')) uyarilar.push({seviye:'kritik',metin:'İstenen alpha teslim ortamı seçilmemiş.'});
  if (ortamlar.some(o => o !== 'alpha')) uyarilar.push({seviye:'uyari',metin:'Alpha sonrası ortamlar geleceğe ait tasarımdır; bu çalışma yayın yetkisi vermez.'});
  const kritikKararlar = new Set(['ajan:openclaw', 'durumSahibi:n8n', 'birlestirme:squash', 'birlestirme:merge', 'qa:yok']);
  for (const k of KARARLAR) {
    if (k.tur !== 'radyo') continue;
    const s = k.secenekler.find((x) => x.deger === karar(k.id));
    if (s?.uyari) uyarilar.push({ seviye: kritikKararlar.has(`${k.id}:${s.deger}`) ? 'kritik' : 'uyari', metin: `${k.baslik} · ${s.etiket}: ${s.uyari}`, kaynak: k.kaynak.join(', ') });
  }
  if (karar('qa') !== 'yok' && karar('qa') === karar('ajan'))
    uyarilar.push({ seviye: 'uyari', metin: 'QA ile kodlayıcı aynı çalıştırıcı: ortak kör noktalar ve kendi ailesini kayırma riski.', kaynak: 'B2 S14, Pano C' });
  else if (CALISTIRICI_SAGLAYICI[karar('ajan')] && CALISTIRICI_SAGLAYICI[karar('ajan')] === CALISTIRICI_SAGLAYICI[karar('qa')] && CALISTIRICI_SAGLAYICI[karar('qa')] !== 'acik')
    uyarilar.push({ seviye: 'uyari', metin: 'QA ile kodlayıcı aynı sağlayıcıdan.', kaynak: 'Pano C' });
  if (fazUstu.length)
    uyarilar.push({ seviye: 'uyari', metin: `${fazUstu.length} kural hedef fazın (Faz ${d.hedefFaz}) üstünde açık: ${fazUstu.map((k) => k.id).join(', ')}. Önceki pilotta ECA, Kaizen ve SAFe temel akış kanıtlanmadan eklendi.`, kaynak: 'KP-03, R71' });
  const kapaliCekirdek = KURALLAR.filter((k) => k.faz === 0 && !aktif(k.id));
  if (kapaliCekirdek.length)
    uyarilar.push({ seviye: 'kritik', metin: `${kapaliCekirdek.length} çekirdek (Faz 0) kural kapalı: ${kapaliCekirdek.map((k) => `${k.id} ${k.baslik}`).join('; ')}.`, kaynak: 'Sorunlar ve önlemler sayfası' });
  if (gorunum === 'kume') {
    const sahipAd = sahip.toLowerCase();
    for (const k of d.kumeler) {
      const t = k.teknoloji.toLowerCase();
      const orkestrator = ORKESTRATORLER.find((o) => t.includes(o));
      if (orkestrator && !sahipAd.toLowerCase().includes(orkestrator)) {
        uyarilar.push(aktif('R54')
          ? { seviye: 'bilgi', metin: `"${k.teknoloji}" kümesinin önerilen rolü tetik, zamanlama veya bildirimdir; bu tasarımda yaşam döngüsü sahibi ${sahip} tutar (R54).`, kaynak: 'KP-01, E6' }
          : { seviye: 'kritik', metin: `"${k.teknoloji}" ve ${sahip} birlikte seçilmiş; R54 kapalı. Yaşam döngüsü yazma yetkisi açıkça ayrılmalı.`, kaynak: 'KP-01, D1-13' });
      }
      if (/laya/i.test(k.teknoloji)) uyarilar.push({ seviye: 'bilgi', metin: '"Laya" kaynaklarda ve katalogda bulunamadı; risk bilgisi gösterilemiyor.' });
    }
    const uygulamaKumesi = d.kumeler.find((k) => k.id === kumeOf('GRN'));
    if (uygulamaKumesi && !uygulamaKumesi.teknoloji.toLowerCase().includes(ajanAd.toLowerCase()) && !/seçilmedi/i.test(uygulamaKumesi.teknoloji))
      uyarilar.push({ seviye: 'bilgi', metin: `"${uygulamaKumesi.ad}" kümesinin teknolojisi (${uygulamaKumesi.teknoloji}) ile kodlama çalıştırıcısı kararı (${ajanAd}) farklı. Diyagramda ikisi de görünür.` });
  } else if (karar('gorunum') === 'kume') {
    uyarilar.push({ seviye: 'bilgi', metin: 'Bu senaryoda küme yok; dört ana bölüm gösteriliyor. Kümeler bölümünden küme ekleyebilirsin.' });
  }
  if (aktif('R39') && Number(deger('R39', 'yukselt')) <= Number(deger('R39', 'hatirlat')))
    uyarilar.push({ seviye: 'uyari', metin: 'R39: yükseltme süresi hatırlatmadan kısa ya da eşit.' });
  if (!(d.kararlar.bildirim as string[])?.length)
    uyarilar.push({ seviye: 'uyari', metin: 'Bildirim kanalı seçilmedi: insan beklemesi görünmez kalır (KP-15).' });
  for (const u of senaryo.uyarilar) uyarilar.push({ seviye: 'bilgi', metin: u, kaynak: `Senaryo: ${senaryo.ad}` });
  const sira: Record<UyariSeviye, number> = { kritik: 0, uyari: 1, bilgi: 2 };
  uyarilar.sort((a, b) => sira[a.seviye] - sira[b.seviye]);

  // ---- Notlar ----
  const notlar = [...TEMEL_NOTLAR, ...(senaryo.notlar ?? [])];

  // ---- Senaryo varsayılanından değişenler ----
  const taban = senaryodanDurum(d.senaryoId);
  const degisenKararlar = Object.keys(d.kararlar).filter((k) => JSON.stringify(d.kararlar[k]) !== JSON.stringify(taban.kararlar[k]));
  const degisenKurallar = KURALLAR.filter((k) => JSON.stringify(d.kurallar[k.id]) !== JSON.stringify(taban.kurallar[k.id])).map((k) => k.id);

  return {
    senaryo, aktif, deger, metin, aktifKurallar, kapaliKurallar, fazUstu, kapsam, uyarilar, gorunum, kumeOf,
    asamaTeknoloji, karar, kararlarListe: AKIS_SIRASI, teknolojiler, notlar, degisenKararlar, degisenKurallar,
  };
}
