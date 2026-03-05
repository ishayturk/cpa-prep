# exam_page.py | Version: v1.0

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

    user_name = st.session_state.get("user_name", "")
    st.markdown(f"### שלום {user_name}, ברוכים הבאים לסימולציית בחינות לשכת רואי החשבון")
    st.markdown("לכניסה לבחינה אנא בחר נושא:")

    subject_options = ["בחר נושא..."] + EXAM_SUBJECTS
    selected = st.selectbox("נושא הבחינה", subject_options, label_visibility="collapsed")

    if selected != "בחר נושא...":
        if st.button("המשך להוראות הבחינה"):
            st.session_state.exam_subject = selected
            st.session_state.page = "exam_instructions"
            st.rerun()

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
