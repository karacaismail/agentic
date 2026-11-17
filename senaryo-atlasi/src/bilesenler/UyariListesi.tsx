import { Alert, Stack, Text } from '@mantine/core';
import { IconAlertOctagon, IconAlertTriangle, IconInfoCircle } from '@tabler/icons-react';
import type { Uyari } from '../durum/hesap';

const STIL = {
  kritik: { renk: 'red', ikon: IconAlertOctagon, ad: 'Kritik' },
  uyari: { renk: 'yellow', ikon: IconAlertTriangle, ad: 'Uyarı' },
  bilgi: { renk: 'blue', ikon: IconInfoCircle, ad: 'Bilgi' },
};

export function UyariListesi({ uyarilar, enFazla }: { uyarilar: Uyari[]; enFazla?: number }) {
  const liste = enFazla ? uyarilar.slice(0, enFazla) : uyarilar;
  if (!liste.length) return <Text size="sm" c="dimmed">Uyarı yok.</Text>;
  return (
    <Stack gap={6}>
      {liste.map((u, i) => {
        const s = STIL[u.seviye];
        return (
          <Alert key={i} color={s.renk} variant="light" icon={<s.ikon size={16} />} p="xs" title={<Text size="xs" fw={700}>{s.ad}</Text>}>
            <Text size="sm">{u.metin}</Text>
            {u.kaynak && <Text size="xs" c="dimmed" mt={2}>Kaynak: {u.kaynak}</Text>}
          </Alert>
        );
      })}
    </Stack>
  );
}
