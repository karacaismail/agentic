import { useState } from 'react';
import analiz from '../analiz/bulgular.json';
const KEY = 'senaryo-atlasi:kanit-notlari:v1';
export type KararNotu = { secenek: string; not: string };
export function notlariDogrula(raw: unknown): Record<string, KararNotu> {
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) throw new Error('Geçerli bir bulgu notu dosyası değil.');
  const sonuc: Record<string, KararNotu> = {};
  for (const [id, value] of Object.entries(raw)) {
    const b = analiz.briefs.find(b => b.id === id);
    const n = value as KararNotu;
    if (!b || !n || typeof n.not !== 'string' || n.not.length > 3000 || typeof n.secenek !== 'string' || (n.secenek !== '' && !b.options.some(o => o.label === n.secenek))) throw new Error('Bulgu kimliği, seçenek veya not boyutu geçersiz.');
    sonuc[id] = { secenek: n.secenek, not: n.not };
  }
  return sonuc;
}
export function notlariKaydet(notlar: Record<string, KararNotu>) { localStorage.setItem(KEY, JSON.stringify(notlar)); }
export function notlariOku(): Record<string, KararNotu> {
  try {
    const raw = JSON.parse(localStorage.getItem(KEY) ?? '{}');
    return Object.fromEntries(analiz.briefs.flatMap(b => {
      const n = raw?.[b.id];
      return n && typeof n.not === 'string' && typeof n.secenek === 'string' && (n.secenek === '' || b.options.some(o => o.label === n.secenek))
        ? [[b.id, { secenek: n.secenek, not: n.not.slice(0, 3000) }]] : [];
    }));
  } catch { return {}; }
}
export function useKararNotlari() {
  const [notlar, setNotlar] = useState(notlariOku);
  const [hata, setHata] = useState('');
  const yukle = (raw: unknown) => {
    const yeni = notlariDogrula(raw);
    notlariKaydet(yeni); setNotlar(yeni); setHata('');
  };
  const yaz = (id: string, not: KararNotu) => {
    const yeni = { ...notlar, [id]: not };
    setNotlar(yeni);
    try { localStorage.setItem(KEY, JSON.stringify(yeni)); setHata(''); }
    catch { setHata('Tarayıcı kaydı yapılamadı. Notlarını JSON olarak indir.'); }
  };
  return { notlar, yaz, yukle, hata };
}
