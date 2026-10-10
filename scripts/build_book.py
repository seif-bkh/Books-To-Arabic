#!/usr/bin/env python3
"""Build a partial Arabic reading edition for one book project.

One repository can host several book projects. Each project lives in
``books/<slug>/`` with its own manifest, Arabic sources, stylesheet, coverage
records, and editions. Originals in their native language live in ``sources/``
and are only ever read.

The local Chromium/Paged.js renderer handles Arabic shaping and pagination.
No network or translation service is used during the build. Fonts are bundled;
explicit HTML dir attributes keep commands left-to-right. See README.md and
docs/method/.
"""

from __future__ import annotations

import argparse
import base64
from dataclasses import dataclass
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import tempfile
from typing import Any
from urllib.parse import unquote, urlsplit

import markdown
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
BOOKS_DIR = ROOT / "books"
FONTS = ROOT / "assets/fonts"
REQUIRED_FONTS = ("Amiri-Regular.ttf", "Amiri-Bold.ttf", "FiraMono-Regular.ttf")
STATUS_AR = {"draft": "مسودة متاحة", "pending": "لم يبدأ إعدادها"}
BIDI_CONTROLS = re.compile("[\u200e\u200f\u202a-\u202e\u2066-\u2069]")
FENCED_CODE = re.compile(r"^```([^\n]*)\n(.*?)^```\s*$", re.M | re.S)


@dataclass(frozen=True)
class Project:
    """A single book project and the repository it belongs to."""

    slug: str
    dir: Path
    root: Path = ROOT

    @property
    def manifest_path(self) -> Path:
        return self.dir / "manifest.json"

    @property
    def stylesheet(self) -> Path:
        """Per-book override when present, otherwise the shared stylesheet."""
        override = self.dir / "assets" / "print.css"
        return override if override.is_file() else self.root / "assets" / "print.css"

    @property
    def editions_dir(self) -> Path:
        return self.dir / "editions"

    @property
    def fonts_dir(self) -> Path:
        return self.root / "assets" / "fonts"

    @classmethod
    def available(cls, root: Path = ROOT) -> list[str]:
        books = root / "books"
        if not books.is_dir():
            return []
        return sorted(p.name for p in books.iterdir() if (p / "manifest.json").is_file())

    @classmethod
    def resolve(cls, slug: str | None = None, root: Path = ROOT) -> "Project":
        found = cls.available(root)
        if not found:
            raise ValueError("No book project found under books/")
        if slug is None:
            if len(found) > 1:
                raise ValueError(
                    "Several book projects exist; pass --book: " + ", ".join(found)
                )
            slug = found[0]
        if slug not in found:
            raise ValueError(f"Unknown book project: {slug}. Available: {', '.join(found)}")
        return cls(slug=slug, dir=(root / "books" / slug).resolve(), root=root.resolve())


