"""Repository-wide layout and provenance checks shared by every book project.

These tests enforce the canonical structure documented in docs/method/00-repo-layout.md
so a new book cannot be added in an ad-hoc shape that the build and the review
process cannot rely on.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import build_book as book  # noqa: E402

METHOD_DOCS = [
    "docs/method/README.md",
    "docs/method/00-repo-layout.md",
    "docs/method/01-translation-method.md",
    "docs/method/02-terminology-policy.md",
    "docs/method/03-rtl-typesetting.md",
    "docs/method/04-build-and-validation.md",
    "docs/method/05-source-and-rights.md",
    "docs/method/06-lessons-log.md",
]
REQUIRED_MANIFEST_KEYS = ("edition", "source", "documents", "chapters",
                          "other_source_material")


class RepositoryLayoutTests(unittest.TestCase):
    def test_shared_tooling_lives_at_the_root(self):
        for path in ("scripts/build_book.py", "scripts/render_pdf.mjs",
                     "scripts/new_book.py", "AGENTS.md", "CONTRIBUTING.md",
                     "README.md", "package.json", "requirements.txt"):
            self.assertTrue((ROOT / path).is_file(), path)

    def test_the_single_book_layout_is_gone(self):
        # The pre-multi-book layout must not reappear alongside books/<slug>/.
        for path in ("book", "editions", "HowLinuxWorks.pdf"):
            self.assertFalse((ROOT / path).exists(), f"Legacy path reappeared: {path}")

    def test_canonical_method_docs_exist_and_are_linked(self):
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for relative in METHOD_DOCS:
            self.assertTrue((ROOT / relative).is_file(), relative)
            self.assertIn(relative, agents + readme, f"{relative} is not discoverable")
        index = (ROOT / "docs/method/README.md").read_text(encoding="utf-8")
        for relative in METHOD_DOCS[1:]:
            self.assertIn(Path(relative).name, index, relative)

    def test_every_book_project_has_the_required_shape(self):
        slugs = book.Project.available()
        self.assertTrue(slugs, "books/ holds no project")
        for slug in slugs:
            with self.subTest(book=slug):
                project = book.Project.resolve(slug)
                self.assertRegex(slug, r"^[a-z][a-z0-9-]*$")
                for relative in ("manifest.json", "README.md", "ar", "editions"):
                    self.assertTrue((project.dir / relative).exists(), relative)
                # Either the shared stylesheet or an explicit per-book override.
                self.assertTrue(project.stylesheet.is_file(), project.stylesheet)
                self.assertIn(project.stylesheet,
                              (project.dir / "assets" / "print.css",
                               ROOT / "assets" / "print.css"))
                data = json.loads(project.manifest_path.read_text(encoding="utf-8"))
                for key in REQUIRED_MANIFEST_KEYS:
                    self.assertIn(key, data)
                self.assertEqual(data["project"]["slug"], slug)
                self.assertTrue(re.fullmatch(r"[a-z]{2}", data["project"]["language"]))

    def test_originals_are_registered_with_provenance(self):
        for slug in book.Project.available():
            project = book.Project.resolve(slug)
            data = book.load_manifest(project)
            source = data["source"]
            source_dir = ROOT / source["dir"]
            with self.subTest(book=slug, source=source["dir"]):
                self.assertTrue(source_dir.is_dir(), source["dir"])
                self.assertEqual(source_dir.parent, ROOT / "sources")
                record = json.loads((source_dir / "source.json").read_text(encoding="utf-8"))
                for key in ("title", "author", "publisher", "language", "file",
                            "sha256", "pages", "rights"):
                    self.assertIn(key, record, key)
                self.assertIn("status", record["rights"])
                self.assertEqual(record["sha256"], source["sha256"])
                self.assertEqual(record["pages"], source["pages"])
                original = source_dir / record["file"]
                self.assertTrue(original.is_file(), record["file"])
                digest = hashlib.sha256(original.read_bytes()).hexdigest()
                self.assertEqual(digest, record["sha256"],
                                 "The original changed; record the new provenance deliberately")
                book.verify_source(data, project)

    def test_project_files_never_escape_their_project_directory(self):
        for slug in book.Project.available():
            project = book.Project.resolve(slug)
            data = json.loads(project.manifest_path.read_text(encoding="utf-8"))
            relatives = [d["file"] for d in data["documents"]]
            relatives += [d["coverage_file"] for d in data["documents"]
                          if "coverage_file" in d]
            relatives += [f["file"] for e in data.get("archived_editions", [])
                          for f in e["files"]]
            for relative in relatives:
                with self.subTest(book=slug, path=relative):
                    self.assertFalse(Path(relative).is_absolute(), relative)
                    self.assertNotIn("..", Path(relative).parts, relative)
                    self.assertTrue((project.dir / relative).is_file(), relative)

    def test_bundled_fonts_and_licenses_are_shared(self):
        fonts = ROOT / "assets" / "fonts"
        for name in (*book.REQUIRED_FONTS, "Amiri-OFL.txt", "FiraMono-OFL.txt", "README.md"):
            self.assertTrue((fonts / name).is_file(), name)
        for name in ("Amiri-OFL.txt", "FiraMono-OFL.txt"):
            self.assertIn("SIL OPEN FONT LICENSE", (fonts / name).read_text(encoding="utf-8"))
        # Fonts are shared, so no book may carry a private duplicate.
        for slug in book.Project.available():
            self.assertFalse((book.Project.resolve(slug).dir / "assets" / "fonts").exists(),
                             f"{slug} duplicates the shared fonts")


if __name__ == "__main__":
    unittest.main()
