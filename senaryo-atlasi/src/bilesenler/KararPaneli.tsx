import { Badge, Checkbox, Group, Paper, Radio, SimpleGrid, Stack, Text } from '@mantine/core';
import { KARARLAR } from '../veri/kararlar';
import { useDurum } from '../durum/depo';
import { useTuretilen } from '../durum/kanca';

export function KararPaneli() {
  const { durum, gonder } = useDurum();
  const t = useTuretilen();
  return (
    <Stack gap="sm">
      <Text size="sm" c="dimmed">Kararlar diyagramdaki teknoloji etiketlerini ve uyarıları değiştirir. Kırmızı ⚠ işareti, o seçeneğin araştırmada bulunan riskini gösterir.</Text>
      <SimpleGrid cols={{ base: 1, lg: 2 }} spacing="sm">
        {KARARLAR.filter((k) => k.id !== 'gorunum').map((k) => {
          const degisti = t.degisenKararlar.includes(k.id);
          return (
            <Paper key={k.id} withBorder p="sm" radius="md">
              <Group justify="space-between" wrap="nowrap">
                <Text fw={650}>{k.baslik}</Text>
                {degisti && <Badge size="xs" color="grape" variant="light">senaryodan farklı</Badge>}
              </Group>
              <Text size="sm" c="dimmed" mb="xs">{k.soru}</Text>
              {k.tur === 'radyo' ? (
                <Radio.Group value={String(durum.kararlar[k.id])} onChange={(v) => gonder({ tur: 'karar', id: k.id, deger: v })}>
                  <Stack gap={8}>
                    {k.secenekler.map((s) => (
                      <Radio key={s.deger} value={s.deger} label={s.etiket}
                        description={(s.aciklama || s.uyari) ? (
                          <>
                            {s.aciklama}
                            {s.uyari && <Text component="span" size="xs" c="red.7" display="block">⚠ {s.uyari}</Text>}
                          </>
                        ) : undefined} />
                    ))}
                  </Stack>
                </Radio.Group>
              ) : (
                <Checkbox.Group value={(durum.kararlar[k.id] as string[]) ?? []} onChange={(v) => gonder({ tur: 'karar', id: k.id, deger: v })}>
                  <Group gap="md">{k.secenekler.map((s) => <Checkbox key={s.deger} value={s.deger} label={s.etiket} />)}</Group>
                </Checkbox.Group>
              )}
              {k.kaynak.length > 0 && <Text size="xs" c="dimmed" mt="xs">Kaynak: {k.kaynak.join(' · ')}</Text>}
            </Paper>
          );
        })}
      </SimpleGrid>
    </Stack>
  );
}
