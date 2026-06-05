# 📱 تطبيق مدير الملفات المتقدم - APK

## 🎯 نظرة عامة

تطبيق Android احترافي وخفيف الوزن لإدارة ملفات جهازك بسهولة وسرعة.

## ✨ الميزات الرئيسية

### 🗂️ إدارة الملفات
- تصفح سهل للملفات والمجلدات
- عرض معلومات الملف (الحجم، التاريخ)
- دعم أنواع ملفات متعددة
- ترتيب تلقائي (المجلدات أولاً)

### 🎨 واجهة المستخدم
- تصميم Material Design 3
- دعم الوضع المظلم (Dark Mode)
- واجهة كاملة باللغة العربية
- دعم RTL

### ⚙️ الأداء
- حجم APK أقل من 5MB
- استهلاك ذاكرة منخفض
- معالجة سريعة للملفات الكبيرة
- دعم Android 7.0 إلى Android 14

## 📋 متطلبات النظام

**الحد الأدنى:**
- Android 7.0 (API 24)
- 100MB مساحة تخزين
- RAM: 512MB

**موصى به:**
- Android 10 فما فوق
- RAM: 2GB أو أكثر

## 📥 التثبيت

### من ملف APK

1. حمّل ملف `filemanager-release.apk`
2. مكّن "تثبيت من مصادر غير معروفة" في الإعدادات
3. افتح الملف واتبع التعليمات
4. اسمح بالأذونات المطلوبة

### من Android Studio

```bash
git clone https://github.com/Bot2030-bo/Booot.git
cd Booot
./gradlew assembleRelease
```

ستجد APK في: `build/outputs/apk/release/`

## 🔒 الأذونات المطلوبة

- `READ_EXTERNAL_STORAGE` - قراءة الملفات
- `WRITE_EXTERNAL_STORAGE` - حذف ونقل الملفات
- `MANAGE_EXTERNAL_STORAGE` - إدارة التخزين (Android 11+)

## 🛠️ البناء والتطوير

### المتطلبات
- Android Studio 2023.1+
- JDK 11+
- Gradle 8.0+

### الخطوات

1. استنسخ المشروع
2. افتحه في Android Studio
3. اضغط "Sync Now"
4. اختر "Run" للتشغيل أو "Build APK"

## 📁 هيكل المشروع

```
Booot/
├── src/
│   ├── main/
│   │   ├── kotlin/com/filemanager/pro/
│   │   │   ├── MainActivity.kt
│   │   │   └── FileAdapter.kt
│   │   ├── res/
│   │   │   ├── layout/
│   │   │   ├── values/
│   │   │   └── drawable/
│   │   └── AndroidManifest.xml
│   └── test/
├── build.gradle
├── settings.gradle
└── README.md
```

## 🎯 الميزات المستقبلية

- [ ] ضغط وفك ضغط ملفات
- [ ] بحث متقدم
- [ ] حذف آمن (استعادة)
- [ ] نسخ احتياطي
- [ ] مشغل وسائط مدمج
- [ ] محرر نصوص

## 🐛 حل المشاكل

### المشكلة: "الأذونات مطلوبة"
**الحل**: توجه إلى الإعدادات → التطبيقات → مدير الملفات → الأذونات

### المشكلة: "الملف غير موجود"
**الحل**: قد يكون الملف محذوفاً أو تحت حماية

### المشكلة: بطء التطبيق
**الحل**: مسح ذاكرة التطبيق من الإعدادات

## 📊 الإحصائيات

- حجم APK: ~4MB
- الحد الأدنى من SDK: 24
- الهدف من SDK: 34
- لغة البرمجة: 100% Kotlin

## 👨‍💻 المساهمة

نرحب بمساهماتك!

1. Fork المشروع
2. أنشئ فرع (`git checkout -b feature/amazing`)
3. Commit التغييرات (`git commit -m 'Add feature'`)
4. Push للفرع (`git push origin feature/amazing`)
5. فتح Pull Request

## 📄 الترخيص

هذا المشروع مرخص تحت [MIT License](LICENSE)

## 📞 التواصل

- GitHub: [@Bot2030-bo](https://github.com/Bot2030-bo)
- الإصدارات: [Releases](https://github.com/Bot2030-bo/Booot/releases)

## ⭐ شكراً!

إذا أعجبك التطبيق، يرجى إضافة نجمة ⭐

---

**آخر تحديث**: يونيو 2026
**الإصدار**: 1.0.0
**الحالة**: متاح للتحميل
