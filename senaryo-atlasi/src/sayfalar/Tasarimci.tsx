import { useMemo, useState } from 'react';
import { Alert, Badge, Button, FileButton, Grid, Group, Paper, SegmentedControl, SimpleGrid, Stack, Tabs, Text, Title, Tooltip } from '@mantine/core';
import { IconArrowBackUp, IconDownload, IconFileTypePdf, IconRefresh, IconSitemap, IconUpload } from '@tabler/icons-react';
import { paket } from '../motor/paket';
import { notlariDogrula, notlariKaydet } from '../durum/karar-notlari';
import { SENARYOLAR } from '../veri/senaryolar';
import { useDurum, durumGecerliMi, type Durum } from '../durum/depo';
import { useTuretilen } from '../durum/kanca';
import { genelDiyagram } from '../diyagram/uretec';
import { MermaidGorunum } from '../diyagram/MermaidGorunum';
import { KararPaneli } from '../bilesenler/KararPaneli';
import { KuralPaneli } from '../bilesenler/KuralPaneli';
import { KumePaneli } from '../bilesenler/KumePaneli';
import { UyariListesi } from '../bilesenler/UyariListesi';
import { indir, useSayfa } from '../bilesenler/ortak';
import type { Faz } from '../veri/tipler';

function CanliOzet() {
  const { durum } = useDurum();
  const t = useTuretilen();
  const { git } = useSayfa();
  const genel = useMemo(() => genelDiyagram(durum, t), [durum, t]);
  const kritik = t.uyarilar.filter((u) => u.seviye === 'kritik').length;
  return (
    <Stack gap="sm" style={{ position: 'sticky', top: 74 }}>
      <Paper withBorder p="md" radius="md">
        <Text className="eyebrow">TASLAKTAKİ BAĞLANTILAR</Text>
        <Text fw={650} mt="xs">{t.aktifKurallar.length} seçili kural · {t.kapaliKurallar.length} kapalı</Text>
        <Text size="sm" c="dimmed" mt="sm">{t.kapsam.toplam} sorun kaydının {t.kapsam.kapsanan}'i seçili önlem veya kararlarla eşlenmiş. Bu bir başarı oranı değildir.</Text>
        <Text size="sm" mt="sm">Gerçek sistem uygunluk deneyi: 0</Text>
        <Button size="compact-sm" variant="subtle" px={0} mt="sm" onClick={()=>git('sorunlar?durum=acik')}>{t.kapsam.acikSorunlar.length} eşlenmemiş kaydı gör →</Button>
      </Paper>
      <Paper withBorder p="md" radius="md">
        <Group justify="space-between" mb="xs">
          <Text fw={650}>Uyarılar</Text>
          <Group gap={4}>{kritik > 0 && <Badge color="red">{kritik} kritik</Badge>}<Badge variant="light">{t.uyarilar.length}</Badge></Group>
        </Group>
        <UyariListesi uyarilar={t.uyarilar} enFazla={4} />
        {t.uyarilar.length > 4 && <Button size="compact-xs" variant="subtle" mt={6} onClick={() => git('tasarimci?sekme=uyarilar')}>Tümünü gör</Button>}
      </Paper>
      <Paper withBorder p="sm" radius="md">
        <Group justify="space-between" mb="xs">
          <Text fw={650}>{genel.baslik}</Text>
          <Button size="compact-xs" variant="light" leftSection={<IconSitemap size={14} />} onClick={() => git('diyagramlar')}>Bütün diyagramlar</Button>
        </Group>
        <MermaidGorunum kod={genel.kod} />
      </Paper>
    </Stack>
  );
}

