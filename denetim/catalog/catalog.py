"""Exact source units and serial, content-bound preparation. No model or source writes."""

import argparse
import contextlib
import copy
import fcntl
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET

CATALOG_HOME = Path(__file__).resolve().parent
LIVE_HOME = CATALOG_HOME.parent
SOURCE_HOME = LIVE_HOME.parent.parent
PDF_HELPER_SHA256 = '7cabb8dec652fc3bd5fe394407556aa4794d6445951e6b56e1df63ce2f58448a'
EXTERIOR_CHUNK_SIZE = 500
MAX_UNITS_PER_EXTERIOR_CALL = 3  # Counts every unit in a call that includes exterior chunks.
PLAN_VERSIONS = (2, 3)


class SourceChanged(ValueError):
    pass


def strict_json(text):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(text, object_pairs_hook=unique)


def file_sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def leaves(value, pointer=()):
    if isinstance(value, dict) and value:
        for key, item in value.items():
            yield from leaves(item, pointer + (key,))
    elif isinstance(value, list) and value:
        for index, item in enumerate(value):
            yield from leaves(item, pointer + (index,))
    else:
        yield pointer, value


def json_units(value, limit=12000):
    units = []

    def emit(pointer, mode, **extra):
        units.append({"id": f"j{len(units) + 1:06d}", "pointer": list(pointer),
                      "mode": mode, **extra})

    def size(item):
        return len(json.dumps(item, ensure_ascii=False, separators=(",", ":")))

    def walk(item, pointer):
        if size(item) <= limit:
            emit(pointer, "node")
        elif isinstance(item, str):
            for start in range(0, len(item), limit):
                emit(pointer, "string_slice", start=start, end=min(start + limit, len(item)))
        elif isinstance(item, (dict, list)):
            pending, used = [], 2

            def flush():
                if not pending:
                    return
                if isinstance(item, dict):
                    emit(pointer, "keys", keys=list(pending))
                else:
                    emit(pointer, "slice", start=pending[0], end=pending[-1] + 1)
                pending.clear()

            pairs = item.items() if isinstance(item, dict) else enumerate(item)
            for key, child in pairs:
                cost = size(child) + (len(str(key)) + 4 if isinstance(item, dict) else 1)
                if cost > limit:
                    flush()
                    used = 2
                    walk(child, pointer + (key,))
                else:
                    if used + cost > limit:
                        flush()
                        used = 2
                    pending.append(key)
                    used += cost
            flush()
        else:
            emit(pointer, "node")

    walk(value, ())
    return units


def select(value, unit):
    for part in unit.get("pointer", []):
        value = value[part]
    mode = unit["mode"]
    if mode == "keys":
        return {key: value[key] for key in unit["keys"]}
    if mode in ("slice", "string_slice"):
        return value[unit["start"]:unit["end"]]
    return value


def unit_leaves(value, unit):
    pointer = tuple(unit.get("pointer", []))
    item = select(value, unit)
    if unit["mode"] == "slice":
        for index, child in enumerate(item, unit["start"]):
            yield from leaves(child, pointer + (index,))
    elif unit["mode"] == "string_slice":
        yield pointer + ((unit["start"], unit["end"]),), item
    else:
        yield from leaves(item, pointer)


def text_units(text, limit=12000):
    units, start, line = [], 0, 1
    while start < len(text):
        end = min(start + limit, len(text))
        if end < len(text):
            boundary = text.rfind("\n", start + limit // 2, end)
            if boundary >= 0:
                end = boundary + 1
        count = text[start:end].count("\n")
        units.append({"id": f"t{len(units) + 1:06d}", "start": start, "end": end,
                      "line_start": line, "line_end": line + count - int(text[end-1:end] == "\n")})
        start, line = end, line + count
    return units or [{"id": "t000001", "start": 0, "end": 0, "line_start": 1, "line_end": 1}]


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=".catalog-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def immutable(path, data):
    path = Path(path)
    if path.is_symlink():
        raise ValueError("Artifact must not be a symlink")
    if path.exists():
        if path.read_bytes() != data:
            raise SourceChanged(f"Prepared artifact differs: {path}")
        return
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=".artifact-")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(name, path)
        except FileExistsError:
            if path.is_symlink() or path.read_bytes() != data:
                raise SourceChanged(f"Prepared artifact differs: {path}")
    finally:
        Path(name).unlink(missing_ok=True)


