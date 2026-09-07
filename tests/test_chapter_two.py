"""Source-derived Chapter 2 coverage and explicitly reviewed sandbox labs."""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import unittest

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import build_book as book  # noqa: E402

LAB_PATTERN = re.compile(r"<!-- lab: ([a-z0-9-]+) -->\n```sh\n(.*?)\n```", re.S)


class ChapterTwoSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = book.load_manifest()
        cls.spec = next(d for d in cls.data["documents"] if d["id"] == "chapter-2")
        cls.text = (ROOT / cls.spec["file"]).read_text(encoding="utf-8")
        cls.coverage = json.loads((ROOT / cls.spec["coverage_file"]).read_text())

    def test_coverage_matches_all_original_numbered_headings(self):
        found = []
        with pymupdf.open(ROOT / "HowLinuxWorks.pdf") as source:
            for number in range(15, 42):
                for line in source[number - 1].get_text().splitlines():
                    match = re.match(r"^(2(?:\.\d+)+)\s+(.+)$", line)
                    if match:
                        found.append((match[1], match[2].strip(), number))
        expected = [(s["number"], s["title_en"], s["source_page"])
                    for s in self.coverage["sections"]]
        self.assertEqual(found, expected)
        self.assertEqual(len(found), 63)
        self.assertEqual([s[0] for s in found if s[0].count(".") == 1],
                         [f"2.{n}" for n in range(1, 22)])
        book.validate_coverage(self.spec, self.text, ROOT)

    def test_missing_section_is_rejected(self):
        text = self.text.replace("### 2.14.1 الإخراج القياسي للأخطاء", "### الإخراج القياسي للأخطاء")
        with self.assertRaisesRegex(ValueError, "Missing, reordered"):
            book.validate_coverage(self.spec, text, ROOT)

    def test_heading_without_explanation_is_rejected(self):
        text = re.sub(r"(^### 2\.4\.2 [^\n]+\n).*?(?=^### )", r"\1\n", self.text,
                      count=1, flags=re.M | re.S)
        with self.assertRaisesRegex(ValueError, "substantive Arabic"):
            book.validate_coverage(self.spec, text, ROOT)

    def test_original_tables_figures_and_labs_are_accounted_for(self):
        self.assertEqual(self.coverage["figures"], ["2-1", "2-2"])
        self.assertEqual(self.coverage["tables"], ["2-1", "2-2", "2-3", "2-4"])
        for number in self.coverage["figures"]:
            self.assertIn(f'<figcaption>الشكل <span dir="ltr">{number}</span>', self.text)
        for number in self.coverage["tables"]:
            self.assertIn(f'الجدول <span dir="ltr">{number}</span>', self.text)
        self.assertEqual(list(dict(LAB_PATTERN.findall(self.text))), self.coverage["labs"])
        for label in ("توضيح حديث", "إضافة تعليمية", "إجابات مقترحة", "الفصل الثالث لم يُعد بعد"):
            self.assertIn(label, self.text)

    def test_archived_part_one_is_unchanged(self):
        book.verify_archives(self.data)
        self.assertEqual(len(self.data["archived_editions"]), 1)
        self.assertEqual(self.data["archived_editions"][0]["pdf_pages"], 32)
        self.assertEqual(self.data["archived_editions"][0]["files"][0]["sha256"],
                         "c102918e0d5fe5f4a46d063ff0447ac9d8a0653d942455e3aff8ee83f4e306f6")

    def test_modified_archive_is_rejected(self):
        data = {"archived_editions": [{"files": [{"file": "old.pdf", "sha256": "0" * 64}]}]}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "old.pdf").write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "Archived review artifact was changed"):
                book.verify_archives(data, root)

    def test_active_slug_cannot_overwrite_an_archive(self):
        data = copy.deepcopy(self.data)
        data["edition"]["slug"] = data["archived_editions"][0]["slug"]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "book").mkdir()
            (root / "book/manifest.json").write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "cannot overwrite"):
                book.load_manifest(root)

    def test_edition_label_and_scope_are_not_hardcoded_to_part_one(self):
        data = copy.deepcopy(self.data)
        data["edition"]["label"] = "دفعة اختبار"
        docs = book.prepare_documents(data)
        html = book.compose_html(data, docs)
        styled = book.inline_styles(html, data)
        self.assertIn("دفعة اختبار", book.cover_html(data))
        self.assertIn("<title>كيف يعمل لينكس — دفعة اختبار</title>", html)
        self.assertIn("إعداد عربي تعليمي · دفعة اختبار", styled)
        self.assertNotIn("__BOOK_RUNNING_HEADER__", styled)
        toc_ids = {e["id"] for e in book.toc_entries(docs)}
        self.assertIn("chapter-2-2-1", toc_ids)
        self.assertIn("chapter-2-2-21", toc_ids)
        roadmap = book.roadmap_markdown(data)
        self.assertIn("الفصل 3: الأجهزة", roadmap)
        self.assertNotIn("إعداد الفصل الثاني", roadmap)

    @unittest.skipUnless(shutil.which("bash"), "Bash is required for syntax-only checks")
    def test_shell_examples_parse_without_executing_them(self):
        env = {"PATH": "/usr/bin:/bin", "LC_ALL": "C"}
        for language, code in book.FENCED_CODE.findall(self.text):
            if language != "sh":
                continue
            with self.subTest(code=code[:90]):
                result = subprocess.run(
                    ["bash", "--noprofile", "--norc", "-n"], input=code,
                    env=env, capture_output=True, text=True, timeout=5,
                )
                self.assertEqual(result.returncode, 0, result.stderr)


class ChapterTwoLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        text = (ROOT / "book/ar/02-basic-commands.md").read_text()
        cls.blocks = dict(LAB_PATTERN.findall(text))
        cls.allowlist = json.loads((ROOT / "tests/chapter02_labs.json").read_text())["labs"]

    def test_only_five_reviewed_labs_are_allowlisted(self):
        self.assertEqual(set(self.blocks), set(self.allowlist))
        self.assertEqual(len(self.blocks), 5)
        for name, script in self.blocks.items():
            self.assertEqual(hashlib.sha256(script.encode()).hexdigest(), self.allowlist[name]["sha256"],
                             f"Review the changed script before allowing execution: {name}")
            self.assertNotRegex(script, r"\b(?:sudo|su|passwd|chsh|visudo|vipw|rm)\b")

    @unittest.skipUnless(sys.platform.startswith("linux"), "Linux labs")
    def test_reviewed_labs_in_disposable_directories_and_process_groups(self):
        tools = ("bash", "sh", "mkdir", "printf", "cat", "grep", "sort", "touch", "chmod",
                 "ln", "readlink", "ls", "tar", "gzip", "diff", "sleep", "ps")
        missing = [name for name in tools if shutil.which(name) is None]
        if missing:
            self.skipTest(f"Missing conventional Linux tools: {missing}")
        for name, policy in self.allowlist.items():
            with self.subTest(lab=name), tempfile.TemporaryDirectory(prefix="hlw-ch02-test-") as directory:
                root = Path(directory)
                script = self.blocks[name]
                # This must happen before Popen, independently of the other test.
                self.assertEqual(hashlib.sha256(script.encode()).hexdigest(), policy["sha256"],
                                 "Unreviewed script: refusing to execute")
                env = {"PATH": "/usr/bin:/bin", "LC_ALL": "C", "HOME": directory, "TMPDIR": directory}
                process = subprocess.Popen(
                    ["bash", "--noprofile", "--norc", "-c", script], cwd=root, env=env,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True,
                )
                try:
                    stdout, stderr = process.communicate(timeout=15)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.communicate()
                    self.fail(f"Lab timed out; its isolated process group was stopped: {name}")
                self.assertEqual(process.returncode, 0, stderr)
                if "stdout" in policy:
                    self.assertEqual(stdout, policy["stdout"])
                if "stdout_pattern" in policy:
                    self.assertRegex(stdout, policy["stdout_pattern"])
                for path, contents in policy.get("files", {}).items():
                    self.assertEqual((root / path).read_text(), contents)
                for path in policy.get("exists", []):
                    self.assertTrue((root / path).is_file())
                for path, mode in policy.get("modes", {}).items():
                    self.assertEqual(stat.S_IMODE((root / path).stat().st_mode), mode)
                for path, target in policy.get("symlinks", {}).items():
                    self.assertTrue((root / path).is_symlink())
                    self.assertEqual(os.readlink(root / path), target)


if __name__ == "__main__":
    unittest.main()