export function Tasarimci() {
  const { durum, gonder } = useDurum();
  const t = useTuretilen();
  const { param, git } = useSayfa();
  const sekme = param.get('sekme') ?? 'kararlar';
  const hedefKural = param.get('kural');
  const [onceki, setOnceki] = useState<Durum | null>(null);
  const [yuklemeHatasi, setYuklemeHatasi] = useState<string | null>(null);

  const senaryoSec = (id: string) => {
    if (id === durum.senaryoId) return;
    if (t.degisenKararlar.length + t.degisenKurallar.length > 0) setOnceki(durum); else setOnceki(null);
    gonder({ tur: 'senaryo', id });
  };
  const jsonIndir = () => indir(`senaryo-kararlari-${durum.senaryoId}.json`, JSON.stringify(paket(durum), null, 2), 'application/json');
  const jsonYukle = async (f: File | null) => {
    if (!f) return;
    try {
      if (f.size > 2_000_000) throw new Error('Karar dosyası en fazla 2 MB olabilir.');
      const raw = JSON.parse(await f.text());
      const d = raw.durum ?? raw;
      if (!durumGecerliMi(d)) throw new Error('Dosya bu merkezin karar dosyası değil.');
      if (raw.bulguNotlari !== undefined) notlariKaydet(notlariDogrula(raw.bulguNotlari));
      gonder({ tur: 'yukle', durum: d });
      setYuklemeHatasi(null);
    } catch (e) { setYuklemeHatasi(e instanceof Error ? e.message : String(e)); }
  };

  return (
    <Stack gap="md">
      <Group justify="space-between" align="flex-end">
        <div>
          <Title order={2}>Senaryo tasarımcısı</Title>
          <Text c="dimmed" size="sm">Hazır senaryolar örnek ayarlardır; verilmiş karar değildir. Koşulları değiştirip kendi taslağını oluşturabilirsin.</Text>
        </div>
        <Group gap="xs">
          <FileButton onChange={jsonYukle} accept="application/json">{(p) => <Button {...p} size="xs" variant="default" leftSection={<IconUpload size={14} />}>Karar dosyası yükle</Button>}</FileButton>
          <Button size="xs" variant="default" leftSection={<IconDownload size={14} />} onClick={jsonIndir}>Kararları indir (JSON)</Button>
          <Tooltip label="Bu senaryonun hazır ayarlarına dön">
            <Button size="xs" variant="default" leftSection={<IconRefresh size={14} />} onClick={() => { setOnceki(durum); gonder({ tur: 'sifirla' }); }}>Sıfırla</Button>
          </Tooltip>
          <Button size="xs" leftSection={<IconFileTypePdf size={14} />} onClick={() => git('rapor?yazdir=1')}>PDF</Button>
        </Group>
      </Group>

      {onceki && (
        <Alert color="indigo" variant="light" withCloseButton onClose={() => setOnceki(null)} title="Ayarlar değişti">
          <Group justify="space-between">
            <Text size="sm">Önceki ayarların saklandı.</Text>
            <Button size="xs" variant="light" leftSection={<IconArrowBackUp size={14} />} onClick={() => { gonder({ tur: 'yukle', durum: onceki }); setOnceki(null); }}>Önceki ayarlara dön</Button>
          </Group>
        </Alert>
      )}
      {yuklemeHatasi && <Alert color="red" withCloseButton onClose={() => setYuklemeHatasi(null)}>{yuklemeHatasi}</Alert>}

      <SimpleGrid cols={{ base: 1, sm: 2, lg: 4 }} spacing="sm">
        {SENARYOLAR.map((s) => (
          <Paper key={s.id} withBorder p="sm" radius="md" className={`senaryo-karti${s.id === durum.senaryoId ? ' secili' : ''}`}
            onClick={() => senaryoSec(s.id)} role="button" tabIndex={0} aria-pressed={s.id === durum.senaryoId}
            onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); senaryoSec(s.id); } }}>
            <Group justify="space-between" wrap="nowrap" mb={4}>
              <Badge size="xs" variant={s.id === durum.senaryoId ? 'filled' : 'light'}>{s.kisa}</Badge>
              <Badge size="xs" variant="outline" color="gray">Faz {s.hedefFaz}{s.kumeler ? ` · ${s.kumeler.length} küme` : ''}</Badge>
            </Group>
            <Text fw={650} size="sm">{s.ad}</Text>
            <Text size="xs" c="dimmed" lineClamp={3}>{s.ozet}</Text>
          </Paper>
        ))}
      </SimpleGrid>

      <Paper withBorder p="sm" radius="md">
        <Group justify="space-between" wrap="wrap" gap="sm">
          <div>
            <Text size="sm"><b>{t.senaryo.ad}.</b> {t.senaryo.neZaman}</Text>
          </div>
          <Group gap="xs">
            <Text size="sm" fw={600}>Hedef faz</Text>
            <SegmentedControl size="xs" value={String(durum.hedefFaz)} onChange={(v) => gonder({ tur: 'faz', faz: Number(v) as Faz })}
              data={[{ label: 'Faz 0', value: '0' }, { label: 'Faz 1', value: '1' }, { label: 'Faz 2', value: '2' }, { label: 'Faz 3', value: '3' }]} />
            <Tooltip label="Faz yalnız hedef olgunluk etiketidir; seçtiğin kurallar korunur" multiline w={220}><Badge variant="light">{t.aktifKurallar.length} kural açık</Badge></Tooltip>
          </Group>
        </Group>
      </Paper>

      <Grid gutter="md">
        <Grid.Col span={{ base: 12, lg: 7 }}>
          <Tabs value={sekme} onChange={(v) => git(`tasarimci?sekme=${v}`)} keepMounted={false}>
            <Tabs.List mb="sm">
              <Tabs.Tab value="kararlar">Kararlar{t.degisenKararlar.length ? ` (${t.degisenKararlar.length})` : ''}</Tabs.Tab>
              <Tabs.Tab value="kurallar">ECA kuralları ({t.aktifKurallar.length})</Tabs.Tab>
              <Tabs.Tab value="kumeler">Kümeler ({durum.kumeler.length})</Tabs.Tab>
              <Tabs.Tab value="uyarilar">Uyarılar ({t.uyarilar.length})</Tabs.Tab>
            </Tabs.List>
            <Tabs.Panel value="kararlar"><KararPaneli /></Tabs.Panel>
            <Tabs.Panel value="kurallar"><KuralPaneli hedef={hedefKural} /></Tabs.Panel>
            <Tabs.Panel value="kumeler"><KumePaneli /></Tabs.Panel>
            <Tabs.Panel value="uyarilar"><UyariListesi uyarilar={t.uyarilar} /></Tabs.Panel>
          </Tabs>
        </Grid.Col>
        <Grid.Col span={{ base: 12, lg: 5 }}>
          <CanliOzet />
        </Grid.Col>
      </Grid>
    </Stack>
  );
}
