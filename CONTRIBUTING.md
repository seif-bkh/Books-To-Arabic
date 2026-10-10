<div dir="rtl" lang="ar">

# دليل المساهمة

> **قبل أي عمل:** اقرأ [docs/method/README.md](docs/method/README.md) — المرجع القار
> للطريقة والصعوبات وحلولها — و[AGENTS.md](AGENTS.md) لبوابة الموافقة وحالة المراجعة.
> هذا الملف ملخص تنفيذي فقط؛ عند التعارض يُعتمد المرجعان أعلاه.

## القواعد التي لا تُكسر

1. **دفعة واحدة في كل مرة**، ولا يبدأ فصل جديد قبل تأكيد المستخدم على PDF الدفعة
   الحالية. نجاح الاختبارات أو طلب الـ commit ليس موافقة.
2. **`editions/` مولّدة**: لا تُحرَّر يدويًا. تُحدَّث بالبناء فقط.
3. **`sources/` لا تتغير**: الأصل المحفوظ ببصمته لا يُعدَّل؛ الأصل المختلف أصل جديد.
4. **لا تنفيذ أعمى** لأوامر الكتاب في الاختبارات؛ تُنفَّذ فقط المختبرات المراجعة
   ببصماتها.
5. **لا إضعاف لفحص** ليمرّ إخراج ناقص.
6. **كل صعوبة جديدة وحلّها يُسجّلان** في
   [docs/method/06-lessons-log.md](docs/method/06-lessons-log.md) في الجلسة نفسها.

## إضافة كتاب

```sh
python scripts/new_book.py add-source --file ~/book.pdf --slug some-book-1st-en \
    --title "Some Book" --author "A. Author" --publisher "Publisher" \
    --edition 1 --year 2020 --language en --rights-status unresolved
python scripts/new_book.py add-book --slug some-book-ar --source some-book-1st-en \
    --title-ar "بعض الكتاب" --author-ar "المؤلف"
```

ثم اقرأ فهرس الأصل وثبّت `chapters` في `books/<slug>/manifest.json`: رقم كل فصل، عنوانه
بالعربية والإنجليزية، ونطاق صفحاته **الفيزيائي** في الملف. لا تُخمَّن النطاقات ولا تُؤخذ
من العلامات المرجعية وحدها. راجع
[docs/method/05-source-and-rights.md](docs/method/05-source-and-rights.md) لحقوق الأصل
قبل رفعه.

## إضافة فصل

1. اقرأ نطاقه في الأصل، واحصر أقسامه وأشكاله وجداوله وأوامره وتحذيراته.
2. أنشئ `books/<slug>/coverage/chapter-NN.json` **قبل** الصياغة، واربطه بـ `coverage_file`.
3. اكتب المادة في `books/<slug>/ar/`، والتزم معجم الكتاب
   ([السياسة](docs/method/02-terminology-policy.md)).
4. وسم الإضافات: **إضافة تعليمية** و**توضيح حديث** بمرجع.
5. حدّث المعجم وملاحظات الإعداد وبيان المشروع وبطاقته وREADME المستودع.
6. افحص وابنِ واختبر، **ثم افتح PDF فعلًا** قبل التسليم.

```sh
python scripts/build_book.py --book <slug> --check --verify-source
python scripts/build_book.py --book <slug> --output-dir build/preview
python -m unittest discover -s tests -v
python scripts/build_book.py --book <slug>
```

## قبل التسليم

- قارن المحتوى بالأصل على مستوى الأقسام والأفكار، لا عدد الكلمات.
- حدّث حالة المراجعة والبصمة في `AGENTS.md`.
- اذكر ما أُعدّ وما بقي وما راجعته فعلًا؛ الفحوص الآلية ليست مراجعة لغوية بشرية.
- أبقِ المخرجات التجريبية في `build/` المستثنى من Git.

</div>
