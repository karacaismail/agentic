import { useMemo, useState } from 'react';
import { Accordion, Anchor, Badge, Button, Code, Group, Paper, Select, Stack, Text, TextInput, Title } from '@mantine/core';
import esleme from '../veri/kanit-eslemeleri.json';
import analiz from '../analiz/bulgular.json';
import { useDurum } from '../durum/depo';
import kanit from '../veri/kanitlar.json';
import { indir, useSayfa, useListeOdak } from '../bilesenler/ortak';
const mapping = [...esleme.crosswalk.local, ...esleme.crosswalk.world, ...esleme.crosswalk.deep];
const external = kanit.dosyalar.flatMap(f => {try {return (JSON.parse(f.icerik).sources ?? []) as {id:string;url?:string;title?:string}[];} catch {return [];}}).filter(s => s.url && /^https?:\/\//.test(s.url));
export function KanitDefteri() {
 const {durum}=useDurum(); const {param,git}=useSayfa();
 const [q,setQ]=useState(''); const [grup,setGrup]=useState<string|null>(null); const [tur,setTur]=useState<string|null>(null);
 const liste=useMemo(()=>kanit.kayitlar.filter(r=>(!grup||r.grup===grup)&&(!tur||analiz.record_index.find(i=>i.id===r.id)?.kind===tur)&&JSON.stringify(r).toLocaleLowerCase('tr').includes(q.toLocaleLowerCase('tr'))),[q,grup,tur]);
 const r=liste.find(r=>r.id===param.get('id'))??liste[0]; const i=analiz.record_index.find(i=>i.id===r?.id);
 useListeOdak(r?.id);
 const m=mapping.find(x=>x.canonical_id===r?.id);const rules=m?('candidate_eca_ids' in m?m.candidate_eca_ids:m.existing_eca_ids):[];
 const excerpt=i?analiz.local_excerpt_registry.filter(e=>i.source_ids.includes(e.id)):[];
 const links=i?external.filter((s,n,a)=>i.source_ids.includes(s.id)&&a.findIndex(t=>t.url===s.url)===n):[];
 const trace=r && 'failure_trace' in r.ham ? r.ham.failure_trace as string[]:[];
 return <Stack gap="lg"><div className="page-intro"><div><Text className="eyebrow">ARAŞTIRMA / ÖZGÜN KAYITLAR</Text><Title order={1}>Kanıt defteri</Title><Text c="dimmed">18 yerel geçmiş · 36 dış vaka/araştırma · 28 mimari inceleme</Text></div><Button variant="default" size="sm" onClick={()=>indir('kanit-defteri.json',JSON.stringify(kanit.kayitlar,null,2),'application/json')}>Özgün kayıtları indir</Button></div>
 <div className="quiet-note">Bir kayıt, bir bağımsız olay demek değildir. Statik kod yolu, kullanıcı raporu ve yeniden üretilmiş olay farklı kanıt türleridir. Seçili önlem, kaydı “çözüldü” yapmaz.</div>
 <div className="research-layout"><aside className="research-index"><TextInput label="Kayıtlarda ara" placeholder="OOM, oracle, K05…" value={q} onChange={e=>setQ(e.target.value)}/><Select mt="sm" label="Kaynak kümesi" placeholder="Tümü" clearable data={['Yerel geçmiş','Dünya vakaları','Mimari inceleme']} value={grup} onChange={setGrup}/><Select mt="sm" label="Kanıt türü" placeholder="Tümü" clearable data={[...new Set(analiz.record_index.map(i=>i.kind))]} value={tur} onChange={setTur}/><Text size="xs" c="dimmed" mt="md" mb="xs" role="status">{liste.length} kayıt</Text><div className="research-items">{liste.map(x=><button className={`finding-index-item ${r?.id===x.id?'active':''}`} key={x.id} aria-current={r?.id===x.id?'true':undefined} onClick={()=>git(`kanit?id=${x.id}`)}><span className="finding-index-meta">{x.id}<span>{x.grup}</span></span><strong>{x.baslik}</strong></button>)}</div></aside>
 {r&&i?<article className="finding-detail" key={r.id}><div className="finding-heading"><Group><span className="record-id">{r.id}</span><Badge color="gray" variant="outline" tt="none">{i.kind}</Badge></Group><Title order={2}>{r.baslik}</Title><Text size="sm" c="dimmed">Kaydın dönemi: {i.period}</Text></div><section className="finding-observation"><Text className="eyebrow">KAYITTA NE VAR?</Text><Text>{i.observation}</Text></section>
 {i.mechanism&&<section className="reading-section"><h3>Kaynağın neden değerlendirmesi</h3><p>{i.mechanism}</p></section>}
 {trace.length>0&&<section className="reading-section"><h3>İncelenen kod yolu · canlı olay değil</h3><ol>{trace.map((s,n)=><li key={n}>{s}</li>)}</ol></section>}
 <div className="boundary-note"><Text size="sm" fw={650}>Kanıtın sınırı</Text><Text size="sm" mt={6}>{i.boundary}</Text></div>
 <section className="reading-section"><h3>Kaydedilen sonuç / düzeltme</h3><p>{i.status==='documented_not_implemented'?'Belgelendi; uygulanmadı.':i.status}</p><Text c="dimmed" size="sm">Güncel çalışma zamanı bu atlas içinde yeniden test edilmedi.</Text></section>
 {i.test&&<section className="measurement-note"><Text className="eyebrow">DOĞRULAMA İÇİN ÖNERİLEN DENEY</Text><Text>{i.test}</Text><Text size="xs" c="dimmed" mt="sm">Deney önerisi; bu ekranda çalıştırılmaz.</Text></section>}
 {i.brief_ids.length>0&&<Group mt="lg">{i.brief_ids.map(id=><Button key={id} variant="light" onClick={()=>git(`bulgular?id=${id}`)}>{id} · karar sorusunu aç</Button>)}</Group>}
 <Accordion mt="lg" variant="separated">
 <Accordion.Item value="sources"><Accordion.Control>Kaynak izi ve belge alıntıları ({i.source_ids.length})</Accordion.Control><Accordion.Panel><div className="source-trace"><b>{r.pointer}</b><span>{r.kaynak}</span><code>SHA-256 {r.sha256}</code></div><Button variant="default" size="xs" mt="sm" onClick={()=>git(`kaynaklar?dosya=${encodeURIComponent(r.kaynak)}`)}>Tam kaynak dosyasını oku</Button>
 {links.map(s=><Text mt="sm" key={s.url}><Anchor size="sm" href={s.url} target="_blank" rel="noreferrer">{s.id} · {s.title??s.url}</Anchor></Text>)}
 {excerpt.map(e=><div className="source-excerpt" key={e.id}><Text fw={650} size="sm">{e.id} · {e.source_id} · satır {e.line_start}–{e.line_end}</Text><Text size="xs" c="dimmed">{e.kind} · Alıntı kısaltılmış olabilir</Text><p>{e.excerpt}</p></div>)}
 {excerpt.length===0&&links.length===0&&<Text mt="sm" size="sm">Kaynak kimlikleri: {i.source_ids.join(', ')||'Özgün kayıtta'}. Ayrıntılı atıflar ham kayıt ve kaynak dosyasında korunur.</Text>}
 </Accordion.Panel></Accordion.Item>
 <Accordion.Item value="rules"><Accordion.Control>İlişkili önlem taslakları ({rules.length})</Accordion.Control><Accordion.Panel><Text size="sm" mb="sm">Aday/kısmi eşlemelerdir. Yeterlilik veya sorunun çözüldüğü kanıtı değildir.</Text><Group>{rules.map(id=><Button size="xs" variant="default" key={id} onClick={()=>git(`tasarimci?sekme=kurallar&kural=${id}`)}>{id} · {durum.kurallar[id]?.acik?'seçili':'kapalı'}</Button>)}</Group></Accordion.Panel></Accordion.Item>
 <Accordion.Item value="raw"><Accordion.Control>Özgün JSON kaydı</Accordion.Control><Accordion.Panel><Code block className="kod-blok">{JSON.stringify(r.ham,null,2)}</Code><Button size="xs" mt="sm" variant="default" onClick={()=>indir(`${r.id}.json`,JSON.stringify(r,null,2),'application/json')}>Bu kaydı indir</Button></Accordion.Panel></Accordion.Item>
 </Accordion></article>:<Paper p="xl" withBorder><Text>Bu filtrelerde kayıt bulunamadı.</Text><Button mt="sm" variant="light" onClick={()=>{setQ('');setGrup(null);setTur(null);}}>Filtreleri temizle</Button></Paper>}
 </div></Stack>;
}
