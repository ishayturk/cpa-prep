# quiz_page.py | Version: v1.0
# quiz_page.py — שאלון תת נושא

import streamlit as st
import google.generativeai as genai
import json
import re


def _is_mobile():
    """בנייד — טקסט קצר לכפתורים"""
    return False  # Streamlit לא חושף user-agent; ברירת מחדל מחשב


def generate_quiz(topic, sub, lesson_txt):
    """מייצר 10 שאלות מ-Gemini על בסיס חומר השיעור"""
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = f"""בהתבסס על חומר השיעור הבא בנושא "{sub}" (חלק מ"{topic}"):

---
{lesson_txt[:6000]}
---

צור 10 שאלות אמריקאיות (בחירה מרובה) לבחינת הבנה עמוקה של החומר.

כללים:
- 4 תשובות לכל שאלה, רק אחת נכונה
- אם יש 3 תשובות נכונות — הוסף "הכל נכון" כתשובה רביעית והיא הנכונה
- השאלות יבדקו הבנה, לא רק שינון
- ציין לכל שאלה מאיפה ניתן ללמוד (חוק/סעיף/תקן/עקרון)

החזר JSON בלבד, ללא טקסט נוסף, בפורמט הזה:
[
  {{
    "q": "טקסט השאלה",
    "answers": ["א. תשובה1", "ב. תשובה2", "ג. תשובה3", "ד. תשובה4"],
    "correct": 0,
    "source": "מקור הלמידה"
  }}
]
כאשר "correct" הוא האינדקס (0-3) של התשובה הנכונה."""

    response = model.generate_content(prompt)
    raw = response.text.strip()
    # נקה backticks אם יש
    raw = re.sub(r"^```json|^```|```$", "", raw, flags=re.MULTILINE).strip()
    return json.loads(raw)


