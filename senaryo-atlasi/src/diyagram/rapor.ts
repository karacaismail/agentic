import type {Durum} from '../durum/depo';
import type {Turetilen} from '../durum/hesap';
import type {Diyagram} from './uretec';
import {AKIS_SIRASI,asamaBul} from '../veri/asamalar';
import {KURALLAR} from '../veri/kurallar';
const text=(s:string)=>s.replace(/["<>\[\]{}|`]/g,' ').replace(/\n/g,' ');
export function raporDiyagramlari(d:Durum,t:Turetilen):Diyagram[]{
 const out:Diyagram[]=[{id:'pdf-overview',baslik:'Teslim zinciri',aciklama:'Seçili tasarım. Bir sonraki sayfalarda aşamalar ve koşullar açılır.',notlar:[],kod:'flowchart TB\nP["Plane: görev formu / In Progress"] --> A["Agentic TDD: araştırma / plan / RED / GREEN"] --> G["GitHub: bağımsız CI / seri bütünleştirme"] --> D["Alpha: artefakt ve sürüm doğrulama"] --> H["İnsan: yolculuk testi / kabul veya ret"]\nH -->|"ret: kanıtlı yeni görev"| P'}];
 for(let i=0;i<AKIS_SIRASI.length;i+=3){
  const ids=AKIS_SIRASI.slice(i,i+3);const lines=['flowchart TB'];
  for(const id of ids){const a=asamaBul(id);const k=d.kumeler.find(x=>x.id===t.kumeOf(id));
   lines.push(`${id}["${text(a.ad)}<br/>${text(t.asamaTeknoloji(id))}<br/>${text(k?'Küme: '+k.ad:'')}<br/>${text('Ajan: '+(a.ajanlar.join(', ')||'yok'))}<br/>${text('Skill: '+(a.skill.join(', ')||'yok'))}<br/>${text('MCP: '+(a.mcp.join(', ')||'yok'))}<br/>${text('Seçili ECA: '+KURALLAR.filter(r=>r.asama===id&&t.aktif(r.id)).map(r=>r.id).join(', '))}"]`);
  }
  for(let j=1;j<ids.length;j++)lines.push(`${ids[j-1]} -->|"${text(asamaBul(ids[j-1]).cikti)}"| ${ids[j]}`);
  out.push({id:`pdf-flow-${i}`,baslik:`Aşamalar ${i+1}–${i+ids.length}`,aciklama:ids.map(a=>asamaBul(a).ad).join(' → '),kod:lines.join('\n'),notlar:[]});
 }
 out.push({id:'pdf-pool',baslik:'Yetenek edinme ve göreve dönme',aciklama:'Skill / MCP / agent değişimi üretim yetkisi vermez; eval ve izin kapısı gerekir.',notlar:[],kod:'flowchart TB\nA["Görevde eksik yetenek"] --> B["Talep: sahip / süre / bütçe / görev revisionu"] --> C["Dış keşif: yalnız aday"] --> D["Karantina: lisans / kaynak / izin / sandbox"] --> E{"Eval ve sözleşme geçti mi?"}\nE -->|"evet"| F["Sürümlü sicil / digest / minimum yetki"] --> G["Checkpoint üzerinden aynı göreve dön"]\nE -->|"hayır"| H["Gerekçeli ret / başka aday / görünür blokaj"]'});
 return out;
}
