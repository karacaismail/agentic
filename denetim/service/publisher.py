"""Single deterministic publisher. Models propose content, never choose output paths."""

import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def durable_json(path, value):
    fd, name = tempfile.mkstemp(dir=path.parent, prefix='.publication-')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write('\n')
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
        sync_dir(path.parent)
    finally:
        Path(name).unlink(missing_ok=True)


def sync_dir(path):
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


class ReportPublisher:
    """Publish at most one report per proposal, using exclusive hard links and a journal.

    A crash after the report link but before the ledger update reuses the same inode.
    Existing unrelated numbered files are never overwritten or adopted.
    Validation checks evidence structure and source hashes, not the truth of analysis.
    The read-only coordinator is responsible for actual source comparison.
    """

    def __init__(self, owned_root, report_root, source_root, evidence_roots):
        self.owned_root = Path(owned_root).resolve(strict=True)
        self.report_root = Path(report_root).resolve(strict=True)
        self.source_root = Path(source_root).resolve(strict=True)
        if self.report_root != self.source_root:
            raise ValueError('Reports must be in the source root')
        self.evidence_roots = tuple(Path(p).resolve(strict=True) for p in evidence_roots)
        self.journals = self.owned_root / 'service/publications'
        self.journals.mkdir(parents=True, exist_ok=True)
        if not self.journals.resolve().is_relative_to(self.owned_root):
            raise ValueError('Publication directory escaped ownership')

    def _validate(self, report, proposal_id):
        required = {'report_id', 'markdown', 'source_refs', 'evidence_paths', 'needs'}
        if not isinstance(report, dict) or set(report) != required:
            raise ValueError('Report schema differs')
        for value in (proposal_id, report['report_id']):
            if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,100}', value):
                raise ValueError('Invalid publication identity')
        markdown = report['markdown']
        if not isinstance(markdown, str) or len(markdown.strip()) < 100 or len(markdown) > 200000:
            raise ValueError('Report text missing or too large')
        for key in ('source_refs', 'evidence_paths', 'needs'):
            if not isinstance(report[key], list) or not report[key]:
                raise ValueError(f'{key} must be a nonempty list')
        units = set()
        for ref in report['source_refs']:
            if not isinstance(ref, dict) or set(ref) != {'source', 'sha256', 'unit_ids'}:
                raise ValueError('Source reference schema differs')
            relative = Path(ref['source'])
            if relative.is_absolute() or '..' in relative.parts:
                raise ValueError('Source reference must stay in source root')
            source = (self.source_root / relative).resolve(strict=True)
            if not source.is_relative_to(self.source_root) or not source.is_file():
                raise ValueError('Source reference escaped root')
            if sha_bytes(source.read_bytes()) != ref['sha256']:
                raise ValueError('Source changed since comparison')
            if not isinstance(ref['unit_ids'], list) or not ref['unit_ids'] or not all(isinstance(u, str) and u for u in ref['unit_ids']):
                raise ValueError('Source unit identities missing')
            units.update(ref['unit_ids'])
        for value in report['evidence_paths']:
            path = Path(value).resolve(strict=True)
            if not path.is_file() or not any(path.is_relative_to(root) for root in self.evidence_roots):
                raise ValueError('Evidence path outside allowed roots')
        fields = {'need', 'source_items', 'tool_or_llm_process', 'unknowns_experiment', 'limits',
                  'internal_risks', 'external_risks', 'sustainability'}
        for need in report['needs']:
            if not isinstance(need, dict) or set(need) != fields:
                raise ValueError('Need analysis is incomplete')
            if any(not isinstance(need[k], str) or not need[k].strip() for k in fields - {'source_items'}):
                raise ValueError('Need analysis text missing')
            items = need['source_items']
            if not isinstance(items, list) or not items or not all(
                isinstance(item, str) and any(item.startswith(unit + '/') for unit in units) for item in items
            ):
                raise ValueError('Need is not tied to source items')

    @staticmethod
    def _publish_link(body, target):
        os.link(body, target)
        sync_dir(target.parent)

    def publish(self, report, proposal_id):
        if not isinstance(report, dict):
            raise ValueError('Report must be an object')
        for identity in (proposal_id, report.get('report_id')):
            if not isinstance(identity, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,100}', identity):
                raise ValueError('Invalid publication identity')
        payload = json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
        payload_sha = sha_bytes(payload)
        key = sha_bytes(proposal_id.encode())
        folder = self.journals / key
        with (self.journals / 'publisher.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            folder.mkdir(exist_ok=True)
            if folder.is_symlink():
                raise ValueError('Journal must not be a symlink')
            journal_path, body = folder / 'journal.json', folder / 'body.md'
            journal = json.loads(journal_path.read_text()) if journal_path.exists() else None
            if journal and journal['payload_sha256'] != payload_sha:
                raise ValueError('Same publication identity has different content')
            if journal is None:
                self._validate(report, proposal_id)
                text = '# Analiz raporu\n\n'
                text += 'Bu rapor yalnız aşağıdaki kaynak birimlerini kapsar.\n'
                text += 'Yazıcı kaynak özetini ve çıktı biçimini denetledi.\n'
                text += 'Kaynak karşılaştırmasının kapsamı raporda ve bağlı kanıtlarda açıklanır.\n'
                text += 'Dosyanın yayımlanması tek başına kabul kararı değildir.\n'
                text += 'Kaynak okuması, çalışan uygulamanın doğrulandığı anlamına gelmez.\n\n'
                text += report['markdown'].rstrip() + '\n\n'
                text += '## İhtiyaçların süreç ve deney karşılığı\n\n'
                for n, need in enumerate(report['needs'], 1):
                    text += f"### {n}. {need['need']}\n\n"
                    for field, label in [('source_items', 'Kaynak öğeleri'), ('tool_or_llm_process', 'Araç veya dil modeli süreci'),
                                         ('unknowns_experiment', 'Bilinmeyeni sınayan deney'), ('internal_risks', 'İç riskler'),
                                         ('external_risks', 'Dış riskler'), ('sustainability', 'Sürdürülebilirlik'), ('limits', 'Kanıt sınırı')]:
                        value = ', '.join(need[field]) if field == 'source_items' else need[field]
                        text += f'**{label}:** {value}\n\n'
                text += '## Kaynak kapsamı\n\n'
                for ref in report['source_refs']:
                    text += f"- {ref['source']}: {', '.join(ref['unit_ids'])}. SHA256 `{ref['sha256']}`.\n"
                text += '\n## Doğrulama kanıtları\n\n'
                text += '\n'.join(f'- {path}' for path in report['evidence_paths']) + '\n\n'
                text += 'Gerçek okurla denenmedi. Teknik kimlikler ve yollar uzunluk istisnasıdır.\n'
                body_bytes = text.encode('utf-8')
                fd, temp = tempfile.mkstemp(dir=folder, prefix='.body-')
                try:
                    with os.fdopen(fd, 'wb') as handle:
                        handle.write(body_bytes)
                        handle.flush()
                        os.fsync(handle.fileno())
                    os.chmod(temp, 0o444)
                    try:
                        os.link(temp, body)
                    except FileExistsError:
                        if body.is_symlink() or body.read_bytes() != body_bytes:
                            raise ValueError('Journal body differs')
                finally:
                    Path(temp).unlink(missing_ok=True)
                journal = {'proposal_id': proposal_id, 'report_id': report['report_id'], 'payload_sha256': payload_sha,
                           'sha256': sha_bytes(body_bytes), 'status': 'prepared', 'path': None}
                durable_json(journal_path, journal)
            if body.is_symlink() or sha_bytes(body.read_bytes()) != journal['sha256']:
                raise ValueError('Journal body was changed')
            if journal['path']:
                target = Path(journal['path'])
                if target.parent != self.report_root or not re.fullmatch(r'[0-9]+\.md', target.name):
                    raise ValueError('Journal target escaped report root')
                if target.exists() and not target.is_symlink() and os.path.samefile(body, target):
                    journal['status'] = 'published'
                    durable_json(journal_path, journal)
                    return {k: journal[k] for k in ('path', 'sha256', 'report_id', 'proposal_id', 'status')}
                if journal['status'] == 'published':
                    raise ValueError('Published report was removed or replaced')
            # A journal alone is not publication. Recheck sources before a new link.
            self._validate(report, proposal_id)
            while True:
                numbers = [int(p.stem) for p in self.report_root.iterdir() if re.fullmatch(r'[0-9]+\.md', p.name)]
                for saved in self.journals.glob('*/journal.json'):
                    prior_path = json.loads(saved.read_text()).get('path')
                    if prior_path:
                        prior = Path(prior_path)
                        if prior.parent != self.report_root or not re.fullmatch(r'[0-9]+\.md', prior.name):
                            raise ValueError('Historical publication path differs')
                        numbers.append(int(prior.stem))
                number = max([102] + numbers) + 1
                target = self.report_root / f'{number}.md'
                journal.update(path=str(target), status='prepared')
                durable_json(journal_path, journal)
                try:
                    self._publish_link(body, target)
                except FileExistsError:
                    continue
                journal['status'] = 'published'
                durable_json(journal_path, journal)
                return {k: journal[k] for k in ('path', 'sha256', 'report_id', 'proposal_id', 'status')}


def publish(report, proposal_id):
    """Production callback. Output roots are code-owned, never model-supplied."""
    live = Path(__file__).resolve().parent.parent
    source = live.parent.parent
    proposals = Path('/Users/w6x/.config/claude-denetim/codex-proposals')
    return ReportPublisher(live, source, source, [live, proposals]).publish(report, proposal_id)
