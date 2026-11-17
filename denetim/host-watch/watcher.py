"""Keep the authorized Pane application available without dispatching agent work."""
import argparse
import fcntl
import json
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import threading
import time
from typing import Optional

PANE_EXECUTABLE = '/Applications/Pane.app/Contents/MacOS/Pane'
PANE_APP = '/Applications/Pane.app'


class StopRequested(Exception):
    """Interrupt a pending process probe before it can trigger a launch."""


def process_is_pane(command: str) -> bool:
    """The MCP helper uses the same executable but is not the desktop app."""
    return command.strip() == PANE_EXECUTABLE


def pane_running() -> Optional[bool]:
    try:
        result = subprocess.run(['/bin/ps', '-A', '-o', 'command='],
                                capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    return any(process_is_pane(line) for line in result.stdout.splitlines())


def launch_pane() -> None:
    subprocess.run(['/usr/bin/open', '-g', '-j', '-a', PANE_APP],
                   check=True, capture_output=True, timeout=20)


class Watcher:
    def __init__(self, enabled: Path, launch=launch_pane, restart_delay: float = 30):
        self.enabled = enabled
        self.launch = launch
        self.restart_delay = restart_delay
        self.retry_after = 0.0

    def step(self, running: Optional[bool], now: float) -> str:
        if not self.enabled.exists():
            return 'disabled'
        if running is None:
            return 'unknown'
        if running:
            return 'healthy'
        if now < self.retry_after:
            return 'waiting_for_launch'
        self.retry_after = now + self.restart_delay
        try:
            self.launch()
        except (OSError, subprocess.SubprocessError):
            return 'launch_failed'
        return 'launch_requested'


def publish_state(directory: Path, state: dict) -> None:
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8',
                                     dir=directory, delete=False) as handle:
        temporary = Path(handle.name)
        try:
            json.dump(state, handle)
            handle.write('\n')
            handle.flush()
            os.fsync(handle.fileno())
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    try:
        temporary.replace(directory / 'status.json')
    finally:
        temporary.unlink(missing_ok=True)


def run(directory: Path) -> int:
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    enabled = directory / 'enabled'
    if not enabled.exists():
        return 0
    with (directory / 'watcher.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return 0
        logger = logging.getLogger('pane-host-watch')
        logger.setLevel(logging.INFO)
        handler = RotatingFileHandler(directory / 'watcher.log',
                                      maxBytes=1048576, backupCount=2)
        handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
        logger.addHandler(handler)
        stopped = threading.Event()
        watcher = Watcher(enabled)
        sleep_guard = None
        previous = None
        try:
            def stop(*_):
                stopped.set()
                raise StopRequested()

            for signum in (signal.SIGINT, signal.SIGTERM):
                signal.signal(signum, stop)
            while not stopped.is_set():
                state = watcher.step(pane_running(), time.monotonic())
                if state != previous:
                    logger.info('state=%s', state)
                    previous = state
                if state == 'disabled':
                    break
                if sleep_guard is None or sleep_guard.poll() is not None:
                    try:
                        sleep_guard = subprocess.Popen(
                            ['/usr/bin/caffeinate', '-i', '-w', str(os.getpid())],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    except OSError:
                        logger.error('idle_sleep_guard_start_failed')
                publish_state(directory, {
                    'pid': os.getpid(), 'updated_at_unix': time.time(),
                    'pane_state': state,
                    'idle_sleep_guard_running': sleep_guard is not None and sleep_guard.poll() is None,
                    'scope': 'Pane process only; does not dispatch or accept agent work',
                })
                stopped.wait(5)
        except StopRequested:
            pass
        finally:
            # A second stop request must not interrupt cleanup.
            for signum in (signal.SIGINT, signal.SIGTERM):
                signal.signal(signum, signal.SIG_IGN)
            if sleep_guard is not None and sleep_guard.poll() is None:
                sleep_guard.terminate()
                try:
                    sleep_guard.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    sleep_guard.kill()
                    sleep_guard.wait()
            publish_state(directory, {'pid': os.getpid(), 'updated_at_unix': time.time(),
                                      'pane_state': 'stopped', 'idle_sleep_guard_running': False})
            logger.info('stopped')
            logger.removeHandler(handler)
            handler.close()
        return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--state-dir', type=Path, required=True)
    args = parser.parse_args()
    return run(args.state_dir)


if __name__ == '__main__':
    raise SystemExit(main())
