import builtins
import copy
import fcntl
import hashlib
import io
import json
import os
import pathlib
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
import catalog

EXTERIOR_TOTAL = 27929
PARENT_ID = "p0001-text-exterior"
VISUAL_IDS = [f"p0001-r{r:03d}-c{c:03d}" for r in range(3) for c in range(3)]


def exterior_words(total=EXTERIOR_TOTAL):
    # Short words, digits, punctuation, empty text and duplicates must all survive.
    samples = ["Agent", ".", "2", "8", "a", "", "I", "-", "otomasyon", "x", "Agent", "0"]
    return [{"text": samples[i % len(samples)],
             "bbox": [-6679.47113 + i * 0.123456789, -39672.835938 + i / 7,
                      -6612.535880168 + i * 0.123456789, -39648.835938 + i / 7]}
            for i in range(total)]


def s0032_v2_entry(digest):
    units = [{"id": uid, "page": 1, "row": int(uid[7:10]), "col": int(uid[12:15])} for uid in VISUAL_IDS]
    units.append({"id": PARENT_ID, "page": 1, "mode": "exterior_text", "visual_region": False})
    return {"id": "S0032", "source": "agents/11Agentic.pdf", "sha256": digest, "kind": "pdf",
            "units": units, "review_state": "unverified", "prepared": False}


def chunk_units(parent_sha, total, size=500):
    return [{"id": f"{PARENT_ID}-s{n:03d}", "page": 1, "mode": "exterior_text", "visual_region": False,
             "parent": PARENT_ID, "parent_sha256": parent_sha, "start": start,
             "end": min(start + size, total)}
            for n, start in enumerate(range(0, total, size), 1)]


class LiveFixture:
    """Temporary copy of the live layout. The real catalog, ledger and PDF are never touched."""

    def __init__(self, td, total=EXTERIOR_TOTAL):
        base = Path(td).resolve()
        self.root, self.live = base / "source", base / "live"
        self.catalog_home = self.live / "catalog"
        self.prepared = self.catalog_home / "prepared"
        self.pdf = self.root / "agents/11Agentic.pdf"
        self.pdf.parent.mkdir(parents=True)
        self.pdf.write_bytes(b"%PDF-1.7 fixture, content is only hashed\n")
        self.digest = catalog.file_sha(self.pdf)
        self.v2 = self.prepared / self.digest / "v2"
        self.v2.mkdir(parents=True)
        self.words = exterior_words(total)
        self.parent_bytes = json.dumps(self.words, ensure_ascii=False, indent=2).encode()
        self.parent_path = self.v2 / (PARENT_ID + ".json")
        self.parent_path.write_bytes(self.parent_bytes)
        self.parent_sha = hashlib.sha256(self.parent_bytes).hexdigest()
        self.chunks = chunk_units(self.parent_sha, total)
        visual = [unit for unit in s0032_v2_entry(self.digest)["units"] if unit["id"] in VISUAL_IDS]
        self.entry = {**s0032_v2_entry(self.digest), "plan_version": 3, "units": visual + self.chunks,
                      "retired_units": [{"id": PARENT_ID, "page": 1, "mode": "exterior_text",
                                         "visual_region": False, "retired": True}]}
        self.catalog_path = self.catalog_home / "catalog.json"
        self.write_catalog([self.entry])

    def write_catalog(self, sources):
        self.catalog_path.write_text(json.dumps({"schema": 2, "source_root": str(self.root),
                                                 "live_root": str(self.live), "sources": sources}))

    def owned_paths(self):
        return patch.multiple(catalog, CATALOG_HOME=self.catalog_home, LIVE_HOME=self.live,
                              SOURCE_HOME=self.root)

    def tree(self):
        return {str(path.relative_to(self.prepared)): path.read_bytes()
                for path in self.prepared.rglob("*") if path.is_file()}

    def pdf_helper(self):
        """Install a fake PDF helper and word cache. Returns the helper digest patch."""
        helper = self.root / ".claude-denetim/pdf_scope.py"
        helper.parent.mkdir()
        helper.write_text(
            "import hashlib, pathlib\n"
            "NS = {'h': 'http://www.w3.org/1999/xhtml'}\n"
            "RUNTIME = None\n"
            "def _snapshot(source, base):\n"
            "    digest = hashlib.sha256(pathlib.Path(source).read_bytes()).hexdigest()\n"
            "    cache = pathlib.Path(base) / digest\n"
            "    cache.mkdir(parents=True, exist_ok=True)\n"
            "    return digest, pathlib.Path(source), cache\n"
            "def _render(args, snapshot, destination):\n"
            "    pathlib.Path(destination).write_bytes(('png:' + ' '.join(args)).encode())\n")
        cache = self.live / "pdf/snapshots" / self.digest
        cache.mkdir(parents=True)
        (cache / "pages.xhtml").write_text(
            '<html xmlns="http://www.w3.org/1999/xhtml"><body><doc>'
            '<page width="3360" height="3040"><line>'
            '<word xMin="1990" yMin="1990" xMax="2010" yMax="2010">8</word>'
            '<word xMin="-9000" yMin="-9000" xMax="-8990" yMax="-8990">2</word>'
            '</line></page></doc></body></html>')
        return patch.object(catalog, "PDF_HELPER_SHA256", catalog.file_sha(helper))


def lock_held(lock_path):
    fd = os.open(lock_path, os.O_RDWR | os.O_CREAT)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        return True
    else:
        fcntl.flock(fd, fcntl.LOCK_UN)
        return False
    finally:
        os.close(fd)


class FileObserver:
    """Record every opened path and whether prepare.lock is held at catalog read and replace."""

    def __init__(self, catalog_path, lock_path):
        self.catalog_path, self.lock_path = catalog_path, lock_path
        self.opened, self.catalog_reads, self.catalog_writes = set(), [], []
        self._patches = []

    def _seen(self, target):
        try:
            resolved = Path(os.fspath(target)).resolve()
        except TypeError:
            return
        self.opened.add(resolved)
        if resolved == self.catalog_path:
            self.catalog_reads.append(lock_held(self.lock_path))

    def __enter__(self):
        real_path_open, real_open, real_replace = pathlib.Path.open, builtins.open, os.replace
        observer = self

        def path_open(path, *args, **kwargs):
            observer._seen(path)
            return real_path_open(path, *args, **kwargs)

        def plain_open(file, *args, **kwargs):
            observer._seen(file)
            return real_open(file, *args, **kwargs)

        def replace(src, dst, *args, **kwargs):
            if Path(os.fspath(dst)).resolve() == observer.catalog_path:
                observer.catalog_writes.append(lock_held(observer.lock_path))
            return real_replace(src, dst, *args, **kwargs)

        self._patches = [patch.object(pathlib.Path, "open", path_open), patch("builtins.open", plain_open),
                         patch.object(os, "replace", replace)]
        for item in self._patches:
            item.start()
        return self

    def __exit__(self, *exc):
        for item in reversed(self._patches):
            item.stop()
        return False


