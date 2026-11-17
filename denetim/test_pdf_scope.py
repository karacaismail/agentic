"""Regression checks for changing sources and simultaneous preparation."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

import pdf_scope


XML = '<html xmlns="http://www.w3.org/1999/xhtml"><page width="100" height="100"><line><word xMin="1" xMax="2" yMin="1" yMax="2">{}</word></line></page></html>'


class PdfPreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.folder = self.root / 'sources'
        self.folder.mkdir()
        self.source = self.folder / 'a.pdf'
        self.source.write_bytes(b'A')

    def fake_tool(self, args, **kwargs):
        source = Path(args[-2])
        target = Path(args[-1])
        if target.suffix == '.xhtml':
            target.write_text(XML.format(source.read_text()))
        else:
            target.with_suffix('.png').write_bytes(source.read_bytes())

    def test_source_changes_during_extraction_cannot_poison_original_digest(self):
        def changing_tool(args, **kwargs):
            if str(args[-1]).endswith('.xhtml'):
                self.source.write_bytes(b'B')
                self.fake_tool(args, **kwargs)
                self.source.write_bytes(b'A')
            else:
                self.fake_tool(args, **kwargs)

        with patch.object(pdf_scope.subprocess, 'run', side_effect=changing_tool):
            scope = pdf_scope.prepare_scope(self.root, self.folder, [])
        unit = scope['selected']['regions'][0]
        self.assertEqual(Path(unit['text']).read_text(), 'A')
        self.assertEqual(Path(unit['image']).read_bytes(), b'A')
        self.assertEqual(scope['selected']['sha256'], pdf_scope.sha256(self.source))

    def test_simultaneous_preparations_never_share_an_active_writer(self):
        mutex = threading.Lock()
        active = 0
        highest = 0

        def slow_tool(args, **kwargs):
            nonlocal active, highest
            with mutex:
                active += 1
                highest = max(highest, active)
            try:
                time.sleep(0.03)
                self.fake_tool(args, **kwargs)
            finally:
                with mutex:
                    active -= 1

        with patch.object(pdf_scope.subprocess, 'run', side_effect=slow_tool):
            with ThreadPoolExecutor(max_workers=2) as pool:
                futures = [pool.submit(pdf_scope.prepare_scope, self.root, self.folder, []) for _ in range(2)]
                results = [f.result() for f in futures]
        self.assertEqual(highest, 1)
        for result in results:
            self.assertEqual(Path(result['selected']['regions'][0]['text']).read_text(), 'A')

    def test_reader_keeps_complete_published_text_during_next_preparation(self):
        with patch.object(pdf_scope.subprocess, 'run', side_effect=self.fake_tool):
            scope = pdf_scope.prepare_scope(self.root, self.folder, [])
            text_path = Path(scope['selected']['regions'][0]['text'])
            with text_path.open() as existing_reader:
                (text_path.parent / 'pages.xhtml').write_text(XML.format('B'))
                pdf_scope.prepare_scope(self.root, self.folder, [])
                self.assertEqual(existing_reader.read(), 'A')
                self.assertEqual(text_path.read_text(), 'B')


if __name__ == '__main__':
    unittest.main()
