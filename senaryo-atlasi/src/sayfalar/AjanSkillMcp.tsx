import { useMemo } from 'react';
import { Badge, List, Paper, SimpleGrid, Stack, Table, Tabs, Text, Title, Alert } from '@mantine/core';
import { IconInfoCircle } from '@tabler/icons-react';
import { CODEX_ROLLERI, HAVUZ_OLGULARI, MCP_EKLENMEYECEK, MCP_KURUM_MODELI, MCP_SUNUCULARI, ONERILEN_YAPI, SKILL_CERCEVELERI, SKILLER, TERMINAL_SONUCLAR } from '../veri/ajanlar';
import { asamaBul } from '../veri/asamalar';
import { havuzDiyagrami } from '../diyagram/uretec';
import { MermaidGorunum } from '../diyagram/MermaidGorunum';
import veri from '../veri/uretilen.json';

const KARAR_RENK: Record<string, string> = { 'Kalsın': 'teal', 'Ayarla': 'yellow', 'Ajan değil': 'blue' };

export function AjanSkillMcp() {
  const havuz = useMemo(() => havuzDiyagrami(), []);
  return (
    <Stack gap="md">
      <div>
        <Title order={2}>Ajanlar, skill'ler ve MCP</Title>
        <Text c="dimmed" size="sm">Hangi ajan ne yapar, hangi skill'ler yazılır, skill'ler nereden ve nasıl beslenir, hangi MCP sunucusu hangi yetkiyle kullanılır.</Text>
      </div>
      <Tabs defaultValue="ajanlar" keepMounted={false}>
        <Tabs.List mb="sm">
          <Tabs.Tab value="ajanlar">Ajanlar</Tabs.Tab>
          <Tabs.Tab value="skill">Skill'ler</Tabs.Tab>
          <Tabs.Tab value="havuz">Skill havuzu (besleme)</Tabs.Tab>
          <Tabs.Tab value="mcp">MCP</Tabs.Tab>
        </Tabs.List>

        <Tabs.Panel value="ajanlar">
          <Stack gap="md">
            <Paper withBorder p="md" radius="md">
              <Title order={4} mb={4}>Önerilen yapı</Title>
              <Text size="sm" mb="xs">{ONERILEN_YAPI.ozet}</Text>
              <List size="sm" spacing={4}>{ONERILEN_YAPI.maddeler.map((m) => <List.Item key={m}>{m}</List.Item>)}</List>
              <Text size="xs" c="dimmed" mt="xs">Kaynak: {ONERILEN_YAPI.kaynak}</Text>
            </Paper>
            <Paper withBorder p="md" radius="md">
              <Title order={4} mb={4}>Panondaki 21 ajan: ne olmalı?</Title>
              <Text size="sm" c="dimmed" mb="sm">Kaynak: senin ajan–sağlayıcı panon ve agentic-stack-docs önerileri. "Ajan değil" satırları deterministik koddur.</Text>
              <Table.ScrollContainer minWidth={820}>
                <Table fz="xs" striped verticalSpacing={6}>
                  <Table.Thead><Table.Tr><Table.Th>Ajan</Table.Th><Table.Th>Panodaki seçim</Table.Th><Table.Th>Karar</Table.Th><Table.Th>Öneri</Table.Th></Table.Tr></Table.Thead>
                  <Table.Tbody>
                    {veri.panoAjanlari.map((a) => (
                      <Table.Tr key={a.ajan}>
                        <Table.Td fw={600}>{a.ajan}</Table.Td>
                        <Table.Td>{a.panoSecimi}</Table.Td>
                        <Table.Td><Badge size="xs" variant="light" color={KARAR_RENK[a.karar] ?? 'gray'}>{a.karar}</Badge></Table.Td>
                        <Table.Td>{a.oneri}</Table.Td>
                      </Table.Tr>
                    ))}
                  </Table.Tbody>
                </Table>
              </Table.ScrollContainer>
            </Paper>
            <SimpleGrid cols={{ base: 1, md: 2 }}>
              <Paper withBorder p="md" radius="md">
                <Title order={4} mb={4}>Codex'in 12 rol şablonu (referans)</Title>
                <Text size="xs" c="dimmed" mb="xs">Pasif şablonlar; kurulmuş değil. Evre: ilk koşuda gerekip gerekmediği.</Text>
                <Table fz="xs" verticalSpacing={4}>
                  <Table.Tbody>{CODEX_ROLLERI.map((r) => <Table.Tr key={r.id}><Table.Td w={54}>{r.id}</Table.Td><Table.Td>{r.ad}</Table.Td><Table.Td><Badge size="xs" variant="outline" color={r.evre === 'MVP' ? 'teal' : 'gray'}>{r.evre}</Badge></Table.Td></Table.Tr>)}</Table.Tbody>
                </Table>
              </Paper>
              <Paper withBorder p="md" radius="md">
                <Title order={4} mb={4}>Her ajanın döndürebileceği 6 sonuç</Title>
                <Text size="xs" c="dimmed" mb="xs">Ajan "bitti" demez; bu altı sonuçtan birini döndürür (Codex tasarımı, E4).</Text>
                <Table fz="xs" verticalSpacing={4}>
                  <Table.Tbody>{TERMINAL_SONUCLAR.map((s) => <Table.Tr key={s.ad}><Table.Td><code>{s.ad}</code></Table.Td><Table.Td>{s.ne}</Table.Td></Table.Tr>)}</Table.Tbody>
                </Table>
              </Paper>
            </SimpleGrid>
          </Stack>
        </Tabs.Panel>

        <Tabs.Panel value="skill">
          <Stack gap="md">
            <Alert icon={<IconInfoCircle size={16} />} color="blue" variant="light">
              İlk koşuda 3–5 skill yeter. Toplamda 20'yi geçme: 20 skill'e kadar seçim doğruluğu %90'ın üstünde, 30'dan sonra düşüyor (A3). Aşağıdaki 18 skill bütün akışı kapsar.
            </Alert>
            <Paper withBorder p="md" radius="md">
              <Title order={4} mb="xs">Yazılacak iç skill'ler (aşamaya göre)</Title>
              <Table.ScrollContainer minWidth={720}>
                <Table fz="xs" striped verticalSpacing={6}>
                  <Table.Thead><Table.Tr><Table.Th>Skill</Table.Th><Table.Th>Aşama</Table.Th><Table.Th>Ne yapar</Table.Th><Table.Th>Kaynak</Table.Th></Table.Tr></Table.Thead>
                  <Table.Tbody>
                    {SKILLER.map((s) => (
                      <Table.Tr key={s.id}>
                        <Table.Td><code>{s.id}</code><Text size="xs" c="dimmed">{s.ad}</Text></Table.Td>
                        <Table.Td>{asamaBul(s.asama).ad}</Table.Td>
                        <Table.Td>{s.ne}</Table.Td>
                        <Table.Td>{s.kaynak}</Table.Td>
                      </Table.Tr>
                    ))}
                  </Table.Tbody>
                </Table>
              </Table.ScrollContainer>
            </Paper>
            <Title order={4}>Skill oluşturma çerçeveleri</Title>
            <SimpleGrid cols={{ base: 1, md: 2, lg: 3 }}>
              {SKILL_CERCEVELERI.map((c) => (
                <Paper key={c.ad} withBorder p="md" radius="md">
                  <Text fw={650} mb={4}>{c.ad}</Text>
                  <Text size="sm">{c.ne}</Text>
                  <Text size="sm" mt={6}><b>Nasıl kullanılır:</b> {c.nasil}</Text>
                  <Text size="xs" c="dimmed" mt={6}>Kaynak: {c.kaynak}</Text>
                </Paper>
              ))}
            </SimpleGrid>
          </Stack>
        </Tabs.Panel>

        <Tabs.Panel value="havuz">
          <Stack gap="md">
            <Text size="sm">Skill ve MCP "veritabanları" (pazarlar, kayıtlar) yalnız <b>keşif kaynağıdır</b>. Güven iç katalogdan gelir: aday karantinaya girer, incelenir, sınanır, sabitlenir; işe yalnız kısa ömürlü izinle açılır.</Text>
            <Paper withBorder p="md" radius="md"><MermaidGorunum kod={havuz.kod} /></Paper>
            <SimpleGrid cols={{ base: 1, md: 2 }}>
              {HAVUZ_OLGULARI.map((o) => (
                <Paper key={o.metin} withBorder p="sm" radius="md">
                  <Text size="sm">{o.metin}</Text>
                  <Text size="xs" c="dimmed" mt={4}>Kaynak: {o.kaynak}</Text>
                </Paper>
              ))}
            </SimpleGrid>
          </Stack>
        </Tabs.Panel>

        <Tabs.Panel value="mcp">
          <Stack gap="md">
            <Paper withBorder p="md" radius="md">
              <Title order={4} mb="xs">Başlangıç sunucuları (rol başına en az)</Title>
              <Table.ScrollContainer minWidth={760}>
                <Table fz="xs" striped verticalSpacing={6}>
                  <Table.Thead><Table.Tr><Table.Th>Sunucu</Table.Th><Table.Th>Aşamalar</Table.Th><Table.Th>Kullanım</Table.Th><Table.Th>Yetki</Table.Th><Table.Th>Not</Table.Th></Table.Tr></Table.Thead>
                  <Table.Tbody>
                    {MCP_SUNUCULARI.map((m) => (
                      <Table.Tr key={m.ad}>
                        <Table.Td fw={600}>{m.ad}</Table.Td>
                        <Table.Td>{m.asamalar.map((a) => asamaBul(a).ad).join(', ')}</Table.Td>
                        <Table.Td>{m.kullanim}</Table.Td>
                        <Table.Td>{m.yetki}</Table.Td>
                        <Table.Td>{m.not} <Text span size="xs" c="dimmed">({m.kaynak})</Text></Table.Td>
                      </Table.Tr>
                    ))}
                  </Table.Tbody>
                </Table>
              </Table.ScrollContainer>
            </Paper>
            <SimpleGrid cols={{ base: 1, md: 2 }}>
              <Paper withBorder p="md" radius="md">
                <Title order={4} mb="xs">Eklenmeyecekler</Title>
                <List size="sm" spacing={4}>{MCP_EKLENMEYECEK.map((m) => <List.Item key={m}>{m}</List.Item>)}</List>
              </Paper>
              <Paper withBorder p="md" radius="md">
                <Title order={4} mb="xs">Kurum modeli</Title>
                <List size="sm" spacing={4}>{MCP_KURUM_MODELI.map((m) => <List.Item key={m}>{m}</List.Item>)}</List>
                <Text size="xs" c="dimmed" mt="xs">Kaynak: A3 §4</Text>
              </Paper>
            </SimpleGrid>
          </Stack>
        </Tabs.Panel>
      </Tabs>
    </Stack>
  );
}
