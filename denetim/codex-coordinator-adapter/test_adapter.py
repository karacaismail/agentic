import json
from pathlib import Path
import tempfile
import subprocess
import sys
import time
import unittest
import adapter


class AdapterTests(unittest.TestCase):
    def test_command_preserves_auth_guard_and_read_only_boundary(self):
        argv = adapter.command('02', Path('/tmp/final.json'))
        self.assertEqual(argv[0], '/Users/w6x/.config/claude-denetim/codex-02.sh')
        self.assertIn('--ignore-user-config', argv)
        self.assertEqual(argv[argv.index('--sandbox') + 1], 'read-only')
        self.assertIn('approval_policy="never"', argv)
        self.assertIn('mcp_servers={}', argv)
        self.assertNotIn('--dangerously-bypass-approvals-and-sandbox', argv)

    def test_failed_or_incomplete_turn_never_becomes_candidate(self):
        events = [{'type': 'turn.completed'}]
        self.assertEqual(adapter.classify(3, events, '{"ok": true}'), 'failed')
        self.assertEqual(adapter.classify(0, [], '{"ok": true}'), 'incomplete')
        self.assertEqual(adapter.classify(0, events, 'ordinary prose'), 'invalid_final')
        self.assertEqual(adapter.classify(0, events, '[1,2]'), 'invalid_final')
        self.assertEqual(adapter.classify(0, events, '{"ok": true}'), 'final_candidate')

    def test_exact_result_and_brief_identity_are_bound(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            brief = root / 'brief.md'
            brief.write_text('Read the exact evidence.')
            def fake_run(argv, prompt, events_path, stderr_path, timeout):
                Path(argv[argv.index('--output-last-message') + 1]).write_text('{"proposal_id":"A"}')
                events_path.write_text('{"type":"thread.started","thread_id":"fixture-thread"}\n{"type":"turn.completed"}\n')
                return 0
            receipt = adapter.run_job('COORD-1', '01', brief, root / 'jobs', 60, fake_run)
            self.assertEqual(receipt['status'], 'final_candidate')
            self.assertEqual(receipt['job_id'], 'COORD-1')
            self.assertEqual(receipt['brief_sha256'], adapter.digest(brief.read_bytes()))
            self.assertEqual(receipt['final_sha256'], adapter.digest(b'{"proposal_id":"A"}'))
            self.assertFalse(receipt['accepted'])
            with self.assertRaises(FileExistsError):
                adapter.run_job('COORD-1', '01', brief, root / 'jobs', 60, fake_run)

    def test_quota_block_has_no_final_candidate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            brief = root / 'brief.md'
            brief.write_text('bounded job')
            def blocked(argv, prompt, events_path, stderr_path, timeout):
                events_path.write_text('{"state":"subscription_wait"}\n')
                return 3
            result = adapter.run_job('COORD-2', '02', brief, root / 'jobs', 60, blocked)
            self.assertEqual(result['status'], 'failed')
            self.assertIsNone(result['final_sha256'])

    def test_rejects_traversal_and_unknown_accounts(self):
        for job in ('../escape', '/absolute', 'x y'):
            with self.assertRaises(ValueError):
                adapter.validate(job, '01', 60)
        with self.assertRaises(ValueError):
            adapter.validate('okay', '03', 60)

    def test_exit_does_not_leave_owned_child_running(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = "import os,time,signal; p=os.fork(); print(p,flush=True) if p else (signal.signal(signal.SIGTERM,signal.SIG_IGN),time.sleep(20)); os._exit(0)"
            adapter.native_run([sys.executable, '-c', script], '', root/'events', root/'err', 3)
            child = int((root/'events').read_text().strip())
            status = subprocess.run(['/bin/ps','-o','stat=','-p',str(child)],capture_output=True,text=True).stdout.strip()
            # Reaped or zombie: neither can keep consuming or issuing model requests.
            self.assertTrue(not status or status.startswith('Z'), status)

    def test_deadline_includes_blocked_stdin(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            started = time.monotonic()
            with self.assertRaises(TimeoutError):
                adapter.native_run([sys.executable, '-c', 'import time; time.sleep(10)'],
                                   'x' * 200000, root/'events', root/'err', 0.15)
            self.assertLess(time.monotonic() - started, 2)


if __name__ == '__main__':
    unittest.main()