def checked_source(root, entry):
    root = Path(root).resolve()
    relative = Path(entry["source"])
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("Source must be relative")
    source = (root / relative).resolve(strict=True)
    if not source.is_relative_to(root) or not source.is_file():
        raise ValueError("Source outside root")
    if file_sha(source) != entry["sha256"]:
        raise SourceChanged(entry["source"])
    return source


def render_verified(image, render):
    checksum = image.with_suffix(".sha256")
    if image.is_symlink() or checksum.is_symlink():
        raise SourceChanged("Image or integrity record is a symlink")
    if image.exists() and checksum.is_file():
        if checksum.read_text() != file_sha(image):
            raise SourceChanged(f"Existing image lacks matching integrity record: {image}")
        return
    fd, name = tempfile.mkstemp(dir=image.parent, prefix=".render-", suffix=".png")
    os.close(fd)
    temporary = Path(name)
    temporary.unlink()
    try:
        render(temporary)
        data = temporary.read_bytes()
        if image.exists() and image.read_bytes() != data:
            raise SourceChanged(f"Existing image differs from immutable source render: {image}")
        immutable(checksum, hashlib.sha256(data).hexdigest().encode())
        immutable(image, data)
    finally:
        temporary.unlink(missing_ok=True)


def prepare_text(root, prepared_root, entry, selected=None):
    source = checked_source(root, entry)
    data = source.read_bytes()
    if hashlib.sha256(data).hexdigest() != entry["sha256"]:
        raise SourceChanged(entry["source"])
    out = Path(prepared_root) / entry["sha256"] / "v2"
    out.mkdir(parents=True, exist_ok=True)
    if entry["kind"] == "image":
        target = out / ("source" + source.suffix)
        immutable(target, data)
        records = [{"id": "image000001", "image": str(target), "source": entry["source"]}]
    else:
        text = data.decode("utf-8")
        value = strict_json(text) if entry["kind"] == "json" else None
        records = []
        for unit in entry["units"]:
            if selected is not None and unit["id"] not in selected:
                continue
            if entry["kind"] == "json":
                content = json.dumps(select(value, unit), ensure_ascii=False, indent=2)
                suffix = ".json"
            else:
                content, suffix = text[unit["start"]:unit["end"]], ".txt"
            target = out / (unit["id"] + suffix)
            immutable(target, content.encode("utf-8"))
            records.append({**unit, "text": str(target), "source": entry["source"]})
    if file_sha(source) != entry["sha256"]:
        raise SourceChanged(entry["source"])
    return publish_manifest(out, entry, records)


def publish_manifest(out, entry, records):
    # Identical bytes can occur at distinct source paths. Keep provenance separate.
    source_key = hashlib.sha256(entry["source"].encode()).hexdigest()[:20]
    path = out / ("manifest-" + source_key + ".json")
    previous = json.loads(path.read_text()) if path.exists() else {}
    if previous and (previous.get("source") != entry["source"] or previous.get("sha256") != entry["sha256"]
                     or previous.get("plan_version") != entry.get("plan_version")):
        raise SourceChanged("Previous manifest provenance differs")
    planned = {unit["id"] for unit in entry["units"]}
    # Only a parent the catalog explicitly retired may leave the active list. Its record is kept.
    retired_ids = {unit["id"] for unit in entry.get("retired_units", []) if unit.get("retired") is True}
    retired = {unit["id"]: unit for unit in previous.get("retired_units", [])}
    by_id = {}
    for unit in previous.get("units", []):
        if unit["id"] not in planned and unit["id"] in retired_ids:
            retired[unit["id"]] = {**unit, "retired": True}
        else:
            by_id[unit["id"]] = unit
    by_id.update({unit["id"]: unit for unit in records})
    if not set(by_id) <= planned:
        raise SourceChanged("Previous manifest units differ")
    if not set(retired) <= retired_ids or set(retired) & set(by_id):
        raise SourceChanged("Previous manifest retired units differ")
    manifest = {"source": entry["source"], "sha256": entry["sha256"],
                "prepared": True, "prepared_scope": "listed_units_only",
                "prepared_units": len(by_id), "unit_total": len(entry["units"]),
                "complete": len(by_id) == len(entry["units"]), "review_state": "unverified",
                "manifest_path": str(path),
                "units": [by_id[key] for key in sorted(by_id)]}
    if retired:
        manifest["retired_units"] = [retired[key] for key in sorted(retired)]
    if entry.get("plan_version") is not None:
        manifest["plan_version"] = entry["plan_version"]
    atomic_json(path, manifest)
    return manifest


