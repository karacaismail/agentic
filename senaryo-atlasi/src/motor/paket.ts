import analiz from '../analiz/bulgular.json';
import {notlariOku} from '../durum/karar-notlari';
import type {Durum} from '../durum/depo';
import {turet} from '../durum/hesap';
import {tumDiyagramlar} from '../diyagram/uretec';
import {KURALLAR} from '../veri/kurallar';
import {CODEX_ROLLERI,SKILLER,MCP_SUNUCULARI} from '../veri/ajanlar';
import {BELGELER} from '../veri/belgeler';
import uyarlama from '../veri/uyarlama-sozlesmesi.json';
import kararModelleri from '../veri/karar-modelleri.json';
import kanit from '../veri/kanitlar.json';
import {simulasyonGecmisi} from './simulasyon';
export function belgeIcerigi(b:typeof BELGELER[number],d:Durum){
 const t=turet(d);
 if(b.tur==='yaml') return `# Tasarım: uygulanmadı; çalıştırılabilir motor konfigürasyonu değildir.\n# Senaryo: ${t.senaryo.ad}\n` + JSON.stringify({schema:'scenario-policy/draft-v1',lifecycle_owner:d.kararlar.durumSahibi,worker:d.kararlar.ajan,decision_engine:d.kararlar.kararModeli,eca:d.kurallar,unknown_effect:'reconcile_before_retry',real_system_qualification:'not_run'},null,2)+'\n';
 if(b.tur==='diğer') return '# Tasarım taslağı: '+t.senaryo.ad+'\n'+b.sablon;
 return `# Tasarım bağlamı\n\nSenaryo: ${t.senaryo.ad}\nYaşam döngüsü sahibi: ${d.kararlar.durumSahibi}\nKodlama çalışanı: ${d.kararlar.ajan}\nTipli karar adayı: ${d.kararlar.kararModeli}\nHedef: Plane → agentic-tdd-development → GitHub CI/CD → alpha → insan\nDurum: taslak; uygulanmadı. Sürüm ve endpoint alanları nitelendirme sırasında doldurulacak.\n\n---\n\n${b.sablon}\n\n## Bu karara bağlı ECA seçimi\n${KURALLAR.map(k=>`- ${k.id} [${d.kurallar[k.id].acik?'seçili':'kapalı'}] ${k.baslik}`).join('\n')}\n`;
}
export function paket(d:Durum){
 const t=turet(d);
 return {format:'senaryo-atlasi/karar-paketi',surum:1,uretildi:new Date().toISOString(),durum:d,
  sinir:'Tasarım ve yerel simülasyon. Kurulum yapılmadı; gerçek sistem uygunluğu kanıtlanmadı.',
  bulguNotlari:notlariOku(),kararDestegi:analiz.briefs,
  eca:KURALLAR.map(k=>({id:k.id,acik:t.aktif(k.id),olay:t.metin(k,'olay'),kosul:t.metin(k,'kosul'),eylem:t.metin(k,'eylem'),parametreler:d.kurallar[k.id].degerler,kaynak:k.kaynak,kanitIdleri:k.onler})),
  uyarlama:uyarlama.component_contracts,kararModeli:kararModelleri.candidates.find(c=>c.id===d.kararlar.kararModeli)??{id:d.kararlar.kararModeli,status:'candidate_only'},
  oncelik:['iptal ve yetki iptali','belirsiz dış etki uzlaştırma','sert bütçe','olaya özel kurtarma'],
  uyarilar:t.uyarilar,acikPlanBosluklari:t.kapsam.acikSorunlar.map(s=>({id:s.id,baslik:s.baslik})),
  roller:CODEX_ROLLERI,skills:SKILLER,mcp:MCP_SUNUCULARI,teknolojiler:t.teknolojiler,
  diyagramlar:tumDiyagramlar(d,t),belgeler:BELGELER.map(b=>({yol:b.yol,icerik:belgeIcerigi(b,d)})),
  kanit:kanit.kayitlar.map(r=>({id:r.id,grup:r.grup,yol:r.kaynak,sha256:r.sha256,pointer:r.pointer})),
  kaynakManifesti:kanit.dosyalar.map(f=>({yol:f.yol,sha256:f.sha256})),
  simulasyonlar:simulasyonGecmisi(d),qualification:'not_run',uygulanmisOnlemSayisi:0,
  acikSorular:['Gerçek repo / alpha hedefi ve proje profili','Araç sürümleri ve adaptör uygunluk deneyleri','Bağımsız oracle ve alan kabul verisi','Ölçülmüş kaynak ve insan çıktı inceleme kapasitesi'],
 };
}
