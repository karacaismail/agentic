import { Button, Group, Paper, SimpleGrid, Stack, Text, Title } from '@mantine/core';
import { IconArrowRight, IconArrowUpRight } from '@tabler/icons-react';
import { useSayfa } from '../bilesenler/ortak';
import { useTuretilen } from '../durum/kanca';
import analiz from '../analiz/bulgular.json';
import kanit from '../veri/kanitlar.json';
export function Baslangic() {
 const {git}=useSayfa();const t=useTuretilen();
 return <Stack gap="xl">
   <section className="atlas-intro"><div><Text className="eyebrow">İNSAN–AJAN YAZILIM ÜRETİMİ</Text><Title order={1}>Önce bulgu.<br/><span>Sonra senin kararın.</span></Title><Text className="intro-copy">Görevden alpha’ya uzanan sistem için araştırma masan. Yaşanan sorunları, kanıtın sınırlarını ve seçeneklerin bedelini birlikte incele.</Text><Group mt="lg"><Button size="md" rightSection={<IconArrowRight size={17}/>} onClick={()=>git('bulgular')}>Bulguları incele</Button><Button variant="subtle" onClick={()=>git('tasarimci')}>Senaryolara geç</Button></Group></div><div className="intro-aside"><span className="edition-label">ARAŞTIRMA DOSYASI / 27 EYLÜL 2026</span><p>Plane <span>→</span> Agentic TDD<br/>GitHub CI/CD <span>→</span> Alpha</p><Text size="sm" c="dimmed">Hedef: insanın girdiyi ve çıktıyı gördüğü, içerideki sürecin kanıtla izlendiği bir çalışma sistemi.</Text><div className="design-only">Tasarım alanı · canlı sisteme bağlı değil</div></div></section>
   <div className="evidence-strip">{[['24','kaynaklı karar sorusu'],['18','yerel geçmiş kaydı'],['36','dış vaka / araştırma'],['28','mimari inceleme kaydı']].map(([n,s])=><div key={s}><strong>{n}</strong><span>{s}</span></div>)}</div>
   <section><div className="section-heading"><div><Text className="eyebrow">ÖNE ÇIKAN ÜÇ BULGU</Text><Title order={2}>Aynı belirti, farklı nedenler.</Title></div><Button variant="subtle" rightSection={<IconArrowUpRight size={16}/>} onClick={()=>git('bulgular')}>24 bulgunun tamamı</Button></div><SimpleGrid cols={{base:1,md:3}} spacing="lg">{[analiz.briefs[0],analiz.briefs[1],analiz.briefs[3]].map((b,i)=><Paper withBorder p="xl" className="featured-finding" key={b.id}><Text className="eyebrow">{['KAPASİTE','İLERLEME','TEŞHİS'][i]} / {b.record_ids[0]}</Text><Title order={3}>{b.title}</Title><Text className="finding-teaser">{[
   '51 testlik koşu raporsuz bitti. Kernel OOM kaydı var; aynı aday 2 GB ile üç kez geçti.',
   'Test yaklaşık 70 dakika sürüyordu. Gözetleyici 600 saniyede kesip üç kez yeniden başlattı.',
   'Okuma aracı yoktu, içerik girdiye eklenmemişti. “Okuyamadım” çıktısı başarı diye kaydedildi.'
   ][i]}</Text><Button px={0} variant="subtle" rightSection={<IconArrowRight size={16}/>} onClick={()=>git(`bulgular?id=${b.id}`)}>Kanıtı ve sınırını oku</Button></Paper>)}</SimpleGrid></section>
   <div className="workspace-bottom"><section><Text className="eyebrow">ÇALIŞMA SIRAN</Text><div className="step-links">{[
     ['01','Kanıtı oku','Özgün kayıt, olay tarihi ve doğrulama sınırı.','kanit'],
     ['02','Alternatifleri karşılaştır','Önceden seçilmemiş yaklaşımlar; kendi karar notun.','bulgular'],
     ['03','Senaryoyu biçimlendir','ECA koşulları, teknoloji rolleri ve hata akışları.','tasarimci'],
     ['04','Çıktını yanında götür','Diyagram, belge, karar notları ve PDF.','rapor']
   ].map(([n,title,desc,page])=><button key={n} onClick={()=>git(page)}><span>{n}</span><div><strong>{title}</strong><small>{desc}</small></div><IconArrowUpRight size={18}/></button>)}</div></section><section className="working-copy"><Text className="eyebrow">AÇIK SENARYO TASLAĞI</Text><Title order={3}>{t.senaryo.ad}</Title><Text size="sm" c="dimmed" mt="sm">Bu hazır senaryonun ayarlarıdır; araç tavsiyesi veya verilmiş karar sayılmaz.</Text><Group mt="lg" gap="lg"><div><strong>{t.aktifKurallar.length}</strong><Text size="xs" c="dimmed">seçili kural</Text></div><div><strong>0</strong><Text size="xs" c="dimmed">gerçek sistem uygunluk deneyi</Text></div></Group><Button variant="default" mt="lg" onClick={()=>git('tasarimci')}>Taslağı aç</Button><Text size="xs" c="dimmed" mt="lg">{kanit.dosyalar.length} gömülü belge · çevrimdışı okunabilir<br/>Seçili önlem ≠ doğrulanmış çözüm</Text></section></div>
 </Stack>;
}