def load_manifest(project: Project) -> dict[str, Any]:
    """Validate one project's manifest and return it."""
    data = json.loads(project.manifest_path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 2:
        raise ValueError("Unsupported manifest schema_version (expected 2)")
    chapters = data["chapters"]
    if data["edition"]["slug"] in {e["slug"] for e in data.get("archived_editions", [])}:
        raise ValueError("The active edition cannot overwrite an archived review edition")
    if [ch["number"] for ch in chapters] != list(range(1, len(chapters) + 1)):
        raise ValueError("Chapter numbers must be a contiguous sequence starting at 1")
    ids = [item["id"] for item in data["documents"]]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate document IDs")
    names = [Path(item["file"]).name for item in data["documents"]]
    if len(names) != len(set(names)):
        raise ValueError("Document basenames must be unique for cross-links")
    for item in data["documents"]:
        if not re.fullmatch(r"[a-z][a-z0-9-]*", item["id"]):
            raise ValueError(f"Invalid document ID: {item['id']}")
        path = (project.dir / item["file"]).resolve()
        if not path.is_relative_to(project.dir.resolve()) or not path.is_file():
            raise ValueError(f"Missing or out-of-project source: {item['file']}")
        text = path.read_text(encoding="utf-8")
        if not text.startswith(f"# {item['title']}\n"):
            raise ValueError(f"Title does not match manifest: {item['file']}")
        if len(re.findall(r"[\u0600-\u06ff]", text)) < 500:
            raise ValueError(f"Document lacks substantive Arabic content: {item['file']}")
        validate_coverage(item, text, project)
        if text.count("```") % 2:
            raise ValueError(f"Unclosed code fence: {item['file']}")
        for language, code in FENCED_CODE.findall(text):
            if language not in {"sh", "text"}:
                raise ValueError(f"Unrecognized code block language: {language}")
            if BIDI_CONTROLS.search(code):
                raise ValueError(f"Hidden direction controls in code: {item['file']}")
            if not code.isascii():
                raise ValueError(f"Unexpected non-ASCII shell/output text: {item['file']}")
    for item in chapters + data["other_source_material"]:
        if item["status"] not in STATUS_AR:
            raise ValueError(f"Unknown status: {item['status']}")
        start, end = item["source_pages"]
        if not (1 <= start <= end <= data["source"]["pages"]):
            raise ValueError("Source page range is out of bounds")
        if item in chapters:
            if item["status"] == "draft" and item.get("document_id") not in ids:
                raise ValueError("A drafted chapter must have a real source document")
            if item["status"] == "pending" and "document_id" in item:
                raise ValueError("A pending chapter cannot masquerade as included content")
    return data


def validate_coverage(document: dict[str, Any], text: str, project: Project) -> None:
    """Match a drafted chapter against its reviewed, source-derived checklist."""
    if "coverage_file" not in document:
        return
    path = (project.dir / document["coverage_file"]).resolve()
    if not path.is_relative_to(project.dir.resolve()) or not path.is_file():
        raise ValueError("Missing or out-of-project chapter coverage file")
    coverage = json.loads(path.read_text(encoding="utf-8"))
    number = coverage["chapter"]
    found = re.findall(rf"^#{{2,3}} ({number}(?:\.\d+)+)\s+([^\n]+)$", text, re.M)
    expected = [(item["number"], item["title_ar"]) for item in coverage["sections"]]
    if found != expected:
        raise ValueError(f"Missing, reordered, or mismatched sections in {document['file']}")
    if coverage["source_pages"] != document["source_pages"]:
        raise ValueError("Chapter coverage and document page ranges disagree")
    for item in coverage["sections"]:
        if not coverage["source_pages"][0] <= item["source_page"] <= coverage["source_pages"][1]:
            raise ValueError("Section source page is outside the chapter range")
        body = re.search(
            rf"^#{{2,3}} {re.escape(item['number'])} [^\n]+\n(.*?)(?=^#{{1,6}} |\Z)",
            text, re.M | re.S,
        )
        if not body or len(re.findall(r"[\u0600-\u06ff]", body[1])) < 20:
            raise ValueError(f"Section has no substantive Arabic explanation: {item['number']}")
    figures = re.findall(r'<figure[^>]+id="figure-([^"]+)"', text)
    if figures != coverage["figures"]:
        raise ValueError("Chapter figure coverage does not match")
    for label in coverage["tables"]:
        if f'الجدول <span dir="ltr">{label}</span>' not in text:
            raise ValueError(f"Missing original numbered table: {label}")
    if re.findall(r"<!-- lab: ([a-z0-9-]+) -->", text) != coverage["labs"]:
        raise ValueError("Chapter lab checklist does not match")


def verify_archives(data: dict[str, Any], project: Project) -> None:
    """A new cumulative edition must not replace a previous review artifact."""
    for edition in data.get("archived_editions", []):
        for artifact in edition["files"]:
            path = (project.dir / artifact["file"]).resolve()
            if not path.is_relative_to(project.dir.resolve()) or not path.is_file():
                raise ValueError("Missing or out-of-project archived artifact")
            if hashlib.sha256(path.read_bytes()).hexdigest() != artifact["sha256"]:
                raise ValueError(f"Archived review artifact was changed: {artifact['file']}")


def verify_source(data: dict[str, Any], project: Project) -> None:
    """Check the original file against both the manifest and its source record."""
    source_dir = project.root / data["source"]["dir"]
    record_path = source_dir / "source.json"
    if not record_path.is_file():
        raise ValueError(f"Missing provenance record: {data['source']['dir']}/source.json")
    record = json.loads(record_path.read_text(encoding="utf-8"))
    for key in ("file", "sha256", "pages", "title", "author"):
        if record.get(key) != data["source"].get(key):
            raise ValueError(f"source.json and manifest disagree on '{key}'")
    source = source_dir / record["file"]
    actual = hashlib.sha256(source.read_bytes()).hexdigest()
    if actual != record["sha256"]:
        raise ValueError("The original file differs from the documented source fingerprint")
    with pymupdf.open(source) as pdf:
        if len(pdf) != record["pages"]:
            raise ValueError("Original page count differs from the source record")


def heading_slug(document: dict[str, Any], title: str, separator: str) -> str:
    if title == document["title"]:
        return document["id"]
    number = re.match(r"^(\d+(?:\.\d+)+)\s", title)
    suffix = number[1].replace(".", "-") if number else hashlib.sha256(
        title.encode("utf-8")
    ).hexdigest()[:12]
    return f"{document['id']}-{suffix}"


def flatten_headings(tokens: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for token in tokens:
        result.append({
            "id": token["id"],
            "level": token["level"],
            "title": html.unescape(re.sub(r"<[^>]+>", "", token["name"])),
        })
        result.extend(flatten_headings(token["children"]))
    return result


def document_link(target: str, mapping: dict[str, str]) -> str:
    parsed = urlsplit(html.unescape(target))
    if not parsed.scheme and not parsed.netloc and parsed.path.endswith(".md"):
        name = Path(unquote(parsed.path)).name
        if name not in mapping:
            raise ValueError(f"Unknown Markdown cross-reference: {target}")
        if parsed.query or parsed.fragment:
            raise ValueError("Use document-level .md links or explicit in-document #anchors")
        return "#" + mapping[name]
    return target


def enforce_direction(fragment: str) -> str:
    def replace(match: re.Match[str]) -> str:
        tag, attrs = match.groups()
        if re.search(r"\bdir\s*=", attrs):
            return match[0]
        direction = "ltr" if tag in {"pre", "code", "kbd", "samp"} else "rtl"
        return f'<{tag} dir="{direction}"{attrs}>'

    # Explicit direction also protects mixed text when styles are changed.
    return re.sub(r"<(pre|code|kbd|samp|h[1-6]|table)([^>]*)>", replace, fragment)


def prepare_documents(data: dict[str, Any], project: Project) -> list[dict[str, Any]]:
    mapping = {Path(d["file"]).name: d["id"] for d in data["documents"]}
    documents = []
    for spec in data["documents"]:
        text = (project.dir / spec["file"]).read_text(encoding="utf-8")
        converter = markdown.Markdown(
            extensions=["fenced_code", "tables", "toc", "md_in_html"],
            extension_configs={"toc": {
                "slugify": lambda title, sep, doc=spec: heading_slug(doc, title, sep),
            }},
        )
        fragment = converter.convert(text)
        fragment = re.sub(
            r'href="([^"]+)"',
            lambda m: f'href="{html.escape(document_link(m[1], mapping), quote=True)}"',
            fragment,
        )
        fragment = enforce_direction(fragment)
        if spec["id"] == "glossary":
            fragment = re.sub(
                r"<tr>(.*?)</tr>",
                lambda m: "<tr>" + m[1].replace("<td>", '<td dir="ltr">', 1) + "</tr>",
                fragment,
                flags=re.S,
            )
        documents.append({
            **spec,
            "markdown": text,
            "html": fragment,
            "headings": flatten_headings(converter.toc_tokens),
        })
    return documents


def roadmap_markdown(data: dict[str, Any]) -> str:
    roadmap = data.get("roadmap", {})
    total = len(data["chapters"])
    available = sum(ch["status"] == "draft" for ch in data["chapters"])
    rows = [
        "# خريطة إنجاز الكتاب",
        "",
        f"**عدد الفصول ذات المسودات: {available} من أصل {total}، "
        f"{roadmap.get('extra_scope', 'إضافة إلى المقدمة العربية')}.** "
        + roadmap.get(
            "header_note",
            "هذه أعداد فصول، وليست نسبة مئوية من كلمات الكتاب أو صفحاته. "
            "«مسودة متاحة» تعني وجود نص قابل للقراءة والمراجعة، لا اعتماد ترجمة نهائية.",
        ),
        "",
        "| الفصل | العنوان العربي المقترح | صفحات ملف المصدر | الحالة |",
        "| --- | --- | --- | --- |",
    ]
    for chapter in data["chapters"]:
        start, end = chapter["source_pages"]
        rows.append(
            f'| {chapter["number"]} | {chapter["title_ar"]} | <span dir="ltr">{start}–{end}</span> | '
            f"{STATUS_AR[chapter['status']]} |"
        )
    pending = [ch for ch in data["chapters"] if ch["status"] == "pending"]
    next_step = (f"ثم إعداد الفصل {pending[0]['number']}: {pending[0]['title_ar']}. "
                 if pending else "لا توجد فصول مرقمة متبقية؛ راجع المواد الأخرى وحالة المراجعة. ")
    rows.extend([""])
    rows.extend(note for note in roadmap.get("notes", []))
    if roadmap.get("notes"):
        rows.append("")
    other = [item["title_ar"] for item in data["other_source_material"]
             if item["status"] == "pending"]
    if other:
        rows.extend(["**مواد أخرى لم تُعد بعد:** " + "، ".join(other) + ".", ""])
    rows.extend([
        "**الخطوة التالية بعد المراجعة:** "
        + roadmap.get(
            "review_gate",
            "انتظار ملاحظات المستخدم على الدفعة الحالية؛ ",
        )
        + next_step + "لا يحتوي هذا الإصدار على "
        "صفحات فارغة أو ملخصات بديلة تدّعي أنها الفصول المتبقية.",
        "",
    ])
    return "\n".join(rows)


def cover_html(data: dict[str, Any]) -> str:
    edition = data["edition"]
    source = data["source"]
    subtitle = "<br />".join(html.escape(line) for line in edition["cover_lines"])
    title = "<br />".join(html.escape(line) for line in edition["cover_title_lines"])
    original = "<br />".join(html.escape(line) for line in source["cover_lines"])
    return f'''<div class="cover" dir="rtl">
<p class="cover-kicker">{html.escape(edition['kicker'])} · {html.escape(edition['label'])}</p>
<p class="cover-title">{title}</p>
<p class="cover-subtitle">{subtitle}</p>
<p class="cover-credit">{html.escape(edition['cover_credit'])}</p>
<p class="cover-author">{html.escape(source['author_ar'])}</p>
<p class="cover-original" dir="ltr">{original}</p>
<div class="cover-scope" dir="rtl"><strong>{html.escape(edition['cover_scope'])}</strong><br />
{html.escape(edition['cover_disclaimer'])}<br />{html.escape(edition['pending_note'])}</div>
<p class="cover-date">{html.escape(edition['date_ar'])} · Markdown + PDF</p>
</div>'''


def toc_entries(documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    entries = []
    for document in documents:
        entries.extend(h for h in document["headings"]
                       if h["level"] <= document.get("toc_depth", 1))
    entries.append({"id": "roadmap", "title": "خريطة إنجاز الكتاب", "level": 1})
    return entries


def compose_html(data: dict[str, Any], documents: list[dict[str, Any]],
                 pages: dict[str, int] | None = None) -> str:
    pages = pages or {}
    rows = []
    for entry in toc_entries(documents):
        cls = "toc-sub" if entry["level"] > 1 else "toc-main"
        title = html.escape(entry["title"])
        rows.append(
            f'<tr><td class="{cls}"><a href="#{entry["id"]}">{title}</a></td>'
            f'<td class="toc-number" dir="ltr">{pages.get(entry["id"], "—")}</td></tr>'
        )
    contents = '''<div class="contents" dir="rtl">
<h1 id="contents" dir="rtl">محتويات هذه الدفعة</h1>
<p>مسار تأسيسي بالعربية: اقرأ الفكرة، شاهد المخطط، ثم جرّب ولاحظ.</p>
<table class="toc-table" dir="rtl">''' + "".join(rows) + '''</table>
<p class="contents-note">العناوين روابط داخلية. الأرقام تشير إلى صفحات هذه النسخة العربية،
بما فيها الغلاف. إحالات المصدر في المتن تشير إلى صفحات الملف الإنجليزي.
يمكنك كذلك التنقل من العلامات المرجعية في قارئ PDF.</p>
</div>'''
    chapters = "\n".join(
        f'<div class="chapter {d["id"]}" dir="rtl">{d["html"]}</div>'
        for d in documents
    )
    roadmap = markdown.markdown(roadmap_markdown(data), extensions=["tables"])
    roadmap = roadmap.replace("<h1>", '<h1 id="roadmap">', 1)
    roadmap = '<div class="chapter roadmap" dir="rtl">' + enforce_direction(roadmap) + '</div>'
    return (
        '<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8" />'
        f'<title>{html.escape(data["edition"]["title"])} — {html.escape(data["edition"]["label"])}</title></head><body dir="rtl">'
        + cover_html(data) + contents + chapters + roadmap + '</body></html>'
    )


class HTMLAudit(HTMLParser):
    """Reject duplicate/missing targets and unisolated command text before layout."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.errors: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        identifier = values.get("id")
        if identifier:
            if identifier in self.ids:
                self.errors.append(f"Duplicate HTML ID: {identifier}")
            self.ids.add(identifier)
        if tag == "a" and values.get("href"):
            self.links.append(values["href"])
        if tag in {"pre", "code", "kbd", "samp"} and values.get("dir") != "ltr":
            self.errors.append(f"Missing dir=ltr on {tag}")
        if tag in {"img", "link", "script", "iframe"}:
            self.errors.append(f"Unexpected external/active asset tag: {tag}")

    def validate(self) -> None:
        for link in self.links:
            if link.startswith("#") and link[1:] not in self.ids:
                self.errors.append(f"Broken internal link: {link}")
            if not link.startswith(("#", "https://")):
                self.errors.append(f"Unexpected link: {link}")
        if self.errors:
            raise ValueError("\n".join(self.errors))


def check_html(markup: str) -> None:
    audit = HTMLAudit()
    audit.feed(markup)
    audit.validate()


def combined_markdown(data: dict[str, Any], documents: list[dict[str, Any]]) -> str:
    mapping = {Path(d["file"]).name: d["id"] for d in documents}
    edition = data["edition"]
    lines = [
        '<div dir="rtl" lang="ar">', "",
        f"# {edition['title']} — {edition['label']}", "",
        f"**{edition['subtitle']} · {edition['date_ar']}**", "",
        f"> {edition['scope_note']}", "",
        edition["attribution_note"], "",
        "## محتويات الدفعة", "",
    ]
    lines.extend(f"- [{d['title']}](#{d['id']})" for d in documents)
    lines.extend(["- [خريطة إنجاز الكتاب](#roadmap)", ""])
    for document in documents:
        text = re.sub(
            r"(\]\()([^\s)]+\.md)(\))",
            lambda m: m[1] + document_link(m[2], mapping) + m[3],
            document["markdown"],
        )
        lines.extend([f'<a id="{document["id"]}"></a>', "", text.rstrip(), ""])
    lines.extend(['<a id="roadmap"></a>', "", roadmap_markdown(data), '</div>', ""])
    return "\n".join(lines)


def inline_styles(markup: str, data: dict[str, Any], project: Project) -> str:
    css = project.stylesheet.read_text(encoding="utf-8")
    header = (f"{data['edition']['title']} · {data['edition']['kicker']} · "
              f"{data['edition']['label']}")
    css = css.replace('"__BOOK_RUNNING_HEADER__"', json.dumps(header, ensure_ascii=False))
    fonts_dir = project.fonts_dir

    def font_url(match: re.Match[str]) -> str:
        path = (fonts_dir / match[1]).resolve()
        if not path.is_relative_to(fonts_dir.resolve()) or path.suffix != ".ttf":
            raise ValueError("The stylesheet may only load bundled TTF fonts")
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        return f'url("data:font/ttf;base64,{encoded}")'

    css = re.sub(r'url\("([^"]+)"\)', font_url, css)
    return markup.replace("</head>", "<style>" + css + "</style></head>", 1)


def build(output_dir: Path, project: Project) -> dict[str, Any]:
    data = load_manifest(project)
    verify_archives(data, project)
    documents = prepare_documents(data, project)
    markup = compose_html(data, documents)
    check_html(markup)
    edition = data["edition"]
    with tempfile.TemporaryDirectory(prefix=f"{project.slug}-") as directory:
        scratch = Path(directory)
        source = scratch / "book.html"
        raw_pdf = scratch / "book.pdf"
        report_path = scratch / "pagination.json"
        source.write_text(inline_styles(markup, data, project), encoding="utf-8")
        try:
            subprocess.run(
                ["node", str(project.root / "scripts" / "render_pdf.mjs"), str(source),
                 str(raw_pdf), str(report_path)],
                cwd=project.root, check=True, capture_output=True, text=True, timeout=180,
            )
        except subprocess.CalledProcessError as exc:
            raise ValueError(
                "Local PDF renderer failed. Run npm ci and check the prerequisites.\n"
                + exc.stderr.strip()
            ) from exc
        except subprocess.TimeoutExpired as exc:
            raise ValueError("PDF renderer exceeded the 180-second limit") from exc
        report = json.loads(report_path.read_text(encoding="utf-8"))
        pages = report["headingPages"]
        headings = [{"id": "contents", "level": 1, "title": "محتويات هذه الدفعة"}]
        for document in documents:
            headings.extend(document["headings"])
        headings.append({"id": "roadmap", "level": 1, "title": "خريطة إنجاز الكتاب"})
        missing = [entry["id"] for entry in headings if entry["id"] not in pages]
        if missing:
            raise ValueError(f"Headings missing from the rendered PDF: {missing}")
        with pymupdf.open(raw_pdf) as pdf:
            if len(pdf) != report["pageCount"]:
                raise ValueError("Printed page count differs from the paginated contents")
            pdf.set_toc([[h["level"], h["title"], pages[h["id"]]] for h in headings], collapse=1)
            date = edition["date"].replace("-", "")
            pdf.set_metadata({
                "title": f"{edition['title']} — {edition['label']} "
                         f"({edition['pdf_partial_label']})",
                "author": edition["pdf_author"],
                "subject": edition["scope_note"],
                "keywords": ", ".join(
                    [*edition["pdf_keywords"], *(
                        f"Chapter {ch['number']}"
                        for ch in data["chapters"] if ch["status"] == "draft"
                    )],
                ),
                "creator": "scripts/build_book.py + scripts/render_pdf.mjs",
                "producer": pdf.metadata.get("producer", "Chromium"),
                "creationDate": f"D:{date}000000",
                "modDate": f"D:{date}000000",
            })
            pdf.xref_set_key(pdf.pdf_catalog(), "Lang", "(ar)")
            pdf.xref_set_key(pdf.pdf_catalog(), "ViewerPreferences", "<< /Direction /R2L >>")
            pdf.xref_set_key(pdf.pdf_catalog(), "PageMode", "/UseOutlines")
            output_dir.mkdir(parents=True, exist_ok=True)
            pdf_path = output_dir / (edition["slug"] + ".pdf")
            md_path = output_dir / (edition["slug"] + ".md")
            pdf.save(pdf_path, garbage=4, deflate=True, deflate_fonts=True, no_new_id=True)
            page_count = len(pdf)
        md_path.write_text(combined_markdown(data, documents), encoding="utf-8")
    return {"pdf": pdf_path, "markdown": md_path, "pages": page_count,
            "heading_pages": pages, "verified_blocks": report["verifiedBlocks"]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--book", help="Book project slug under books/ "
                                       "(required once the repository holds more than one)")
    parser.add_argument("--output-dir", type=Path, default=None,
                        help="Defaults to books/<slug>/editions")
    parser.add_argument("--check", action="store_true",
                        help="Validate sources and links without writing outputs")
    parser.add_argument("--verify-source", action="store_true",
                        help="Also verify the unchanged original file in sources/")
    parser.add_argument("--list", action="store_true", help="List book projects and exit")
    args = parser.parse_args()
    try:
        if args.list:
            for slug in Project.available():
                print(slug)
            return
        project = Project.resolve(args.book)
        data = load_manifest(project)
        verify_archives(data, project)
        for font in REQUIRED_FONTS:
            if not (project.fonts_dir / font).is_file():
                raise ValueError(f"Missing bundled font: {font}")
        if args.verify_source:
            verify_source(data, project)
        if args.check:
            check_html(compose_html(data, prepare_documents(data, project)))
            print(f"OK: {project.slug} — Arabic sources, roadmap, command direction, "
                  "and internal links")
            return
        result = build(args.output_dir or project.editions_dir, project)
        print(f"PDF: {result['pdf']} ({result['pages']} pages)")
        print(f"Markdown: {result['markdown']}")
        available = [str(ch["number"]) for ch in data["chapters"] if ch["status"] == "draft"]
        if not data["chapters"]:
            print("Scope: scaffold only — the roadmap is empty; fill 'chapters' in "
                  f"books/{project.slug}/manifest.json from the original's table of contents")
        elif available:
            print(f"Scope: introduction + chapters {', '.join(available)}; "
                  f"{len(data['chapters']) - len(available)} chapters remain pending")
        else:
            print(f"Scope: no drafted chapter yet; all {len(data['chapters'])} remain pending")
    except (ValueError, OSError, KeyError) as exc:
        parser.exit(1, f"Book build failed: {exc}\n")


if __name__ == "__main__":
    main()
