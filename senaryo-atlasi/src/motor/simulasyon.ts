import type {Durum} from '../durum/depo';
export const OLAYLAR = [
 ['oom','İşçi öldü / bellek şüphesi'],['stall','Ajan ilerlemiyor'],['duplicate','Aynı görev yeniden geldi'],['effect','Dağıtım sonucu bilinmiyor'],['stale','Eski CI geç tamamlandı'],['reject','İnsan alpha çıktısını reddetti'],['skill','Eksik skill / MCP istendi'],['budget','Yeni deneme bütçeyi aşacak'],['cancel','Görev iptal edildi'],['ci','CI tamamlandı'],
] as const;
export type Olay = typeof OLAYLAR[number][0];
export interface Girdi {olay:Olay;oom:boolean;eskiIsci:boolean;uzunTest:boolean;tekrar:boolean;eskiNesil:boolean;acTam:boolean;zorunluKapilarGecti:boolean;onayliSkill:boolean;bellek:number;bosBellek:number;ilerlemesiz:number;maliyet:number;ekMaliyet:number;sure:number;deneme:number;infraDeneme:number}
export const ilkGirdi:Girdi={olay:'oom',oom:true,eskiIsci:false,uzunTest:false,tekrar:true,eskiNesil:true,acTam:true,zorunluKapilarGecti:true,onayliSkill:false,bellek:1,bosBellek:8,ilerlemesiz:25,maliyet:4,ekMaliyet:1,sure:40,deneme:1,infraDeneme:0};
export interface Iz {kural:string;kosul:string;sonuc:string}
export interface Sonuc {kod:string;eylem:string;iz:Iz[];eksik:string[];durum:'tasarim_simulasyonu';canliDogrulama:false}
export function simule(d:Durum,g:Girdi):Sonuc {
 const iz:Iz[]=[]; const eksik:string[]=[];
 const ac=(id:string)=>!!d.kurallar[id]?.acik;
 const say=(id:string,k:string)=>Number(d.kurallar[id]?.degerler[k]);
 const bitir=(kod:string,eylem:string):Sonuc=>({kod,eylem,iz,eksik,durum:'tasarim_simulasyonu',canliDogrulama:false});
 const gerekli=(ids:string[])=>{for(const id of ids){const ok=ac(id);iz.push({kural:id,kosul:'Seçili önlem tasarımda açık mı?',sonuc:ok?'açık':'kapalı'});if(!ok)eksik.push(id);}return eksik.length===0;};
 // Priority 0: revoke/cancel always precedes recovery; fail closed in the simulator.
 if(g.olay==='cancel') {if(!gerekli(['R19','R07']))return bitir('GAP','İptal ve nesil sözleşmesi eksik; çalışana yeni iş verme.');return bitir('REVOKE','Nesli iptal et → yazma yetkisini kes → çocuk süreçleri durdur → son kanıtı sakla.');}
 // Priority 1: ambiguous effects are reconciled even if spend budget expired; never blindly replay.
 if(g.olay==='effect') {if(!gerekli(['R37','R36']))return bitir('GAP','Belirsiz etki rotası eksik. Yeni dağıtımı durdur; durum sorgusu için kontrollü operasyon gerekir.');return bitir('RECONCILE','Niyet/işlem kimliğiyle remote sürümü sorgula. Makbuz varsa kaydet; kanıt yoksa unknown_effect. Kör yeniden dağıtım yok.');}
 const tasarimTavani = say('R17','tavan');
 const asim = g.maliyet+g.ekMaliyet>tasarimTavani || g.sure>=say('R17','dakika') || g.deneme>=say('R17','deneme');
 iz.push({kural:'R17 / R59',kosul:`Tahmini toplam ${g.maliyet+g.ekMaliyet} $ / tavan ${tasarimTavani} $; süre ${g.sure} dk; deneme ${g.deneme}`,sonuc:asim?'sınır aşılıyor':'sınır içinde'});
 if(!gerekli(['R17']))return bitir('GAP','Sert bütçe kuralı kapalı. Otomatik yeniden deneme güvenli varsayılamaz.');
 if(asim)return bitir('STOP_BUDGET','Yeni ücretli iş başlatma. Durumu ve kısmi kanıtı kaydet; sayaçlar ajan değişince sıfırlanmaz.');
 switch(g.olay){
 case 'oom':{
  if(!gerekli(['R46','R48','R19']))return bitir('GAP','Hata sınıflandırma, OOM veya iptal önlemi eksik.');
  iz.push({kural:'R48',kosul:'cgroup OOM sayacı artmış mı?',sonuc:g.oom?'kanıt var':'kanıt yok'});
  if(!g.oom)return bitir('DIAGNOSE','Exit 137 tek başına OOM değildir. Sinyal, host ve süreç loglarıyla nedeni ayır; RAM otomatik artırılmaz.');
  if(g.eskiIsci)return bitir('FENCE','Önce eski çalışanın yazma yetkisini ve lease neslini kes. İkinci işçi şimdi başlatılmaz.');
  const merdiven=String(d.kurallar.R48.degerler.profil).split('-').map(Number);
  const next=merdiven.find(x=>x>g.bellek);
  if(!next)return bitir('RESHAPE','Kaynak profili tavanı. Testleri/granüler işi yeniden böl, parent AC yükümlülüklerini koru; sınırsız RAM artırma yok.');
  if(next>g.bosBellek)return bitir('WAIT_CAPACITY','Kaynak rezervasyonu yok. Sahipli ve süreli kapasite beklemesine al; diğer işi öldürme.');
  if(g.infraDeneme>=say('R47','tekrar'))return bitir('STOP_RETRY','Altyapı tekrar sınırı doldu. Kanıtlı problem çıktısı üret; yeniden deneme sayacını sıfırlama.');
  if(!gerekli(['R47','R62','R59','R76']))return bitir('GAP','Kaynak/bütçe rezervasyonu veya sınırlı yeniden deneme seçilmemiş.');
  return bitir('RESIZE',`${next} GiB rezervasyonu → yeni nesil → temiz checkpoint → sınırlı yeniden deneme. Test grubu: ${say('R48','grup')}. Gerçek maliyet tüm denemeleri içerir.`);
 }
 case 'stall':
  if(!gerekli(['R18','R49']))return bitir('GAP','İlerleme gözetimi veya sahipli bekleme eksik.');
  if(g.uzunTest)return bitir('OBSERVE_TEST','Uzun test telemetrisi ilerliyor. Yalnız commit sessizliği nedeniyle öldürme; test zaman aşımı ve bütçe izle.');
  if(g.ilerlemesiz<say('R18','dakika'))return bitir('OBSERVE','İlerlemesiz süre seçili eşiğin altında; gözlem sürer.');
  return bitir('UNBLOCK','Tıkanıklık sınıfını belirle → strateji değiştir veya sınırlı alt iş çıkar → devir manifestiyle devam; aynı komutu sonsuz tekrarlama.');
 case 'duplicate':
  if(!gerekli(['R03','R07']))return bitir('GAP','Yinelenen kabul / görev nesli önlemi eksik.');
  return g.tekrar?bitir('DEDUP','Mevcut görev+nesil makbuzunu döndür; ikinci ücretli koşu oluşturma.'):bitir('ADMIT','Yetkili girdi sürümünü sabitle; tekil görev+nesil kimliğiyle kabul et.');
 case 'stale':
  if(!gerekli(['R24','R35','R36']))return bitir('GAP','Son aday veya sürüm/nesil kapısı eksik.');
  return g.eskiNesil?bitir('REJECT_STALE','CI kanıtı eski aday/nesle ait. Alpha’yı geriye taşıma; güncel adayı yeniden doğrula.'):bitir('CANDIDATE','Sürüm eşleşiyor; zorunlu CI, artefakt ve kabul kapsamını ayrıca değerlendir.');
 case 'reject':
  if(!gerekli(['R43','R44']))return bitir('GAP','İnsan reddini kalıcılaştırma veya yeni iş rotası eksik.');
  return bitir('REOPEN','İnsan reddini teslim kimliğine bağla → kanıtlı yeni issue → yeni nesil. Veri göçü varsa kör rollback yapma; telafi politikasını kullan.');
 case 'skill':
  if(!gerekli(['R66','R70','R75']))return bitir('GAP','Karantina/sicil veya eval kuralı eksik; pazar adayını canlı göreve yükleme.');
  return g.onayliSkill?bitir('PIN','Yetki kapsamı ve digest ile nitelendirilmiş yeteneği sabitle; görevi checkpoint üzerinden sürdür.'):bitir('QUALIFY','Eksik yetenek talebi → sahipli bekleme → keşif → karantina → lisans/izin/sandbox → eval → sürümlü sicil → görevde devam.');
 case 'ci':
  if(!gerekli(['R21','R22','R23','R24','R28','R31','R78']))return bitir('GAP','Zorunlu CI/kapsam/bütünleştirme kapılarından biri kapalı.');
  if(!(d.kurallar.R21.degerler.kapilar as string[])?.length)return bitir('GAP','CI kapısı seçilmedi; boş küme başarı değildir.');
  return !g.acTam||!g.zorunluKapilarGecti?bitir('REWORK','Eksik AC veya başarısız/bitmemiş zorunlu kapı var. Bütünleştirme yapılmaz.'):bitir('QUEUE','Tam aday SHA’sı için kanıt manifestini doğrula → seri bütünleştirme → artefakt/sürüm kapısı → alpha.');
 default: return bitir('WITHIN_BUDGET','Bu girdiler bütçe içinde. Diğer güvenlik ve teslim kapıları ayrıca uygulanır.');
 }
}
const gecmis=new Map<string,{girdi:Girdi;sonuc:Sonuc;tarih:string}[]>();
export function kaydet(d:Durum,g:Girdi,s:Sonuc){const key=JSON.stringify(d);gecmis.set(key,[...(gecmis.get(key)??[]),{girdi:{...g},sonuc:s,tarih:new Date().toISOString()}].slice(-30));}
export const simulasyonGecmisi=(d:Durum)=>gecmis.get(JSON.stringify(d))??[];