def prepare_pdf(root, live, entry, selected, chunk_plan=None):
    source = checked_source(root, entry)
    root, live = Path(root), Path(live)
    if file_sha(root / ".claude-denetim/pdf_scope.py") != PDF_HELPER_SHA256:
        raise SourceChanged("PDF helper changed; interface review required")
    spec = importlib.util.spec_from_file_location("audit_pdf_scope", root / ".claude-denetim/pdf_scope.py")
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    base = live / "pdf/snapshots"
    base.mkdir(parents=True, exist_ok=True)
    with (base / "prepare.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        digest, snapshot, cache = helper._snapshot(source, base)
        if digest != entry["sha256"]:
            raise SourceChanged(entry["source"])
        bbox = cache / "pages.xhtml"
        if not bbox.exists():
            temporary = cache / "catalog.tmp.xhtml"
            subprocess.run([str(helper.RUNTIME / "python/bin/python3"),
                            str(root / ".claude-denetim/pdf_words.py"), str(snapshot), str(temporary)],
                           check=True, capture_output=True, timeout=120)
            ET.parse(temporary)
            temporary.replace(bbox)
        pages = ET.parse(bbox).findall(".//h:page", helper.NS)
        out = live / "catalog/prepared" / digest / "v2"
        out.mkdir(parents=True, exist_ok=True)
        records = []
        for unit in entry["units"]:
            if unit["id"] not in selected:
                continue
            if "parent" in unit:
                raise ValueError("Exterior chunks use prepare_exterior_chunks")
            page = pages[unit["page"] - 1]
            width, height = math.ceil(float(page.get("width"))), math.ceil(float(page.get("height")))
            if unit.get("mode") == "exterior_text":
                words = [{"text": w.text or "", "bbox": [float(w.get(k)) for k in ("xMin", "yMin", "xMax", "yMax")]}
                         for w in page.findall(".//h:word", helper.NS)
                         if word_owner(w, float(page.get("width")), float(page.get("height"))) is None]
                target = out / (unit["id"] + ".json")
                immutable(target, json.dumps(words, ensure_ascii=False, indent=2).encode())
                records.append({**unit, "text": str(target), "word_count": len(words),
                                "visual_region": False, "source": entry["source"]})
                continue
            x, y = max(0, unit["col"] * 1400 - 80), max(0, unit["row"] * 1400 - 80)
            right, bottom = min(width, (unit["col"] + 1) * 1400 + 80), min(height, (unit["row"] + 1) * 1400 + 80)
            image, text = out / (unit["id"] + ".png"), out / (unit["id"] + ".txt")
            overview = out / ("p%04d-overview.png" % unit["page"])
            render_verified(image, lambda destination: helper._render(["-r", "72", "-f", str(unit["page"]), "-l", str(unit["page"]),
                                "-x", str(x), "-y", str(y), "-W", str(right-x), "-H", str(bottom-y),
                                "-singlefile", "-png"], snapshot, destination))
            render_verified(overview, lambda destination: helper._render(["-f", str(unit["page"]), "-l", str(unit["page"]), "-scale-to", "1600",
                                "-singlefile", "-png"], snapshot, destination))
            lines, context = [], []
            for line in page.findall(".//h:line", helper.NS):
                words = [w.text or "" for w in line.findall("h:word", helper.NS)
                         if word_owner(w, float(page.get("width")), float(page.get("height"))) == (unit["row"], unit["col"])]
                context_words = [w.text or "" for w in line.findall("h:word", helper.NS)
                         if x <= float(w.get("xMax")) and float(w.get("xMin")) <= right
                         and y <= float(w.get("yMax")) and float(w.get("yMin")) <= bottom
                         and word_owner(w, float(page.get("width")), float(page.get("height"))) != (unit["row"], unit["col"])]
                if words:
                    lines.append(" ".join(words))
                if context_words:
                    context.append(" ".join(context_words))
            immutable(text, "\n".join(lines).encode("utf-8"))
            context_path = out / (unit["id"] + "-context.txt")
            immutable(context_path, "\n".join(context).encode("utf-8"))
            records.append({**unit, "bbox": [x, y, right, bottom], "image": str(image),
                            "text": str(text), "context_text": str(context_path),
                            "text_ownership": "word_center_in_nonoverlapping_1400pt_cell",
                            "context_counts_as_coverage": False,
                            "overview": str(overview), "source": entry["source"]})
        manifest_target = manifest_dir(out, live, entry)
        if chunk_plan is not None:
            if chunk_plan["out"].resolve() != manifest_target.resolve():
                raise ValueError("Exterior chunks and visual units need one v3 manifest")
            records.extend(write_exterior_chunks(chunk_plan, entry))
            verify_exterior_plan(chunk_plan, entry)
        if file_sha(source) != digest:
            raise SourceChanged(entry["source"])
        return publish_manifest(manifest_target, entry, records)


PLAIN_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")


def plain_id(value):
    if not isinstance(value, str) or not PLAIN_ID.fullmatch(value) or ".." in value:
        raise ValueError(f"Identity must be a plain name: {value!r}")
    return value


def source_dirs(live, entry):
    """Return owned prepared/<source sha>, its v2 and v3 dirs. Every call uses this boundary."""
    prepared_root = (Path(live) / "catalog/prepared").resolve()
    if prepared_root != (CATALOG_HOME / "prepared").resolve():
        raise ValueError("Prepared root escapes catalog")
    digest = entry["sha256"]
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ValueError("Invalid source digest")
    base = prepared_root / digest
    dirs = (base, base / "v2", base / "v3")
    for path in dirs:
        if path.is_symlink() or (path.exists() and path.resolve() != path):
            raise ValueError(f"Source directory is not owned: {path}")
    return dirs


def manifest_dir(v2_out, live, entry):
    # Version 3 manifests live beside v2 and may reference unchanged v2 visual artifacts.
    source_dirs(live, entry)
    version = entry.get("plan_version", 2)
    if version == 2:
        return v2_out
    if version == 3:
        target = v2_out.parent / "v3"
        target.mkdir(exist_ok=True)
        source_dirs(live, entry)
        return target
    raise ValueError("Unsupported plan version")


def owned_path(base, relative):
    path = base / relative
    if path.is_symlink() or not path.resolve().is_relative_to(base):
        raise ValueError(f"Path escapes owned prepared root: {relative}")
    return path


def exterior_word_list(data):
    words = strict_json(data.decode("utf-8"))
    if not isinstance(words, list) or not words:
        raise ValueError("Exterior parent must be a non-empty word list")
    for word in words:
        bbox = word.get("bbox") if isinstance(word, dict) else None
        if (not isinstance(word, dict) or "index" in word or not isinstance(word.get("text"), str)
                or not isinstance(bbox, list) or len(bbox) != 4
                or any(isinstance(v, bool) or not isinstance(v, (int, float)) for v in bbox)):
            raise ValueError("Exterior parent word has an unexpected shape")
    return words


def check_chunk_ranges(units, total):
    position = 0
    for unit in sorted(units, key=lambda item: item.get("start") if isinstance(item.get("start"), int) else -1):
        start, end = unit.get("start"), unit.get("end")
        if any(isinstance(v, bool) or not isinstance(v, int) for v in (start, end)):
            raise ValueError(f"Chunk range is not integer: {unit['id']}")
        if start != position or end <= start or end > total:
            raise ValueError(f"Chunk ranges must cover each index exactly once: {unit['id']}")
        position = end
    if position != total:
        raise ValueError("Chunk ranges do not reach the parent word count")


def plan_exterior_split(entry, parent_id, parent_bytes, parent_sha256, size=EXTERIOR_CHUNK_SIZE):
    """Return a plan_version 3 copy of entry. The given entry is never mutated."""
    plain_id(parent_id)
    if isinstance(size, bool) or not isinstance(size, int) or size < 1:
        raise ValueError("Chunk size must be a positive integer")
    parent = next((unit for unit in entry["units"] if unit["id"] == parent_id), None)
    if (parent is None or parent.get("mode") != "exterior_text" or parent.get("visual_region") is not False
            or "parent" in parent):
        raise ValueError("Parent must be an existing exterior text unit")
    if hashlib.sha256(parent_bytes).hexdigest() != parent_sha256:
        raise SourceChanged("Exterior parent JSON digest differs")
    total = len(exterior_word_list(parent_bytes))
    children = [{"id": f"{parent_id}-s{number:03d}", "page": parent["page"], "mode": "exterior_text",
                 "visual_region": False, "parent": parent_id, "parent_sha256": parent_sha256,
                 "start": start, "end": min(start + size, total)}
                for number, start in enumerate(range(0, total, size), 1)]
    result = copy.deepcopy(entry)
    kept = [unit for unit in result["units"] if unit["id"] != parent_id]
    if {unit["id"] for unit in kept} & {unit["id"] for unit in children}:
        raise ValueError("Chunk identity collides with an existing unit")
    check_chunk_ranges(children, total)
    retired = {**copy.deepcopy(parent), "retired": True, "replaced_by": [unit["id"] for unit in children]}
    result.update(plan_version=3, units=kept + children,
                  retired_units=list(result.get("retired_units", [])) + [retired])
    return result


def exterior_chunk_plan(root, live, entry, selected):
    """Validate paths, digests and ranges and build chunk payloads. Writes nothing."""
    _, v2, out = source_dirs(live, entry)
    digest = entry["sha256"]
    units = [unit for unit in entry["units"] if unit["id"] in selected]
    for unit in units:
        plain_id(unit["id"])
    # A call may cross a page boundary. Each parent is validated on its own before any write.
    parent_ids = sorted({plain_id(unit.get("parent")) for unit in units})
    targets = {unit["id"]: owned_path(out, unit["id"] + ".json") for unit in units}
    source = checked_source(root, entry)
    parents, payloads = [], []
    for parent_id in parent_ids:
        siblings = [unit for unit in entry["units"] if unit.get("parent") == parent_id]
        digests = {unit.get("parent_sha256") for unit in siblings}
        if len(digests) != 1:
            raise ValueError("Exterior chunks disagree on the parent digest")
        parent_sha = digests.pop()
        if any(unit.get("mode") != "exterior_text" or unit.get("visual_region") is not False for unit in siblings):
            raise ValueError("Exterior chunks must not be visual regions")
        # Parent is always prepared/<this source sha>/v2/<plain id>.json, never another source.
        parent_path = owned_path(v2, parent_id + ".json")
        data = parent_path.read_bytes()
        if hashlib.sha256(data).hexdigest() != parent_sha:
            raise SourceChanged("Exterior parent JSON digest differs")
        words = exterior_word_list(data)
        check_chunk_ranges(siblings, len(words))
        parents.append((parent_path, parent_sha))
        for unit in sorted((u for u in units if u.get("parent") == parent_id), key=lambda item: item["start"]):
            content = {"parent": parent_id, "parent_sha256": parent_sha, "start": unit["start"], "end": unit["end"],
                       "words": [{"index": index, **words[index]} for index in range(unit["start"], unit["end"])]}
            payloads.append((unit, targets[unit["id"]],
                             json.dumps(content, ensure_ascii=False, indent=2).encode("utf-8")))
    if file_sha(source) != digest:
        raise SourceChanged(entry["source"])
    return {"out": out, "source": source, "parents": parents, "items": payloads}


def write_exterior_chunks(plan, entry):
    plan["out"].mkdir(exist_ok=True)
    records = []
    for unit, target, payload in plan["items"]:
        immutable(target, payload)
        records.append({**unit, "text": str(target), "word_count": unit["end"] - unit["start"],
                        "visual_region": False, "source": entry["source"]})
    return records


def verify_exterior_plan(plan, entry):
    if file_sha(plan["source"]) != entry["sha256"] or any(
            file_sha(path) != parent_sha for path, parent_sha in plan["parents"]):
        raise SourceChanged("Source or exterior parent changed during preparation")


def prepare_exterior_chunks(root, live, entry, selected):
    plan = exterior_chunk_plan(root, live, entry, selected)
    records = write_exterior_chunks(plan, entry)
    verify_exterior_plan(plan, entry)
    return publish_manifest(plan["out"], entry, records)


def word_owner(word, width, height):
    x = (float(word.get("xMin")) + float(word.get("xMax"))) / 2
    y = (float(word.get("yMin")) + float(word.get("yMax"))) / 2
    return (int(y // 1400), int(x // 1400)) if 0 <= x < width and 0 <= y < height else None


@contextlib.contextmanager
def catalog_lock(already_held=False):
    """The one lock for catalog reads, catalog writes and preparation."""
    if already_held:
        yield
        return
    with (CATALOG_HOME / "prepare.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield


def update_totals(document):
    groups = {}
    for entry in document["sources"]:
        groups.setdefault(entry["sha256"], []).append(entry)
    document.update(source_count=len(document["sources"]),
                    unit_count=sum(len(entry["units"]) for entry in document["sources"]),
                    unique_content_unit_count=sum(len(items[0]["units"]) for items in groups.values()),
                    unique_content_count=len(groups))
    return document


def split(catalog_path, source_id, parent_id):
    """Replace one large exterior parent with a version 3 child plan. Idempotent for the same parent.

    Reads only the catalog, the source PDF and the v2 parent JSON. Never reads ledger, state or backlog.
    """
    path = CATALOG_HOME / "catalog.json"
    if Path(catalog_path).resolve() != path:
        raise ValueError("Catalog path outside owned catalog")
    plain_id(parent_id)
    with catalog_lock():
        document = strict_json(path.read_text(encoding="utf-8"))
        if (Path(document["source_root"]).resolve() != SOURCE_HOME
                or Path(document["live_root"]).resolve() != LIVE_HOME):
            raise ValueError("Catalog roots differ from owned paths")
        matches = [i for i, item in enumerate(document["sources"]) if item.get("id") == source_id]
        if len(matches) != 1:
            raise ValueError("Unknown source")
        index = matches[0]
        entry = document["sources"][index]
        if entry.get("kind") != "pdf":
            raise ValueError("Only PDF exterior parents can be split")
        if sum(item.get("sha256") == entry["sha256"] for item in document["sources"]) != 1:
            raise ValueError("Duplicate content entries would diverge")
        version = entry.get("plan_version", 2)
        if version not in PLAN_VERSIONS:
            raise ValueError("Unsupported plan version")
        # An unsplit parent stays in units, also in a version 3 entry with another split page.
        # A split parent is in retired_units and is checked idempotently.
        unsplit = [unit for unit in entry["units"] if unit.get("id") == parent_id]
        retired = [unit for unit in entry.get("retired_units", []) if unit.get("id") == parent_id]
        already_split = bool(retired)
        parent = retired if already_split else unsplit
        if (len(unsplit) + len(retired) != 1 or parent[0].get("mode") != "exterior_text"
                or "parent" in parent[0] or (already_split and version != 3)):
            raise ValueError("Parent must be one exterior text unit of this source")
        _, v2, _ = source_dirs(Path(document["live_root"]), entry)
        source = checked_source(document["source_root"], entry)
        parent_path = owned_path(v2, parent_id + ".json")
        if not parent_path.is_file():
            raise ValueError("Exterior parent JSON is not prepared")
        parent_bytes = parent_path.read_bytes()
        parent_sha = hashlib.sha256(parent_bytes).hexdigest()
        words = exterior_word_list(parent_bytes)
        if already_split:
            planned = entry
            children = [unit for unit in entry["units"] if unit.get("parent") == parent_id]
            if not children or {unit.get("parent_sha256") for unit in children} != {parent_sha}:
                raise SourceChanged("Exterior parent JSON differs from the version 3 plan")
            check_chunk_ranges(children, len(words))
        else:
            if len(words) <= EXTERIOR_CHUNK_SIZE:
                raise ValueError("Exterior parent has 500 or fewer words; no split needed")
            planned = plan_exterior_split(entry, parent_id, parent_bytes, parent_sha)
        # Source and parent must be unchanged from planning until the catalog write.
        if file_sha(source) != entry["sha256"] or file_sha(parent_path) != parent_sha:
            raise SourceChanged("Source or exterior parent changed during split")
        if not already_split:
            document["sources"][index] = planned
            atomic_json(path, update_totals(document))
        return {"source_id": planned["id"], "source": planned["source"], "sha256": planned["sha256"],
                "parent_id": parent_id, "parent_sha256": parent_sha,
                "child_ids": [unit["id"] for unit in planned["units"] if unit.get("parent") == parent_id],
                "plan_version": 3, "catalog_sha256": file_sha(path)}


def previous_v3_entries():
    path = CATALOG_HOME / "catalog.json"
    if not path.exists():
        return {}
    document = strict_json(path.read_text(encoding="utf-8"))
    return {entry["id"]: entry for entry in document.get("sources", []) if entry.get("plan_version") == 3}


def prepare(catalog_path, source_id, unit_ids):
    if Path(catalog_path).resolve() != CATALOG_HOME / "catalog.json":
        raise ValueError("Catalog path outside owned catalog")
    wanted = set(unit_ids)
    if not wanted:
        raise ValueError("Unknown or empty units")
    # The catalog is read under the same lock that guards preparation and publication.
    with (CATALOG_HOME / "prepare.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        catalog = json.loads(Path(catalog_path).read_text())
        if Path(catalog["source_root"]).resolve() != SOURCE_HOME or Path(catalog["live_root"]).resolve() != LIVE_HOME:
            raise ValueError("Catalog roots differ from owned paths")
        entry = next(item for item in catalog["sources"] if item["id"] == source_id)
        units = {unit["id"]: unit for unit in entry["units"]}
        if not wanted <= set(units):
            raise ValueError("Unknown or empty units")
        if entry.get("plan_version", 2) not in PLAN_VERSIONS or (
                entry.get("plan_version", 2) == 3 and entry["kind"] != "pdf"):
            raise ValueError("Unsupported plan version")
        live = Path(catalog["live_root"])
        if not (live / "catalog/prepared").resolve().is_relative_to(CATALOG_HOME):
            raise ValueError("Prepared root escapes catalog")
        source_dirs(live, entry)  # Same source directory boundary for every call type, before any write.
        chunks ={uid for uid in wanted if "parent" in units[uid]}
        if chunks:
            if entry["kind"] != "pdf" or entry.get("plan_version") != 3:
                raise ValueError("Exterior chunks require a version 3 PDF plan")
            if len(wanted) > MAX_UNITS_PER_EXTERIOR_CALL:
                raise ValueError("Too many units in one call with exterior chunks")
            visual = wanted - chunks
            if not visual:
                return prepare_exterior_chunks(catalog["source_root"], live, entry, chunks)
            # Validate chunks before any visual artifact is rendered or written.
            plan = exterior_chunk_plan(catalog["source_root"], live, entry, chunks)
            return prepare_pdf(catalog["source_root"], live, entry, visual, plan)
        if entry["kind"] == "pdf":
            return prepare_pdf(catalog["source_root"], live, entry, wanted)
        return prepare_text(catalog["source_root"], live / "catalog/prepared", entry, wanted)


def build(root, live, lock_held=False):
    """Plan the catalog. Existing version 3 plans are kept. Writes nothing; main writes under the lock."""
    root, live = Path(root).resolve(), Path(live).resolve()
    if root != SOURCE_HOME or live != LIVE_HOME:
        raise ValueError("Build roots differ from owned paths")
    with catalog_lock(lock_held):
        return _build(root, live, previous_v3_entries())


def _build(root, live, previous):
    inventory = json.loads((live / "inventory/source-inventory-001.json").read_text())
    pdfs = {item["path"]: item for item in json.loads((live / "inventory/pdf-coverage-001.json").read_text())["pdfs"]}
    sources, errors = [], []
    for index, record in enumerate(inventory["files"], 1):
        entry = {"id": f"S{index:04d}", "source": record["path"], "sha256": record["sha256"],
                 "kind": "text", "units": [], "review_state": "unverified", "prepared": False}
        try:
            source = checked_source(root, entry)
            if record["type"] == ".pdf":
                entry["kind"] = "pdf"
                for page in pdfs[record["path"]]["pages"]:
                    for region in page["regions"]:
                        _, row, col = region["id"].split("-")
                        entry["units"].append({"id": region["id"], "page": page["page"],
                                               "row": int(row[1:]), "col": int(col[1:])})
                    entry["units"].append({"id": f"p{page['page']:04d}-text-exterior", "page": page["page"],
                                           "mode": "exterior_text", "visual_region": False})
            elif record["type"] in (".png", ".jpg", ".webp"):
                entry.update(kind="image", units=[{"id": "image000001"}])
            else:
                data = source.read_bytes()
                if hashlib.sha256(data).hexdigest() != entry["sha256"]:
                    raise SourceChanged(entry["source"])
                text = data.decode("utf-8")
                if record["type"] == ".json":
                    entry.update(kind="json", units=json_units(strict_json(text)))
                else:
                    entry["units"] = text_units(text)
            if file_sha(source) != entry["sha256"]:
                raise SourceChanged(entry["source"])
            if not entry["units"]:
                raise ValueError("Source has no planned units")
        except (OSError, ValueError, KeyError) as exc:
            entry["preparation_error"] = type(exc).__name__
            errors.append({"source": entry["source"], "error": str(exc)})
        sources.append(entry)
    # Fail closed: a version 3 plan is kept only for the same id, source path and source SHA.
    for source_id, old in previous.items():
        index = next((i for i, item in enumerate(sources) if item["id"] == source_id), None)
        current = sources[index] if index is not None else None
        if (current is None or current.get("preparation_error") or current["source"] != old["source"]
                or current["sha256"] != old["sha256"]):
            raise SourceChanged(f"Version 3 plan source changed or missing: {source_id}")
        sources[index] = copy.deepcopy(old)
    groups = {}
    for entry in sources:
        groups.setdefault(entry["sha256"], []).append(entry)
    for digest, entries in groups.items():
        for entry in entries:
            entry.update(content_group=digest, duplicate_of=entries[0]["id"] if entry != entries[0] else None,
                         duplicate_paths=[item["source"] for item in entries])
    return {"schema": 2, "source_root": str(root), "live_root": str(live),
            "inventory_sha256": file_sha(live / "inventory/source-inventory-001.json"),
            "sources": sources, "errors": errors, "source_count": len(sources),
            "unit_count": sum(len(item["units"]) for item in sources),
            "unique_content_unit_count": sum(len(items[0]["units"]) for items in groups.values()),
            "unique_content_count": len(groups), "plan_valid": not errors,
            "review_note": "Planned units are not prepared or accepted. Duplicate content is not independent evidence."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build", "prepare"))
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--live", type=Path)
    parser.add_argument("--source-id")
    parser.add_argument("--units", nargs="+")
    args = parser.parse_args()
    if args.command == "build":
        if not args.root or not args.live:
            parser.error("build requires root and live")
        if args.catalog.resolve() != CATALOG_HOME / "catalog.json":
            parser.error("Catalog output must be the owned catalog.json")
        # One lock from reading the previous catalog until the new catalog is written.
        with catalog_lock():
            result = build(args.root, args.live, lock_held=True)
            atomic_json(args.catalog, result)
        print(json.dumps({"sources": result["source_count"], "units": result["unit_count"], "errors": result["errors"]}))
        if result["errors"]:
            raise SystemExit(2)
    else:
        print(json.dumps(prepare(args.catalog, args.source_id, args.units), ensure_ascii=False))


if __name__ == "__main__":
    main()
