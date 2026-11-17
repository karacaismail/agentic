import analiz from '../analiz/bulgular.json';
import {notlariOku} from '../durum/karar-notlari';
import { useEffect, useMemo, useRef, useState } from 'react';
import { Alert, Button, Group, Stack, Text } from '@mantine/core';
import { IconPrinter, IconInfoCircle } from '@tabler/icons-react';
import { useDurum } from '../durum/depo';
import { useTuretilen } from '../durum/kanca';
import { raporDiyagramlari } from '../diyagram/rapor';
import { simulasyonGecmisi } from '../motor/simulasyon';
import { paket } from '../motor/paket';
import { indir } from '../bilesenler/ortak';
import { MermaidGorunum } from '../diyagram/MermaidGorunum';
import { KARARLAR } from '../veri/kararlar';
import { AKIS_SIRASI, ASAMALAR, asamaBul } from '../veri/asamalar';
import { KURALLAR } from '../veri/kurallar';
import { SKILLER, MCP_SUNUCULARI } from '../veri/ajanlar';
import { BELGELER } from '../veri/belgeler';
import { CERCEVELER } from '../veri/teknolojiler';
import { KAYNAK_ADI } from '../veri/sorunlar';
import { HUKUM, SEVIYE_AD, useSayfa } from '../bilesenler/ortak';

const bugun = () => new Date().toLocaleDateString('tr-TR', { day: '2-digit', month: 'long', year: 'numeric' });

