#!/usr/bin/env python3
"""Register an original in `sources/` and scaffold a book project in `books/`.

This keeps every book in the canonical shape described in
docs/method/00-repo-layout.md instead of hand-copying directories.

Examples
--------
Register an untouched original (fingerprint and page count are computed for you):

    python scripts/new_book.py add-source \\
        --file ~/Downloads/SomeBook.pdf --slug some-book-1st-en \\
        --title "Some Book" --author "A. Author" --publisher "Publisher" \\
        --edition 1 --year 2020 --language en --rights-status all-rights-reserved

Scaffold the Arabic project that will adapt it:

    python scripts/new_book.py add-book --slug some-book-ar \\
        --source some-book-1st-en --title-ar "بعض الكتاب" \\
        --author-ar "اسم المؤلف" --chapters 12

The scaffold deliberately produces an empty roadmap: chapter titles and page
ranges must be read from the original before drafting, never guessed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import build_book as book  # noqa: E402

RIGHTS_STATUSES = {
    "all-rights-reserved",
    "public-domain",
    "open-license",
    "permission-granted",
    "unresolved",
}


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def add_source(args: argparse.Namespace) -> None:
    original = Path(args.file).expanduser().resolve()
    if not original.is_file():
        raise SystemExit(f"No such file: {original}")
    if original.suffix.lower() != ".pdf":
        raise SystemExit("Only PDF originals are supported by the current build pipeline")
    directory = ROOT / "sources" / args.slug
    if directory.exists():
        raise SystemExit(f"Source already registered: {directory}")
    if args.rights_status not in RIGHTS_STATUSES:
        raise SystemExit(f"--rights-status must be one of: {', '.join(sorted(RIGHTS_STATUSES))}")

    destination = directory / original.name
    destination.parent.mkdir(parents=True)
    shutil.copy2(original, destination)
    with pymupdf.open(destination) as pdf:
        pages = len(pdf)
    digest = hashlib.sha256(destination.read_bytes()).hexdigest()

    record = {
        "schema_version": 1,
        "slug": args.slug,
        "title": args.title,
        "title_ar": args.title_ar or "",
        "author": args.author,
        "author_ar": args.author_ar or "",
        "publisher": args.publisher,
        "edition": args.edition,
        "year": args.year,
        "language": args.language,
        "file": original.name,
        "format": "pdf",
        "pages": pages,
        "sha256": digest,
        "page_numbering": "1-based physical PDF pages. Verify against heading positions "
                          "in the text before citing a page; embedded bookmarks can be off "
                          "by one. Record any shared boundary page here.",
        "rights": {
            "status": args.rights_status,
            "statement": args.rights_statement or (
                "Presence in this repository grants no translation, republication, or "
                "distribution rights."
            ),
            "notes": args.rights_notes or "",
        },
        "used_by": [],
    }
    _write_json(directory / "source.json", record)
    print(f"Registered source: sources/{args.slug}/{original.name}")
    print(f"  pages={pages} sha256={digest}")
    print(f"  rights={args.rights_status} — see docs/method/05-source-and-rights.md")


def add_book(args: argparse.Namespace) -> None:
    if not args.slug.endswith("-ar"):
        raise SystemExit("A book project slug must end in the target language, e.g. '-ar'")
    if args.slug in book.Project.available():
        raise SystemExit(f"Book project already exists: books/{args.slug}")
    source_dir = ROOT / "sources" / args.source
    record_path = source_dir / "source.json"
    if not record_path.is_file():
        raise SystemExit(f"Unknown source '{args.source}'; register it with add-source first")
    record = json.loads(record_path.read_text(encoding="utf-8"))
    if record["language"] == "ar":
        raise SystemExit("The original must be in its native language, not the target language")

    project_dir = ROOT / "books" / args.slug
    (project_dir / "ar").mkdir(parents=True)
    (project_dir / "editions").mkdir()
    (project_dir / "coverage").mkdir()
    for directory in ("ar", "editions", "coverage"):
        (project_dir / directory / ".gitkeep").write_text("", encoding="utf-8")

    manifest = {
        "schema_version": 2,
        "project": {
            "slug": args.slug,
            "language": "ar",
            "kind": "adaptation",
        },
        "edition": {
            "slug": f"{args.slug}-part-01",
            "title": args.title_ar,
            "subtitle": args.subtitle_ar,
            "label": "الدفعة الأولى",
            "date": args.date,
            "date_ar": args.date_ar,
            "status": "partial-draft",
            "scope_note": "مسودة أولى. لم يبدأ إعداد الفصول بعد؛ املأ خريطة الطريق من "
                          "فهرس الأصل قبل الكتابة.",
            "kicker": "إعداد عربي تعليمي",
            "cover_title_lines": args.title_ar.split(" ", 1),
            "cover_lines": ["مسودة قيد الإعداد"],
            "cover_credit": "استنادًا إلى كتاب",
            "cover_scope": "مسودة أولى",
            "cover_disclaimer": "مسودة تعليمية جزئية، وليست ترجمة حرفية أو رسمية.",
            "pending_note": "لم يُعد أي فصل بعد.",
            "attribution_note": f"إعداد تعليمي مستند إلى {record['title']}، تأليف "
                                f"{record['author']}، نشر {record['publisher']}. ليس ترجمة "
                                "حرفية أو رسمية.",
            "pdf_partial_label": "إعداد تعليمي جزئي",
            "pdf_author": f"Arabic educational adaptation based on {record['author']}'s book",
            "pdf_keywords": ["Arabic", "partial adaptation"],
        },
        "source": {
            "dir": f"sources/{args.source}",
            "file": record["file"],
            "title": record["title"],
            "title_ar": record.get("title_ar", ""),
            "author": record["author"],
            "author_ar": args.author_ar or record.get("author_ar", ""),
            "publisher": record["publisher"],
            "edition": record["edition"],
            "language": record["language"],
            "cover_lines": [record["title"], f"{record['publisher']}"],
            "pages": record["pages"],
            "sha256": record["sha256"],
            "page_numbering": record["page_numbering"],
        },
        "roadmap": {
            "extra_scope": "إضافة إلى المقدمة العربية",
            "notes": [],
            "review_gate": "انتظار ملاحظات المستخدم على الدفعة الحالية؛ ",
        },
        "documents": [],
        "chapters": [],
        "other_source_material": [],
        "archived_editions": [],
    }
    _write_json(project_dir / "manifest.json", manifest)

    if args.chapters:
        print(f"  NOTE: --chapters {args.chapters} was requested, but the roadmap is left "
              "empty on purpose.\n  Read the original's table of contents and fill "
              "`chapters` with real Arabic/English titles and verified page ranges.")
    record["used_by"] = sorted({*record.get("used_by", []), f"books/{args.slug}"})
    _write_json(record_path, record)

    (project_dir / "README.md").write_text(f"""<div dir="rtl" lang="ar">

