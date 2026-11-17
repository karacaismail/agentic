import { useMemo, useState } from 'react';
import { Anchor, Badge, Chip, Group, Paper, Select, Stack, Table, Text, TextInput, Title, useComputedColorScheme } from '@mantine/core';
import { IconSearch } from '@tabler/icons-react';
import { useTuretilen } from '../durum/kanca';
import { HUKUM, SEVIYE_AD, SEVIYE_RENK, useSayfa } from '../bilesenler/ortak';
import { GrafikKarti } from '../bilesenler/GrafikKarti';
import { yatayCubuk } from '../grafik/secenekler';
import { DURUM_RENK, grafikTemasi } from '../tema';
import { CERCEVELER } from '../veri/teknolojiler';
import veri from '../veri/uretilen.json';

const SEVIYE_GRAFIK: Record<string, string> = { kritik: DURUM_RENK.kritik, yuksek: DURUM_RENK.ciddi, orta: DURUM_RENK.uyari, dusuk: DURUM_RENK.iyi };

export function Teknolojiler() {
  const t = useTuretilen();
  const { param } = useSayfa();
  const koyu = useComputedColorScheme('light') === 'dark';
  const g = grafikTemasi(koyu);
  const [ara, setAra] = useState(param.get('ad') ?? '');
  const [kategori, setKategori] = useState<string | null>(null);
  const [hukumler, setHukumler] = useState<string[]>(['kullan', 'aday', 'sinirli', 'kullanma', 'disi']);
  const riskli = t.teknolojiler.filter((x) => x.riskPuani !== undefined).sort((a, b) => (b.riskPuani ?? 0) - (a.riskPuani ?? 0));
  const katalog = useMemo(() => {
    const q = ara.trim().toLocaleLowerCase('tr-TR');
    return veri.katalog.araclar.filter((a) => (!kategori || a.kategori === kategori) && hukumler.includes(a.hukum) &&
      (!q || `${a.ad} ${a.ne} ${a.uyum} ${a.dikkat}`.toLocaleLowerCase('tr-TR').includes(q)));
  }, [ara, kategori, hukumler]);
  const katAd = Object.fromEntries(veri.katalog.kategoriler.map((k) => [k.key, k.label]));

  return (
    <Stack gap="md">
      <div>
        <Title order={2}>Teknolojiler</Title>
        <Text c="dimmed" size="sm">Bu hazır senaryodaki örnek adaylar ve tarihî 127 araçlık katalog. Eski risk puanları istatistiksel hata oranı veya güncel ürün tavsiyesi değildir; seçilen sürüm yeniden nitelendirilmelidir.</Text>
      </div>
      <Paper withBorder p="md" radius="md">
        <Title order={4} mb="xs">Bu senaryonun yığını</Title>
        <Table.ScrollContainer minWidth={640}>
          <Table striped fz="sm">
            <Table.Thead><Table.Tr><Table.Th>Teknoloji</Table.Th><Table.Th>Rolü</Table.Th><Table.Th>Tarihî kaynak hükmü</Table.Th><Table.Th>Tarihî risk puanı</Table.Th></Table.Tr></Table.Thead>
            <Table.Tbody>
              {t.teknolojiler.map((x) => (
                <Table.Tr key={x.ad}>
                  <Table.Td fw={600}>{x.ad}</Table.Td>
                  <Table.Td>{x.rol}</Table.Td>
                  <Table.Td>{x.hukum ? <Badge variant="light" color={HUKUM[x.hukum]?.renk}>{HUKUM[x.hukum]?.ad}</Badge> : <Text size="xs" c="dimmed">katalogda yok</Text>}</Table.Td>
                  <Table.Td>{x.riskPuani !== undefined ? <Badge variant="light" color={SEVIYE_RENK[x.riskSeviye ?? 'orta']}>{x.riskPuani} · {SEVIYE_AD[x.riskSeviye ?? 'orta']}</Badge> : <Text size="xs" c="dimmed">—</Text>}</Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </Table.ScrollContainer>
        <Text size="xs" c="dimmed" mt="xs">Tarihî risk puanı 0–100; risk haritasının yöntemiyle hesaplandı (güvenlik geçmişi, bakım, lisans, sahiplik…). Yüksek puan "kullanma" demek değildir; önlem gerektirir.</Text>
      </Paper>
      {riskli.length > 0 && (
        <GrafikKarti baslik="Arşivdeki risk puanları · ölçülmüş hata oranı değil" aciklama="Renk risk seviyesini gösterir; değer çubuğun ucunda yazılı." kaynak="risk-haritasi/00-risk-haritasi.json"
          secenek={yatayCubuk(g, riskli.map((x) => x.ad), riskli.map((x) => x.riskPuani ?? 0), { renkler: riskli.map((x) => SEVIYE_GRAFIK[x.riskSeviye ?? 'orta']) })}
          yukseklik={Math.max(180, riskli.length * 26)}
          tablo={{ basliklar: ['Teknoloji', 'Puan', 'Seviye'], satirlar: riskli.map((x) => [x.ad, x.riskPuani ?? '', SEVIYE_AD[x.riskSeviye ?? ''] ?? '']) }} />
      )}
      <Paper withBorder p="md" radius="md">
        <Title order={4} mb="xs">Çerçeveler ve protokoller</Title>
        <Stack gap={4}>{CERCEVELER.map((c) => <Text key={c.ad} size="sm"><b>{c.ad}:</b> {c.rol}</Text>)}</Stack>
      </Paper>
      <Paper withBorder p="md" radius="md">
        <Title order={4}>Senin araç kataloğun (127)</Title>
        <Text size="sm" c="dimmed" mb="sm">agentic-stack-docs kataloğundan; hükümler eski araştırmanın yazarına aittir; senin kararların olarak alınmaz.</Text>
        <Group gap="sm" mb="sm">
          <TextInput size="xs" w={240} placeholder="Ara" leftSection={<IconSearch size={14} />} value={ara} onChange={(e) => setAra(e.currentTarget.value)} />
          <Select size="xs" w={220} placeholder="Kategori" clearable value={kategori} onChange={setKategori} data={veri.katalog.kategoriler.map((k) => ({ value: k.key, label: k.label }))} />
          <Chip.Group multiple value={hukumler} onChange={setHukumler}>
            <Group gap={4}>{Object.entries(HUKUM).map(([k, h]) => <Chip key={k} value={k} size="xs" color={h.renk}>{h.ad}</Chip>)}</Group>
          </Chip.Group>
          <Text size="xs" c="dimmed">{katalog.length} araç</Text>
        </Group>
        <Table.ScrollContainer minWidth={900}>
          <Table fz="xs" verticalSpacing={6} striped>
            <Table.Thead><Table.Tr><Table.Th>Araç</Table.Th><Table.Th>Kategori</Table.Th><Table.Th>Hüküm</Table.Th><Table.Th>Bu hatta yeri</Table.Th><Table.Th>Dikkat</Table.Th><Table.Th>Risk</Table.Th></Table.Tr></Table.Thead>
            <Table.Tbody>
              {katalog.map((a) => (
                <Table.Tr key={a.ad}>
                  <Table.Td fw={600}>{a.url ? <Anchor href={a.url} target="_blank" rel="noreferrer" size="xs">{a.ad}</Anchor> : a.ad}</Table.Td>
                  <Table.Td>{katAd[a.kategori] ?? a.kategori}</Table.Td>
                  <Table.Td><Badge size="xs" variant="light" color={HUKUM[a.hukum]?.renk}>{HUKUM[a.hukum]?.ad}</Badge></Table.Td>
                  <Table.Td>{a.uyum || a.ne}</Table.Td>
                  <Table.Td>{a.dikkat}</Table.Td>
                  <Table.Td>{a.risk ? <Badge size="xs" variant="light" color={SEVIYE_RENK[a.risk.seviye]}>{a.risk.puan}</Badge> : '—'}</Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </Table.ScrollContainer>
      </Paper>
    </Stack>
  );
}
