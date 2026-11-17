import { useMemo } from 'react';
import { AppShell, Badge, Burger, Button, Group, Kbd, NavLink, ActionIcon, ScrollArea, Stack, Text, Tooltip, UnstyledButton, useComputedColorScheme, useMantineColorScheme } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { Spotlight, spotlight, type SpotlightActionGroupData } from '@mantine/spotlight';
import {
  IconCompass, IconAdjustmentsHorizontal, IconSitemap, IconAlertTriangle, IconStack2, IconRobot, IconFileText,
  IconChartBar, IconBooks, IconReport, IconSearch, IconSun, IconMoon, IconFileTypePdf, IconRoute, IconBolt,
} from '@tabler/icons-react';
import { useSayfa } from './bilesenler/ortak';
import { useDurum } from './durum/depo';
import { useTuretilen } from './durum/kanca';
import { SENARYOLAR } from './veri/senaryolar';
import { KURALLAR } from './veri/kurallar';
import { SORUNLAR } from './veri/sorunlar';
import { BELGELER } from './veri/belgeler';
import { KARARLAR } from './veri/kararlar';
import { Baslangic } from './sayfalar/Baslangic';
import { Tasarimci } from './sayfalar/Tasarimci';
import { Diyagramlar } from './sayfalar/Diyagramlar';
import { Sorunlar } from './sayfalar/Sorunlar';
import { Teknolojiler } from './sayfalar/Teknolojiler';
import { AjanSkillMcp } from './sayfalar/AjanSkillMcp';
import { Belgeler } from './sayfalar/Belgeler';
import { Istatistikler } from './sayfalar/Istatistikler';
import { Kaynaklar } from './sayfalar/Kaynaklar';
import { Uyarlama } from './sayfalar/Uyarlama';
import { KararModelleri } from './sayfalar/KararModelleri';
import { Simulasyon } from './sayfalar/Simulasyon';
import { KanitDefteri } from './sayfalar/KanitDefteri';
import { Bulgular } from './sayfalar/Bulgular';
import analiz from './analiz/bulgular.json';
import { Rapor } from './sayfalar/Rapor';

const SAYFALAR = [
  { id: 'baslangic', ad: 'Çalışma masası', alt: 'Bulgular ve çalışma sırası', ikon: IconCompass, bilesen: Baslangic },
  { id: 'bulgular', ad: 'Bulgudan karara', alt: '24 soru; kanıt, sınır ve seçenekler', ikon: IconCompass, bilesen: Bulgular },
  { id: 'tasarimci', ad: 'Senaryo tasarımcısı', alt: 'Senaryo, karar, ECA kuralı, küme', ikon: IconAdjustmentsHorizontal, bilesen: Tasarimci },
  { id: 'simulasyon', ad: 'Olay laboratuvarı', alt: 'OOM, durma, çift görev ve teslim', ikon: IconBolt, bilesen: Simulasyon },
  { id: 'kanit', ad: 'Kanıt defteri', alt: '18 yerel + 36 dünya + 28 inceleme', ikon: IconBooks, bilesen: KanitDefteri },
  { id: 'diyagramlar', ad: 'Diyagramlar', alt: 'Mermaid, SVG ve kaynak aktarımı', ikon: IconSitemap, bilesen: Diyagramlar },
  { id: 'sorunlar', ad: 'Sorunlar ve önlemler', alt: 'Kestra + dünya + ön-ölüm', ikon: IconAlertTriangle, bilesen: Sorunlar },
  { id: 'uyarlama', ad: 'Tak-çıkar sözleşmeleri', alt: 'Durum, yetki, kanıt ve adaptörler', ikon: IconRoute, bilesen: Uyarlama },
  { id: 'teknolojiler', ad: 'Teknolojiler', alt: 'Kullanılanlar + 127 araçlık katalog', ikon: IconStack2, bilesen: Teknolojiler },
  { id: 'karar-modelleri', ad: 'Tipli karar katmanı', alt: 'Jev, Laya ve diğer adaylar', ikon: IconRoute, bilesen: KararModelleri },
  { id: 'ajanlar', ad: 'Ajan · Skill · MCP', alt: 'Roller, skill havuzu, MCP', ikon: IconRobot, bilesen: AjanSkillMcp },
  { id: 'belgeler', ad: 'Hazırlanacak dosyalar', alt: '.md şablonları (CLAUDE.md hariç)', ikon: IconFileText, bilesen: Belgeler },
  { id: 'istatistikler', ad: 'İstatistikler', alt: 'Araştırmanın sayıları', ikon: IconChartBar, bilesen: Istatistikler },
  { id: 'kaynaklar', ad: 'Kaynaklar', alt: 'Araştırma dosyaları', ikon: IconBooks, bilesen: Kaynaklar },
  { id: 'rapor', ad: 'Rapor ve PDF', alt: 'Kararlarının çıktısı', ikon: IconReport, bilesen: Rapor },
];

