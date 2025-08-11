# 🎯 AI Personal Code Reviewer

מערכת AI חכמה שמנתחת את הקוד שלך בזמן אמת ונותנת המלצות מותאמות אישית לסגנון הכתיבה שלך!

## 📋 תכונות עיקריות

- 🎨 **למידת סגנון אישי** - המערכת לומדת את סגנון הקוד הייחודי שלך
- 🐛 **זיהוי דפוסי באגים** - מזהה patterns חוזרים בבאגים שלך
- 💡 **המלצות מותאמות אישית** - נותן המלצות שיפור בהתאם לסגנון שלך
- 🔧 **Refactoring אוטומטי** - מציע שיפורי קוד בסגנון שלך

## 🚀 התקנה והפעלה

```bash
# התקנת תלויות
pip install -r requirements.txt

# הפעלת השרת
python main.py

# גישה לממשק
http://localhost:5000
```

## 📁 מבנה הפרויקט

```
AI_Personal_Code_Reviewer/
├── main.py                 # נקודת הכניסה הראשית
├── core/
│   ├── analyzer.py        # מנתח קוד ראשי
│   ├── style_learner.py   # לומד סגנון אישי
│   ├── pattern_detector.py # מזהה דפוסים
│   └── recommendation.py   # מנוע המלצות
├── models/
│   ├── code_model.py      # מודל נתוני קוד
│   └── user_profile.py    # פרופיל משתמש
├── api/
│   └── routes.py          # API endpoints
├── ui/
│   ├── templates/
│   └── static/
└── utils/
    ├── code_parser.py     # פרסור קוד
    └── metrics.py         # מדדי איכות
```

## 🎯 שימוש

1. העלה קובץ קוד או הדבק קוד ישירות
2. המערכת תנתח את הקוד בזמן אמת
3. קבל המלצות מותאמות אישית
4. בחר האם לקבל את השיפורים המוצעים

## 🔧 טכנולוגיות

- Python 3.8+
- Flask (Web Framework)
- AST (Abstract Syntax Tree) לניתוח קוד
- Machine Learning לזיהוי דפוסים
- SQLite לשמירת נתונים
