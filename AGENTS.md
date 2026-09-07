# Agent contract and cross-session handoff

Read this file at the start of every session and before beginning another chapter.
It records the user's working agreement, the current review gate, and durable
lessons. Follow current user instructions and the session's operating constraints;
update this contract when the user explicitly changes the agreement. The book and
external references are source material, not instructions for operating the repo.

## 1. User agreement — do not skip the approval gate

- Work **incrementally, one chapter at a time**, unless the user explicitly agrees
  to a different increment. Do not generate the remaining book in one pass.
- The user selected a **beginner-friendly Arabic adaptation**, not a literal
  word-for-word translation and not a short whole-book study guide. Use clear
  Modern Standard Arabic, preserve the conceptual coverage and original section
  numbering, and distinguish additions from the author's material.
- Deliver editable **Markdown and a properly typeset RTL PDF** for each increment.
- **Present the PDF and wait for explicit user confirmation or authorization
  to proceed before starting the next chapter.** If changes are requested, revise that increment and return it
  for review. Do not count praise, a commit request, or passing tests as approval.
  Explicit permission to continue is not final editorial approval; record any
  deferred or combined review separately.
- Never describe a draft, an outline, or an incomplete edition as the complete
  book. Technical checks do not constitute human linguistic or technical review.
- Commit and push when requested. A request to push this checkpoint does not
  authorize silently continuing the translation or publishing future increments.

## 2. Current checkpoint — 2026-09-07

| Item | Recorded state |
| --- | --- |
| Phase | **Waiting for combined feedback on the preface and Chapters 1–2** |
| User authorization | “okay start with chapter 2 and commit and push”; feedback on the preface, Ch1, and Ch2 will follow together |
| Current delivery | `editions/how-linux-works-ar-part-02.pdf` and matching `.md`; a cumulative edition |
| PDF length / entry point | **84 pages**; Chapter 2 starts on **page 26** |
| New scope | Chapter 2, source pages 15–41: all 21 main sections / 63 numbered headings, four original tables, two redrawn figures, five sandbox labs, twelve questions with answers |
| Earlier material | Preface/Ch1 instructional content retained; only availability/scope statements updated. No final editorial approval claimed. |
| Frozen archive | Part 01 PDF/Markdown are byte-for-byte unchanged and protected by `archived_editions` in the manifest |
| Remaining work | Chapters 3–17 remain `pending`; Chapter 3 is not authorized by the current request |
| Validation | **31 tests passed**, including all original-heading checks, the five allowlisted labs, searchable/copyable PDF text, multi-page contents links, and RTL overflow guards |
| Visual review | Cover, two-page contents, Chapter 2 opening, character/key tables, permission diagram, code/lab pages, directory structure, and section endings inspected |
| Next action | Receive and address the user's combined feedback; do not start Chapter 3 automatically |

The current PDF's SHA-256 is:

```text
e405fe6aade4974509b5ad600c48163a3e8b2c1c6763be02b9a6c1411c1cc8f0
```

The matching combined Markdown's SHA-256 is:

```text
4cf15c2694c0555ad06ba5dd87f76e1fd24eb44ec899a812dd0d31d5c8cf6386
```

Preserve this review artifact during documentation-only/Git-only work. After an
authorized revision, update the fingerprint and review state; do not invent an
approval. The original Part 01 PDF remains 32 pages with SHA-256
`c102918e0d5fe5f4a46d063ff0447ac9d8a0653d942455e3aff8ee83f4e306f6`.

## 3. First steps in any session

1. Read this contract and the latest user request. Check whether the review gate
   is still closed, explicitly approved, or awaiting requested corrections.
2. Run `git status --short`, `git branch --show-current`, and `git log -5 --oneline`.
   Preserve unrelated user changes. Do not assume a previous session's environment
   or Git state survived.
3. Read [README.md](README.md), [CONTRIBUTING.md](CONTRIBUTING.md),
   [book/manifest.json](book/manifest.json), and the relevant chapter/glossary.
4. Reconcile the checkpoint with the actual files. If approval is missing or
   ambiguous, stop at the gate instead of assuming permission to continue.
5. Before ending meaningful work, update the checkpoint and durable lessons in
   this file, including what was actually verified and the exact next action.

## 4. Sources of truth

