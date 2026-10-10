<div dir="rtl" lang="ar">

# كيف يعمل لينكس — مشروع الإعداد العربي

إعداد عربي تعليمي للمبتدئين مستند إلى **How Linux Works: What Every Superuser Should
Know**، الطبعة الثانية، تأليف **Brian Ward**، نشر **No Starch Press**.

> **الحالة: الدفعة الثانية، مسودة تراكمية بانتظار المراجعة.** المتاح المقدمة والفصلان
> الأول والثاني فقط؛ الفصول من الثالث إلى السابع عشر لم تُعد بعد. لا توجد موافقة
> تحريرية نهائية على أي جزء. الحالة التفصيلية وبوابة الموافقة في
> [AGENTS.md](../../AGENTS.md).

## الأصل

| البند | القيمة |
| --- | --- |
| الأصل | [`sources/how-linux-works-2nd-en/HowLinuxWorks.pdf`](../../sources/how-linux-works-2nd-en/HowLinuxWorks.pdf) |
| صفحات الأصل | 338 (فيزيائية 1-based) |
| البصمة | `de56a39307fe5d8d9b5283d884ee8418241b283556fbf5ae9b13dc2360d065fa` |
| الحقوق | محفوظة للمؤلف والناشر — راجع [`source.json`](../../sources/how-linux-works-2nd-en/source.json) |

## الدفعة الحالية

- **[PDF — 84 صفحة](editions/how-linux-works-ar-part-02.pdf)**: المقدمة والفصلان الأول
  والثاني، مع معجم ومختبرات ومراجع. الفصل الثاني يبدأ في الصفحة 26.
- **[Markdown المجمّع](editions/how-linux-works-ar-part-02.md)**: المادة نفسها نصيًا.
- الدفعة الأولى محفوظة دون تغيير في `editions/how-linux-works-ar-part-01.*` وبصماتها
  مثبتة في `archived_editions`.

| المادة | الملف | نطاق المصدر |
| --- | --- | --- |
| المقدمة التعليمية | [00-preface.md](ar/00-preface.md) | صفحات 4–6 |
| الفصل الأول: الصورة العامة | [01-the-big-picture.md](ar/01-the-big-picture.md) | صفحات 8–14 |
| الفصل الثاني: الأوامر الأساسية وبنية الأدلة | [02-basic-commands.md](ar/02-basic-commands.md) | صفحات 15–41 |
| المعجم | [glossary.md](ar/glossary.md) | — |
| ملاحظات الإعداد والمراجع | [references.md](ar/references.md) | — |

## ملفات المشروع

| الملف | الدور |
| --- | --- |
| [`manifest.json`](manifest.json) | الحقيقة الآلية: النطاق، الفصول، الوثائق، الأرشيف، وبيانات الغلاف وPDF |
| [`ar/`](ar) | المصادر العربية القابلة للتحرير — التحرير هنا فقط |
| [`coverage/chapter-02.json`](coverage/chapter-02.json) | سجل مقابلة عناوين الفصل الثاني بالأصل وصفحاته |
| `assets/print.css` | غير موجود: يُستخدم [`assets/print.css`](../../assets/print.css) المشترك |
| [`editions/`](editions) | المخرجات المسلّمة (مولّدة بالبناء، لا تُحرَّر يدويًا) |

## البناء

```sh
python scripts/build_book.py --book how-linux-works-ar --check --verify-source
python scripts/build_book.py --book how-linux-works-ar
python -m unittest discover -s tests -v
```

الطريقة العامة وقواعدها في [docs/method/](../../docs/method/README.md).

</div>
