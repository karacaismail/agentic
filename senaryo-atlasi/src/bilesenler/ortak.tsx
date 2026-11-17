import { useEffect, useState } from 'react';
import { Badge, Tooltip } from '@mantine/core';
import { kuralBul } from '../veri/kurallar';

// Hash tabanlı sayfa gezinmesi: #/sayfa?anahtar=değer
export function useSayfa(): { sayfa: string; param: URLSearchParams; git: (s: string) => void } {
  const oku = () => {
    const [yol, sorgu] = window.location.hash.replace(/^#\/?/, '').split('?');
    return { sayfa: yol || 'baslangic', param: new URLSearchParams(sorgu ?? '') };
  };
  const [d, setD] = useState(oku);
  useEffect(() => {
    const f = () => { setD(oku()); window.scrollTo({ top: 0, behavior: 'instant' }); };
    window.addEventListener('hashchange', f);
    return () => window.removeEventListener('hashchange', f);
  }, []);
  return { ...d, git: (s: string) => { window.location.hash = `/${s}`; } };
}

export function useListeOdak(secili: string | undefined) {
  useEffect(() => {
    const liste = document.querySelector<HTMLElement>('.research-items');
    const aktif = liste?.querySelector<HTMLElement>('[aria-current="true"]');
    if (!liste || !aktif) return;
    const l = liste.getBoundingClientRect(), a = aktif.getBoundingClientRect();
    if (a.top < l.top || a.bottom > l.bottom) liste.scrollTop += a.top - l.top;
  }, [secili]);
}

export function indir(dosya: string, icerik: string, tur = 'text/plain;charset=utf-8') {
  const url = URL.createObjectURL(new Blob([icerik], { type: tur }));
  const a = document.createElement('a');
  a.href = url; a.download = dosya;
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1500);
}

export function KuralRozeti({ id, aktif, onClick }: { id: string; aktif: boolean; onClick?: () => void }) {
  const k = kuralBul(id);
  return (
    <Tooltip label={k ? `${k.baslik} · ${aktif ? 'açık' : 'kapalı'}` : id} withArrow>
      <Badge variant={aktif ? 'light' : 'outline'} color={aktif ? 'teal' : 'red'} style={{ cursor: onClick ? 'pointer' : undefined }} onClick={onClick} tt="none">
        {aktif ? '✓' : '✗'} {id}
      </Badge>
    </Tooltip>
  );
}

export const SEVIYE_RENK: Record<string, string> = { kritik: 'red', yuksek: 'orange', orta: 'yellow', dusuk: 'green' };
export const SEVIYE_AD: Record<string, string> = { kritik: 'kritik', yuksek: 'yüksek', orta: 'orta', dusuk: 'düşük' };
export const HUKUM: Record<string, { ad: string; renk: string }> = {
  kullan: { ad: 'Kaynak: kullan', renk: 'gray' }, aday: { ad: 'Kaynak: aday', renk: 'gray' }, sinirli: { ad: 'Kaynak: sınırlı rol', renk: 'gray' },
  kullanma: { ad: 'Kaynak: kullanma', renk: 'gray' }, disi: { ad: 'Kaynak: kapsam dışı', renk: 'gray' },
};
