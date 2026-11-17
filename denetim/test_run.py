import fcntl
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest

from run import run_once
from pdf_scope import choose_pending


def response(key="first"):
    return {
        "primary_finding_key": key,
        "primary_finding_title": "Kabul ölçütü eksik",
        "finding_status": "unverified",
        "covered_need_ids": ["N-1"],
        "unit_reviews": [],
        "report_markdown": "\n".join(
            "## " + heading + "\n" + "Kaynak henüz bu sonucu doğrulamıyor. " * 15
            for heading in [
                "Geliştirme odaklı eleştiri", "Farkında olmadığımız bilinmeyenler",
                "İhtiyaçlar ve çözüm önerileri", "Bütünsel mimariye etkisi",
                "Kanıtlar ve doğrulama sınırları",
                "Veri ve iş akışı dökümü", "Dot araçlarıyla karşılaştırma",
            ]
        ),
    }


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "alpha").mkdir()
        (self.root / "beta").mkdir()

    def test_rotation_numbering_and_history(self):
        seen = []

        def reviewer(folder, history, number):
            seen.append((folder.name, len(history), number))
            return response(str(number))

        for _ in range(3):
            self.assertEqual(run_once(self.root, reviewer)["status"], "written")
        self.assertEqual(seen, [("alpha", 0, 101), ("beta", 1, 102), ("alpha", 2, 103)])
        self.assertTrue((self.root / "103.md").is_file())

    def test_existing_report_is_never_overwritten(self):
        (self.root / "105.md").write_text("User report")
        result = run_once(self.root, lambda *args: response())
        self.assertEqual(result["number"], 106)
        self.assertEqual((self.root / "105.md").read_text(), "User report")

    def test_failure_does_not_consume_number(self):
        def fail(*args):
            raise RuntimeError("provider unavailable")

        with self.assertRaises(RuntimeError):
            run_once(self.root, fail)
        result = run_once(self.root, lambda *args: response())
        self.assertEqual(result["number"], 101)

    def test_overlap_does_not_start_second_claude(self):
        control = self.root / ".claude-denetim"
        control.mkdir()
        with (control / "run.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            result = run_once(self.root, lambda *args: self.fail("overlapping run"))
        self.assertEqual(result["status"], "already_running")

    def test_output_failure_does_not_publish_partial_report(self):
        bad = response()
        bad["report_markdown"] = "Incomplete"
        with self.assertRaises(ValueError):
            run_once(self.root, lambda *args: bad)
        self.assertFalse((self.root / "101.md").exists())

    def test_duplicate_finding_rejected_without_claiming_new_discovery(self):
        run_once(self.root, lambda *args: response())
        with self.assertRaises(ValueError):
            run_once(self.root, lambda *args: response())
        self.assertFalse((self.root / "102.md").exists())

    def test_no_new_issue_is_reportable_without_fabrication(self):
        item = response()
        item["finding_status"] = "no_new_issue"
        run_once(self.root, lambda *args: item)
        self.assertEqual(run_once(self.root, lambda *args: item)["number"], 102)

    def test_new_folder_enters_rotation_and_symlink_is_excluded(self):
        run_once(self.root, lambda *args: response("one"))
        (self.root / "aaa-new").mkdir()
        (self.root / "000-symlink").symlink_to(self.root / "alpha", target_is_directory=True)
        selected = []
        run_once(self.root, lambda folder, *args: selected.append(folder.name) or response("two"))
        self.assertEqual(selected, ["aaa-new"])

    def test_other_writer_cannot_be_overwritten_during_review(self):
        def reviewer(*args):
            (self.root / "101.md").write_text("Concurrent report")
            return response()

        with self.assertRaises(FileExistsError):
            run_once(self.root, reviewer)
        self.assertEqual((self.root / "101.md").read_text(), "Concurrent report")

    def test_termination_stops_child_before_releasing_run(self):
        control = self.root / ".claude-denetim"
        control.mkdir()
        (control / "GOREV.md").write_text("test")
        (control / "DOT-BAGLAMI.md").write_text("test")
        fake = self.root / "fake_claude.py"
        fake.write_text(
            "#!" + sys.executable + "\n"
            "import os, pathlib, time\n"
            "pathlib.Path('child.pid').write_text(str(os.getpid()))\n"
            "time.sleep(60)\n"
        )
        fake.chmod(0o700)
        code = (
            "import run; from pathlib import Path; "
            "run.ROOT=Path(" + repr(str(self.root)) + "); "
            "run.CLAUDE=Path(" + repr(str(fake)) + "); run.main()"
        )
        parent = subprocess.Popen([sys.executable, "-B", "-c", code],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        child = None
        try:
            deadline = time.monotonic() + 5
            while not (self.root / "child.pid").exists() and time.monotonic() < deadline:
                time.sleep(0.02)
            self.assertTrue((self.root / "child.pid").exists(), "child did not start")
            child = int((self.root / "child.pid").read_text())
            parent.terminate()
            parent.wait(timeout=8)
            with self.assertRaises(ProcessLookupError):
                os.kill(child, 0)
        finally:
            if parent.poll() is None:
                parent.kill()
                parent.wait()
            if child is not None:
                try:
                    os.killpg(child, signal.SIGKILL)
                except ProcessLookupError:
                    pass

    def test_partial_region_reappears_and_changed_pdf_resets_coverage(self):
        old = {"sha256": "old", "units": [{"id": "a"}, {"id": "b"}]}
        history = [{"pdf_scope": {"sha256": "old"}, "unit_reviews": [
            {"unit_id": "a", "status": "complete"},
            {"unit_id": "b", "status": "partial"},
        ]}]
        self.assertEqual(choose_pending([old], history)[1], [{"id": "b"}])
        changed = dict(old, sha256="new")
        self.assertEqual(choose_pending([changed], history)[1], old["units"])

    def test_coverage_cannot_claim_regions_outside_selected_scope(self):
        item = response()
        item["pdf_scope"] = {"source": "example.pdf", "sha256": "abc",
                             "regions": [{"id": "allowed"}]}
        item["unit_reviews"] = [{"unit_id": "invented", "status": "complete",
                                 "item_ids": ["x"], "next_cursor": ""}]
        with self.assertRaises(ValueError):
            run_once(self.root, lambda *args: item)


if __name__ == "__main__":
    unittest.main()
