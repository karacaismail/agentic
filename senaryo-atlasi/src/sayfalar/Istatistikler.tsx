import {useState} from 'react';
import {Alert,Grid,Group,NumberInput,Paper,SimpleGrid,Stack,Text,Title,useComputedColorScheme} from '@mantine/core';
import {GrafikKarti} from '../bilesenler/GrafikKarti';
import {yatayCubuk} from '../grafik/secenekler';
import {grafikTemasi} from '../tema';
import {useTuretilen} from '../durum/kanca';
import {KURALLAR} from '../veri/kurallar';
import kanit from '../veri/kanitlar.json';
import veri from '../veri/uretilen.json';
export function Istatistikler(){
 const g=grafikTemasi(useComputedColorScheme('light')==='dark');const t=useTuretilen();
 const [ajan,setAjan]=useState(2),[saat,setSaat]=useState(8),[gun,setGun]=useState(22),[birim,setBirim]=useState(0);
 const kaynak=['Yerel geçmiş','Dünya vakaları','Mimari inceleme'];const sayilar=kaynak.map(k=>kanit.kayitlar.filter(r=>r.grup===k).length);
 const plan=['Seçili kurallar','Kapalı kurallar','Gerçek sistemde doğrulanmış'];const deger=[t.aktifKurallar.length,t.kapaliKurallar.length,0];
 const gruplar=Object.entries(veri.ihtiyac.alan).map(([k,v])=>[k.replace(/^[A-F]-/,'').replace(/-/g,' '),Number(v)] as const);
 return <Stack><Title order={2}>İstatistikler</Title><Text c="dimmed">ECharts / SVG. Seçili tasarımın sayıları ve araştırma envanterleri ayrı gösterilir.</Text><Alert color="blue">Bunlar olay sıklığı veya araçların hata oranı değildir. Kaynak kümeleri örtüşebilir. Seçilen önlem sayısı güvenlik puanı değildir.</Alert>
 <SimpleGrid cols={{base:2,md:4}}>{[['82','özgün kayıt'],[String(kanit.dosyalar.length),'gömülü belge'],[String(KURALLAR.length),'tasarım kuralı'],['0','runtime doğrulaması']].map(([n,l])=><Paper key={l} withBorder p="md"><Text className="kpi-deger">{n}</Text><Text size="sm" c="dimmed">{l}</Text></Paper>)}</SimpleGrid>
 <Grid><Grid.Col span={{base:12,md:6}}><GrafikKarti baslik="Özgün kayıtların kaynak kümeleri" kaynak="Kanıt defteri / dosya SHA-256 manifesti" aciklama="18 + 36 + 28; aynı olaya ilişkin birden çok kayıt olabilir." secenek={yatayCubuk(g,kaynak,sayilar)} yukseklik={230} tablo={{basliklar:['Kaynak','Kayıt'],satirlar:kaynak.map((k,i)=>[k,sayilar[i]])}}/></Grid.Col><Grid.Col span={{base:12,md:6}}><GrafikKarti baslik="Seçili tasarımın kural durumu" kaynak="Senaryo ayarları" aciklama="Değişikliklerin bu grafiğe anında yansır." secenek={yatayCubuk(g,plan,deger)} yukseklik={230} tablo={{basliklar:['Durum','Kural'],satirlar:plan.map((k,i)=>[k,deger[i]])}}/></Grid.Col></Grid>
 <GrafikKarti baslik="Tarihî ihtiyaç envanteri" kaynak="coding / ihtiyac-haritasi / 00-indeks.json" aciklama="Bu klasörün ihtiyaç sayımıdır; coding 2 envanteriyle toplanmaz veya tekilleştirilmiş sayılmaz." secenek={yatayCubuk(g,gruplar.map(x=>x[0]),gruplar.map(x=>x[1]),{etiketGenislik:180})} yukseklik={280} tablo={{basliklar:['Alan','Kayıt'],satirlar:gruplar.map(x=>[x[0],x[1]])}}/>
 <Paper withBorder p="lg"><Title order={3}>Kapasite ve maliyet varsayımı</Title><Text size="sm" c="dimmed" mb="md">Birim maliyeti kendi ölçümünle gir. 128 GB RAM’den ajan veya insan sayısı hesaplanamaz; CPU, I/O, eşzamanlı build, model kotası ve inceleme kuyruğu da ölçülmeli.</Text><SimpleGrid cols={{base:2,md:4}}><NumberInput label="Eşzamanlı işçi" value={ajan} min={1} max={1000} onChange={v=>setAjan(Number(v)||1)}/><NumberInput label="Saat / gün" value={saat} min={1} max={24} onChange={v=>setSaat(Number(v)||1)}/><NumberInput label="Gün / ay" value={gun} min={1} max={31} onChange={v=>setGun(Number(v)||1)}/><NumberInput label="Ölçülen $ / işçi-saat" value={birim} min={0} max={10000} onChange={v=>setBirim(Number(v)||0)}/></SimpleGrid><Group mt="lg"><Text fw={700} size="xl">{birim>0?`${(ajan*saat*gun*birim).toLocaleString('tr-TR')} $ / ay`:'Birim maliyet girilmedi'}</Text><Text c="dimmed" size="sm">Varsayım hesabı · insan ve altyapı hariç</Text></Group></Paper></Stack>
}