def render_quiz(logo_tag):
    st.markdown('<div class="wrap">', unsafe_allow_html=True)
    render_top_bar_inline(logo_tag)
    st.markdown("### 📚 שיעורי לימוד")

    topic = st.session_state.get("selected_topic", "")
    sub = st.session_state.get("selected_sub", "")

    # טעינת שאלות
    if not st.session_state.get("quiz_questions"):
        with st.spinner("מכין שאלון..."):
            try:
                lesson_txt = st.session_state.get("lesson_txt", "")
                questions = generate_quiz(topic, sub, lesson_txt)
                st.session_state.quiz_questions = questions
                st.session_state.quiz_idx = 0
                st.session_state.quiz_answers = [None] * len(questions)
                st.session_state.quiz_checked = [False] * len(questions)
                st.rerun()
            except Exception as e:
                st.error(f"שגיאה ביצירת השאלון: {e}")
                return

    questions = st.session_state.quiz_questions
    idx = st.session_state.get("quiz_idx", 0)
    total = len(questions)
    q = questions[idx]

    # כותרת
    st.markdown(f"**שאלון: {sub}**")
    st.markdown(f"שאלה {idx + 1} מתוך {total}")
    st.divider()

    # שאלה
    checked = st.session_state.quiz_checked[idx]
    selected = st.session_state.quiz_answers[idx]

    st.markdown(f"**{q['q']}**")
    st.markdown("")

    # תשובות — radio
    if not checked:
        choice = st.radio(
            "בחר תשובה:",
            options=list(range(len(q["answers"]))),
            format_func=lambda i: q["answers"][i],
            key=f"quiz_radio_{idx}",
            index=selected if selected is not None else 0,
            label_visibility="collapsed"
        )
        st.session_state.quiz_answers[idx] = choice
    else:
        # נעול — מציג תשובות בלי radio
        correct_idx = q["correct"]
        for i, ans in enumerate(q["answers"]):
            if i == correct_idx:
                st.markdown(f'<div style="background:#d4edda; padding:8px; border-radius:6px; margin:4px 0;">✅ {ans}</div>', unsafe_allow_html=True)
            elif i == selected and selected != correct_idx:
                st.markdown(f'<div style="background:#f8d7da; padding:8px; border-radius:6px; margin:4px 0;">❌ {ans}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div style="padding:8px; margin:4px 0;">{ans}</div>', unsafe_allow_html=True)

        # משוב
        if selected == correct_idx:
            st.markdown('<div style="background:#d4edda; padding:8px; border-radius:6px; margin-top:12px; font-weight:bold;">✅ נכון!</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="background:#f8d7da; padding:8px; border-radius:6px; margin-top:12px; font-weight:bold;">❌ לא נכון &nbsp;|&nbsp; תשובה נכונה: {q["answers"][correct_idx]}</div>', unsafe_allow_html=True)

        st.markdown(f'<div style="background:#cce5ff; padding:8px; border-radius:6px; margin-top:6px;">📖 מקור: {q["source"]}</div>', unsafe_allow_html=True)

    st.divider()

    # תפריט שאלון
    is_last = idx == total - 1
    has_answer = st.session_state.quiz_answers[idx] is not None

    st.markdown('<div style="background:#f0f4f8; padding:10px; border-radius:10px; margin-bottom:8px;">', unsafe_allow_html=True)
    qc1, qc2, qc3 = st.columns(3)
    with qc1:
        if st.button("בדוק תשובה", disabled=(not has_answer or checked), key=f"check_{idx}"):
            st.session_state.quiz_checked[idx] = True
            st.rerun()
    with qc2:
        if is_last:
            st.button("לשאלה הבאה", disabled=True, key=f"next_{idx}")
        else:
            if st.button("לשאלה הבאה", disabled=not checked, key=f"next_{idx}"):
                st.session_state.quiz_idx += 1
                st.rerun()
    with qc3:
        show_summary = is_last and checked
        if st.button("סיכום", disabled=not show_summary, key=f"summary_{idx}"):
            st.session_state.page = "quiz_summary"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # תפריט ראשי
    st.divider()
    mc1, mc2, mc3, mc4 = st.columns(4)
    with mc1:
        st.button("📝 שאלון תת נושא", disabled=True, key="quiz_sub_btn")
    with mc2:
        if st.button("📋 שאלון נושא כללי", key="quiz_topic_btn"):
            st.session_state.page = "quiz_topic"
            st.rerun()
    with mc3:
        st.markdown('<a href="#top" style="display:block;text-align:center;padding:10px 0;font-weight:800;text-decoration:none;color:#31333f;">⬆️ לראש העמוד</a>', unsafe_allow_html=True)
    with mc4:
        if st.button("🏠 תפריט ראשי", key="quiz_home_btn"):
            st.session_state.page = "welcome"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def render_quiz_summary(logo_tag):
    st.markdown('<div class="wrap">', unsafe_allow_html=True)
    render_top_bar_inline(logo_tag)

    questions = st.session_state.get("quiz_questions", [])
    answers = st.session_state.get("quiz_answers", [])
    total = len(questions)
    correct = sum(1 for i, q in enumerate(questions) if answers[i] == q["correct"])

    sub = st.session_state.get("selected_sub", "")
    st.markdown(f"### סיכום שאלון: {sub}")
    st.markdown(f"**ענית נכון על {correct} מתוך {total} שאלות**")

    st.divider()
    mc1, mc2, mc3, mc4 = st.columns(4)
    with mc1:
        if st.button("📝 שאלון תת נושא", key="sum_sub"):
            st.session_state.quiz_questions = None
            st.session_state.page = "quiz_sub"
            st.rerun()
    with mc2:
        if st.button("📋 שאלון נושא כללי", key="sum_topic"):
            st.session_state.page = "quiz_topic"
            st.rerun()
    with mc3:
        if st.button("📖 חזרה לשיעור", key="sum_lesson"):
            st.session_state.page = "lesson"
            st.rerun()
    with mc4:
        if st.button("🏠 תפריט ראשי", key="sum_home"):
            st.session_state.page = "welcome"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def render_top_bar_inline(logo_tag):
    user_name = st.session_state.get("user_name", "משתמש")
    st.markdown(f"""
        <div id="top" style="display:flex; align-items:center; justify-content:space-between; margin-bottom:4px;">
            <div style="display:flex; align-items:center; gap:6px; margin-right:16px;">
                <span style="font-size:0.9rem; font-weight:600;">{user_name}</span>
                <span style="font-size:1.2rem;">👤</span>
            </div>
            <div class="logo-wrap" style="margin:0;">{logo_tag}</div>
        </div>
    """, unsafe_allow_html=True)
