"""App liveness checks never affect agent ownership or the user's stop switch."""
from pathlib import Path
import tempfile
import unittest
import signal
from unittest.mock import Mock, patch

from watcher import Watcher, process_is_pane, run


class WatcherTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.enabled = Path(self.tmp.name) / 'enabled'
        self.enabled.touch()
        self.launch = Mock()
        self.watcher = Watcher(self.enabled, self.launch, restart_delay=30)

    def test_running_pane_is_untouched(self):
        self.assertEqual(self.watcher.step(True, 100), 'healthy')
        self.launch.assert_not_called()

    def test_missing_pane_is_launched_once_before_backoff(self):
        self.assertEqual(self.watcher.step(False, 100), 'launch_requested')
        self.assertEqual(self.watcher.step(False, 110), 'waiting_for_launch')
        self.launch.assert_called_once()
        self.watcher.step(False, 131)
        self.assertEqual(self.launch.call_count, 2)

    def test_launch_request_is_not_reported_as_recovery(self):
        self.watcher.step(False, 100)
        self.assertEqual(self.watcher.step(True, 102), 'healthy')

    def test_user_disable_prevents_any_launch(self):
        self.enabled.unlink()
        self.assertEqual(self.watcher.step(False, 100), 'disabled')
        self.launch.assert_not_called()

    def test_unknown_process_state_never_launches_another_copy(self):
        self.assertEqual(self.watcher.step(None, 100), 'unknown')
        self.launch.assert_not_called()

    def test_open_failure_uses_backoff(self):
        self.launch.side_effect = OSError('unavailable')
        self.assertEqual(self.watcher.step(False, 100), 'launch_failed')
        self.assertEqual(self.watcher.step(False, 110), 'waiting_for_launch')
        self.launch.assert_called_once()

    def test_cli_child_is_not_the_pane_app(self):
        self.assertTrue(process_is_pane('/Applications/Pane.app/Contents/MacOS/Pane'))
        self.assertFalse(process_is_pane('/Applications/Pane.app/Contents/MacOS/Pane /some/cli.js mcp'))
        self.assertFalse(process_is_pane('/Applications/Pane Helper.app/Contents/MacOS/Pane Helper'))

    def test_stop_during_process_probe_cannot_request_restart(self):
        handlers = {}

        def register(signum, handler):
            handlers[signum] = handler

        def slow_probe():
            handlers[signal.SIGTERM](signal.SIGTERM, None)
            return False

        with patch('watcher.signal.signal', side_effect=register), \
                patch('watcher.pane_running', side_effect=slow_probe), \
                patch.object(Watcher, 'step', return_value='disabled') as step:
            self.assertEqual(run(self.enabled.parent), 0)
            step.assert_not_called()


if __name__ == '__main__':
    unittest.main()