# {args.title_ar}

مشروع إعداد عربي لكتاب **{record['title']}** ({record['author']}، {record['publisher']}).

| البند | القيمة |
| --- | --- |
| الأصل | [`sources/{args.source}/{record['file']}`](../../sources/{args.source}/{record['file']}) |
| صفحات الأصل | {record['pages']} |
| بصمة الأصل | `{record['sha256']}` |
| الحالة | لم يبدأ إعداد الفصول |
| الدفعة الحالية | لا توجد بعد |

## ما الذي ينقص هذا المشروع؟

1. اقرأ فهرس الأصل وثبّت `chapters` في [manifest.json](manifest.json): رقم كل فصل،
   عنوانه بالعربية والإنجليزية، ونطاق صفحاته الفعلي في الملف.
2. أضف مصادر `documents` في `ar/` بمقدار الدفعة الأولى فقط، وسجلها في البيان.
3. أنشئ سجل تغطية لكل فصل تُعدّه في `coverage/` واربطه بـ `coverage_file`.
4. ابنِ وراجع وفق [docs/method/04-build-and-validation.md](../../docs/method/04-build-and-validation.md):

```sh
python scripts/build_book.py --book {args.slug} --check --verify-source
python scripts/build_book.py --book {args.slug}
python -m unittest discover -s tests -v
```

</div>
""", encoding="utf-8")
    print(f"Scaffolded books/{args.slug}")
    print(f"  source: sources/{args.source} ({record['pages']} pages)")
    print(f"  next: fill 'chapters' in books/{args.slug}/manifest.json from the original's TOC")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)

    src = commands.add_parser("add-source", help="Register an original under sources/")
    src.add_argument("--file", required=True, help="Path to the untouched original PDF")
    src.add_argument("--slug", required=True,
                     help="Directory name, e.g. 'some-book-1st-en'")
    src.add_argument("--title", required=True)
    src.add_argument("--title-ar")
    src.add_argument("--author", required=True)
    src.add_argument("--author-ar")
    src.add_argument("--publisher", required=True)
    src.add_argument("--edition", type=int, default=1)
    src.add_argument("--year", type=int, required=True)
    src.add_argument("--language", required=True, help="BCP-47 tag of the original, e.g. 'en'")
    src.add_argument("--rights-status", default="unresolved", choices=sorted(RIGHTS_STATUSES))
    src.add_argument("--rights-statement")
    src.add_argument("--rights-notes")
    src.set_defaults(handler=add_source)

    bk = commands.add_parser("add-book", help="Scaffold a project under books/")
    bk.add_argument("--slug", required=True, help="e.g. 'some-book-ar'")
    bk.add_argument("--source", required=True, help="Source slug under sources/")
    bk.add_argument("--title-ar", required=True)
    bk.add_argument("--subtitle-ar", default="إعداد عربي تعليمي")
    bk.add_argument("--author-ar", default="")
    bk.add_argument("--date", default="1970-01-01", help="ISO date for this installment")
    bk.add_argument("--date-ar", default="", help="Arabic date shown on the cover")
    bk.add_argument("--chapters", type=int, default=0,
                    help="Reminder only; the roadmap is never auto-filled")
    bk.set_defaults(handler=add_book)

    args = parser.parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