export function App() {
  const [acik, { toggle, close }] = useDisclosure();
  const { sayfa, git } = useSayfa();
  const { durum, gonder } = useDurum();
  const t = useTuretilen();
  const { setColorScheme } = useMantineColorScheme();
  const sema = useComputedColorScheme('light', { getInitialValueInEffect: true });
  const aktifSayfa = SAYFALAR.find((s) => s.id === sayfa) ?? SAYFALAR[0];
  const Bilesen = aktifSayfa.bilesen;
  const degisiklik = t.degisenKararlar.length + t.degisenKurallar.length;

  const aramalar = useMemo<SpotlightActionGroupData[]>(() => [
    { group: 'Sayfalar', actions: SAYFALAR.map((s) => ({ id: `s-${s.id}`, label: s.ad, description: s.alt, onClick: () => git(s.id) })) },
    { group: 'Bulgular', actions: analiz.briefs.map(b => ({id: b.id, label: b.title, description: b.decision_question, onClick: () => git(`bulgular?id=${b.id}`)})) },
    { group: 'Senaryolar', actions: SENARYOLAR.map((s) => ({ id: `n-${s.id}`, label: s.ad, description: s.ozet, onClick: () => { gonder({ tur: 'senaryo', id: s.id }); git('tasarimci'); } })) },
    { group: 'Kararlar', actions: KARARLAR.map((k) => ({ id: `k-${k.id}`, label: k.baslik, description: k.soru, onClick: () => git('tasarimci?sekme=kararlar') })) },
    { group: 'ECA kuralları', actions: KURALLAR.map((k) => ({ id: `r-${k.id}`, label: `${k.id} · ${k.baslik}`, description: `${k.olay} → ${k.eylem}`, onClick: () => git(`tasarimci?sekme=kurallar&kural=${k.id}`) })) },
    { group: 'Sorunlar', actions: SORUNLAR.map((s) => ({ id: `p-${s.id}`, label: `${s.id} · ${s.baslik}`, description: s.ozet, onClick: () => git(`sorunlar?id=${s.id}`) })) },
    { group: 'Dosyalar', actions: BELGELER.map((b) => ({ id: `b-${b.yol}`, label: b.yol, description: b.neIse, onClick: () => git(`belgeler?yol=${encodeURIComponent(b.yol)}`) })) },
  ], [git, gonder]);

  return (
    <>
      <a className="skip-link" href="#ana-icerik" onClick={e=>{e.preventDefault();document.getElementById('ana-icerik')?.focus();}}>İçeriğe geç</a>
      <AppShell header={{ height: 64 }} navbar={{ width: 248, breakpoint: 'sm', collapsed: { mobile: !acik } }} padding="md">
        <AppShell.Header className="ekran-yalniz">
          <Group h="100%" px="md" justify="space-between" wrap="nowrap">
            <Group gap="sm" wrap="nowrap">
              <Burger opened={acik} onClick={toggle} hiddenFrom="sm" size="sm" aria-label="Menü" />
              <UnstyledButton onClick={() => git('baslangic')}>
                <Group gap={8} wrap="nowrap">
                  <IconRoute size={22} stroke={1.8} />
                  <Text fw={700} visibleFrom="xs">Senaryo Atlası</Text>
                </Group>
              </UnstyledButton>
              <Tooltip label="Açık hazır senaryo taslağı; kullanıcı onayı veya araç tavsiyesi değildir.">
                <Badge variant="light" size="lg" radius="sm" visibleFrom="md" style={{ cursor: 'pointer' }} onClick={() => git('tasarimci')}>
                  Taslak · {t.senaryo.ad}{degisiklik ? ` · ${degisiklik} değişiklik` : ''}
                </Badge>
              </Tooltip>
            </Group>
            <Group gap="xs" wrap="nowrap">
              <Button variant="default" size="xs" leftSection={<IconSearch size={14} />} onClick={() => spotlight.open()} rightSection={<Kbd size="xs" visibleFrom="sm">⌘K</Kbd>}>
                Ara
              </Button>
              <Button size="xs" leftSection={<IconFileTypePdf size={15} />} onClick={() => git('rapor?yazdir=1')}>PDF</Button>
              <Tooltip label={sema === 'dark' ? 'Açık tema' : 'Koyu tema'}>
                <ActionIcon variant="default" size="lg" aria-label="Tema" onClick={() => setColorScheme(sema === 'dark' ? 'light' : 'dark')}>
                  {sema === 'dark' ? <IconSun size={18} /> : <IconMoon size={18} />}
                </ActionIcon>
              </Tooltip>
            </Group>
          </Group>
        </AppShell.Header>

        <AppShell.Navbar p="xs" className="ekran-yalniz">
          <AppShell.Section grow component={ScrollArea}>
            <Stack gap={2}>
              {[
                {ad:'ARAŞTIR', ids:['baslangic','bulgular','kanit','kaynaklar']},
                {ad:'BİÇİMLENDİR',ids:['tasarimci','simulasyon','sorunlar','teknolojiler','karar-modelleri','uyarlama','ajanlar']},
                {ad:'ÇIKTI AL',ids:['diyagramlar','belgeler','istatistikler','rapor']},
              ].map(group => <div key={group.ad}><Text className="nav-group-label">{group.ad}</Text>{group.ids.map(id=>SAYFALAR.find(s=>s.id===id)!).map(s =>
                <NavLink key={s.id} active={s.id===aktifSayfa.id} label={s.ad} aria-current={s.id===aktifSayfa.id?'page':undefined} leftSection={<s.ikon size={18} stroke={1.6}/>}
                  onClick={()=>{git(s.id);close();}} variant="light"/>
              )}</div>)}
            </Stack>
          </AppShell.Section>
          <AppShell.Section p="xs">
            <Stack gap={6}>
              <Text size="xs" fw={600}>Tasarım taslağı</Text>
              <Text size="xs" c="dimmed">Seçili önlem ≠ uygulanmış çözüm</Text>
              <Group gap={6}>
                <IconBolt size={14} />
                <Text size="xs" c="dimmed">Faz {durum.hedefFaz} · {t.aktifKurallar.length}/{KURALLAR.length} kural açık</Text>
              </Group>
            </Stack>
          </AppShell.Section>
        </AppShell.Navbar>

        <AppShell.Main id="ana-icerik" tabIndex={-1}>
          <div className="page-content"><Bilesen /></div>
        </AppShell.Main>
      </AppShell>
      <Spotlight actions={aramalar} nothingFound="Sonuç yok" highlightQuery limit={40} scrollable maxHeight={460}
        searchProps={{ leftSection: <IconSearch size={18} />, placeholder: 'Kural, sorun, dosya, senaryo ara…' }} shortcut={['mod + K']} />
    </>
  );
}
