"""Observe official Claude statusLine data without making model or auth requests.

Only quota windows and a one-way change marker are persisted. This is a cached
CLI observation, not a fresh provider query, admission grant or billing limit.
"""

import argparse
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import tempfile
import time

ROOT = Path('/Users/w6x/.config/claude-denetim/claude-observations')
WORKTREE = Path('/Users/w6x/.config/claude-denetim/workspace/worktrees/dosya-denetimi')
ACCOUNTS = ('01', '02', '03', '04', '05')
WINDOWS = ('five_hour', 'seven_day')


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def normalize(payload, account, now):
    windows = {}
    rates = payload.get('rate_limits')
    rates = rates if isinstance(rates, dict) else {}
    for key in WINDOWS:
        window = rates.get(key)
        if not isinstance(window, dict):
            windows[key] = None
            continue
        used, reset = window.get('used_percentage'), window.get('resets_at')
        windows[key] = {'used_percent': used, 'resets_at': reset} if (
            number(used) and 0 <= used <= 100 and number(reset) and reset > 0
        ) else None
    return {
        'account': account, 'source': 'official_claude_statusLine',
        'observed_at_unix': now, 'received_at_unix': now, 'windows': windows,
        'change_marker': hashlib.sha256(json.dumps(windows, sort_keys=True).encode()).hexdigest(),
        'allow_extra_credits': False,
        'fresh_provider_query': False,
    }


def classify(data, now, max_age=120):
    result = {key: data.get(key) for key in ('account', 'source', 'observed_at_unix', 'windows')}
    result.update(state='unknown', allow_extra_credits=False, fresh_provider_query=False)
    observed = data.get('observed_at_unix')
    windows = data.get('windows') or {}
    present = [windows.get(key) for key in WINDOWS]
    if not number(observed) or observed > now or now - observed > max_age:
        return result
    valid = [w for w in present if isinstance(w, dict)
             and number(w.get('used_percent')) and 0 <= w['used_percent'] <= 100
             and number(w.get('resets_at')) and w['resets_at'] > now]
    if any(w['used_percent'] >= 100 for w in valid):
        result['state'] = 'subscription_wait'
    elif any(w['used_percent'] >= 95 for w in valid):
        result['state'] = 'handoff_margin'
    elif len(valid) == len(WINDOWS):
        result['state'] = 'observed_headroom'
    return result


def atomic_write(path, data):
    fd, name = tempfile.mkstemp(prefix='.usage-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            json.dump(data, handle, ensure_ascii=False)
            handle.write('\n')
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def capture(root, account, payload, now):
    if account not in ACCOUNTS or not isinstance(payload, dict):
        raise ValueError('Invalid account or payload')
    session = payload.get('session_id')
    if not isinstance(session, str) or not session or len(session) > 256:
        raise ValueError('Missing session identity')
    directory = Path(root) / account
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    path = directory / (hashlib.sha256(session.encode()).hexdigest() + '.json')
    with (directory / '.lock').open('a') as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        try:
            previous = json.loads(path.read_text())
        except (FileNotFoundError, json.JSONDecodeError):
            previous = {}
        data = normalize(payload, account, now)
        if data['change_marker'] == previous.get('change_marker'):
            data['observed_at_unix'] = previous.get('observed_at_unix', now)
        blocked = [w for w in data['windows'].values() if isinstance(w, dict)
                   and w['used_percent'] >= 100 and w['resets_at'] > now]
        previous_blocks = previous.get('blocked_windows') or []
        data['blocked_windows'] = [w for w in previous_blocks if w['resets_at'] > now] + blocked
        data['blocked_windows'] = list({json.dumps(w, sort_keys=True): w for w in data['blocked_windows']}.values())
        atomic_write(path, data)
    return data


def read_account(root, account, now, max_age=120):
    if account not in ACCOUNTS:
        raise ValueError('Invalid account')
    rows = []
    for path in (Path(root) / account).glob('*.json'):
        try:
            row = json.loads(path.read_text())
            if isinstance(row, dict) and row.get('account') == account:
                rows.append(row)
        except (OSError, json.JSONDecodeError):
            continue
    unknown = {'account': account, 'state': 'unknown', 'windows': {},
               'allow_extra_credits': False, 'source': 'official_claude_statusLine',
               'fresh_provider_query': False}
    # Exhaustion cannot be cleared by another idle session's stale low snapshot.
    blocked = [w for row in rows for w in row.get('blocked_windows', [])
               if isinstance(w, dict) and number(w.get('resets_at')) and w['resets_at'] > now]
    if blocked:
        return dict(unknown, state='subscription_wait', blocked_windows=blocked)
    rows.sort(key=lambda row: row.get('observed_at_unix', 0), reverse=True)
    if not rows:
        return unknown
    return classify(rows[0], now, max_age=max_age)


def inferred_account():
    config = os.environ.get('CLAUDE_CONFIG_DIR')
    if not config or Path(config).resolve() == Path('/Users/w6x/.claude'):
        return '01'
    for account in ACCOUNTS[1:]:
        if Path(config).resolve() == Path('/Users/w6x/.config/claude-denetim/accounts') / account:
            return account
    raise ValueError('Unknown config directory')


def main(argv=None):
    parser = argparse.ArgumentParser(description='Claude usage observation')
    parser.add_argument('--read', choices=ACCOUNTS)
    args = parser.parse_args(argv)
    try:
        now = time.time()
        if args.read:
            print(json.dumps(read_account(ROOT, args.read, now)))
            return 0
        raw = sys.stdin.read(1024 * 1024 + 1)
        if len(raw) > 1024 * 1024:
            raise ValueError('Input too large')
        payload = json.loads(raw)
        workspace = payload.get('workspace') or {}
        cwd = workspace.get('current_dir') or payload.get('cwd')
        if not isinstance(cwd, str) or Path(cwd).resolve() != WORKTREE:
            return 0
        account = inferred_account()
        data = capture(ROOT, account, payload, now)
        details = ['%s %s%%' % (key, value['used_percent'])
                   for key, value in data['windows'].items() if isinstance(value, dict)]
        print('Claude %s: %s' % (account, ', '.join(details) or 'Kullanım bilgisi bekleniyor'))
        return 0
    except (OSError, ValueError, TypeError, AttributeError):
        # Do not echo stdin, transcript paths or authentication data on errors.
        if args.read:
            print(json.dumps({'account': args.read, 'state': 'unknown', 'allow_extra_credits': False}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
