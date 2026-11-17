import importlib.util
from pathlib import Path
import tempfile
import unittest


class ClaudeUsageTests(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).with_name('claude_usage.py')
        self.assertTrue(path.exists(), 'Claude usage observer is not implemented')
        spec = importlib.util.spec_from_file_location('claude_usage', path)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def payload(self):
        return {'session_id': 'session-1', 'prompt_id': 'prompt-1',
                'context_window': {'total_output_tokens': 10},
                'rate_limits': {'five_hour': {'used_percentage': 20, 'resets_at': 2000},
                                'seven_day': {'used_percentage': 50, 'resets_at': 3000}},
                'transcript_path': '/secret/path', 'secret': 'do-not-save'}

    def test_captures_only_usage_and_requires_both_windows(self):
        data = self.module.normalize(self.payload(), '02', 1000)
        self.assertNotIn('secret', str(data))
        self.assertNotIn('transcript', str(data))
        self.assertEqual(self.module.classify(data, 1001)['state'], 'observed_headroom')
        del data['windows']['five_hour']
        self.assertEqual(self.module.classify(data, 1001)['state'], 'unknown')

    def test_exhaustion_and_margin_are_not_available(self):
        data = self.module.normalize(self.payload(), '02', 1000)
        data['windows']['five_hour']['used_percent'] = 100
        self.assertEqual(self.module.classify(data, 1001)['state'], 'subscription_wait')
        data['windows']['five_hour']['used_percent'] = 95
        self.assertEqual(self.module.classify(data, 1001)['state'], 'handoff_margin')

    def test_stale_or_expired_low_usage_never_reopens(self):
        data = self.module.normalize(self.payload(), '02', 1000)
        self.assertEqual(self.module.classify(data, 1201)['state'], 'unknown')
        self.assertEqual(self.module.classify(data, 2001, max_age=2000)['state'], 'unknown')

    def test_malformed_window_is_unknown(self):
        for value in (None, 'invalid', {'used_percentage': False},
                      {'used_percentage': float('nan'), 'resets_at': 3000}):
            payload = self.payload()
            payload['rate_limits']['five_hour'] = value
            data = self.module.normalize(payload, '02', 1000)
            self.assertEqual(self.module.classify(data, 1001)['state'], 'unknown')

    def test_repeated_ui_callback_does_not_refresh_old_quota(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = self.module.capture(root, '02', self.payload(), 1000)
            second = self.module.capture(root, '02', self.payload(), 1100)
            self.assertEqual(first['observed_at_unix'], second['observed_at_unix'])
            payload = self.payload()
            payload['context_window']['total_output_tokens'] += 1
            third = self.module.capture(root, '02', payload, 1101)
            self.assertEqual(third['observed_at_unix'], 1000)
            self.assertEqual(self.module.read_account(root, '02', 1102)['state'], 'observed_headroom')

    def test_prompt_change_does_not_make_a_stale_snapshot_current(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = self.payload()
            self.module.capture(root, '02', payload, 1000)
            payload['prompt_id'] = 'new-prompt'
            self.module.capture(root, '02', payload, 1300)
            self.assertEqual(self.module.read_account(root, '02', 1301)['state'], 'unknown')

    def test_unknown_callback_cannot_erase_known_exhaustion(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = self.payload()
            payload['rate_limits']['seven_day']['used_percentage'] = 100
            self.module.capture(root, '02', payload, 1000)
            self.module.capture(root, '02', {'session_id': 'other'}, 1001)
            self.assertEqual(self.module.read_account(root, '02', 1002)['state'], 'subscription_wait')
            self.assertEqual(self.module.read_account(root, '02', 3001)['state'], 'unknown')


if __name__ == '__main__':
    unittest.main()
