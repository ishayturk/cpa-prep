# exam_page.py | Version: v1.4

import streamlit as st
from utils import render_top_bar, EXAM_FILES, EXAM_OVERRIDES

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

EXAM_QUESTIONS_DEFAULT = 40
EXAM_MINUTES_DEFAULT = 120


def minutes_to_text(minutes):
    """ממיר דקות לטקסט קריא בעברית. לדוגמה: 120 → 'שעתיים', 215 → 'שלוש שעות ו-35 דקות'"""
    hours = minutes // 60
    mins = minutes % 60
    hour_words = {1: "שעה", 2: "שעתיים", 3: "שלוש שעות", 4: "ארבע שעות",
                  5: "חמש שעות", 6: "שש שעות"}
    hour_str = hour_words.get(hours, f"{hours} שעות")
    if mins == 0:
        return hour_str
    return f"{hour_str} ו-{mins} דקות"


def render_exam_topic(logo_tag):
    st.markdown('<div class="wrap">', unsafe_allow_html=True)
    render_top_bar(logo_tag)

    user_name = st.session_state.get("user_name", "")
    st.markdown(f"### שלום {user_name}, ברוכים הבאים לסימולציית בחינות לשכת רואי החשבון")
    st.markdown("לכניסה לבחינה אנא בחר נושא:")

    subject_options = ["בחר נושא..."] + EXAM_SUBJECTS
    selected = st.selectbox("נושא הבחינה", subject_options, label_visibility="collapsed")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("המשך להוראות הבחינה", disabled=(selected == "בחר נושא...")):
            st.session_state.exam_subject = selected
            st.session_state.exam_file = None  # יבחר אקראי בתחילת הבחינה
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

    # קריאת זמן — דיפולט 120 אם הנושא לא מופיע ב-EXAM_OVERRIDES
    exam_minutes = EXAM_OVERRIDES.get(subject, {}).get("duration_minutes", EXAM_MINUTES_DEFAULT)
    exam_questions = EXAM_QUESTIONS_DEFAULT  # תמיד 40

    st.markdown(f"### הוראות בחינה — {subject}")

    st.markdown(f"""
**מבנה הבחינה:**
- מספר שאלות: {exam_questions}
- זמן הבחינה: {exam_minutes} דקות, {minutes_to_text(exam_minutes)}
- כל שאלה כוללת 4 או 5 תשובות אפשריות, רק אחת נכונה

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


def render_exam_feedback(logo_tag):
    # exam_page.py | render_exam_feedback | Version: v2.0
    import math
    import json, os
    from utils import render_top_bar, EXAM_FILES, EXAMS_DIR

    st.markdown('<div class="wrap">', unsafe_allow_html=True)
    render_top_bar(logo_tag)

    subject = st.session_state.get("exam_subject", "")
    answers = st.session_state.get("exam_answers", [])
    total = len(answers)

    # טעינת בחינה מ-JSON — אותו קובץ שנבחר בתחילת הבחינה
    exam_data = None
    files = EXAM_FILES.get(subject, [])
    if files:
        chosen = st.session_state.get("exam_file")
        if not chosen or chosen not in files:
            chosen = files[0]
        path = os.path.join(EXAMS_DIR, chosen)
        try:
            with open(path, "r", encoding="utf-8") as f:
                exam_data = json.load(f)
        except Exception:
            pass

    questions = exam_data.get("questions", {}) if exam_data else {}

    # חישוב ציון
    correct_count = 0
    answered_count = 0
    for i, a in enumerate(answers):
        if a is None:
            continue
        answered_count += 1
        q_data = questions.get(str(i + 1), {})
        if not q_data:
            continue
        opts = list(q_data.get("options", {}).keys())
        correct_label = q_data.get("correct_label", "")
        if opts and a < len(opts) and opts[a] == correct_label:
            correct_count += 1

    score = round(100 * correct_count / total) if total > 0 else 0

    # כותרת
    st.markdown(f"### {subject}")
    st.markdown(f"**ציון: {score}** &nbsp;&nbsp; {correct_count} נכון מתוך {answered_count} שאלות שנענו")
    st.markdown("---")

    # משוב לכל שאלה
    for i in range(total):
        a = answers[i]
        if a is None:
            st.markdown(f'<div style="color:#888; margin-bottom:4px;">שאלה {i+1}: לא נענתה</div>', unsafe_allow_html=True)
            continue

        q_data = questions.get(str(i + 1), {})
        if not q_data:
            continue

        opts_dict = q_data.get("options", {})
        opts_keys = list(opts_dict.keys())
        correct_label = q_data.get("correct_label", "")
        explanation = q_data.get("explanation", "")

        user_label = opts_keys[a] if a < len(opts_keys) else "?"
        user_text = opts_dict.get(user_label, "")
        correct_text = opts_dict.get(correct_label, "")

        if user_label == correct_label:
            st.markdown(f'<div style="background:#d4edda; padding:8px 12px; border-radius:6px; margin-bottom:6px;">'
                        f'<b>שאלה {i+1}: ✓ נכון</b></div>', unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div style="background:#f8d7da; padding:8px 12px; border-radius:6px 6px 0 0; margin-bottom:1px;">'
                f'<b>שאלה {i+1}: ✗ טעית</b> — ענית: {user_label}. {user_text}</div>',
                unsafe_allow_html=True)
            st.markdown(
                f'<div style="background:#fff3cd; padding:8px 12px; border-radius:0 0 6px 6px; margin-bottom:1px;">'
                f'תשובה נכונה: {correct_label}. {correct_text}</div>',
                unsafe_allow_html=True)

        if explanation:
            st.markdown(
                f'<div style="background:#f0f4ff; padding:6px 12px; border-radius:0 0 6px 6px; '
                f'font-size:0.88rem; color:#444; margin-bottom:8px;">{explanation}</div>',
                unsafe_allow_html=True)

    st.markdown("---")
    if st.button("חזרה לתפריט הראשי"):
        subject = st.session_state.get("exam_subject", "")
        used_file = st.session_state.get("exam_file")
        if subject and used_file:
            if "exam_file_last_used" not in st.session_state:
                st.session_state.exam_file_last_used = {}
            st.session_state.exam_file_last_used[subject] = used_file
        for k in ["exam_start_time", "exam_answers", "exam_visited",
                  "exam_current", "exam_frozen", "exam_finished", "exam_subject", "exam_file"]:
            st.session_state.pop(k, None)
        st.query_params.clear()
        st.session_state.page = "welcome"
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