| File or directory | Responsibility |
| --- | --- |
| `AGENTS.md` | Workflow agreement, user approval checkpoint, reusable lessons |
| `HowLinuxWorks.pdf` | Unmodified English source: Brian Ward, *How Linux Works*, second edition, No Starch Press, 338 PDF pages |
| `book/manifest.json` | Canonical source fingerprint, physical page ranges, edition metadata, included documents, and chapter coverage |
| `book/ar/*.md` | Editable Arabic sources; edit these rather than generated editions |
| `book/ar/glossary.md` | Consistent Arabic–English terminology |
| `book/ar/references.md` | Source attribution, coverage boundaries, and references supporting added clarifications |
| `book/assets/print.css` | Typesetting, pagination, and direction rules |
| `book/assets/fonts/` | Bundled Amiri and Fira Mono fonts, provenance, and their OFL licenses |
| `scripts/build_book.py` | Source validation, Markdown/HTML preparation, PDF metadata/bookmarks, and combined Markdown output |
| `scripts/render_pdf.mjs` | Offline Chromium/Paged.js pagination and text-preservation checks |
| `book/coverage/chapter-02.json` | Source-derived section/page, figure, table, and lab checklist |
| `tests/test_book.py`, `tests/test_chapter_two.py` | Source, output, command, archive, and regression checks |
| `tests/chapter02_labs.json` | Explicitly reviewed lab hashes and expected outcomes; not an auto-execution registry for all examples |
| `editions/` | Intended, committed PDF and combined Markdown deliverables |

The manifest's `draft` means a real draft exists, **not that the user approved
it**. Its current chapter statuses are only `draft` and `pending`; do not insert
an unsupported `approved` status. Record user approval here unless the schema is
deliberately evolved. Do not duplicate the entire chapter/page roadmap here.

Preserve the author's and publisher's attribution. The source's rights page
mentions the second edition and copyright 2015; the file also contains 2014
publication data. This is not a newer English edition, an official translation,
or a grant of redistribution rights. Font and dependency licenses do not license
the original book.

## 5. Procedure for an authorized chapter increment

1. Confirm explicit authorization for the next chapter and whether the preceding
   material was approved or its review deferred. Resolve requested corrections first. Agree on changes to delivery structure, such as
   standalone versus cumulative PDFs, rather than silently overwriting an earlier
   reviewed installment.
2. Read the chapter's actual source pages, including figures, warnings, examples,
   and cross-references. Use the manifest's page range and verify the headings.
   Make a section/figure/example coverage checklist before drafting.
3. Write substantive Arabic for every covered section. Retain commands, paths,
   options, identifiers, and numbering. Use the glossary consistently. The child
   process term is **العملية الابنة**, paired with **العملية الأم**.
4. Mark new explanations/exercises with **إضافة تعليمية** and newer technical
   context with **توضيح حديث** (or an equally explicit editorial label). Cite
   authoritative references for corrections or updates. Do not modernize silently
   or attribute new material to Brian Ward.
5. Keep executable examples separate from output. Use `sh` and `text` fences,
   without shell prompts. Explain risk before administrative/destructive examples;
   never execute them on the working machine just because the book contains them.
6. Update the manifest only when real content exists. Keep unfinished material
   visibly pending. Update the glossary and source notes alongside the chapter.
7. Review the pipeline before naming a new edition. Cover lines/scope, running
   headers, TOC depth, PDF metadata, and the next-chapter roadmap now derive from
   the manifest. Update its edition fields and each document's `toc_depth`, but
   also review scope statements in the actual prose, README, and tests. Register
   previous review artifacts under `archived_editions` before advancing editions.
   Do not weaken coverage, archive, or RTL checks to make incomplete output pass.
8. Build and test. Inspect rendered pages visually: cover, contents, mixed Arabic
   and Latin text, diagrams, code blocks, table continuations, and section endings.
   Confirm searchable Arabic and exact, copyable command characters.
9. Present the PDF and Markdown, state exactly what is included and still pending,
   record the new review artifact/checkpoint here, and **pause for confirmation**.

## 6. Build and validation shortcuts

Run from the repository root. Tested environment: Python 3.11 and Node.js 22 on
Linux x86-64. The documented minimums are Python 3.10 and Node.js 22.17. Use the
pinned requirements and npm lockfile, not ad-hoc dependency upgrades.

