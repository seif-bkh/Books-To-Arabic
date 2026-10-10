<div dir="rtl" lang="ar">

# مقدمة في استرجاع المعلومات

مشروع إعداد عربي لكتاب **Introduction to Information Retrieval** (Christopher D. Manning, Prabhakar Raghavan, and Hinrich Schütze، Cambridge University Press).

| البند | القيمة |
| --- | --- |
| الأصل | [`sources/introduction-to-information-retrieval-1st-en/intro_to_ir.pdf`](../../sources/introduction-to-information-retrieval-1st-en/intro_to_ir.pdf) |
| صفحات الأصل | 581 |
| بصمة الأصل | `ab67ad67d89309a3d03de219173cfdea471e856a5083c83e49b11be8c01581ea` |
| الحالة | لم يبدأ إعداد الفصول |
| الدفعة الحالية | لا توجد بعد |

## ما الذي ينقص هذا المشروع؟

1. اقرأ فهرس الأصل وثبّت `chapters` في [manifest.json](manifest.json): رقم كل فصل،
   عنوانه بالعربية والإنجليزية، ونطاق صفحاته الفعلي في الملف.
2. أضف مصادر `documents` في `ar/` بمقدار الدفعة الأولى فقط، وسجلها في البيان.
3. أنشئ سجل تغطية لكل فصل تُعدّه في `coverage/` واربطه بـ `coverage_file`.
4. ابنِ وراجع وفق [docs/method/04-build-and-validation.md](../../docs/method/04-build-and-validation.md):

```sh
python scripts/build_book.py --book introduction-to-information-retrieval-ar --check --verify-source
python scripts/build_book.py --book introduction-to-information-retrieval-ar
python -m unittest discover -s tests -v
```

</div>
