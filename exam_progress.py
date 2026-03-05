# exam_page.py | Version: v1.1

import streamlit as st
from utils import render_top_bar

EXAM_SUBJECTS = [
    "תמחור וחשבונאות ניהולית מתקדמת",
    "טכנולוגיות מידע",
    "משפט עסקי",
    "דיני מיסים א'",
    "דיני מיסים ב'",
    "חשבונאות פיננסית א'",
    "דיני תאגידים ומסחר",
    "סטטיסטיקה",
    "מימון",
    "ביקורת חשבונות ובעיות ביקורת מורכבות",
    "חשבונאות פיננסית מתקדמת",
    "כלכלה",
    "מבוא לחשבונאות",
    "יסודות ביקורת החשבונות",
]

EXAM_QUESTIONS = 40
EXAM_MINUTES = 120


def render_exam_topic(logo_tag):
    st.markdown('<div class="wrap">', unsafe_allow_html=True)
    render_top_bar(logo_tag)

    st.markdown("### ברוכים הבאים לסימולציית בחינות לשכת רואי החשבון")
    st.markdown("לכניסה לבחינה אנא בחר נושא:")

    subject_options = ["בחר נושא..."] + EXAM_SUBJECTS
    selected = st.selectbox("נושא הבחינה", subject_options, label_visibility="collapsed")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("המשך להוראות הבחינה", disabled=(selected == "בחר נושא...")):
            st.session_state.exam_subject = selected
            st.session_state.page = "exam_instructions"
            st.rerun()
    with col2:
        if st.button("חזרה לתפריט הראשי", key="exam_topic_home"):
            st.session_state.page = "welcome"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def render_exam_instructions(logo_tag):
    st.markdown('<div class="wrap">', unsafe_allow_html=True)
    render_top_bar(logo_tag)

    subject = st.session_state.get("exam_subject", "")
    st.markdown(f"### הוראות בחינה — {subject}")

    st.markdown(f"""
**מבנה הבחינה:**
- מספר שאלות: {EXAM_QUESTIONS}
- זמן הבחינה: {EXAM_MINUTES} דקות
- כל שאלה כוללת 4 תשובות אפשריות, רק אחת נכונה

**ניווט בבחינה:**
- ניתן לעבור בין שאלות בחופשיות
- ניתן לסמן שאלה לחזרה מאוחרת
- ניתן לשנות תשובה בכל שלב לפני הגשה

**סיום הבחינה:**
- ניתן להגיש בכל עת לפני פקיעת הזמן
- בסיום הזמן הבחינה תוגש אוטומטית

**משוב וציון:**
- לאחר ההגשה יוצג ציון מיידי
- ניתן לעיין בכל שאלה עם הסבר לתשובה הנכונה
- ציון עובר: 60 ומעלה
""")

    st.markdown("---")
    confirmed = st.checkbox("קראתי והבנתי את הוראות הבחינה")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("התחל/י בחינה", disabled=not confirmed):
            st.session_state.page = "exam_progress"
            st.rerun()

    with col2:
        if st.button("חזרה לבחירת נושא"):
            st.session_state.page = "exam_topic"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# סוף קובץ


def render_exam_feedback(logo_tag):
    # exam_page.py | render_exam_feedback | Version: v1.1
    import math
    from utils import render_top_bar

    st.markdown('<div class="wrap">', unsafe_allow_html=True)
    render_top_bar(logo_tag)

    subject = st.session_state.get("exam_subject", "")
    answers = st.session_state.get("exam_answers", [])
    total = len(answers)

    # 5 שאלות בדיקה עם תשובות ידועות
    TEST_QUESTIONS = [
        {"q": "מה סכום זוויות משולש?", "answers": ["90°", "180°", "270°", "360°"], "correct": 1},
        {"q": "כמה ימים בשבוע?", "answers": ["5", "6", "7", "8"], "correct": 2},
        {"q": "מה הצבע של השמיים?", "answers": ["ירוק", "אדום", "כחול", "צהוב"], "correct": 2},
        {"q": "כמה חודשים בשנה?", "answers": ["10", "11", "12", "13"], "correct": 2},
        {"q": "מה בירת ישראל?", "answers": ["תל אביב", "חיפה", "ירושלים", "באר שבע"], "correct": 2},
    ]

    # חישוב ציון
    answered = [i for i, a in enumerate(answers) if a is not None and i < len(TEST_QUESTIONS)]
    correct = [i for i in answered if answers[i] == TEST_QUESTIONS[i]["correct"]]
    correct_count = len(correct)
    score = math.ceil(100 / total * correct_count) if total > 0 else 0

    # כותרת
    st.markdown(f"### {subject}")
    st.markdown(f"**ציון: {score}** &nbsp;&nbsp; פתרת {correct_count} שאלות מתוך {total} שאלות הבחינה")
    st.markdown("---")

    # משוב לכל שאלה
    first_unanswered = None
    for i in range(total):
        a = answers[i]
        if a is None:
            if first_unanswered is None:
                first_unanswered = i + 1
            continue

        if i >= len(TEST_QUESTIONS):
            continue
        q_data = TEST_QUESTIONS[i]
        if a == q_data["correct"]:
            st.markdown(f'<div style="color:#1a7a1a; font-weight:bold; margin-bottom:4px;">שאלה {i+1}: ✓ נכון</div>', unsafe_allow_html=True)
        else:
            user_text = q_data["answers"][a]
            correct_text = q_data["answers"][q_data["correct"]]
            st.markdown(f'<div style="background:#f8d7da; padding:8px; border-radius:6px 6px 0 0; margin-bottom:1px;">שאלה {i+1}: ✗ טעות, ענית: {user_text}</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="background:#f8d7da; padding:8px; border-radius:0 0 6px 6px; margin-bottom:4px;">תשובה נכונה: {correct_text}</div>', unsafe_allow_html=True)

    # שאלות שלא נענו
    if first_unanswered is not None:
        st.markdown("---")
        st.markdown(f"**שאלות {first_unanswered} עד {total} לא ניתנו תשובות**")

    st.markdown("---")
    if st.button("חזרה לתפריט הראשי"):
        for k in ["exam_start_time", "exam_answers", "exam_visited",
                  "exam_current", "exam_frozen", "exam_finished", "exam_subject"]:
            st.session_state.pop(k, None)
        st.query_params.clear()
        st.session_state.page = "welcome"
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
