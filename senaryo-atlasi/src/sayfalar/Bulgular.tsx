import { useMemo, useState } from 'react';
import { Accordion, Alert, Anchor, Badge, Button, FileButton, Group, Paper, Radio, Select, Stack, Text, Textarea, TextInput, Title } from '@mantine/core';
import { IconArrowUpRight, IconSearch, IconDownload } from '@tabler/icons-react';
import analiz from '../analiz/bulgular.json';
import { indir, useSayfa, useListeOdak } from '../bilesenler/ortak';
import { useKararNotlari } from '../durum/karar-notlari';
export function Bulgular() {
  const { param, git } = useSayfa();
  const [q, setQ] = useState(''); const [tema, setTema] = useState<string | null>(null);
  const { notlar, yaz, yukle, hata } = useKararNotlari();
  const [dosyaHatasi, setDosyaHatasi] = useState('');
  const notYukle = async (f: File | null) => {
    if (!f) return;
    try {
      if (f.size > 2_000_000) throw new Error('Not dosyası en fazla 2 MB olabilir.');
      const raw = JSON.parse(await f.text());
      yukle(raw.user_notes ?? raw.bulguNotlari); setDosyaHatasi('');
    } catch (e) { setDosyaHatasi(e instanceof Error ? e.message : String(e)); }
  };
  const liste = useMemo(() => analiz.briefs.filter(b => (!tema || b.theme === tema) && JSON.stringify(b).toLocaleLowerCase('tr').includes(q.toLocaleLowerCase('tr'))), [q, tema]);
  const b = liste.find(x => x.id === param.get('id')) ?? liste[0];
  useListeOdak(b?.id);
  const not = b ? notlar[b.id] ?? { secenek: '', not: '' } : { secenek: '', not: '' };
  const rechecks = analiz.primary_rechecks.filter(x => b?.record_ids.includes(x.record_id));
  const indirNotlar = () => indir('bulgu-ve-karar-notlari.json', JSON.stringify({ format: 'bulgu-karar-defteri/v1', generated_at: new Date().toISOString(), findings: analiz.briefs, user_notes: notlar, decision_policy: analiz.decision_policy }, null, 2), 'application/json');
  return <Stack gap="lg">
    <div className="page-intro"><div><Text className="eyebrow">ARAŞTIRMA / KARAR DESTEĞİ</Text><Title order={1}>Bulgudan karara</Title><Text c="dimmed">Ne oldu? Neyi kanıtlıyor? Hangi bilgiyle karar verebilirsin?</Text></div><Button variant="default" leftSection={<IconDownload size={16}/>} onClick={indirNotlar}>Bulgular ve notlar</Button></div>
    <div className="quiet-note"><b>24 soru · 82 kaynak kaydı.</b> Alternatifler tavsiye sırası taşımaz. Seçimin burada bir nottur; senaryo ayarlarını veya bir sistemi kendiliğinden değiştirmez. <FileButton onChange={notYukle} accept="application/json">{props=><Button {...props} variant="subtle" size="compact-xs">Not dosyası yükle</Button>}</FileButton></div>
    {dosyaHatasi && <Alert color="red" role="alert">{dosyaHatasi}</Alert>}
    <div className="research-layout">
      <aside className="research-index" aria-label="Bulgu listesi">
        <TextInput label="Bulgu ara" placeholder="Bellek, oracle, lease…" leftSection={<IconSearch size={16}/>} value={q} onChange={e => setQ(e.target.value)} />
        <Select label="Konu" placeholder="Bütün konular" clearable value={tema} onChange={setTema} data={[...new Set(analiz.briefs.map(b => b.theme))]} mt="sm"/>
        <Text size="xs" c="dimmed" mt="md" mb="xs" role="status">{liste.length} bulgu</Text>
        <div className="research-items">{liste.map(x => <button key={x.id} className={`finding-index-item ${x.id === b?.id ? 'active' : ''}`} aria-current={x.id === b?.id ? 'true' : undefined} onClick={() => git(`bulgular?id=${x.id}`)}><span className="finding-index-meta">{x.id} <span>{x.theme}</span></span><strong>{x.title}</strong>{notlar[x.id]?.secenek && <small>Seçenek notu eklendi</small>}</button>)}</div>
      </aside>
      {b ? <article className="finding-detail" key={b.id}>
        <div className="finding-heading"><Group gap="xs"><span className="record-id">{b.id}</span><Badge variant="outline" color="gray" tt="none">{b.evidence_kind}</Badge></Group><Title order={2}>{b.title}</Title><Text size="sm" c="dimmed">İnceleme: 27 Eylül 2026 · Olay tarihleri özgün kayıtlarda</Text></div>
        <section className="finding-observation"><Text className="eyebrow">KAYNAKTAKİ SOMUT BULGU</Text><Text>{b.observation}</Text></section>
        <div className="reading-section"><h3>Bu ne anlama geliyor?</h3><p>{b.interpretation}</p></div>
        <div className="boundary-note"><Text fw={650} size="sm">Buradan çıkarılamayacak sonuç</Text><Text size="sm" mt={6}>{b.boundary}</Text></div>
        <section className="reading-section"><h3>Kaynağı aç</h3><Group gap="xs">{b.record_ids.map(id => <Button key={id} variant="default" size="xs" rightSection={<IconArrowUpRight size={14}/>} onClick={() => git(`kanit?id=${id}`)}>{id} · özgün kayıt</Button>)}</Group>{rechecks.map(r => <Text size="sm" key={r.url} mt="sm"><Anchor href={r.url} target="_blank" rel="noreferrer">Birincil kaynak · {r.record_id}</Anchor><span className="source-caption">27 Eylül’de yeniden okundu. {r.boundary}</span></Text>)}</section>
        <section className="decision-section"><Text className="eyebrow">KARAR SORUSU</Text><Title order={3}>{b.decision_question}</Title><Text size="sm" c="dimmed" mt={8} mb="lg">Seçenekler örnek yaklaşımlardır; birlikte kullanılabilir. Kendi yaklaşımını not alanına yazabilirsin.</Text>
          <Radio.Group label="İncelemek istediğim yaklaşım" value={not.secenek} onChange={v => yaz(b.id, { ...not, secenek: v })}>
            <Stack gap="sm" mt="xs"><Radio value="" label="Henüz seçim yapmadım"/>{b.options.map(o => <Paper key={o.label} withBorder p="md" radius="sm"><Radio value={o.label} label={o.label}/><Text size="sm" c="dimmed" mt={6} ml={28}>{o.tradeoff}</Text></Paper>)}</Stack>
          </Radio.Group>
          <Textarea label="Benim notum / başka bir yaklaşım" description="Bu tarayıcıda saklanır; JSON ve karar paketine eklenir." placeholder="Karar için görmek istediğim kanıt…" value={not.not} maxLength={3000} autosize minRows={3} mt="lg" onChange={e => yaz(b.id, { ...not, not: e.target.value })}/>
          {hata && <Text c="red" role="alert">{hata}</Text>}
        </section>
        <section className="measurement-note"><Text className="eyebrow">KARARI GÜÇLENDİRECEK EKSİK ÖLÇÜM</Text><Text>{b.missing_measurement}</Text><Text size="xs" c="dimmed" mt="sm">Önerilen deney · çalıştırılmadı</Text></section>
        <Accordion variant="default"><Accordion.Item value="trace"><Accordion.Control>Dosya, hash ve kayıt yolu</Accordion.Control><Accordion.Panel>{b.sources.map(s => <div className="source-trace" key={s.record_id}><b>{s.record_id}</b><span>{s.path} · {s.pointer}</span><code>SHA-256 {s.sha256}</code></div>)}</Accordion.Panel></Accordion.Item></Accordion>
        <Button variant="subtle" px={0} onClick={() => git('tasarimci')}>Bu bulgularla senaryoları incele →</Button>
      </article> : <Paper p="xl" withBorder><Title order={3}>Eşleşen bulgu yok</Title><Text c="dimmed" mt="sm">Başka bir sözcük dene veya konu filtresini temizle.</Text><Button variant="light" mt="md" onClick={() => {setQ('');setTema(null);}}>Filtreleri temizle</Button></Paper>}
    </div>
  </Stack>;
}