class SplitFixture(LiveFixture):
    """S0032 starts as a v2 plan beside one unrelated text source. Runtime files are decoys."""

    def __init__(self, td, total=1600):
        super().__init__(td, total)
        text = self.root / "notes/a.txt"
        text.parent.mkdir(parents=True)
        text.write_text("hello\n")
        text_sha = catalog.file_sha(text)
        self.other = {"id": "S0002", "source": "notes/a.txt", "sha256": text_sha, "kind": "text",
                      "units": [{"id": "t000001", "start": 0, "end": 6, "line_start": 1, "line_end": 1}],
                      "review_state": "unverified", "prepared": False, "content_group": text_sha,
                      "duplicate_of": None, "duplicate_paths": ["notes/a.txt"]}
        self.v2_entry = {**s0032_v2_entry(self.digest), "content_group": self.digest, "duplicate_of": None,
                         "duplicate_paths": ["agents/11Agentic.pdf"]}
        self.write_full([self.v2_entry, self.other])
        self.runtime = {self.live / "ledger.json": b'{"ledger": true}\n',
                        self.live / "service/state/state.json": b'{"state": true}\n',
                        self.catalog_home / "backlog.json": b'{"items": "not a plan source"}\n'}
        for path, data in self.runtime.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)

    def write_full(self, sources):
        catalog.atomic_json(self.catalog_path, full_catalog(self.root, self.live, sources))

    def runtime_untouched(self, observer=None):
        same = all(path.read_bytes() == data for path, data in self.runtime.items())
        unread = observer is None or not (set(self.runtime) & observer.opened)
        return same and unread

    def expected_v3(self):
        return catalog.plan_exterior_split(self.v2_entry, PARENT_ID, self.parent_bytes, self.parent_sha)


def full_catalog(root, live, sources):
    groups = {}
    for entry in sources:
        groups.setdefault(entry["sha256"], []).append(entry)
    return {"schema": 2, "source_root": str(root), "live_root": str(live), "inventory_sha256": "0" * 64,
            "sources": sources, "errors": [], "source_count": len(sources),
            "unit_count": sum(len(entry["units"]) for entry in sources),
            "unique_content_unit_count": sum(len(items[0]["units"]) for items in groups.values()),
            "unique_content_count": len(groups), "plan_valid": True, "review_note": "fixture"}


