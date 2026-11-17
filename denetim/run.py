"""Run one read-only Claude audit and atomically publish a numbered report."""

import fcntl
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile
from datetime import datetime
from zoneinfo import ZoneInfo

from pdf_scope import prepare_scope, sha256


ROOT = Path(__file__).resolve().parent.parent
CLAUDE = Path("/Users/w6x/.local/bin/claude")
MARKER = "<!-- claude-denetim "
HEADINGS = (
    "Geliştirme odaklı eleştiri",
    "Farkında olmadığımız bilinmeyenler",
    "İhtiyaçlar ve çözüm önerileri",
    "Bütünsel mimariye etkisi",
    "Kanıtlar ve doğrulama sınırları",
    "Veri ve iş akışı dökümü",
    "Dot araçlarıyla karşılaştırma",
)
SCHEMA = {
    "type": "object",
    "properties": {
        "primary_finding_key": {"type": "string"},
        "primary_finding_title": {"type": "string"},
        "finding_status": {
            "type": "string", "enum": ["confirmed", "unverified", "no_new_issue"]
        },
        "covered_need_ids": {"type": "array", "items": {"type": "string"}},
        "report_markdown": {"type": "string"},
        "unit_reviews": {"type": "array", "items": {
            "type": "object", "properties": {
                "unit_id": {"type": "string"},
                "status": {"type": "string", "enum": ["complete", "partial", "unreadable"]},
                "item_ids": {"type": "array", "items": {"type": "string"}},
                "next_cursor": {"type": "string"}},
            "required": ["unit_id", "status", "item_ids", "next_cursor"],
            "additionalProperties": False}},
    },
    "required": ["primary_finding_key", "primary_finding_title", "finding_status",
                 "covered_need_ids", "report_markdown", "unit_reviews"],
    "additionalProperties": False,
}


def read_history(root: Path):
    """Read metadata embedded in complete reports, without separate mutable state."""
    history = []
    numbers = []
    for path in root.iterdir():
        if not re.fullmatch(r"[0-9]+\.md", path.name):
            continue
        number = int(path.stem)
        if number < 101:
            continue
        numbers.append(number)
        if path.is_symlink() or not path.is_file():
            continue
        with path.open(encoding="utf-8") as handle:
            first = handle.readline().strip()
        if first.startswith(MARKER) and first.endswith(" -->"):
            entry = json.loads(first[len(MARKER):-4])
            entry["number"] = number
            entry["report"] = str(path)
            history.append(entry)
    return sorted(history, key=lambda item: item["number"]), max(numbers, default=100) + 1


def validate_result(result, history):
    if not isinstance(result, dict):
        raise ValueError("Claude yanıtı beklenen biçimde değil.")
    for key in ["primary_finding_key", "primary_finding_title", "report_markdown"]:
        if not isinstance(result.get(key), str) or not result[key].strip():
            raise ValueError("Claude yanıtında zorunlu metin eksik: " + key)
    if result.get("finding_status") not in {"confirmed", "unverified", "no_new_issue"}:
        raise ValueError("Bulgunun doğrulama durumu eksik.")
    ids = result.get("covered_need_ids")
    if not isinstance(ids, list) or any(not isinstance(item, str) for item in ids):
        raise ValueError("İncelenen ihtiyaçların listesi eksik.")
    report = result["report_markdown"]
    if len(report) < 1500 or any("## " + heading not in report for heading in HEADINGS):
        raise ValueError("Raporun zorunlu bölümleri eksik.")
    key = result["primary_finding_key"].strip().casefold()
    if result["finding_status"] != "no_new_issue" and any(
        item["primary_finding_key"].strip().casefold() == key for item in history
    ):
        raise ValueError("Önceki ana bulgu yeni bulgu olarak tekrarlandı.")
    scope = result.get("pdf_scope") or {}
    expected = {unit["id"] for unit in scope.get("regions", [])}
    reviews = result.get("unit_reviews")
    if not isinstance(reviews, list):
        raise ValueError("Ayrıntılı inceleme kaydı eksik.")
    seen = set()
    for unit in reviews:
        uid = unit.get("unit_id")
        if uid not in expected or uid in seen:
            raise ValueError("İnceleme kaydı seçilen PDF bölgesiyle eşleşmiyor.")
        seen.add(uid)
        if unit.get("status") not in {"complete", "partial", "unreadable"}:
            raise ValueError("Bölge inceleme durumu geçersiz.")
        items = unit.get("item_ids")
        if not isinstance(items, list) or any(not isinstance(item, str) for item in items):
            raise ValueError("Veri ve akış öğelerinin kimlikleri eksik.")
        if unit["status"] == "complete" and not items:
            raise ValueError("Öğe kaydı olmadan tamamlanmış inceleme yazılamaz.")
        if any(not item.startswith(uid + "/") or item not in report for item in items):
            raise ValueError("Kapsam kaydındaki öğenin raporda değerlendirmesi bulunamadı.")
        if unit["status"] != "complete" and not unit.get("next_cursor"):
            raise ValueError("Kalan bölümün devam kaydı eksik.")
    if seen != expected:
        raise ValueError("Bazı PDF bölgelerinin inceleme durumu yazılmamış.")


