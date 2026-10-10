<div dir="rtl" lang="ar">

# تصميم قواعد البيانات لغير المتخصصين

مشروع إعداد عربي لكتاب **Database Design for Mere Mortals: A Hands-On Guide to Relational Database Design** (Michael J. Hernandez، Addison-Wesley).

| البند | القيمة |
| --- | --- |
| الأصل | [`sources/database-design-for-mere-mortals-4th-en/Database_Design_For_Mere_Mortals.pdf`](../../sources/database-design-for-mere-mortals-4th-en/Database_Design_For_Mere_Mortals.pdf) |
| صفحات الأصل | 485 |
| بصمة الأصل | `59bb8437c147527987e6b524d8d611555a21f86118e88b26d1ccff95e74fa3e0` |
| الحالة | لم يبدأ إعداد الفصول |
| الدفعة الحالية | لا توجد بعد |

## ما الذي ينقص هذا المشروع؟

1. اقرأ فهرس الأصل وثبّت `chapters` في [manifest.json](manifest.json): رقم كل فصل،
   عنوانه بالعربية والإنجليزية، ونطاق صفحاته الفعلي في الملف.
2. أضف مصادر `documents` في `ar/` بمقدار الدفعة الأولى فقط، وسجلها في البيان.
3. أنشئ سجل تغطية لكل فصل تُعدّه في `coverage/` واربطه بـ `coverage_file`.
4. ابنِ وراجع وفق [docs/method/04-build-and-validation.md](../../docs/method/04-build-and-validation.md):

```sh
python scripts/build_book.py --book database-design-for-mere-mortals-ar --check --verify-source
python scripts/build_book.py --book database-design-for-mere-mortals-ar
python -m unittest discover -s tests -v
```

</div>