class CatalogTests(unittest.TestCase):
    def test_json_units_reconstruct_all_leaf_paths_without_omissions(self):
        value = {"rows": [{"id": i, "text": "a" * 90} for i in range(15)], "tail": "z" * 500}
        units = catalog.json_units(value, limit=220)
        rebuilt = {}
        fragments = {}
        for unit in units:
            for path, item in catalog.unit_leaves(value, unit):
                if unit["mode"] == "string_slice":
                    fragments.setdefault(path[:-1], []).append((path[-1], item))
                    continue
                self.assertNotIn(path, rebuilt)
                rebuilt[path] = item
        for path, pieces in fragments.items():
            end, joined = 0, ""
            for (start, stop), text in sorted(pieces):
                self.assertEqual(start, end)
                self.assertEqual(stop - start, len(text))
                joined += text
                end = stop
            self.assertNotIn(path, rebuilt)
            rebuilt[path] = joined
        expected = {("rows", i, "id"): i for i in range(15)}
        expected.update({("rows", i, "text"): "a" * 90 for i in range(15)})
        expected[("tail",)] = "z" * 500
        self.assertEqual(rebuilt, expected)
        self.assertGreater(len(units), 1)
        with self.assertRaisesRegex(ValueError, "Duplicate JSON key"):
            catalog.strict_json('{"id": 1, "id": 2}')

    def test_changed_source_is_refused_before_prepared_publication(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "a.json"
            source.write_text('{"id": 1}')
            digest = catalog.file_sha(source)
            original = catalog.immutable
            def mutate_after_artifact(path, data):
                original(path, data)
                source.write_text('{"id": 2}')
            with patch.object(catalog, "immutable", mutate_after_artifact):
                with self.assertRaises(catalog.SourceChanged):
                    catalog.prepare_text(root, root / "prepared", {"source": "a.json", "sha256": digest,
                        "kind": "json", "units": [{"id": "j000001", "pointer": [], "mode": "node"}]})
            self.assertEqual(list((root / "prepared").rglob("manifest*.json")), [])

    def test_interrupted_publication_leaves_no_partial_target(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "unit.txt"
            with patch.object(catalog.os, "link", side_effect=OSError("interrupted")):
                with self.assertRaises(OSError):
                    catalog.immutable(target, b"complete bytes")
            self.assertFalse(target.exists())
            catalog.immutable(target, b"complete bytes")
            self.assertEqual(target.read_bytes(), b"complete bytes")

    def test_partial_manifest_and_changed_provenance(self):
        with tempfile.TemporaryDirectory() as td:
            entry = {"source": "a.txt", "sha256": "a" * 64, "units": [{"id": "a"}, {"id": "b"}]}
            result = catalog.publish_manifest(Path(td), entry, [{"id": "a"}])
            self.assertEqual(result["prepared_units"], 1)
            self.assertFalse(result["complete"])
            entry["sha256"] = "b" * 64
            with self.assertRaises(catalog.SourceChanged):
                catalog.publish_manifest(Path(td), entry, [{"id": "b"}])

    def test_manifest_moves_only_catalog_retired_parent_and_keeps_other_refusals(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            base = {"source": "a.pdf", "sha256": "a" * 64, "plan_version": 3,
                    "units": [{"id": "old"}, {"id": "keep"}]}
            catalog.publish_manifest(out, base, [{"id": "old", "text": "old.json"}, {"id": "keep"}])
            retired = {**base, "units": [{"id": "keep"}, {"id": "old-s001"}],
                       "retired_units": [{"id": "old", "retired": True}]}
            result = catalog.publish_manifest(out, retired, [{"id": "old-s001"}])
            self.assertEqual([u["id"] for u in result["units"]], ["keep", "old-s001"])
            self.assertEqual(result["retired_units"], [{"id": "old", "text": "old.json", "retired": True}])
            again = catalog.publish_manifest(out, retired, [])
            self.assertEqual(again["retired_units"], result["retired_units"])
            path = Path(result["manifest_path"])
            for name, entry in {
                    "retired record no longer retired in catalog": {**retired, "retired_units": []},
                    "retired flag missing": {**retired, "retired_units": [{"id": "old"}]},
                    "changed sha": {**retired, "sha256": "b" * 64},
                    "changed plan version": {**retired, "plan_version": 2}}.items():
                with self.subTest(name):
                    before = path.read_bytes()
                    with self.assertRaises(catalog.SourceChanged):
                        catalog.publish_manifest(out, entry, [])
                    self.assertEqual(path.read_bytes(), before)
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            catalog.publish_manifest(out, base, [{"id": "old"}])
            path = next(out.glob("manifest-*.json"))
            before = path.read_bytes()
            for name, entry in {
                    "active id removed without retirement": {**base, "units": [{"id": "keep"}]},
                    "retired id without flag": {**base, "units": [{"id": "keep"}],
                                                "retired_units": [{"id": "old", "retired": False}]}}.items():
                with self.subTest(name), self.assertRaises(catalog.SourceChanged):
                    catalog.publish_manifest(out, entry, [])
                self.assertEqual(path.read_bytes(), before)

    def test_pdf_words_have_single_owner_or_explicit_exterior(self):
        word = {"xMin": "1390", "xMax": "1410", "yMin": "100", "yMax": "110"}
        self.assertEqual(catalog.word_owner(word, 3000, 2000), (0, 1))
        self.assertIsNone(catalog.word_owner(word, 1000, 2000))
        self.assertEqual(catalog.text_units("one\ntwo\n")[0]["line_end"], 2)

    def test_unverified_existing_image_is_not_blessed(self):
        with tempfile.TemporaryDirectory() as td:
            image = Path(td) / "region.png"
            image.write_bytes(b"corrupt")
            with self.assertRaises(catalog.SourceChanged):
                catalog.render_verified(image, lambda destination: destination.write_bytes(b'correct'))

    def test_image_publication_recovers_checksum_interruption(self):
        with tempfile.TemporaryDirectory() as td:
            image = Path(td) / 'region.png'
            def render(*paths):
                (paths[0] if paths else image).write_bytes(b'complete image')
            with patch.object(catalog, 'immutable', side_effect=OSError('crash')):
                with self.assertRaises(OSError):
                    catalog.render_verified(image, render)
            catalog.render_verified(image, render)
            self.assertEqual(image.read_bytes(), b'complete image')
            self.assertEqual(image.with_suffix('.sha256').read_text(), catalog.file_sha(image))
            image.with_suffix('.sha256').unlink()
            catalog.render_verified(image, render)
            self.assertEqual(image.with_suffix('.sha256').read_text(), catalog.file_sha(image))


class ExteriorSplitTests(unittest.TestCase):
    """Contract for splitting S0032 exterior text into 500-word reading units.

    Expected implementation surface (not yet present, so these tests fail first):
    - catalog.plan_exterior_split(entry, parent_id, parent_bytes, parent_sha256, size=500)
      returns a new plan_version 3 entry and never mutates the given entry.
    - catalog.prepare(...) prepares units carrying "parent"/"parent_sha256"/"start"/"end"
      from the existing v2 parent JSON. It writes one chunk JSON per requested unit:
      {"parent", "parent_sha256", "start", "end", "words": [{"index", "text", "bbox"}]}.
    Controller-owned rules (task start order, acceptance gate, ledger) are not tested here.
    """

    def test_plan_splits_27929_words_into_56_units_and_keeps_visual_identity(self):
        with tempfile.TemporaryDirectory() as td:
            fx = LiveFixture(td)
            old = s0032_v2_entry(fx.digest)
            before = copy.deepcopy(old)
            new = catalog.plan_exterior_split(old, PARENT_ID, fx.parent_bytes, fx.parent_sha)
        self.assertEqual(old, before, "Old catalog entry must stay unchanged")
        self.assertEqual(new["plan_version"], 3)
        self.assertEqual((new["id"], new["source"], new["sha256"]), (old["id"], old["source"], old["sha256"]))
        self.assertEqual(new["units"][:9], old["units"][:9], "Nine visual units keep identity")
        children = new["units"][9:]
        self.assertEqual(len(children), 56)
        self.assertEqual([u["end"] - u["start"] for u in children], [500] * 55 + [429])
        self.assertEqual(children[0]["start"], 0)
        self.assertEqual(children[-1]["end"], EXTERIOR_TOTAL)
        for previous, current in zip(children, children[1:]):
            self.assertEqual(previous["end"], current["start"])
        ids = [u["id"] for u in new["units"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertNotIn(PARENT_ID, ids, "New units must not inherit the old acceptance identity")
        for unit in children:
            self.assertEqual(unit["mode"], "exterior_text")
            self.assertIs(unit["visual_region"], False)
            self.assertEqual(unit["parent"], PARENT_ID)
            self.assertEqual(unit["parent_sha256"], fx.parent_sha)
            self.assertNotIn("row", unit)
            self.assertNotIn("col", unit)
        retired = [u for u in new["retired_units"] if u["id"] == PARENT_ID]
        self.assertEqual(len(retired), 1)
        self.assertIs(retired[0]["retired"], True)

    def test_plan_refuses_parent_digest_mismatch_and_non_exterior_parent(self):
        with tempfile.TemporaryDirectory() as td:
            fx = LiveFixture(td, total=1600)
            entry = s0032_v2_entry(fx.digest)
            with self.assertRaises(catalog.SourceChanged):
                catalog.plan_exterior_split(entry, PARENT_ID, fx.parent_bytes, "0" * 64)
            for parent in (VISUAL_IDS[0], "p0001-missing"):
                with self.assertRaises(ValueError):
                    catalog.plan_exterior_split(entry, parent, fx.parent_bytes, fx.parent_sha)

    def test_prepared_chunks_rebuild_original_words_exactly_once(self):
        with tempfile.TemporaryDirectory() as td:
            fx = LiveFixture(td)
            v2_before = {k: v for k, v in fx.tree().items() if k.startswith(fx.digest + "/v2/")}
            ids = [unit["id"] for unit in fx.chunks]
            with fx.owned_paths():
                for start in range(0, len(ids), 3):
                    manifest = catalog.prepare(fx.catalog_path, "S0032", ids[start:start + 3])
            records = {unit["id"]: unit for unit in manifest["units"]}
            self.assertEqual(set(records), set(ids))
            rebuilt = []
            for unit in fx.chunks:
                record = records[unit["id"]]
                self.assertEqual(record["mode"], "exterior_text")
                self.assertIs(record["visual_region"], False)
                self.assertNotIn("image", record)
                self.assertEqual(record["word_count"], unit["end"] - unit["start"])
                path = Path(record["text"])
                self.assertTrue(path.is_relative_to(fx.prepared / fx.digest))
                self.assertFalse(path.is_relative_to(fx.v2), "v2 artifacts stay untouched")
                data = json.loads(path.read_text())
                self.assertEqual((data["parent"], data["parent_sha256"], data["start"], data["end"]),
                                 (PARENT_ID, fx.parent_sha, unit["start"], unit["end"]))
                rebuilt.extend(data["words"])
            self.assertEqual([w["index"] for w in rebuilt], list(range(EXTERIOR_TOTAL)))
            self.assertEqual([{"text": w["text"], "bbox": w["bbox"]} for w in rebuilt], fx.words)
            self.assertEqual({k: v for k, v in fx.tree().items() if k.startswith(fx.digest + "/v2/")}, v2_before)

    def test_prepare_writes_only_requested_chunk(self):
        with tempfile.TemporaryDirectory() as td:
            fx = LiveFixture(td, total=1600)
            before = fx.tree()
            with fx.owned_paths():
                manifest = catalog.prepare(fx.catalog_path, "S0032", [fx.chunks[1]["id"]])
            added = {k for k in fx.tree() if k not in before and "/manifest-" not in "/" + k}
            record = next(u for u in manifest["units"] if u["id"] == fx.chunks[1]["id"])
            self.assertEqual(added, {str(Path(record["text"]).relative_to(fx.prepared))})
            self.assertEqual([u["id"] for u in manifest["units"]], [fx.chunks[1]["id"]])

    def test_prepare_refuses_more_than_three_units_before_writing(self):
        with tempfile.TemporaryDirectory() as td:
            fx = LiveFixture(td, total=1600)
            self.assertEqual(len(fx.chunks), 4)
            before = fx.tree()
            with fx.owned_paths(), self.assertRaises(ValueError):
                catalog.prepare(fx.catalog_path, "S0032", [u["id"] for u in fx.chunks])
            self.assertEqual(fx.tree(), before)

    def test_prepare_refuses_changed_source_pdf_before_writing(self):
        with tempfile.TemporaryDirectory() as td:
            fx = LiveFixture(td, total=1600)
            fx.pdf.write_bytes(b"%PDF-1.7 changed\n")
            before = fx.tree()
            with fx.owned_paths(), self.assertRaises(catalog.SourceChanged):
                catalog.prepare(fx.catalog_path, "S0032", [fx.chunks[0]["id"]])
            self.assertEqual(fx.tree(), before)

    def test_prepare_refuses_changed_parent_json_before_writing(self):
        with tempfile.TemporaryDirectory() as td:
            fx = LiveFixture(td, total=1600)
            tampered = copy.deepcopy(fx.words)
            tampered[2]["text"] = "3"
            fx.parent_path.write_bytes(json.dumps(tampered, ensure_ascii=False, indent=2).encode())
            before = fx.tree()
            with fx.owned_paths(), self.assertRaises(catalog.SourceChanged):
                catalog.prepare(fx.catalog_path, "S0032", [fx.chunks[0]["id"]])
            self.assertEqual(fx.tree(), before)

    def test_prepare_refuses_negative_overflowing_or_overlapping_ranges(self):
        cases = {"negative": (0, "start", -1), "overflow": (3, "end", 1601),
                 "overlap": (1, "start", 400), "gap": (1, "start", 501), "bool": (0, "start", False)}
        for name, (index, key, value) in cases.items():
            with self.subTest(name), tempfile.TemporaryDirectory() as td:
                fx = LiveFixture(td, total=1600)
                fx.chunks[index][key] = value
                fx.write_catalog([fx.entry])
                before = fx.tree()
                target = fx.chunks[2]["id"]
                with fx.owned_paths(), self.assertRaises(ValueError):
                    catalog.prepare(fx.catalog_path, "S0032", [target])
                self.assertEqual(fx.tree(), before)

    def test_v3_visual_unit_uses_normal_pdf_path_and_v3_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            fx = LiveFixture(td, total=1600)
            with fx.owned_paths(), fx.pdf_helper():
                manifest = catalog.prepare(fx.catalog_path, "S0032", ["p0001-r001-c001"])
            self.assertEqual(manifest["plan_version"], 3)
            self.assertTrue(Path(manifest["manifest_path"]).is_relative_to(fx.prepared / fx.digest / "v3"))
            self.assertEqual(list(fx.v2.glob("manifest-*.json")), [])
            record = manifest["units"][0]
            self.assertEqual(record["id"], "p0001-r001-c001")
            self.assertTrue(Path(record["image"]).is_relative_to(fx.v2))
            self.assertEqual(Path(record["text"]).read_text(), "8")

    def test_mixed_visual_and_exterior_call_prepares_all_three_in_one_v3_manifest(self):
        # The existing proposal contract allows up to three units of one source per call.
        with tempfile.TemporaryDirectory() as td:
            fx = LiveFixture(td, total=1600)
            visual, first, second = "p0001-r001-c001", fx.chunks[0]["id"], fx.chunks[1]["id"]
            v2_before = {k: v for k, v in fx.tree().items() if k.startswith(fx.digest + "/v2/")}
            with fx.owned_paths(), fx.pdf_helper():
                manifest = catalog.prepare(fx.catalog_path, "S0032", [visual, first, second])
            self.assertEqual(manifest["plan_version"], 3)
            self.assertTrue(Path(manifest["manifest_path"]).is_relative_to(fx.prepared / fx.digest / "v3"))
            self.assertEqual(list(fx.v2.glob("manifest-*.json")), [])
            records = {unit["id"]: unit for unit in manifest["units"]}
            self.assertEqual(set(records), {visual, first, second})
            self.assertTrue(Path(records[visual]["image"]).is_relative_to(fx.v2))
            self.assertEqual(Path(records[visual]["text"]).read_text(), "8")
            for uid, unit in ((first, fx.chunks[0]), (second, fx.chunks[1])):
                record = records[uid]
                self.assertIs(record["visual_region"], False)
                self.assertEqual(record["mode"], "exterior_text")
                self.assertNotIn("image", record)
                data = json.loads(Path(record["text"]).read_text())
                self.assertEqual([w["index"] for w in data["words"]], list(range(unit["start"], unit["end"])))
            v2_after = {k: v for k, v in fx.tree().items() if k.startswith(fx.digest + "/v2/")}
            self.assertEqual({k: v for k, v in v2_after.items() if k in v2_before}, v2_before,
                             "Existing v2 artifacts stay byte-identical")

    def test_mixed_call_with_changed_parent_writes_nothing(self):
        with tempfile.TemporaryDirectory() as td:
            fx = LiveFixture(td, total=1600)
            tampered = copy.deepcopy(fx.words)
            tampered[0]["bbox"][0] += 1
            fx.parent_path.write_bytes(json.dumps(tampered, ensure_ascii=False, indent=2).encode())
            before = fx.tree()
            with fx.owned_paths(), fx.pdf_helper(), self.assertRaises(catalog.SourceChanged):
                catalog.prepare(fx.catalog_path, "S0032", ["p0001-r001-c001", fx.chunks[0]["id"]])
            self.assertEqual(fx.tree(), before, "Visual artifacts must not be written when a chunk is refused")

    def test_mixed_call_still_refuses_more_than_three_units(self):
        with tempfile.TemporaryDirectory() as td:
            fx = LiveFixture(td, total=1600)
            before = fx.tree()
            wanted = ["p0001-r001-c001", "p0001-r001-c000"] + [u["id"] for u in fx.chunks[:2]]
            with fx.owned_paths(), fx.pdf_helper(), self.assertRaises(ValueError):
                catalog.prepare(fx.catalog_path, "S0032", wanted)
            self.assertEqual(fx.tree(), before)

    def test_chunk_parent_must_be_plain_id_under_own_source_v2(self):
        # Regression: a traversal parent bound another PDF's exterior text to source A.
        other_digest = "b" * 64
        cases = [f"../../{other_digest}/v2/{PARENT_ID}", f"../v2/{PARENT_ID}", f"sub/{PARENT_ID}",
                 f"/{PARENT_ID}", "..", ".", ""]
        for parent_id in cases:
            for mixed in (False, True):
                with self.subTest(parent_id=parent_id, mixed=mixed), tempfile.TemporaryDirectory() as td:
                    fx = LiveFixture(td, total=1600)
                    other = fx.prepared / other_digest / "v2"
                    other.mkdir(parents=True)
                    other_bytes = json.dumps(exterior_words(1600)[::-1], ensure_ascii=False, indent=2).encode()
                    (other / (PARENT_ID + ".json")).write_bytes(other_bytes)
                    for unit in fx.chunks:
                        unit["parent"] = parent_id
                        unit["parent_sha256"] = hashlib.sha256(other_bytes).hexdigest()
                    fx.write_catalog([fx.entry])
                    before = fx.tree()
                    wanted = (["p0001-r001-c001"] if mixed else []) + [fx.chunks[0]["id"]]
                    with fx.owned_paths(), fx.pdf_helper(), self.assertRaises(ValueError):
                        catalog.prepare(fx.catalog_path, "S0032", wanted)
                    self.assertEqual(fx.tree(), before, "No visual or chunk artifact may be written")

    def test_chunk_unit_id_must_be_plain(self):
        for unit_id in ("../escape", "a/b", "/abs", "..", ".", ""):
            for mixed in (False, True):
                with self.subTest(unit_id=unit_id, mixed=mixed), tempfile.TemporaryDirectory() as td:
                    fx = LiveFixture(td, total=1600)
                    fx.chunks[0]["id"] = unit_id
                    fx.write_catalog([fx.entry])
                    before = fx.tree()
                    wanted = (["p0001-r001-c001"] if mixed else []) + [unit_id]
                    with fx.owned_paths(), fx.pdf_helper(), self.assertRaises(ValueError):
                        catalog.prepare(fx.catalog_path, "S0032", wanted)
                    self.assertEqual(fx.tree(), before, "No visual or chunk artifact may be written")

    def test_plan_refuses_non_plain_parent_id(self):
        with tempfile.TemporaryDirectory() as td:
            fx = LiveFixture(td, total=1600)
        for parent_id in (f"../../{'b' * 64}/v2/{PARENT_ID}", f"sub/{PARENT_ID}", "..", ""):
            with self.subTest(parent_id=parent_id):
                entry = s0032_v2_entry(fx.digest)
                entry["units"][-1]["id"] = parent_id
                before = copy.deepcopy(entry)
                with self.assertRaises(ValueError):
                    catalog.plan_exterior_split(entry, parent_id, fx.parent_bytes, fx.parent_sha)
                self.assertEqual(entry, before)

    def test_symlinked_v3_dir_is_refused_for_every_call_type(self):
        # Regression: manifest_dir skipped the owned-root check on visual-only v3 calls.
        calls = {"visual": lambda fx: ["p0001-r001-c001"],
                 "chunk": lambda fx: [fx.chunks[0]["id"]],
                 "mixed": lambda fx: ["p0001-r001-c001", fx.chunks[0]["id"]]}
        for name, wanted in calls.items():
            with self.subTest(name), tempfile.TemporaryDirectory() as td:
                fx = LiveFixture(td, total=1600)
                outside = Path(td).resolve() / "outside"
                outside.mkdir()
                (fx.prepared / fx.digest / "v3").symlink_to(outside, target_is_directory=True)
                before = fx.tree()
                with fx.owned_paths(), fx.pdf_helper(), self.assertRaises(ValueError):
                    catalog.prepare(fx.catalog_path, "S0032", wanted(fx))
                self.assertEqual(list(outside.iterdir()), [], "Nothing may be written outside the owned root")
                self.assertEqual(fx.tree(), before, "No artifact may be written before the refusal")

    def test_catalog_is_read_while_prepare_lock_is_held(self):
        with tempfile.TemporaryDirectory() as td:
            fx = LiveFixture(td, total=10)
            text = fx.root / "a.txt"
            text.write_text("hello")
            fx.write_catalog([{"id": "S0001", "source": "a.txt", "sha256": catalog.file_sha(text),
                               "kind": "text", "units": [{"id": "t000001", "start": 0, "end": 5,
                                                          "line_start": 1, "line_end": 1}]}])
            lock_path = fx.catalog_home / "prepare.lock"
            observed = []
            real_path_open, real_open = pathlib.Path.open, builtins.open

            def check(target):
                try:
                    resolved = Path(os.fspath(target)).resolve()
                except TypeError:
                    return
                if resolved != fx.catalog_path:
                    return
                fd = os.open(lock_path, os.O_RDWR | os.O_CREAT)
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError:
                    observed.append(True)
                else:
                    fcntl.flock(fd, fcntl.LOCK_UN)
                    observed.append(False)
                finally:
                    os.close(fd)

            def path_open(self, *args, **kwargs):
                check(self)
                return real_path_open(self, *args, **kwargs)

            def plain_open(file, *args, **kwargs):
                check(file)
                return real_open(file, *args, **kwargs)

            with fx.owned_paths(), patch.object(pathlib.Path, "open", path_open), \
                    patch("builtins.open", plain_open):
                catalog.prepare(fx.catalog_path, "S0001", ["t000001"])
            self.assertTrue(observed, "Catalog read was not observed")
            self.assertTrue(all(observed), "Catalog must be read under live/catalog/prepare.lock")


class CatalogSplitTests(unittest.TestCase):
    """Contract for catalog.split(catalog_path, source_id, parent_id).

    It reads the current catalog under prepare.lock, verifies source and parent JSON digests,
    replaces only the given source with a version 3 child plan and rewrites totals atomically.
    It never reads or writes ledger, controller state or backlog.json.
    """

    def assert_refused(self, fx, call, error=ValueError):
        before = fx.catalog_path.read_bytes()
        prepared = fx.tree()
        with fx.owned_paths(), self.assertRaises(error):
            call()
        self.assertEqual(fx.catalog_path.read_bytes(), before)
        self.assertEqual(fx.tree(), prepared)
        self.assertEqual(list(fx.catalog_home.glob(".catalog-*")), [])
        self.assertTrue(fx.runtime_untouched())

    def test_split_writes_v3_plan_keeps_other_sources_and_updates_totals(self):
        with tempfile.TemporaryDirectory() as td:
            fx = SplitFixture(td)
            prepared = fx.tree()
            with fx.owned_paths(), FileObserver(fx.catalog_path, fx.catalog_home / "prepare.lock") as seen:
                result = catalog.split(fx.catalog_path, "S0032", PARENT_ID)
            expected = fx.expected_v3()
            child_ids = [unit["id"] for unit in expected["units"] if unit.get("parent") == PARENT_ID]
            self.assertEqual(len(child_ids), 4)
            self.assertEqual(result, {"source_id": "S0032", "source": "agents/11Agentic.pdf", "sha256": fx.digest,
                                      "parent_id": PARENT_ID, "parent_sha256": fx.parent_sha,
                                      "child_ids": child_ids, "plan_version": 3,
                                      "catalog_sha256": catalog.file_sha(fx.catalog_path)})
            document = {**full_catalog(fx.root, fx.live, [fx.v2_entry, fx.other]),
                        "sources": [expected, fx.other], "unit_count": 14, "unique_content_unit_count": 14}
            self.assertEqual(fx.catalog_path.read_text(), json.dumps(document, ensure_ascii=False, indent=2) + "\n")
            self.assertTrue(seen.catalog_reads and all(seen.catalog_reads), "Read catalog under prepare.lock")
            self.assertTrue(seen.catalog_writes and all(seen.catalog_writes), "Replace catalog under prepare.lock")
            self.assertTrue(fx.runtime_untouched(seen), "Ledger, state and backlog are not read or written")
            self.assertEqual(fx.tree(), prepared, "Planning writes no prepared artifact")
            self.assertEqual(list(fx.catalog_home.glob(".catalog-*")), [])

    def test_split_is_idempotent_for_existing_v3_plan_of_same_parent(self):
        with tempfile.TemporaryDirectory() as td:
            fx = SplitFixture(td)
            with fx.owned_paths():
                first = catalog.split(fx.catalog_path, "S0032", PARENT_ID)
                written = fx.catalog_path.read_bytes()
                second = catalog.split(fx.catalog_path, "S0032", PARENT_ID)
            self.assertEqual(second, first)
            self.assertEqual(fx.catalog_path.read_bytes(), written)

    def test_split_supports_second_large_parent_in_same_pdf_after_first_split(self):
        # Regression: after page 1 became version 3, the unsplit page 2 parent was refused.
        second_id = "p0002-text-exterior"
        with tempfile.TemporaryDirectory() as td:
            fx = SplitFixture(td)
            fx.v2_entry["units"].append({"id": second_id, "page": 2, "mode": "exterior_text",
                                         "visual_region": False})
            second_bytes = json.dumps(exterior_words(1200)[::-1], ensure_ascii=False, indent=2).encode()
            (fx.v2 / (second_id + ".json")).write_bytes(second_bytes)
            second_sha = hashlib.sha256(second_bytes).hexdigest()
            fx.write_full([fx.v2_entry, fx.other])
            after_first = catalog.plan_exterior_split(fx.v2_entry, PARENT_ID, fx.parent_bytes, fx.parent_sha)
            expected = catalog.plan_exterior_split(after_first, second_id, second_bytes, second_sha)
            with fx.owned_paths():
                first = catalog.split(fx.catalog_path, "S0032", PARENT_ID)
                second = catalog.split(fx.catalog_path, "S0032", second_id)
                written = fx.catalog_path.read_bytes()
                current = catalog.file_sha(fx.catalog_path)
                self.assertEqual(catalog.split(fx.catalog_path, "S0032", PARENT_ID),
                                 {**first, "catalog_sha256": current})
                self.assertEqual(catalog.split(fx.catalog_path, "S0032", second_id), second)
            self.assertEqual(fx.catalog_path.read_bytes(), written, "Repeated splits are idempotent")
            document = catalog.strict_json(written.decode())
            entry = document["sources"][0]
            self.assertEqual(entry, expected)
            first_children = [u for u in after_first["units"] if u.get("parent") == PARENT_ID]
            self.assertEqual([u for u in entry["units"] if u.get("parent") == PARENT_ID], first_children)
            self.assertEqual(entry["retired_units"][0], after_first["retired_units"][0])
            self.assertEqual([u["id"] for u in entry["retired_units"]], [PARENT_ID, second_id])
            self.assertEqual(second["parent_sha256"], second_sha)
            self.assertEqual(second["child_ids"], [f"{second_id}-s{n:03d}" for n in (1, 2, 3)])
            self.assertEqual([(u["start"], u["end"], u["page"]) for u in entry["units"]
                              if u.get("parent") == second_id], [(0, 500, 2), (500, 1000, 2), (1000, 1200, 2)])
            self.assertEqual(document["unit_count"], 9 + 4 + 3 + 1)
            self.assertEqual(second["catalog_sha256"], catalog.file_sha(fx.catalog_path))
            self.assertTrue(fx.runtime_untouched())

    def test_prepared_second_parent_then_split_still_allows_child_prepare(self):
        # Regression (MAJOR): split page 1, prepare the page 2 parent into the v3 manifest,
        # split page 2, then prepare page 2 children. The stale parent record in the v3
        # manifest must not block child preparation or remain an active unit.
        second_id = "p0002-text-exterior"
        with tempfile.TemporaryDirectory() as td:
            fx = SplitFixture(td)
            fx.v2_entry["units"].append({"id": second_id, "page": 2, "mode": "exterior_text",
                                         "visual_region": False})
            fx.write_full([fx.v2_entry, fx.other])
            helper_patch = fx.pdf_helper()
            samples = ["Agent", ".", "2", "8", "a", "I", "-", "0"]
            words_xml = "".join(
                f'<word xMin="{-5000 - i}" yMin="{100 + i}" xMax="{-4990 - i}" yMax="{110 + i}">'
                f'{samples[i % len(samples)]}</word>' for i in range(1200))
            (fx.live / "pdf/snapshots" / fx.digest / "pages.xhtml").write_text(
                '<html xmlns="http://www.w3.org/1999/xhtml"><body><doc>'
                '<page width="3360" height="3040"><line>'
                '<word xMin="1990" yMin="1990" xMax="2010" yMax="2010">8</word></line></page>'
                f'<page width="3360" height="3040"><line>{words_xml}</line></page>'
                '</doc></body></html>')
            with fx.owned_paths(), helper_patch:
                catalog.split(fx.catalog_path, "S0032", PARENT_ID)
                parent_manifest = catalog.prepare(fx.catalog_path, "S0032", [second_id])
                self.assertIn(second_id, [u["id"] for u in parent_manifest["units"]])
                second_path = fx.v2 / (second_id + ".json")
                self.assertTrue(second_path.is_file())
                second_words = json.loads(second_path.read_text())
                self.assertEqual(len(second_words), 1200)
                split_result = catalog.split(fx.catalog_path, "S0032", second_id)
                first_child = split_result["child_ids"][0]
                manifest = catalog.prepare(fx.catalog_path, "S0032", [first_child])
                other_parent_child = catalog.prepare(fx.catalog_path, "S0032", [f"{PARENT_ID}-s001"])
            records = {u["id"]: u for u in manifest["units"]}
            self.assertIn(first_child, records)
            self.assertIs(records[first_child]["visual_region"], False)
            data = json.loads(Path(records[first_child]["text"]).read_text())
            self.assertEqual([w["index"] for w in data["words"]], list(range(500)))
            self.assertEqual([{"text": w["text"], "bbox": w["bbox"]} for w in data["words"]], second_words[:500])
            for listed in (manifest, other_parent_child):
                active = [u for u in listed["units"] if u["id"] == second_id and u.get("retired") is not True]
                self.assertEqual(active, [], "A split parent must not stay an active manifest unit")
            self.assertIn(f"{PARENT_ID}-s001", [u["id"] for u in other_parent_child["units"]])
            self.assertTrue(fx.runtime_untouched())

    def two_split_parents(self, td):
        second_id = "p0002-text-exterior"
        fx = SplitFixture(td)
        fx.v2_entry["units"].append({"id": second_id, "page": 2, "mode": "exterior_text", "visual_region": False})
        second_words = exterior_words(1200)[::-1]
        second_path = fx.v2 / (second_id + ".json")
        second_path.write_bytes(json.dumps(second_words, ensure_ascii=False, indent=2).encode())
        fx.write_full([fx.v2_entry, fx.other])
        with fx.owned_paths():
            catalog.split(fx.catalog_path, "S0032", PARENT_ID)
            catalog.split(fx.catalog_path, "S0032", second_id)
        return fx, second_id, second_words, second_path

    def test_one_call_prepares_children_of_two_parents_in_one_manifest(self):
        # Regression (MAJOR): backlog batches of three can cross a page boundary.
        # Example: last child of page 1 plus first two children of page 2.
        for with_visual in (False, True):
            with self.subTest(with_visual=with_visual), tempfile.TemporaryDirectory() as td:
                fx, second_id, second_words, second_path = self.two_split_parents(td)
                first_last, second_a, second_b = f"{PARENT_ID}-s004", f"{second_id}-s001", f"{second_id}-s002"
                wanted = (["p0001-r001-c001", first_last, second_a] if with_visual
                          else [first_last, second_a, second_b])
                expected = {first_last: (PARENT_ID, fx.parent_sha, 1500, 1600, fx.words),
                            second_a: (second_id, catalog.file_sha(second_path), 0, 500, second_words),
                            second_b: (second_id, catalog.file_sha(second_path), 500, 1000, second_words)}
                with fx.owned_paths(), fx.pdf_helper():
                    manifest = catalog.prepare(fx.catalog_path, "S0032", wanted)
                records = {u["id"]: u for u in manifest["units"]}
                self.assertEqual(set(records), set(wanted), "All units share one v3 manifest")
                self.assertTrue(Path(manifest["manifest_path"]).is_relative_to(fx.prepared / fx.digest / "v3"))
                for uid in wanted:
                    if uid not in expected:
                        continue
                    parent, parent_sha, start, end, words = expected[uid]
                    record = records[uid]
                    self.assertIs(record["visual_region"], False)
                    data = json.loads(Path(record["text"]).read_text())
                    self.assertEqual((data["parent"], data["parent_sha256"], data["start"], data["end"]),
                                     (parent, parent_sha, start, end))
                    self.assertEqual([w["index"] for w in data["words"]], list(range(start, end)))
                    self.assertEqual([{"text": w["text"], "bbox": w["bbox"]} for w in data["words"]],
                                     words[start:end])

    def test_two_parent_call_refuses_when_either_parent_changed(self):
        for changed in ("first", "second"):
            with self.subTest(changed), tempfile.TemporaryDirectory() as td:
                fx, second_id, second_words, second_path = self.two_split_parents(td)
                target = fx.parent_path if changed == "first" else second_path
                words = json.loads(target.read_text())
                words[0]["text"] = "changed"
                target.write_bytes(json.dumps(words, ensure_ascii=False, indent=2).encode())
                before = fx.tree()
                wanted = [f"{PARENT_ID}-s004", f"{second_id}-s001", f"{second_id}-s002"]
                with fx.owned_paths(), self.assertRaises(catalog.SourceChanged):
                    catalog.prepare(fx.catalog_path, "S0032", wanted)
                self.assertEqual(fx.tree(), before, "No chunk or manifest may be written")

    def test_split_of_501_words_makes_two_children(self):
        with tempfile.TemporaryDirectory() as td:
            fx = SplitFixture(td, total=501)
            with fx.owned_paths():
                result = catalog.split(fx.catalog_path, "S0032", PARENT_ID)
            entry = catalog.strict_json(fx.catalog_path.read_text())["sources"][0]
            ranges = [(u["start"], u["end"]) for u in entry["units"] if u["id"] in result["child_ids"]]
            self.assertEqual(ranges, [(0, 500), (500, 501)])

    def test_split_refuses_parent_of_500_or_fewer_words(self):
        with tempfile.TemporaryDirectory() as td:
            fx = SplitFixture(td, total=500)
            self.assert_refused(fx, lambda: catalog.split(fx.catalog_path, "S0032", PARENT_ID))

    def test_split_refuses_changed_source_or_parent(self):
        def change_source(fx):
            fx.pdf.write_bytes(b"%PDF-1.7 changed\n")

        def change_parent(fx):
            words = copy.deepcopy(fx.words)
            words[3]["text"] = "9"
            fx.parent_path.write_bytes(json.dumps(words, ensure_ascii=False, indent=2).encode())

        for name, change in (("source", change_source), ("parent", change_parent)):
            # A v2 parent has no recorded digest, so a change before the first call is undetectable.
            # The first split must instead catch a change made while it plans.
            with self.subTest(name, during_first_split=True), tempfile.TemporaryDirectory() as td:
                fx = SplitFixture(td)
                before = fx.catalog_path.read_bytes()
                real_plan = catalog.plan_exterior_split

                def plan_then_change(*args, **kwargs):
                    planned = real_plan(*args, **kwargs)
                    change(fx)
                    return planned

                with fx.owned_paths(), patch.object(catalog, "plan_exterior_split", plan_then_change), \
                        self.assertRaises(catalog.SourceChanged):
                    catalog.split(fx.catalog_path, "S0032", PARENT_ID)
                self.assertEqual(fx.catalog_path.read_bytes(), before)
                self.assertEqual(list(fx.catalog_home.glob(".catalog-*")), [])
                self.assertTrue(fx.runtime_untouched())
            with self.subTest(name, after_split=True), tempfile.TemporaryDirectory() as td:
                fx = SplitFixture(td)
                with fx.owned_paths():
                    catalog.split(fx.catalog_path, "S0032", PARENT_ID)
                change(fx)
                self.assert_refused(fx, lambda: catalog.split(fx.catalog_path, "S0032", PARENT_ID),
                                    catalog.SourceChanged)

    def test_split_refuses_missing_parent_file(self):
        with tempfile.TemporaryDirectory() as td:
            fx = SplitFixture(td)
            fx.parent_path.unlink()
            self.assert_refused(fx, lambda: catalog.split(fx.catalog_path, "S0032", PARENT_ID), (OSError, ValueError))

    def test_split_refuses_unknown_source_non_exterior_or_non_plain_parent(self):
        cases = [("S9999", PARENT_ID), ("S0002", PARENT_ID), ("S0032", VISUAL_IDS[0]),
                 ("S0032", "p0001-missing"), ("S0032", f"../../{'b' * 64}/v2/{PARENT_ID}")]
        for source_id, parent_id in cases:
            with self.subTest(source_id=source_id, parent_id=parent_id), tempfile.TemporaryDirectory() as td:
                fx = SplitFixture(td)
                self.assert_refused(fx, lambda: catalog.split(fx.catalog_path, source_id, parent_id))

    def test_split_refuses_catalog_outside_owned_path(self):
        with tempfile.TemporaryDirectory() as td:
            fx = SplitFixture(td)
            copy_path = fx.catalog_home / "copy.json"
            copy_path.write_bytes(fx.catalog_path.read_bytes())
            self.assert_refused(fx, lambda: catalog.split(copy_path, "S0032", PARENT_ID))
            self.assertEqual(copy_path.read_bytes(), fx.catalog_path.read_bytes())

    def test_split_refuses_symlinked_source_directory(self):
        with tempfile.TemporaryDirectory() as td:
            fx = SplitFixture(td)
            outside = Path(td).resolve() / "outside-v2"
            fx.v2.rename(outside)
            fx.v2.symlink_to(outside, target_is_directory=True)
            self.assert_refused(fx, lambda: catalog.split(fx.catalog_path, "S0032", PARENT_ID))


class BuildPlanTests(unittest.TestCase):
    """build() keeps an existing version 3 plan and fails closed when its source changed."""

    def write_inventory(self, fx, pdf_sha=None, include_pdf=True):
        files, pdfs = [], []
        if include_pdf:
            files.append({"path": "agents/11Agentic.pdf", "sha256": pdf_sha or fx.digest, "type": ".pdf"})
            pdfs.append({"path": "agents/11Agentic.pdf",
                         "pages": [{"page": 1, "regions": [{"id": uid} for uid in VISUAL_IDS]}]})
        files.append({"path": "notes/a.txt", "sha256": fx.other["sha256"], "type": ".txt"})
        inventory = fx.live / "inventory"
        inventory.mkdir(exist_ok=True)
        (inventory / "source-inventory-001.json").write_text(json.dumps({"files": files}))
        (inventory / "pdf-coverage-001.json").write_text(json.dumps({"pdfs": pdfs}))

    def previous_v3(self, fx):
        return {**fx.expected_v3(), "id": "S0001"}

    def test_build_without_previous_catalog_keeps_v2_plan(self):
        with tempfile.TemporaryDirectory() as td:
            fx = SplitFixture(td)
            fx.catalog_path.unlink()
            self.write_inventory(fx)
            with fx.owned_paths():
                result = catalog.build(fx.root, fx.live)
            pdf = result["sources"][0]
            self.assertEqual([u["id"] for u in pdf["units"]], VISUAL_IDS + [PARENT_ID])
            self.assertNotIn("plan_version", pdf)
            self.assertTrue(result["plan_valid"])

    def test_build_preserves_existing_v3_plan_for_same_source_sha(self):
        with tempfile.TemporaryDirectory() as td:
            fx = SplitFixture(td)
            previous = self.previous_v3(fx)
            fx.write_full([previous, fx.other])
            self.write_inventory(fx)
            before = fx.catalog_path.read_bytes()
            with fx.owned_paths(), FileObserver(fx.catalog_path, fx.catalog_home / "prepare.lock") as seen:
                result = catalog.build(fx.root, fx.live)
            self.assertEqual(result["sources"], [previous, fx.other])
            self.assertEqual(result["unit_count"], 14)
            self.assertEqual(result["unique_content_unit_count"], 14)
            self.assertTrue(result["plan_valid"])
            self.assertTrue(seen.catalog_reads and all(seen.catalog_reads), "Read previous catalog under prepare.lock")
            self.assertEqual(fx.catalog_path.read_bytes(), before, "build() returns a plan and writes nothing")
            self.assertTrue(fx.runtime_untouched(seen))

    def test_main_build_holds_prepare_lock_from_read_until_catalog_write(self):
        # Race: build reads an old catalog, a split lands, then main writes the stale plan over it.
        with tempfile.TemporaryDirectory() as td:
            fx = SplitFixture(td)
            fx.write_full([self.previous_v3(fx), fx.other])
            self.write_inventory(fx)
            lock_path = fx.catalog_home / "prepare.lock"
            gap, real_build = [], catalog.build

            def build_then_concurrent_split(*args, **kwargs):
                result = real_build(*args, **kwargs)
                held = lock_held(lock_path)
                gap.append(held)
                if not held:  # Simulate a split writer that took the free lock in the gap.
                    fd = os.open(lock_path, os.O_RDWR | os.O_CREAT)
                    try:
                        fcntl.flock(fd, fcntl.LOCK_EX)
                        document = json.loads(fx.catalog_path.read_text())
                        document["concurrent_split"] = True
                        fx.catalog_path.write_text(json.dumps(document))
                    finally:
                        fcntl.flock(fd, fcntl.LOCK_UN)
                        os.close(fd)
                return result

            argv = ["catalog.py", "build", "--catalog", str(fx.catalog_path),
                    "--root", str(fx.root), "--live", str(fx.live)]
            with fx.owned_paths(), patch("sys.argv", argv), \
                    patch.object(catalog, "build", build_then_concurrent_split), \
                    patch("sys.stdout", new_callable=io.StringIO), \
                    FileObserver(fx.catalog_path, lock_path) as seen:
                catalog.main()
            final = json.loads(fx.catalog_path.read_text())
            if gap != [True]:
                self.assertIn("concurrent_split", final, "A split written between build read and write was erased")
            self.assertEqual(gap, [True], "prepare.lock must stay held between build() and the catalog write")
            self.assertTrue(seen.catalog_writes and all(seen.catalog_writes), "Catalog write under prepare.lock")
            self.assertEqual(final["sources"][0], self.previous_v3(fx))
            self.assertTrue(fx.runtime_untouched(seen))

    def test_build_fails_closed_when_v3_source_changed_or_missing(self):
        for case in ("changed", "missing"):
            with self.subTest(case), tempfile.TemporaryDirectory() as td:
                fx = SplitFixture(td)
                fx.write_full([self.previous_v3(fx), fx.other])
                if case == "changed":
                    fx.pdf.write_bytes(b"%PDF-1.7 new revision\n")
                    self.write_inventory(fx, pdf_sha=catalog.file_sha(fx.pdf))
                else:
                    self.write_inventory(fx, include_pdf=False)
                before = fx.catalog_path.read_bytes()
                with fx.owned_paths(), self.assertRaises(catalog.SourceChanged):
                    catalog.build(fx.root, fx.live)
                self.assertEqual(fx.catalog_path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