export function Rapor() {
  const { durum } = useDurum();
  const t = useTuretilen();
  const { param } = useSayfa();
  const diyagramlar = useMemo(() => raporDiyagramlari(durum, t), [durum, t]);
  const rev = JSON.stringify(durum);
  const [cizilen, setCizilen] = useState<Record<string,string>>({});
  const [fontHazir,setFontHazir] = useState(false);
  const yazdirildi = useRef(false);
  const yazdir = param.get('yazdir') === '1';
  const hazirSayisi = diyagramlar.filter(d => cizilen[d.id] === rev).length;
  const hazir = hazirSayisi === diyagramlar.length && fontHazir;
  const gecmis = simulasyonGecmisi(durum);
  useEffect(() => { let alive=true; document.fonts.ready.then(()=>{if(alive)setFontHazir(true)});return()=>{alive=false}; },[]);
  useEffect(() => {
    if (!yazdir) {yazdirildi.current=false;return;}
    if (!hazir || yazdirildi.current) return;
    yazdirildi.current = true;
    history.replaceState(null, '', '#/rapor');
    const timer=setTimeout(()=>window.print(),250);
    return()=>clearTimeout(timer);
  }, [yazdir,hazir]);

  const kararDegeri = (id: string) => {
    const k = KARARLAR.find((x) => x.id === id)!;
    const v = durum.kararlar[id];
    const liste = Array.isArray(v) ? v : [v];
    return liste.map((x) => k.secenekler.find((s) => s.deger === x)?.etiket ?? x).join(', ') || '—';
  };
  const acikRiskGruplari = Object.entries(KAYNAK_ADI).map(([k, ad]) => ({ ad, liste: t.kapsam.acikSorunlar.filter((s) => s.kaynak === k) })).filter((g) => g.liste.length);
  const kullaniciNotlari = notlariOku();
  const notluBulgular = analiz.briefs.filter(b=>kullaniciNotlari[b.id]?.secenek || kullaniciNotlari[b.id]?.not);
  const kullanilanSkill = SKILLER.filter((s) => AKIS_SIRASI.includes(s.asama) || t.aktifKurallar.some((k) => k.asama === s.asama));

  return (
    <Stack gap="md" data-report-ready={hazir ? "true" : "false"}>
      <Group justify="space-between" className="ekran-yalniz">
        <Text size="sm" c="dimmed">Bu sayfa PDF'in kendisidir. Düğmeye bas; açılan pencerede hedef olarak "PDF olarak kaydet"i seç.</Text>
        <Group><Button variant="default" onClick={() => indir(`karar-paketi-${durum.senaryoId}.json`,JSON.stringify(paket(durum),null,2),"application/json")}>Karar paketini indir</Button><Button disabled={!hazir} leftSection={<IconPrinter size={16} />} onClick={() => window.print()}>PDF olarak kaydet</Button></Group>
      </Group>
      {!hazir && (
        <Alert className="ekran-yalniz" icon={<IconInfoCircle size={16} />} color="blue">Diyagramlar hazırlanıyor ({hazirSayisi}/{diyagramlar.length}); tümü ve yazı tipleri hazır olmadan PDF alınmaz.</Alert>
      )}
      <article className="rapor">
        <p className="alt">Senaryo Karar Raporu · {bugun()}</p>
        <h1>{t.senaryo.ad}</h1>
        <p>{t.senaryo.ozet}</p><p><b>TASARIM · Uygulanmadı.</b> Seçili önlem doğrulanmış çözüm değildir. Kaynak araştırma kayıtları örtüşebilir; sayılar gerçek hata oranı değildir.</p>
        <p><span className="rozet">Hedef faz: Faz {durum.hedefFaz}</span> <span className="rozet">{t.aktifKurallar.length}/{KURALLAR.length} ECA kuralı açık</span> <span className="rozet">{t.kapsam.kapsanan}/{t.kapsam.toplam} tasarım bağlantısı · uygunluk deneyi: 0</span></p>

        <h2>Kullanıcının bulgu notları</h2>
        <p>Alternatifler otomatik seçilmez. Buradaki notlar senaryo ayarlarını değiştirmez.</p>
        {notluBulgular.length ? notluBulgular.map(b=><section key={b.id}><h3>{b.id} · {b.title}</h3><p><b>Kaynak bulgusu:</b> {b.observation}</p><p><b>Sınırı:</b> {b.boundary}</p><p><b>Benim seçeneğim:</b> {kullaniciNotlari[b.id].secenek||'Henüz seçim yapılmadı'}</p><p style={{whiteSpace:'pre-wrap'}}><b>Benim notum:</b> {kullaniciNotlari[b.id].not||'—'}</p><p><b>Eksik ölçüm:</b> {b.missing_measurement}</p><p className="alt">Kaynak kayıtları: {b.record_ids.join(', ')} · İnceleme: 27 Eylül 2026 · Deney: çalıştırılmadı</p></section>) : <p>Henüz bulguya bağlı kullanıcı seçimi veya notu yok.</p>}
        <h2>1. Senaryo ayarları</h2>
        <p>Hazır senaryo varsayılanları da listelenir; bu tablo tek başına kullanıcı onayı değildir.</p>
        <table>
          <tbody>{KARARLAR.map((k) => <tr key={k.id}><th style={{ width: '32%' }}>{k.baslik}</th><td>{kararDegeri(k.id)}</td></tr>)}</tbody>
        </table>

        <h2>2. Uyarılar</h2>
        {t.uyarilar.length ? (
          <table><tbody>{t.uyarilar.map((u, i) => <tr key={i}><td style={{ width: 70 }}><span className={`rozet ${u.seviye}`}>{u.seviye === 'kritik' ? 'Kritik' : u.seviye === 'uyari' ? 'Uyarı' : 'Bilgi'}</span></td><td>{u.metin}{u.kaynak ? <span className="alt"> · {u.kaynak}</span> : null}</td></tr>)}</tbody></table>
        ) : <p>Uyarı yok.</p>}

        {t.gorunum === 'kume' && durum.kumeler.length > 0 && (
          <>
            <h2>3. Kümeler</h2>
            <table>
              <thead><tr><th>Küme</th><th>Teknoloji</th><th>Aşamalar</th><th>Devir olayı</th></tr></thead>
              <tbody>{durum.kumeler.map((k, i) => (
                <tr key={k.id}><td><span style={{ display: 'inline-block', width: 10, height: 10, background: k.renk, borderRadius: 2, marginRight: 6 }} />{i + 1}. {k.ad}</td><td>{k.teknoloji}</td>
                  <td>{AKIS_SIRASI.filter((a) => t.kumeOf(a) === k.id).map((a) => asamaBul(a).ad).join(', ') || '—'}</td><td>{k.devir || '—'}</td></tr>
              ))}</tbody>
            </table>
          </>
        )}

        <h2>4. Somut iş akışı</h2>
        <table>
          <thead><tr><th>Aşama</th><th>Teknoloji</th><th>Ajan</th><th>Skill</th><th>MCP</th><th>Açık kurallar</th></tr></thead>
          <tbody>{ASAMALAR.map((a) => {
            const acik = KURALLAR.filter((k) => k.asama === a.id && t.aktif(k.id)).map((k) => k.id);
            return (
              <tr key={a.id}>
                <td><b>{a.kod !== '—' ? `${a.kod} · ` : ''}{a.ad}</b></td>
                <td>{t.asamaTeknoloji(a.id) || '—'}</td>
                <td>{a.ajanlar.join(', ') || '—'}</td>
                <td>{a.skill.join(', ') || '—'}</td>
                <td>{a.mcp.join(', ') || '—'}</td>
                <td>{acik.join(', ') || '—'}</td>
              </tr>
            );
          })}</tbody>
        </table>

        
        {diyagramlar.map((d) => (
          <figure key={d.id} className="pdf-diagram">
            <figcaption><b>{d.baslik}.</b> {d.aciklama}</figcaption>
            <MermaidGorunum key={d.id+rev} kod={d.kod} notlar={d.notlar} onSvg={(svg) => {if(svg)setCizilen(s=>s[d.id]===rev?s:{...s,[d.id]:rev});}} />
          </figure>
        ))}

        <h2>Seçili kararla yapılan yerel simülasyonlar</h2>
        <p>{gecmis.length ? `${gecmis.length} örnek olay. Gerçek sistem uygunluğu ispatlanmadı.` : 'Bu karar sürümü için bu oturumda simülasyon kaydı yok.'}</p>
        {gecmis.map((x,i)=><p key={i}><b>{x.girdi.olay} → {x.sonuc.kod}</b>: {x.sonuc.eylem}</p>)}
        <h2>Diyagram notları / bilinen sorunlar</h2>
        <table><tbody>{t.notlar.map((n,i)=><tr key={i}><td>{n.asama} · {n.kural ?? 'bilgi'}</td><td>{n.metin}<br/>Kaynak: {n.kaynak}. {n.kural ? (t.aktif(n.kural)?'Önlem tasarımda seçili.':'Önlem kapalı.') : ''}</td></tr>)}</tbody></table>
        <h2 className="yeni-sayfa">6. Açık ECA kuralları</h2>
        <table>
          <thead><tr><th style={{ width: 115 }}>Kural</th><th>Olay</th><th>Koşul</th><th>Eylem</th><th style={{ width: 44, whiteSpace: 'nowrap' }}>Faz</th></tr></thead>
          <tbody>{t.aktifKurallar.map((k) => (
            <tr key={k.id}><td><b>{k.id}</b><br /><span className="alt">{k.baslik}</span></td><td>{t.metin(k, 'olay')}</td><td>{t.metin(k, 'kosul')}</td><td>{t.metin(k, 'eylem')}</td><td>{k.faz}</td></tr>
          ))}</tbody>
        </table>

        <h2>7. Kapalı kurallar ve açık kalan riskler</h2>
        <p>Kapalı kurallar: {t.kapaliKurallar.map((k) => `${k.id} ${k.baslik}`).join('; ') || 'yok'}.</p>
        {acikRiskGruplari.map((g) => (
          <div key={g.ad}>
            <h3>{g.ad} ({g.liste.length})</h3>
            <p>{g.liste.map((s) => `${s.id} ${s.baslik}`).join(' · ')}</p>
          </div>
        ))}

        <h2>8. Teknolojiler ve çerçeveler</h2>
        <table>
          <thead><tr><th>Teknoloji</th><th>Rolü</th><th>Tarihî kaynak hükmü</th><th>Arşiv puanı</th></tr></thead>
          <tbody>{t.teknolojiler.map((x) => (
            <tr key={x.ad}><td><b>{x.ad}</b></td><td>{x.rol}</td><td>{x.hukum ? HUKUM[x.hukum]?.ad : '—'}</td><td>{x.riskPuani !== undefined ? `${x.riskPuani} (${SEVIYE_AD[x.riskSeviye ?? ''] ?? ''})` : '—'}</td></tr>
          ))}</tbody>
        </table>
        <p>{CERCEVELER.map((c) => <span key={c.ad}><b>{c.ad}:</b> {c.rol}. </span>)}</p>

        <h2>9. Skill'ler ve MCP sunucuları</h2>
        <table>
          <thead><tr><th>Skill</th><th>Aşama</th><th>Ne yapar</th></tr></thead>
          <tbody>{kullanilanSkill.map((s) => <tr key={s.id}><td><b>{s.id}</b></td><td>{asamaBul(s.asama).ad}</td><td>{s.ne}</td></tr>)}</tbody>
        </table>
        <table>
          <thead><tr><th>MCP sunucusu</th><th>Kullanım</th><th>Yetki</th></tr></thead>
          <tbody>{MCP_SUNUCULARI.map((m) => <tr key={m.ad}><td><b>{m.ad}</b></td><td>{m.kullanim}</td><td>{m.yetki}</td></tr>)}</tbody>
        </table>

        <h2>10. Hazırlanacak dosyalar (CLAUDE.md hariç)</h2>
        <table>
          <thead><tr><th>Dosya</th><th>Ne işe yarar</th><th>Ne zaman</th></tr></thead>
          <tbody>{BELGELER.map((b) => <tr key={b.yol}><td><b>{b.yol}</b></td><td>{b.neIse}</td><td>{b.zorunluluk}</td></tr>)}</tbody>
        </table>

        <p className="alt" style={{ marginTop: 24 }}>Kaynaklar: senin panoların (agentic-stack-docs), araştırma dosyaları A0–E6, risk, araç ve ihtiyaç haritaları, Codex derin incelemesi (salt okunur kopya). Ayrıntı: Kaynaklar sayfası.</p>
      </article>
    </Stack>
  );
}
