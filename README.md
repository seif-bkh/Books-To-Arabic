<div dir="rtl" lang="ar">

# كتب مُعدّة إلى العربية

مستودع علمي لإعداد كتب تقنية باللغة العربية الفصحى: لكل كتاب **مشروع مستقل** بمصادره
وسجلات تغطيته ودفعاته المسلّمة، ولكل أصل **سجل مصدر** ببصمته وحالته الحقوقية. الطريقة
والدروس محفوظة في مرجع قار واحد حتى لا يعيد أحد تحقيق مسألة حُلّت.

> **تنبيه حقوقي:** وجود أصل في هذا المستودع لا يمنح إذنًا بترجمته أو إعادة نشره أو
> توزيعه؛ الحقوق تبقى لأصحابها. الإعدادات العربية مسودات تعليمية جزئية، لا ترجمات
> رسمية ولا كتبًا كاملة. راجع
> [سياسة الأصول والحقوق](docs/method/05-source-and-rights.md).

## الكتب

| الكتاب | الأصل | الحالة | أحدث دفعة |
| --- | --- | --- | --- |
| [كيف يعمل لينكس](books/how-linux-works-ar/README.md) | *How Linux Works*, 2nd ed. — Brian Ward | مسودة: المقدمة والفصلان 1–2 من 17 | [PDF · 84 صفحة](books/how-linux-works-ar/editions/how-linux-works-ar-part-02.pdf) |

لكل كتاب بطاقة مشروع في `books/<slug>/README.md` تسجّل حالته ودفعاته وخطوته التالية،
وبيان آلي في `books/<slug>/manifest.json` هو المرجع الوحيد لنطاقه وحالة فصوله.

**لا يوجد أي كتاب مكتمل هنا.** ذكر عنوان فصل في خريطة الطريق لا يعني إعداد محتواه.

## طريقة العمل — المرجع القار

ابدأ من هنا قبل أي عمل. هذه الملفات هي المرجع المعتمد للطريقة وللصعوبات وحلولها:

| الملف | المحتوى |
| --- | --- |
| [docs/method/README.md](docs/method/README.md) | فهرس المرجع والحدود بين ملفاته |
| [docs/method/00-repo-layout.md](docs/method/00-repo-layout.md) | بنية المستودع وقواعد التسمية وإضافة كتاب |
| [docs/method/01-translation-method.md](docs/method/01-translation-method.md) | خطوات الإعداد من الأصل إلى التسليم وبوابة الموافقة |
| [docs/method/02-terminology-policy.md](docs/method/02-terminology-policy.md) | سياسة المصطلحات وما يبقى باللاتينية |
| [docs/method/03-rtl-typesetting.md](docs/method/03-rtl-typesetting.md) | صعوبات الاتجاه العربي والتنضيد وحلولها |
| [docs/method/04-build-and-validation.md](docs/method/04-build-and-validation.md) | أوامر البناء والفحص والاختبار |
| [docs/method/05-source-and-rights.md](docs/method/05-source-and-rights.md) | البصمات، أرقام الصفحات، والحقوق |
| [docs/method/06-lessons-log.md](docs/method/06-lessons-log.md) | سجل الدروس: كل مشكلة وقعت وحلّها ومكان فرضه |

ويكملها:

- [AGENTS.md](AGENTS.md) — عقد العمل مع المستخدم: بوابة الموافقة وحالة المراجعة الجارية.
- [CONTRIBUTING.md](CONTRIBUTING.md) — دليل المساهم المختصر.

## بنية المستودع

```text
docs/method/     المرجع القار للطريقة والدروس
assets/          التنضيد والخطوط المشتركة (مع تراخيصها)
sources/         الأصول بلغتها الأم + source.json لكل أصل — للقراءة فقط
books/<slug>/    مشروع كتاب: manifest.json، ar/، coverage/، editions/
scripts/         build_book.py (--book)، new_book.py، render_pdf.mjs
tests/           فحوص البنية العامة + فحوص كل كتاب باسمه
```

التفاصيل والقواعد في [docs/method/00-repo-layout.md](docs/method/00-repo-layout.md).

## إضافة كتاب جديد

```sh
python scripts/new_book.py add-source --file ~/book.pdf --slug some-book-1st-en \
    --title "Some Book" --author "A. Author" --publisher "Publisher" \
    --edition 1 --year 2020 --language en --rights-status unresolved

python scripts/new_book.py add-book --slug some-book-ar --source some-book-1st-en \
    --title-ar "بعض الكتاب" --author-ar "المؤلف"
```

تُحسب بصمة الأصل وعدد صفحاته تلقائيًا، ويُنشأ المشروع بالهيكل القانوني. خريطة الطريق
تبقى **فارغة عمدًا**: عناوين الفصول ونطاقات صفحاتها تُقرأ من الأصل ولا تُخمَّن.
`tests/test_repository_layout.py` يفرض هذه البنية على كل الكتب.

## البناء والفحص

**المتطلبات:** Python 3.10+ وNode.js 22.17+ وnpm. اختُبر على Linux x86-64 بـ Python 3.11
وNode.js 22. البناء محلي ولا يرسل النص إلى أي خدمة ترجمة أو إلى الإنترنت.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
npm ci

python scripts/build_book.py --book how-linux-works-ar --check --verify-source
python scripts/build_book.py --book how-linux-works-ar
python -m unittest discover -s tests -v
```

`scripts/build_book.py --list` يسرد المشاريع المتاحة. لا تحتاج LaTeX ولا خطوط نظام؛
خطوط Amiri وFira Mono مرفقة في [assets/fonts](assets/fonts/README.md) بتراخيصها. على
منصة أخرى عيّن `BOOK_CHROMIUM_PATH` إلى متصفح متوافق. التفاصيل في
[docs/method/04-build-and-validation.md](docs/method/04-build-and-validation.md).

## متابعة الإعداد

اقرأ [AGENTS.md](AGENTS.md) أولًا: يسجّل بوابة الموافقة وحالة المراجعة. **لا يبدأ فصل
جديد قبل تأكيد المستخدم على PDF الدفعة الحالية**؛ طلب الحفظ أو الدفع إلى Git لا يُعد
موافقة على المحتوى.

</div>

---

**English:** A scientific repository for Arabic (Modern Standard Arabic) educational
adaptations of technical books. Each book is an independent project under `books/<slug>/`;
each original lives untouched under `sources/<slug>/` with a provenance and rights record;
and the translation method, the difficulties encountered, and their solutions are kept in
one durable reference under [`docs/method/`](docs/method/README.md).

Currently one project: **How Linux Works** (Brian Ward, 2nd ed.) — a **partial draft**
covering the preface and Chapters 1–2 of 17, delivered as an 84-page RTL PDF
(SHA-256 `b15b60c2…` recorded in `AGENTS.md`). Chapters 3–17 are pending and no chapter has
final editorial approval. This is not an unabridged or authorized translation, and the
presence of an original grants no redistribution rights.
