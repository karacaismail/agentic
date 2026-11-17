import copy
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from publisher import ReportPublisher


class PublisherTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.live = self.root / 'live'
        self.live.mkdir()
        (self.root / 'source.txt').write_text('source fact')
        (self.live / 'evidence.json').write_text('{"observed": true}')
        self.publisher = ReportPublisher(self.live, self.root, self.root, [self.live])
        self.report = {
            'report_id': 'report-1', 'markdown': '# Kaynak analizi\n\n' + 'Kaynak sınırlı bir gözlemi destekler. ' * 5,
            'source_refs': [{'source': 'source.txt', 'sha256': hashlib.sha256(b'source fact').hexdigest(), 'unit_ids': ['u1']}],
            'evidence_paths': [str(self.live / 'evidence.json')],
            'needs': [{'need': 'Gözlemi doğrula', 'source_items': ['u1/item1'], 'tool_or_llm_process': 'Bağımsız okuma',
                       'unknowns_experiment': 'Tek karşı örnekte dur ve sonucu kaydet.', 'limits': 'Sistem geneli bilinmiyor.',
                       'internal_risks': 'Kaynak içi eksiklik.', 'external_risks': 'Dış sözleşme bilinmiyor.',
                       'sustainability': 'Tekrarda aynı kanıtı yeniden kullan.'}]
        }

    def test_number_allocation_preserves_existing_and_replay(self):
        (self.root / '101.md').write_text('protected')
        (self.root / '104.md').write_text('prior')
        result = self.publisher.publish(self.report, 'P1')
        self.assertEqual(Path(result['path']).name, '105.md')
        self.assertEqual(self.publisher.publish(self.report, 'P1'), result)
        changed_id = copy.deepcopy(self.report)
        changed_id['report_id'] = 'another-id'
        with self.assertRaises(ValueError):
            self.publisher.publish(changed_id, 'P1')
        second = copy.deepcopy(self.report)
        second['report_id'] = 'report-2'
        result2 = ReportPublisher(self.live, self.root, self.root, [self.live]).publish(second, 'P2')
        self.assertEqual(Path(result2['path']).name, '106.md')
        Path(result2['path']).unlink()
        third = copy.deepcopy(self.report)
        third['report_id'] = 'report-3'
        self.assertEqual(Path(self.publisher.publish(third, 'P3')['path']).name, '107.md')
        self.assertEqual((self.root / '101.md').read_text(), 'protected')
        self.assertEqual((self.root / '104.md').read_text(), 'prior')
        self.assertNotIn('Kaynak karşılaştırması yapılmış analiz', Path(result['path']).read_text())
        self.assertEqual(Path(result['path']).stat().st_mode & 0o222, 0)

    def test_crash_after_link_recovers_same_number(self):
        original = self.publisher._publish_link
        def crash(body, target):
            original(body, target)
            raise RuntimeError('crash after link')
        with patch.object(self.publisher, '_publish_link', crash):
            with self.assertRaises(RuntimeError):
                self.publisher.publish(self.report, 'P1')
        (self.root / 'source.txt').write_text('changed after publication')
        result = self.publisher.publish(self.report, 'P1')
        self.assertEqual(Path(result['path']).name, '103.md')
        self.assertEqual(len(list(self.root.glob('[0-9]*.md'))), 1)

    def test_changed_source_or_missing_analysis_is_refused(self):
        (self.root / 'source.txt').write_text('changed')
        with self.assertRaises(ValueError):
            self.publisher.publish(self.report, 'P1')
        (self.root / 'source.txt').write_text('source fact')
        del self.report['needs'][0]['unknowns_experiment']
        with self.assertRaises(ValueError):
            self.publisher.publish(self.report, 'P1')
        self.assertEqual(list(self.root.glob('[0-9]*.md')), [])


if __name__ == '__main__':
    unittest.main()
