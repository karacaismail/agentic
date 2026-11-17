import importlib.util
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest


class SubscriptionGateTests(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).with_name('probe.py')
        self.assertTrue(path.exists(), 'Subscription gate is not implemented')
        spec = importlib.util.spec_from_file_location('subscription_probe', path)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def classify(self, limit):
        return self.module.classify({'rateLimits': limit}, observed_at=10)

    def test_current_subscription_allows_work(self):
        state = self.classify({'primary': {'usedPercent': 21, 'resetsAt': 20}})
        self.assertEqual(state['state'], 'available')

    def test_extra_credits_do_not_override_exhausted_subscription(self):
        state = self.classify({'primary': {'usedPercent': 100, 'resetsAt': 20},
                               'credits': {'hasCredits': True, 'balance': '123'}})
        self.assertEqual(state['state'], 'subscription_wait')
        self.assertNotIn('balance', str(state))

    def test_elapsed_reset_does_not_override_current_exhaustion(self):
        state = self.classify({'primary': {'usedPercent': 100, 'resetsAt': 5}})
        self.assertEqual(state['state'], 'subscription_wait')

    def test_missing_window_is_unknown(self):
        self.assertEqual(self.classify({'credits': {'unlimited': True}})['state'], 'unknown')

    def test_malformed_existing_window_is_unknown(self):
        state = self.classify({'primary': {'usedPercent': 21}, 'secondary': 'invalid'})
        self.assertEqual(state['state'], 'unknown')

    def test_explicit_limit_signal_blocks_low_percentage(self):
        state = self.classify({'primary': {'usedPercent': 1},
                               'rateLimitReachedType': 'rate_limit_reached'})
        self.assertEqual(state['state'], 'subscription_wait')

    def test_exhausted_second_window_blocks_work(self):
        state = self.classify({'primary': {'usedPercent': 20},
                               'secondary': {'usedPercent': 100}})
        self.assertEqual(state['state'], 'subscription_wait')

    def test_proactive_margin_is_a_wait_not_extra_credit_permission(self):
        state = self.classify({'primary': {'usedPercent': 96}})
        self.assertEqual(state['state'], 'handoff_margin')

    def test_unmapped_model_bucket_is_not_silently_ignored(self):
        state = self.module.classify({
            'rateLimits': {'primary': {'usedPercent': 21}},
            'rateLimitsByLimitId': {'codex': {'primary': {'usedPercent': 21}},
                                  'new_model': {'primary': {'usedPercent': 100}}},
        }, observed_at=10)
        self.assertEqual(state['state'], 'unknown')

    def test_sigterm_cleans_real_probe_child(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pidfile = root / 'child.pid'
            fake = root / 'fake-codex'
            fake.write_text('#!' + sys.executable + '\nimport os,time\n'
                            + 'open(' + repr(str(pidfile)) + ',"w").write(str(os.getpid()))\n'
                            + 'time.sleep(30)\n')
            fake.chmod(0o700)
            script = ('import importlib.util,sys; '
                      's=importlib.util.spec_from_file_location("probe",sys.argv[1]); '
                      'm=importlib.util.module_from_spec(s); s.loader.exec_module(m); '
                      'm.CODEX=sys.argv[2]; m.probe("01",timeout=10)')
            parent = subprocess.Popen([sys.executable, '-c', script,
                                       str(Path(__file__).with_name('probe.py')), str(fake)],
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            child_pid = None
            try:
                deadline = time.monotonic() + 4
                while not pidfile.exists() and time.monotonic() < deadline:
                    time.sleep(0.02)
                self.assertTrue(pidfile.exists(), 'Fake child did not start')
                child_pid = int(pidfile.read_text())
                parent.send_signal(signal.SIGTERM)
                parent.wait(timeout=4)
                with self.assertRaises(ProcessLookupError):
                    os.kill(child_pid, 0)
            finally:
                if parent.poll() is None:
                    parent.kill()
                    parent.wait()
                if child_pid is not None:
                    try:
                        os.kill(child_pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass

    def test_sigterm_during_cleanup_cannot_return_available(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            marker = root / 'cleanup-started'
            fake = root / 'fake-codex'
            fake.write_text('#!' + sys.executable + '\nimport json,signal,sys,time\n'
                            'def stop(*args):\n'
                            '    open(' + repr(str(marker)) + ',"w").write("ready")\n'
                            '    time.sleep(0.5)\n    sys.exit(0)\n'
                            'signal.signal(signal.SIGTERM,stop)\n'
                            'for line in sys.stdin:\n'
                            '    value=json.loads(line)\n'
                            '    if "id" in value:\n'
                            '        data={} if value["id"]==1 else {"rateLimits":{"primary":{"usedPercent":21}}}\n'
                            '        print(json.dumps({"id":value["id"],"result":data}),flush=True)\n')
            fake.chmod(0o700)
            script = ('import importlib.util,sys; '
                      's=importlib.util.spec_from_file_location("probe",sys.argv[1]); '
                      'm=importlib.util.module_from_spec(s); s.loader.exec_module(m); '
                      'm.CODEX=sys.argv[2]; print(m.probe("01",timeout=10)["state"])')
            parent = subprocess.Popen([sys.executable, '-c', script,
                                       str(Path(__file__).with_name('probe.py')), str(fake)],
                                      stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
            try:
                deadline = time.monotonic() + 4
                while not marker.exists() and time.monotonic() < deadline:
                    time.sleep(0.02)
                self.assertTrue(marker.exists(), 'Child cleanup did not start')
                parent.send_signal(signal.SIGTERM)
                output, _ = parent.communicate(timeout=4)
                self.assertEqual(output.strip(), 'unknown')
            finally:
                if parent.poll() is None:
                    parent.kill()
                    parent.wait()


if __name__ == '__main__':
    unittest.main()