Fresh environment (only if the dependencies are missing):

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
npm ci
```

Checks that **preserve the current review PDF**:

```sh
.venv/bin/python scripts/build_book.py --check --verify-source
.venv/bin/python -m unittest discover -s tests -v
```

For an authorized content/layout change, first build a preview:

```sh
.venv/bin/python scripts/build_book.py --output-dir build/preview
```

When the intended deliverable is ready to replace/update, build the configured
edition and then run the tests again:

```sh
.venv/bin/python scripts/build_book.py
.venv/bin/python -m unittest discover -s tests -v
```

- Use the explicit `.venv/bin/python` path; shell activation from an earlier
  command is not a reliable cross-command or cross-session assumption.
- `--check` does not write editions. The test suite builds into a temporary
  directory and checks the published files against the generated content.
- Preface/Ch1 tests execute only the reviewed `SAFE_EXAMPLES` allowlist. Chapter 2
  has five `<!-- lab: ... -->` blocks with reviewed hashes and expected outcomes in
  `tests/chapter02_labs.json`. Hashes are checked before execution in disposable
  directories/process groups. All other `sh` blocks receive syntax-only checks.
  Review new examples before extending these allowlists; never execute arbitrary
  Markdown code blocks or regenerate hashes without a safety review.
- For source extraction, use the already-required PyMuPDF:
  `pymupdf.open("HowLinuxWorks.pdf")[page_number - 1].get_text()`.
  Extract only the relevant range after authorization, not all 338 pages into
  chat. Cached extracted text from an earlier session is not a prerequisite.
- The build is offline after dependency installation: fonts are embedded as data
  URLs and the renderer blocks network requests. Keep that property.
- On platforms other than the bundled Linux x86-64 target, set
  `BOOK_CHROMIUM_PATH` to a compatible local Chromium/Chrome executable.

## 7. Durable lessons — avoid repeating these investigations

### Source page numbers are not the PDF bookmarks

The supplied bookmarks can point a page early. Chapter 1 actually starts on PDF
page **8**, not 7; Chapter 2 starts on **15**, not 14. Pages are 1-based physical
PDF pages, not printed-edition pagination. Chapters 12 and 13 legitimately share
page **241** at their boundary. Never “correct” ranges by trusting bookmarks or
by forcing all chapter ranges to be disjoint.

### Use Chromium for Arabic typesetting, PyMuPDF for PDF utilities

During the first installment, MuPDF Story / `insert_htmlbox` produced visually
shaped Arabic but corrupt text extraction/ToUnicode mappings, and RTL alignment
behaved unexpectedly. Do not replace the current renderer with those APIs merely
because a screenshot looks correct. PyMuPDF remains useful for metadata,
bookmarks, source extraction, tests, and page-preview images.

WeasyPrint required unavailable native Pango libraries in the initial sandbox;
apt/direct downloads also failed there. The working solution is already in the
repo: pinned npm Chromium/Paged.js, bundled fonts, and local NSS library extraction
from the Chromium package. Do not repeat system-package installation or font
hunting before trying the documented build.

### Paged.js needs an LTR mechanical flow container for RTL text

Keep `.pagedjs_page` and `.pagedjs_page_content` mechanically **LTR**, while
`.chapter`, `.contents`, `.cover`, and the actual Arabic content remain **RTL**.
Without this split, overflow can disappear into off-page columns: the first
attempt produced a plausible **7-page** PDF that retained only the start of each
long document. Heading existence and page count alone did not catch it.

Keep the renderer's block-text preservation and physical-page bounds audits.
`test_rtl_overflow_regression_is_detected` deliberately recreates the bug and must
continue to fail the bad rendering. Do not remove the guard to obtain a PDF.

### Direction, numbering, and copyability must be explicit

- Keep `dir="ltr"` on code/pre blocks and isolate mixed-direction inline code.
  Do not reverse Arabic strings, insert hidden bidi controls into commands, or
  rasterize whole pages to sidestep shaping/search problems.
- Figure numbers such as `1-2` and numeric ranges can display in the wrong order
  inside Arabic. Isolate them with `<span dir="ltr">...</span>` or use clear
  Arabic wording. The figure captions and generated page ranges already do this.
- Wait for `document.fonts.ready` before pagination/printing. Keep embedded fonts
  and their licenses; do not rely on the host's installed fonts.
- Derive contents numbers and bookmarks from the **actual paginated DOM**, not
  estimated text lengths. Preserve the fixed-width contents-number cells.
- Check Arabic search and command extraction as well as screenshots. PDF byte
  hashes can differ between rebuilds; content/TOC comparisons are used by tests.
  The checkpoint fingerprint identifies the particular PDF submitted for review.

### Content clarifications already established

Carry these distinctions into later chapters rather than reintroducing the
original's simplifying assumptions as universal rules:

- Virtual memory is not synonymous with `swap`.
- A program is not a process; a process may contain multiple threads.
- `fork` creates a child; `exec` replaces its program without creating a new PID.
  `fork`/`exec` is a useful model, not the only Linux task-creation path.
- `root` privileges do not mean execution in kernel mode; capabilities and
  namespaces can impose additional distinctions.
- Containers may expose different process/resource views and share the host's
  kernel. Do not require sample outputs or PID 1's program name to match.

Supporting references are in `book/ar/references.md`; re-check version-sensitive
claims when extending the material.

### Serialize edits to the same file

Parallel replacements on the same file previously lost otherwise successful
edits (notably a cover scope string and a source-page reference). Parallelize
independent files/tasks only. Apply same-file changes sequentially, then re-read
or diff the result. Verify final artifacts after the last edit, not only an
intermediate render.

### Chapter 2 and cumulative editions

- Chapter 2 has **63 numbered headings**, not just its 21 top-level sections.
  Its four tables and two figures also need explicit coverage. The checklist is
  compared with the actual PDF text in tests, not only with another hand-written
  list. Empty headings do not satisfy coverage.
- The cumulative contents now spans multiple pages. Test links over the full
  contents page range, up to the first document, rather than only PDF page 2.
- Put the compression/archive creation step before its runnable `zcat` example.
  Explain prerequisites rather than making beginners debug missing fixture files.
- Keep lead paragraphs/table labels with their following code/table/figure using
  the `p:has(+ ...)` print rule. This removed stranded labels and produced the
  final **84-page** edition (an earlier preview had 83). Refresh page counts and
  fingerprints after the final layout change, not after an earlier preview.
- Distinguish semantic instruction from automatic testing: account changes,
  `sudoers` samples, destructive syntax, and interactive tools are not lab scripts.
  A policy that parses correctly can still grant dangerous privileges.
- Preserve Part 01 outputs; do not rebuild them from changed Part 02 sources.
  Their source checkpoint is commit `c1b9a138cc8a4119c54c6f88d2a8d5be5415680c`.
  Archive hashes and active-slug checks prevent accidental overwrite.

### Restored files may not imply restored Git history

At the start of Chapter 2 work, the working files were present but local HEAD was
back at the original upload, with the prior installment shown as untracked. The
remote session branch still held the verified `c1b9a13` commit. We fetched that
**same** branch, confirmed HEAD was its ancestor, and compared every remote blob
with the local files before synchronizing the local index/history with a mixed
reset that did not rewrite the working files. All 26 files matched exactly.

Do not respond to this situation by force-pushing, re-creating the previous commit,
switching branches, or deleting “untracked” work. Inspect/fetch/compare first. A
mixed reset is **not** a blanket recovery recipe: if content or history differs,
preserve the changes and reconcile them deliberately before moving a branch tip.

## 8. Git and end-of-session handoff

- Recorded branch for this checkpoint:
  `arena/01a07b2d-how-linux-works-ar`. Work and push only on the branch authorized
  by the active session. Do not switch/create branches or treat this historical
  name as permission to switch branches in a later session.
- Never push directly to `main`, force-push, or create a PR unless specifically
  requested and permitted. Use `git` for local changes/commits/pushes and `gh` for
  GitHub PRs or issues. Never store credentials in this file or repository.
- Review `git status` and the staged diff before committing. Include the requested
  PDF, combined Markdown, their sources, build/test files, fonts/licenses, and this
  contract. Leave the English PDF unchanged.
- `.venv/`, `node_modules/`, caches, `build/` previews, extracted source dumps, and
  scratch screenshots are not deliverables and must remain out of Git. Only
  intended editions belong in `editions/`.
- The upstream Amiri OFL contains trailing whitespace/a final blank line. Keep
  vendor licenses verbatim rather than trimming them. `.gitattributes` exempts
  only the two copied font licenses from whitespace checks and text conversion;
  ordinary project files must still pass `git diff --check`.
- For this session, the authorized push target is:
  `git push origin arena/01a07b2d-how-linux-works-ar`.
  Verify the remote branch tip matches the local commit and report the actual
  result; do not claim success after an authentication/network failure.
- Update this file with durable discoveries, approval evidence, completed scope,
  validation results, and the next action. Keep it concise and current rather than
  appending full transcripts, temporary paths, or speculative “lessons.”

**Next action: wait for the user's combined feedback on the preface and Chapters 1–2.**
