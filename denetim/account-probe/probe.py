"""Read subscription availability through the installed official Codex server.

No model turn is created. Extra credits never make an exhausted subscription
eligible. Results are observations, not reserved quota or billing guarantees.
"""
import argparse
import json
import os
from pathlib import Path
import selectors
import signal
import subprocess
import sys
import tempfile
import threading
import time

CODEX = '/Users/w6x/.local/bin/codex'
ACCOUNT_ROOTS = {
    '01': '/Users/w6x/.codex',
    '02': '/Users/w6x/.config/claude-denetim/codex-accounts/02',
}


def classify(payload, observed_at):
    limit = payload.get('rateLimits') or {}
    buckets = payload.get('rateLimitsByLimitId')
    # Current observed server returns a single codex bucket. Do not invent
    # a target-model mapping if the server later exposes additional buckets.
    bucket_unknown = buckets is not None and (
        not isinstance(buckets, dict) or set(buckets) != {'codex'} or
        not isinstance(buckets.get('codex'), dict) or buckets['codex'] != limit)
    malformed_window = any(limit.get(name) is not None and
                           not isinstance(limit[name], dict)
                           for name in ('primary', 'secondary'))
    windows = {name: limit[name] for name in ('primary', 'secondary')
               if isinstance(limit.get(name), dict)}
    percentages = [window.get('usedPercent') for window in windows.values()]
    valid = not bucket_unknown and not malformed_window and percentages and all(type(value) is int and 0 <= value <= 100
                                for value in percentages)
    state = 'unknown'
    if limit.get('rateLimitReachedType') or limit.get('spendControlReached') is True:
        state = 'subscription_wait'
    elif valid:
        state = ('subscription_wait' if max(percentages) >= 100 else
                 'handoff_margin' if max(percentages) >= 95 else 'available')
    return {
        'state': state,
        'observed_at_unix': observed_at,
        'windows': {name: {key: window.get(key) for key in
                          ('usedPercent', 'resetsAt', 'windowDurationMins')}
                    for name, window in windows.items()},
        'allow_extra_credits': False,
        'extra_credits_present': bool((limit.get('credits') or {}).get('hasCredits')),
        'source': 'official_codex_app_server_account/rateLimits/read',
    }


def probe(account, timeout=25):
    env = dict(os.environ)
    for name in ('OPENAI_API_KEY', 'CODEX_API_KEY', 'CODEX_ACCESS_TOKEN'):
        env.pop(name, None)
    # CODEX_HOME is the documented per-process credential/configuration root.
    env['CODEX_HOME'] = ACCOUNT_ROOTS[account]
    process = None
    selector = selectors.DefaultSelector()
    pending = bytearray()
    deadline = time.monotonic() + timeout
    cancelled = False
    previous_handlers = {}
    result = None

    def request_stop(*_):
        # Do not interrupt Popen before its child handle is assigned.
        nonlocal cancelled
        cancelled = True

    if threading.current_thread() is threading.main_thread():
        for signum in (signal.SIGINT, signal.SIGTERM):
            previous_handlers[signum] = signal.signal(signum, request_stop)
    try:
        process = subprocess.Popen([CODEX, 'app-server'], stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                   env=env, bufsize=0)
        selector.register(process.stdout, selectors.EVENT_READ)

        def send(value):
            process.stdin.write((json.dumps(value) + '\n').encode())
            process.stdin.flush()

        def response(request_id):
            while not cancelled and time.monotonic() < deadline:
                while b'\n' in pending:
                    line, _, rest = pending.partition(b'\n')
                    pending[:] = rest
                    if not line.strip():
                        continue
                    message = json.loads(line)
                    if message.get('id') == request_id:
                        if 'error' in message:
                            raise RuntimeError('rpc_rejected')
                        return message['result']
                if selector.select(timeout=min(1, max(0, deadline-time.monotonic()))):
                    chunk = os.read(process.stdout.fileno(), 65536)
                    if not chunk:
                        raise RuntimeError('server_exited')
                    pending.extend(chunk)
                    if len(pending) > 4 * 1024 * 1024:
                        raise RuntimeError('response_too_large')
            raise TimeoutError('probe_cancelled' if cancelled else 'probe_timeout')

        send({'id': 1, 'method': 'initialize', 'params': {
            'clientInfo': {'name': 'subscription_availability', 'version': '1.0'}}})
        response(1)
        send({'method': 'initialized'})
        send({'id': 2, 'method': 'account/rateLimits/read'})
        result = classify(response(2), time.time())
        if cancelled:
            raise TimeoutError('probe_cancelled')
        result['account'] = account
    except (OSError, RuntimeError, ValueError, KeyError, TimeoutError):
        result = None
    finally:
        selector.close()
        if process is not None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            for pipe in (process.stdin, process.stdout):
                if pipe is not None:
                    pipe.close()
        for signum, handler in previous_handlers.items():
            signal.signal(signum, handler)
    if cancelled or result is None:
        return {'account': account, 'state': 'unknown',
                'observed_at_unix': time.time(), 'allow_extra_credits': False}
    return result


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        try:
            json.dump(value, handle, indent=2)
            handle.write('\n')
            handle.flush()
            os.fsync(handle.fileno())
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--account', choices=tuple(ACCOUNT_ROOTS), required=True)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--require-available', action='store_true')
    args = parser.parse_args()
    result = probe(args.account)
    if args.output:
        save(args.output, result)
    if args.require_available:
        if result['state'] != 'available':
            print('Codex abonelik kotası yeni görev için uygun değil: ' + result['state'],
                  file=sys.stderr)
            return 3
    else:
        print(json.dumps(result))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
