<div dir="rtl" lang="ar">

# ما بعد «فايب كودينغ»

مشروع إعداد عربي لكتاب **Beyond Vibe Coding: From Coder to AI-Era Developer** (Addy Osmani، O'Reilly Media).

| البند | القيمة |
| --- | --- |
| الأصل | [`sources/beyond-vibe-coding-1st-en/BeyondVibeCoding.pdf`](../../sources/beyond-vibe-coding-1st-en/BeyondVibeCoding.pdf) |
| صفحات الأصل | 255 |
| بصمة الأصل | `fe15d56a45c4a4d4906b0968447e624655c165a3329d38f24fb06d6b950cf938` |
| الحالة | لم يبدأ إعداد الفصول |
| الدفعة الحالية | لا توجد بعد |

## ما الذي ينقص هذا المشروع؟

1. اقرأ فهرس الأصل وثبّت `chapters` في [manifest.json](manifest.json): رقم كل فصل،
   عنوانه بالعربية والإنجليزية، ونطاق صفحاته الفعلي في الملف.
2. أضف مصادر `documents` في `ar/` بمقدار الدفعة الأولى فقط، وسجلها في البيان.
3. أنشئ سجل تغطية لكل فصل تُعدّه في `coverage/` واربطه بـ `coverage_file`.
4. ابنِ وراجع وفق [docs/method/04-build-and-validation.md](../../docs/method/04-build-and-validation.md):

```sh
python scripts/build_book.py --book beyond-vibe-coding-ar --check --verify-source
python scripts/build_book.py --book beyond-vibe-coding-ar
python -m unittest discover -s tests -v
```

</div>
