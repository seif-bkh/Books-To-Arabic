"""Source checks plus a real, offline Markdown -> paginated PDF build."""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

import pymupdf

# Permit `python -m unittest discover -s tests` from the repository root.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import build_book as book  # noqa: E402


SAFE_EXAMPLES = {
    "ls /",
    "uname -r",
    "cat /etc/os-release",
    "ps -eo pid,ppid,user,comm | head -n 8",
    "ps -p 1 -o pid,comm,args",
    'sleep 5 &\ndemo_pid=$!\nps -o pid,ppid,user,stat,comm -p "$demo_pid"\nwait "$demo_pid"',
    "free -h",
    "id",
}


class SourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = book.load_manifest()
        cls.documents = book.prepare_documents(cls.manifest)
        cls.markup = book.compose_html(cls.manifest, cls.documents)

    def test_original_pdf_fingerprint_and_page_count(self):
        book.verify_source(self.manifest)
        wrong = copy.deepcopy(self.manifest)
        wrong["source"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            book.verify_source(wrong)

    def test_explicit_partial_scope(self):
        self.assertEqual(self.manifest["edition"]["status"], "partial-draft")
        self.assertEqual([c["number"] for c in self.manifest["chapters"]], list(range(1, 18)))
        self.assertEqual([c["number"] for c in self.manifest["chapters"] if c["status"] == "draft"], [1, 2])
        self.assertTrue(all(c["status"] == "pending" for c in self.manifest["chapters"][2:]))
        self.assertIn("ليست نسخة كاملة", self.manifest["edition"]["scope_note"])
        self.assertEqual(self.manifest["edition"]["slug"], "how-linux-works-ar-part-02")
        self.assertIn("الفصول من الثالث إلى السابع عشر لم تُعد بعد", book.cover_html(self.manifest))

    def test_all_original_chapter_one_sections(self):
        chapter = next(d["markdown"] for d in self.documents if d["id"] == "chapter-1")
        sections = re.findall(r"^#{2,3} (1\.\d+(?:\.\d+)?)\s", chapter, re.M)
        self.assertEqual(sections, [
            "1.1", "1.2", "1.3", "1.3.1", "1.3.2", "1.3.3", "1.3.4", "1.4", "1.5", "1.6",
        ])
        self.assertEqual(re.findall(r'<figure[^>]+id="([^"]+)"', chapter),
                         ["figure-1-1", "figure-1-2", "figure-1-3"])
        self.assertEqual(chapter.count("</figure>"), 3)
        for number in range(1, 4):
            self.assertIn(f'<figcaption>الشكل <span dir="ltr">1-{number}</span>', chapter)
        self.assertIn("إجابات مقترحة", chapter)
        self.assertIn("الفصل الثاني متاح الآن", chapter)

    def test_valid_internal_links_and_explicit_code_direction(self):
        book.check_html(self.markup)
        self.assertIn('<html lang="ar" dir="rtl">', self.markup)
        self.assertNotRegex(self.markup, r'href="[^"]*\.md"')
        self.assertIn('href="#glossary"', self.markup)
        self.assertIn('href="#editorial-notes"', self.markup)

    def test_broken_link_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Broken internal link"):
            book.check_html(self.markup.replace('href="#glossary"', 'href="#absent"', 1))
        with self.assertRaisesRegex(ValueError, "Unknown Markdown"):
            book.document_link("missing.md", {})

    def test_duplicate_ids_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate HTML ID"):
            book.check_html(self.markup + '<p id="chapter-1">test</p>')

    def test_missing_code_direction_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Missing dir=ltr"):
            book.check_html(self.markup.replace('<pre dir="ltr">', "<pre>", 1))

    def test_fonts_are_bundled_with_licenses(self):
        for filename in ("Amiri-Regular.ttf", "Amiri-Bold.ttf", "FiraMono-Regular.ttf"):
            data = (book.FONTS / filename).read_bytes()
            self.assertEqual(data[:4], b"\x00\x01\x00\x00")
        for filename in ("Amiri-OFL.txt", "FiraMono-OFL.txt"):
            self.assertIn("SIL OPEN FONT LICENSE", (book.FONTS / filename).read_text())
        embedded = book.inline_styles(self.markup)
        self.assertEqual(embedded.count("data:font/ttf;base64,"), 3)
        self.assertNotRegex(embedded, r"url\([\"']?https?://")

    def test_combined_markdown_is_current(self):
        output = ROOT / "editions" / (self.manifest["edition"]["slug"] + ".md")
        self.assertEqual(output.read_text(), book.combined_markdown(self.manifest, self.documents))

    def test_manifest_cannot_claim_an_unwritten_chapter(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / "book/ar", root / "book/ar")
            data = copy.deepcopy(self.manifest)
            shutil.copytree(ROOT / "book/coverage", root / "book/coverage")
            data["chapters"][2]["status"] = "draft"
            (root / "book/manifest.json").write_text(json.dumps(data, ensure_ascii=False))
            with self.assertRaisesRegex(ValueError, "real source document"):
                book.load_manifest(root)

    def test_check_runs_outside_repository_working_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_book.py"), "--check", "--verify-source"],
                cwd=directory, capture_output=True, text=True, timeout=30,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("OK:", result.stdout)

    def test_reviewed_safe_examples_run(self):
        examples = {
            code.strip()
            for d in self.documents if d["id"] in {"preface", "chapter-1"}
            for language, code in book.FENCED_CODE.findall(d["markdown"])
            if language == "sh"
        }
        # Never blindly execute newly added book commands in a test run.
        self.assertEqual(examples, SAFE_EXAMPLES)
        if not sys.platform.startswith("linux") or not Path("/etc/os-release").exists():
            self.skipTest("The hands-on examples require a conventional Linux environment")
        if any(shutil.which(name) is None for name in ("sh", "ps", "free", "head", "id", "uname", "cat", "ls", "sleep")):
            self.skipTest("Some conventional Linux/procps tools are not installed")
        with tempfile.TemporaryDirectory() as directory:
            for code in sorted(examples):
                with self.subTest(command=code):
                    result = subprocess.run(
                        ["sh", "-c", code], cwd=directory, timeout=15,
                        env={**os.environ, "LC_ALL": "C"}, capture_output=True, text=True,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertTrue(result.stdout.strip())


class PDFTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix="arabic-book-test-")
        cls.result = book.build(Path(cls.scratch.name))
        cls.pdf = pymupdf.open(cls.result["pdf"])
        cls.text = "\n".join(page.get_text() for page in cls.pdf)
        cls.data = book.load_manifest()
        cls.documents = book.prepare_documents(cls.data)

    @classmethod
    def tearDownClass(cls):
        cls.pdf.close()
        cls.scratch.cleanup()

    def test_full_pagination_not_just_first_page_of_each_chapter(self):
        self.assertGreater(len(self.pdf), 65)
        self.assertLess(len(self.pdf), 150)
        self.assertGreater(len(self.text), 110_000)
        self.assertGreaterEqual(self.result["verified_blocks"], 700)
        chapter_two_pages = self.result["heading_pages"]["glossary"] - self.result["heading_pages"]["chapter-2"]
        self.assertGreater(chapter_two_pages, 35)
        for page in self.pdf:
            self.assertAlmostEqual(page.rect.width, 595.28, delta=1)
            self.assertAlmostEqual(page.rect.height, 841.89, delta=1)
            self.assertGreater(len(page.get_text().strip()), 100)

    def test_arabic_is_searchable_not_garbled_glyph_codes(self):
        for word in ("النواة", "الذاكرة", "التجريد", "الصلاحيات", "الصدفة", "الأرشيف"):
            self.assertTrue(any(page.search_for(word) for page in self.pdf), word)
        # Regression guard for a renderer producing correct-looking glyphs but
        # mapping Arabic letters to Hebrew/Indic characters in its ToUnicode map.
        self.assertNotRegex(self.text, "[\u0590-\u05ff\u0900-\u0fff]")
        self.assertEqual(self.pdf.xref_get_key(self.pdf.pdf_catalog(), "Lang"), ("string", "ar"))
        self.assertIn("جزئي", self.pdf.metadata["title"])
        self.assertIn("الدفعة الثانية", self.pdf.metadata["title"])
        self.assertIn("Chapter 2", self.pdf.metadata["keywords"])

    def test_commands_and_example_output_remain_copyable(self):
        for document in self.documents:
            for _, block in book.FENCED_CODE.findall(document["markdown"]):
                for line in block.strip().splitlines():
                    with self.subTest(line=line):
                        self.assertIn(line, self.text)

    def test_every_heading_has_a_real_bookmark_and_page(self):
        toc = self.pdf.get_toc()
        for document in self.documents:
            for heading in document["headings"]:
                expected_page = self.result["heading_pages"][heading["id"]]
                self.assertIn([heading["level"], heading["title"], expected_page], toc)
                self.assertTrue(1 <= expected_page <= len(self.pdf))
        self.assertEqual(toc[0], [1, "محتويات هذه الدفعة", 2])

    def test_contents_links_and_external_references_survive(self):
        start = self.result["heading_pages"]["contents"] - 1
        end = self.result["heading_pages"]["preface"] - 1
        self.assertGreater(end - start, 1, "The expanded contents should span multiple pages")
        contents_links = [link for page in self.pdf.pages(start, end) for link in page.get_links()]
        for target in book.toc_entries(self.documents):
            page_number = self.result["heading_pages"][target["id"]] - 1
            self.assertTrue(any(link.get("page") == page_number for link in contents_links), target)
        links = [link for page in self.pdf for link in page.get_links()]
        self.assertTrue(any("man7.org" in link.get("uri", "") for link in links))

    def test_bundled_fonts_are_embedded(self):
        names = {font[3] for page in self.pdf for font in page.get_fonts()}
        self.assertTrue(any("Amiri" in name for name in names), names)
        self.assertTrue(any("FiraMono" in name or "Fira" in name for name in names), names)
        for xref in {font[0] for page in self.pdf for font in page.get_fonts()}:
            self.assertTrue(self.pdf.extract_font(xref)[3], f"Unembedded font xref {xref}")

    def test_published_pdf_matches_rebuilt_content(self):
        release = ROOT / "editions" / self.result["pdf"].name
        with pymupdf.open(release) as published:
            self.assertEqual(len(published), len(self.pdf))
            self.assertEqual(published.get_toc(), self.pdf.get_toc())
            self.assertEqual("\n".join(p.get_text() for p in published), self.text)

    def test_rtl_overflow_regression_is_detected(self):
        # Without the LTR mechanical column container, Paged.js can produce a
        # plausible seven-page PDF while hiding most of each Arabic chapter.
        markup = book.inline_styles(book.compose_html(self.data, self.documents))
        markup = markup.replace("</head>", '<style>.pagedjs_page_content { direction: rtl !important; }</style></head>')
        scratch = Path(self.scratch.name)
        source = scratch / "broken-rtl.html"
        source.write_text(markup, encoding="utf-8")
        result = subprocess.run(
            ["node", str(ROOT / "scripts/render_pdf.mjs"), str(source),
             str(scratch / "broken.pdf"), str(scratch / "broken.json")],
            cwd=ROOT, capture_output=True, text=True, timeout=60,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Text leaves physical page", result.stderr)
        self.assertFalse((scratch / "broken.pdf").exists())


if __name__ == "__main__":
    unittest.main()
