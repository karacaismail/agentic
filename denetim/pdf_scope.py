"""Prepare bounded, readable PDF regions and retain content-based coverage."""

import fcntl
import hashlib
import math
import os
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET


TILE = 1400
BATCH = 3
NS = {"h": "http://www.w3.org/1999/xhtml"}
RUNTIME = Path("/Users/w6x/.cache/codex-runtimes/codex-primary-runtime/dependencies")
RENDERER = RUNTIME / "native/poppler/bin/pdftoppm"


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def choose_pending(inventory, history):
    """Only complete regions for the same bytes count toward coverage."""
    completed = set()
    for entry in history:
        scope = entry.get("pdf_scope") or {}
        for item in entry.get("unit_reviews", []):
            if item.get("status") == "complete":
                completed.add((scope.get("sha256"), item["unit_id"]))
    for source in inventory:
        pending = [unit for unit in source["units"]
                   if (source["sha256"], unit["id"]) not in completed]
        if pending:
            return source, pending[:BATCH]
    return None, []


def prepare_scope(root: Path, folder: Path, history):
    """Extract text geometry, then render only the next unreviewed regions."""
    # Preparing is serialized; reading finished regions remains parallel.
    # v2 never trusts images extracted from mutable source paths by v1.
    base = root / ".claude-denetim" / "pdf-cache-v2"
    base.mkdir(parents=True, exist_ok=True)
    with (base / "prepare.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        return _prepare_scope(root, folder, history, base)


def _snapshot(source, base):
    """Bind extraction and rendering to the exact bytes named by the digest."""
    with tempfile.NamedTemporaryFile(dir=base, suffix=".pdf", delete=False) as out:
        temporary = Path(out.name)
        try:
            with source.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    out.write(chunk)
            out.flush()
            os.fsync(out.fileno())
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    try:
        digest = sha256(temporary)
        if digest != sha256(source):
            raise RuntimeError("PDF kopyalanırken kaynak değişti: " + str(source))
        cache = base / digest
        cache.mkdir(exist_ok=True)
        snapshot = cache / "source.pdf"
        if not snapshot.exists():
            temporary.replace(snapshot)
            snapshot.chmod(0o444)
        elif sha256(snapshot) != digest:
            raise RuntimeError("PDF kaynak kopyası değişmiş: " + str(snapshot))
        return digest, snapshot, cache
    finally:
        temporary.unlink(missing_ok=True)


def _render(arguments, source, target):
    """Publish only a complete renderer result, never a partial target image."""
    with tempfile.TemporaryDirectory(dir=target.parent) as temporary:
        prefix = Path(temporary) / "page"
        subprocess.run([str(RENDERER)] + arguments + [str(source), str(prefix)],
                       check=True, capture_output=True, timeout=120)
        prefix.with_suffix(".png").replace(target)


def _publish_text(target, content):
    """Readers retain a complete version while the next version is prepared."""
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=target.parent,
                                     delete=False) as handle:
        temporary = Path(handle.name)
        try:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    try:
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)


def _prepare_scope(root, folder, history, base):
    inventory = []
    pdfs = sorted((p for p in folder.rglob("*.pdf") if not p.is_symlink()
                   and not any(part.startswith(".") or part == "node_modules"
                               for part in p.relative_to(folder).parts)),
                  key=lambda p: p.name)
    for source in pdfs:
        if any(parent.is_symlink() for parent in source.parents if parent != root):
            continue
        digest, snapshot, cache = _snapshot(source, base)
        bbox = cache / "pages.xhtml"
        if not bbox.exists():
            temp = cache / "pages.tmp.xhtml"
            subprocess.run([str(RUNTIME / "python/bin/python3"),
                            str(Path(__file__).with_name("pdf_words.py")), str(snapshot), str(temp)],
                           check=True, capture_output=True, timeout=120)
            ET.parse(temp)
            temp.replace(bbox)
        pages = ET.parse(bbox).findall(".//h:page", NS)
        if not pages:
            raise ValueError("PDF sayfa envanteri çıkarılamadı: " + source.name)
        units = []
        for page_number, page in enumerate(pages, 1):
            width, height = float(page.get("width")), float(page.get("height"))
            for row in range(math.ceil(height / TILE)):
                for col in range(math.ceil(width / TILE)):
                    units.append({"id": "p%04d-r%03d-c%03d" % (page_number, row, col),
                                  "page": page_number, "x": col * TILE, "y": row * TILE,
                                  "width": min(TILE, math.ceil(width) - col * TILE),
                                  "height": min(TILE, math.ceil(height) - row * TILE)})
        inventory.append({"source": str(source), "snapshot": str(snapshot), "sha256": digest,
                          "page_count": len(pages), "units": units})
        if choose_pending([inventory[-1]], history)[0] is not None:
            break
    chosen, selected = choose_pending(inventory, history)
    summary = [{"source": item["source"], "sha256": item["sha256"],
                "page_count": item["page_count"], "region_count": len(item["units"])}
               for item in inventory]
    if chosen is None:
        return {"inventory": summary, "selected": None,
                "note": "PDF bölgesi kalmadı. Akışların bütününü ve diğer kaynakları inceleyin."}
    source = Path(chosen["snapshot"])
    cache = base / chosen["sha256"]
    pages = ET.parse(cache / "pages.xhtml").findall(".//h:page", NS)
    prepared = []
    for unit in selected:
        page = pages[unit["page"] - 1]
        prefix = cache / unit["id"]
        png = prefix.with_suffix(".png")
        # Overlap preserves labels and connectors crossing region boundaries.
        x, y = max(0, unit["x"] - 80), max(0, unit["y"] - 80)
        w, h = unit["width"] + unit["x"] - x + 80, unit["height"] + unit["y"] - y + 80
        if not png.exists():
            _render(["-r", "72", "-f", str(unit["page"]),
                            "-l", str(unit["page"]), "-x", str(x), "-y", str(y),
                            "-W", str(w), "-H", str(h), "-singlefile", "-png",
                            ], source, png)
        lines = []
        for line in page.findall(".//h:line", NS):
            words = [word.text or "" for word in line.findall("h:word", NS)
                     if x <= float(word.get("xMax")) and float(word.get("xMin")) <= x + w
                     and y <= float(word.get("yMax")) and float(word.get("yMin")) <= y + h]
            if words:
                lines.append(" ".join(words))
        text_path = prefix.with_suffix(".txt")
        _publish_text(text_path, "\n".join(lines))
        preview = cache / ("page-%04d-preview.png" % unit["page"])
        if not preview.exists():
            _render(["-f", str(unit["page"]), "-l", str(unit["page"]),
                     "-scale-to", "1600", "-singlefile", "-png"], source, preview)
        prepared.append(dict(unit, image=str(png), text=str(text_path), overview=str(preview)))
    return {"inventory": summary, "all_pdf_files": [str(p) for p in pdfs], "selected": {
        "source": chosen["source"], "sha256": chosen["sha256"],
        "page_count": chosen["page_count"], "region_count": len(chosen["units"]),
        "regions": prepared}}
