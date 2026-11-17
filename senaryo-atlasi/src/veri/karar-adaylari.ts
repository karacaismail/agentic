import veri from './karar-modelleri.json';
import type {KararSecenek} from './tipler';
export const KARAR_ADAYLARI:KararSecenek[] = veri.candidates.map(c=>({deger:c.id,etiket:c.ad,aciklama:c.role,uyari:c.status.includes('unverified')?'Kimliği/yeteneği doğrulanmamış aday. Seçmek adaptör uygunluğu anlamına gelmez.':'Birincil kaynak incelendi; bu görev verisinde hız, doğruluk ve kalibrasyon ölçülmedi. Güvenlik ve kabul kapılarını geçersiz kılamaz.'}));
