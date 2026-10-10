"""Source-derived Chapter 1 coverage checks for the Beyond Vibe Coding project."""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys
import unittest

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import build_book as book  # noqa: E402

SLUG = "beyond-vibe-coding-ar"
PROJECT = book.Project.resolve(SLUG)


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


class ChapterOneSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = book.load_manifest(PROJECT)
        cls.spec = next(d for d in cls.data["documents"] if d["id"] == "chapter-1")
        cls.text = (PROJECT.dir / cls.spec["file"]).read_text(encoding="utf-8")
        cls.coverage = json.loads((PROJECT.dir / cls.spec["coverage_file"]).read_text())
        cls.source_pdf = ROOT / cls.data["source"]["dir"] / cls.data["source"]["file"]

    def test_coverage_lists_all_sections_and_validates(self):
        self.assertEqual(len(self.coverage["sections"]), 27)
        numbers = [s["number"] for s in self.coverage["sections"]]
        self.assertEqual([n for n in numbers if n.count(".") == 1],
                         [f"1.{i}" for i in range(1, 10)])
        book.validate_coverage(self.spec, self.text, PROJECT)

    def test_every_section_title_appears_at_its_claimed_source_page(self):
        # The original prints unnumbered headings; verify each English heading
        # actually lives on the page recorded in the coverage file.
        with pymupdf.open(self.source_pdf) as pdf:
            page_cache = {}
            for section in self.coverage["sections"]:
                page = section["source_page"]
                if page not in page_cache:
                    page_cache[page] = _norm(pdf[page - 1].get_text())
                head = _norm(section["title_en"])[:40]
                with self.subTest(number=section["number"]):
                    self.assertIn(head, page_cache[page],
                                  f"{section['number']} not found on page {page}")

    def test_section_pages_lie_within_the_chapter_range(self):
        lo, hi = self.coverage["source_pages"]
        for section in self.coverage["sections"]:
            with self.subTest(number=section["number"]):
                self.assertTrue(lo <= section["source_page"] <= hi)

    def test_figures_are_accounted_and_captioned(self):
        self.assertEqual(self.coverage["figures"], ["1-1", "1-2", "1-3"])
        for number in self.coverage["figures"]:
            self.assertIn(f'<figure class="diagram" id="figure-{number}"', self.text)
            self.assertIn(f'الشكل <span dir="ltr">{number}</span>', self.text)

    def test_missing_section_is_rejected(self):
        text = self.text.replace("### 1.2.1 صعود التوجيه (البرومبت): من التعليمات إلى الأوصاف",
                                 "### صعود التوجيه")
        with self.assertRaisesRegex(ValueError, "Missing, reordered"):
            book.validate_coverage(self.spec, text, PROJECT)

    def test_heading_without_explanation_is_rejected(self):
        text = re.sub(r"(^### 1\.5\.1 [^\n]+\n).*?(?=^### )", r"\1\n", self.text,
                      count=1, flags=re.M | re.S)
        with self.assertRaisesRegex(ValueError, "substantive Arabic"):
            book.validate_coverage(self.spec, text, PROJECT)

    def test_no_executable_shell_blocks_in_this_chapter(self):
        for language, _ in book.FENCED_CODE.findall(self.text):
            self.assertIn(language, {"text"}, "Chapter 1 should carry prompts as text only")

    def test_no_unsupported_glyphs_in_arabic_files(self):
        # Guards against the tofu/stray-glyph incidents (Greek, arrows, box-drawing, CJK, Cyrillic).
        preface = next(d for d in self.data["documents"] if d["id"] == "preface")
        files = [PROJECT.dir / preface["file"], PROJECT.dir / self.spec["file"]]
        forbidden = [(0x0370, 0x03FF), (0x2190, 0x21FF), (0x2500, 0x257F),
                     (0x25A0, 0x25FF), (0x4E00, 0x9FFF), (0x0400, 0x04FF)]
        for path in files:
            text = path.read_text(encoding="utf-8")
            bad = sorted({f"U+{ord(c):04X}" for c in text
                          if any(lo <= ord(c) <= hi for lo, hi in forbidden)})
            self.assertEqual(bad, [], f"{path.name} has unsupported glyphs: {bad}")


if __name__ == "__main__":
    unittest.main()