def publish_report(root: Path, number: int, text: str):
    """Publish a complete file without replacing any existing file."""
    target = root / (str(number) + ".md")
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=root / ".claude-denetim",
        prefix="report-", suffix=".tmp", delete=False
    ) as handle:
        temporary = Path(handle.name)
        try:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    try:
        os.link(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)
    return target


def run_once(root: Path, reviewer):
    """Select the least recently reviewed folder while holding an OS lock."""
    control = root / ".claude-denetim"
    control.mkdir(exist_ok=True)
    with (control / "run.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return {"status": "already_running"}
        history, number = read_history(root)
        folders = [p for p in root.iterdir() if p.is_dir() and not p.is_symlink()
                   and not p.name.startswith(".") and p.name not in
                   {"node_modules", "__pycache__", "venv"}]
        if not folders:
            raise ValueError("Denetlenecek klasör bulunamadı.")
        last = {item["folder"]: item["number"] for item in history}
        folder = min(folders, key=lambda p: (last.get(p.name, 0), p.name.casefold(), p.name))
        result = reviewer(folder, history, number)
        validate_result(result, history)
        source_scope = result.get("pdf_scope")
        if source_scope and sha256(Path(source_scope["source"])) != source_scope["sha256"]:
            raise ValueError("PDF inceleme sırasında değişti. Eski kapsam kaydı kabul edilmedi.")
        metadata = {k: v for k, v in result.items() if k != "report_markdown"}
        metadata.update({"number": number, "folder": folder.name,
                         "created_at": datetime.now(ZoneInfo("Europe/Istanbul")).isoformat()})
        text = MARKER + json.dumps(metadata, ensure_ascii=False) + " -->\n\n"
        text += result["report_markdown"].rstrip() + "\n"
        path = publish_report(root, number, text)
        return {"status": "written", "number": number, "folder": folder.name,
                "report": str(path), "finding_status": result["finding_status"]}


def ask_claude(folder: Path, history, number: int):
    """Use the installed Claude account, with read and research tools only."""
    contract = (ROOT / ".claude-denetim" / "GOREV.md").read_text(encoding="utf-8")
    dot_context = "\n\n".join(path.read_text(encoding="utf-8")
                              for path in sorted((ROOT / ".claude-denetim").glob("DOT-*.md")))
    pdf_context = prepare_scope(ROOT, folder, history)
    context = {"selected_folder": str(folder), "report_number": number,
               "previous_reports": history,
               "pdf_context": pdf_context,
               "started_at": datetime.now(ZoneInfo("Europe/Istanbul")).isoformat()}
    prompt = (contract + "\n\n" + dot_context + "\n\nÇalışma bilgileri:\n"
              + json.dumps(context, ensure_ascii=False))
    print(json.dumps({"status": "reviewing", "folder": folder.name,
                      "pdf": (pdf_context.get("selected") or {}).get("source")},
                     ensure_ascii=False), flush=True)
    read_tools = "Read,Glob,Grep,WebSearch,WebFetch"
    command = [str(CLAUDE), "--print", "--output-format", "json",
               "--json-schema", json.dumps(SCHEMA),
               "--tools", read_tools, "--allowedTools", read_tools,
               "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
               "--permission-mode", "dontAsk", "--permission-prompts", "none",
               "--no-session-persistence", "--disable-slash-commands", "--no-chrome"]
    with subprocess.Popen(command, cwd=str(ROOT), stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True, start_new_session=True) as process:
        try:
            stdout, _ = process.communicate(prompt, timeout=1500)
        except BaseException:
            # Include child processes so a timed-out run cannot outlive its lock.
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.communicate()
            raise
        if process.returncode:
            raise RuntimeError("Claude tamamlanamadı. Çıkış kodu: " + str(process.returncode))
    envelope = json.loads(stdout)
    if envelope.get("is_error"):
        raise RuntimeError("Claude başarısız sonuç döndürdü. Rapor oluşturulmadı.")
    if envelope.get("permission_denials"):
        raise RuntimeError("Claude gerekli okuma iznine ulaşamadı. Rapor oluşturulmadı.")
    result = envelope.get("structured_output")
    if isinstance(result, dict):
        result["pdf_scope"] = pdf_context["selected"]
    return result


def handle_stop(signum, frame):
    """Unwind through child cleanup before the run lock is released."""
    # Ignore repeated shutdown signals while the child group is being reaped.
    for stop_signal in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
        signal.signal(stop_signal, signal.SIG_IGN)
    raise RuntimeError("Denetim durduruldu.")


def main():
    for stop_signal in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
        signal.signal(stop_signal, handle_stop)
    try:
        print(json.dumps(run_once(ROOT, ask_claude), ensure_ascii=False))
    except Exception as error:
        print(json.dumps({"status": "failed", "error": str(error)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
