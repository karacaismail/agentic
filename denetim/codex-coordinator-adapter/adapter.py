"""Run one bounded, subscription-authenticated, read-only Codex proposal in Pane.

The native CLI writes the final artifact outside the model's read-only shell.
A completed response is a candidate only. The controller remains the acceptor.
Python 3.9+, stdlib only. No provider credentials are read or copied here.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import time

BASE = Path('/Users/w6x/.config/claude-denetim')
WORKDIR = BASE / 'codex-readonly'
JOBS = BASE / 'codex-proposals'
MAX_EVENT_BYTES = 64 * 1024 * 1024


def digest(data):
    return hashlib.sha256(data).hexdigest()


def validate(job_id, account, timeout):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,100}', job_id):
        raise ValueError('invalid job id')
    if account not in ('01', '02') or not 30 <= timeout <= 1800:
        raise ValueError('invalid account or timeout')


def command(account, final_path):
    if account not in ('01', '02'):
        raise ValueError('invalid account')
    return [str(BASE / ('codex-' + account + '.sh')), 'exec',
            '--ignore-user-config', '--ephemeral', '--sandbox', 'read-only',
            '--skip-git-repo-check', '--cd', str(WORKDIR), '--json',
            '--model', 'gpt-6-astra', '--color', 'never',
            '-c', 'approval_policy="never"', '-c', 'mcp_servers={}',
            '-c', 'features.apps=false', '-c', 'features.memories=false',
            '-c', 'features.chronicle=false',
            '--output-last-message', str(final_path), '-']


def classify(code, events, final):
    if code != 0:
        return 'failed'
    if not any(e.get('type') == 'turn.completed' for e in events):
        return 'incomplete'
    try:
        value = json.loads(final)
    except (TypeError, ValueError):
        return 'invalid_final'
    return 'final_candidate' if isinstance(value, dict) else 'invalid_final'


def signal_group(pgid, sig):
    try:
        os.killpg(pgid, sig)
    except ProcessLookupError:
        return
    except PermissionError:
        # macOS can return EPERM for a group containing only zombies.
        result = subprocess.run(['/bin/ps', '-axo', 'pgid=,stat='],
                                capture_output=True, text=True, timeout=5)
        states = [line.split()[1] for line in result.stdout.splitlines()
                  if len(line.split()) == 2 and line.split()[0] == str(pgid)]
        if result.returncode or any(not state.startswith('Z') for state in states):
            raise


def native_run(argv, prompt, events_path, stderr_path, timeout):
    """Stop the owned process group on timeout/cancellation; never signal other jobs."""
    proc = None
    old_handlers = {}
    def cancelled(signum, _frame):
        raise InterruptedError('cancelled')
    try:
        for sig in (signal.SIGTERM, signal.SIGINT):
            old_handlers[sig] = signal.signal(sig, cancelled)
        with events_path.open('xb') as out, stderr_path.open('xb') as err:
            proc = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=out, stderr=err,
                                    start_new_session=True)
            deadline = time.monotonic() + timeout
            pending_input = prompt.encode('utf-8')
            while True:
                if time.monotonic() >= deadline or events_path.stat().st_size > MAX_EVENT_BYTES:
                    raise TimeoutError('job deadline or log size exceeded')
                try:
                    proc.communicate(input=pending_input, timeout=min(0.25, max(0.01, deadline-time.monotonic())))
                    break
                except subprocess.TimeoutExpired:
                    pending_input = None
            return proc.returncode
    finally:
        # A second cancellation must not interrupt cleanup of this job.
        for sig in old_handlers:
            signal.signal(sig, signal.SIG_IGN)
        if proc is not None:
            # The leader may exit before its children. Retire its owned group too.
            try:
                signal_group(proc.pid, signal.SIGTERM)
                time.sleep(0.5)
                signal_group(proc.pid, signal.SIGKILL)
            finally:
                proc.wait(timeout=5)
                if proc.stdin and not proc.stdin.closed:
                    proc.stdin.close()
        for sig, handler in old_handlers.items():
            signal.signal(sig, handler)


def run_job(job_id, account, brief, jobs_root=JOBS, timeout=1200, runner=native_run):
    validate(job_id, account, timeout)
    brief = Path(brief).resolve(strict=True)
    if brief.stat().st_size > 256 * 1024:
        raise ValueError('brief too large')
    prompt_bytes = brief.read_bytes()
    prompt = prompt_bytes.decode('utf-8')
    old_umask = os.umask(0o077)
    try:
        WORKDIR.mkdir(mode=0o700, parents=True, exist_ok=True)
        jobs_root = Path(jobs_root)
        jobs_root.mkdir(mode=0o700, parents=True, exist_ok=True)
        job_dir = jobs_root / job_id
        job_dir.mkdir(mode=0o700)  # Never rerun a possibly completed action.
        final_path = job_dir / 'final.json'
        events_path = job_dir / 'events.jsonl'
        receipt = {'job_id': job_id, 'account_id': account, 'accepted': False,
                   'brief_sha256': digest(prompt_bytes), 'started_at_unix': time.time(),
                   'final_path': str(final_path), 'final_sha256': None}
        try:
            code = runner(command(account, final_path), prompt, events_path,
                          job_dir / 'stderr.log', timeout)
            events = []
            if events_path.exists() and events_path.stat().st_size <= MAX_EVENT_BYTES:
                for line in events_path.read_text(errors='replace').splitlines():
                    try:
                        item = json.loads(line)
                        if isinstance(item, dict):
                            events.append(item)
                    except ValueError:
                        continue
            final_bytes = final_path.read_bytes() if final_path.exists() else None
            final = final_bytes.decode('utf-8') if final_bytes is not None else None
            receipt.update(status=classify(code, events, final), exit_code=code)
            if final_bytes is not None:
                receipt['final_sha256'] = digest(final_bytes)
        except (TimeoutError, InterruptedError) as exc:
            receipt.update(status='interrupted', reason=str(exc), exit_code=None)
        except OSError as exc:
            receipt.update(status='failed', reason=type(exc).__name__, exit_code=None)
        receipt['finished_at_unix'] = time.time()
        temporary = job_dir / 'receipt.tmp'
        with temporary.open('x') as stream:
            json.dump(receipt, stream, ensure_ascii=False, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, job_dir / 'receipt.json')
        return receipt
    finally:
        os.umask(old_umask)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--job-id', required=True)
    parser.add_argument('--account', choices=('01', '02'), required=True)
    parser.add_argument('--brief', required=True, type=Path)
    parser.add_argument('--timeout', type=int, default=1200)
    args = parser.parse_args()
    try:
        receipt = run_job(args.job_id, args.account, args.brief, timeout=args.timeout)
    except (ValueError, OSError) as exc:
        print(json.dumps({'status': 'not_started', 'reason': type(exc).__name__}))
        return 3
    print(json.dumps(receipt, ensure_ascii=False), flush=True)
    return 0 if receipt['status'] == 'final_candidate' else 3


if __name__ == '__main__':
    raise SystemExit(main())
