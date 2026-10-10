<div dir="rtl" lang="ar">

# ما بعد «فايب كودينغ» — مشروع الإعداد العربي

إعداد عربي تعليمي للمبتدئين والمتوسطين مستند إلى **Beyond Vibe Coding: From Coder to
AI-Era Developer**، الطبعة الأولى، تأليف **Addy Osmani**، نشر **O'Reilly Media** (2025).

> **الحالة: الدفعة الأولى، مسودة بانتظار المراجعة.** المتاح المقدمة العربية والفصل الأول
> فقط؛ الفصول من الثاني إلى الحادي عشر لم تُعد بعد. لا توجد موافقة تحريرية نهائية على أي
> جزء. بوابة الموافقة وحالة المراجعة في [AGENTS.md](../../AGENTS.md).

## الأصل

| البند | القيمة |
| --- | --- |
| الأصل | [`sources/beyond-vibe-coding-1st-en/BeyondVibeCoding.pdf`](../../sources/beyond-vibe-coding-1st-en/BeyondVibeCoding.pdf) |
| صفحات الأصل | 255 (فيزيائية 1-based) |
| البصمة | `fe15d56a45c4a4d4906b0968447e624655c165a3329d38f24fb06d6b950cf938` |
| الحقوق | محفوظة للمؤلف والناشر — راجع [`source.json`](../../sources/beyond-vibe-coding-1st-en/source.json) |

## الدفعة الحالية

- **[PDF — 40 صفحة](editions/beyond-vibe-coding-ar-part-01.pdf)**: المقدمة العربية والفصل
  الأول، مع معجم ومراجع. الفصل الأول يبدأ في الصفحة 8.
- **[Markdown المجمّع](editions/beyond-vibe-coding-ar-part-01.md)**: المادة نفسها نصيًا.

| المادة | الملف | نطاق المصدر |
| --- | --- | --- |
| المقدمة التعليمية | [00-preface.md](ar/00-preface.md) | صفحات 9–14 |
| الفصل الأول: المقدمة — ما «فايب كودينغ»؟ | [01-introduction-vibe-coding.md](ar/01-introduction-vibe-coding.md) | صفحات 17–52 |
| المعجم | [glossary.md](ar/glossary.md) | — |
| ملاحظات الإعداد والمراجع | [references.md](ar/references.md) | — |

يحافظ الفصل الأول على **27 عنوانًا مرقمًا** (تسعة أقسام وثمانية عشر قسمًا فرعيًا) و**ثلاثة
أشكال** أعيد رسمها بتسميات عربية. الأصل لا يطبع أرقام أقسام؛ اعتمدنا ترقيمًا تعليميًا موثقًا
في [coverage/chapter-01.json](coverage/chapter-01.json). لا توجد أوامر طرفية في هذا الفصل؛
التوجيهات النصية معروضة كتل `text` قابلة للنسخ، ولا مختبرات آلية.

## ملفات المشروع

| الملف | الدور |
| --- | --- |
| [`manifest.json`](manifest.json) | الحقيقة الآلية: النطاق، الفصول، الوثائق، وبيانات الغلاف وPDF |
| [`ar/`](ar) | المصادر العربية القابلة للتحرير — التحرير هنا فقط |
| [`coverage/chapter-01.json`](coverage/chapter-01.json) | سجل مقابلة عناوين الفصل الأول بالأصل وصفحاته |
| [`editions/`](editions) | المخرجات المسلّمة (مولّدة بالبناء، لا تُحرَّر يدويًا) |

## الخطوة التالية

انتظار ملاحظات المستخدم على الدفعة الأولى؛ ثم إعداد الفصل الثاني (صفحات 53–78) بعد إذن
جديد. الطريقة العامة في [docs/method/](../../docs/method/README.md).

```sh
python scripts/build_book.py --book beyond-vibe-coding-ar --check --verify-source
python scripts/build_book.py --book beyond-vibe-coding-ar
python -m unittest discover -s tests -v
```

</div>
