# study_page.py | Version: v1.5

import streamlit as st
import google.generativeai as genai
import json, re, threading
from utils import SYLLABUS, clean_lesson, render_top_bar

QUIZ_KEYS = ["quiz_questions", "quiz_idx", "quiz_answers", "quiz_checked", "quiz_show_summary", "show_quiz", "quiz_questions_pending", "quiz_thread"]


def _clear_quiz():
    for k in QUIZ_KEYS:
        st.session_state.pop(k, None)


def _generate_one_question(topic, sub, lesson_txt, q_number, total, existing_qs):
    """מייצר שאלה אחת ומחזיר dict"""
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-2.0-flash")
        existing_json = json.dumps(existing_qs, ensure_ascii=False) if existing_qs else "[]"
        prompt = f"""בהתבסס על חומר השיעור הבא בנושא "{sub}" (חלק מ"{topic}"):

---
{lesson_txt[:5000]}
---

צור שאלה אמריקאית מספר {q_number} מתוך {total} לבחינת הבנה עמוקה.
שאלות שכבר נוצרו (אל תחזור עליהן): {existing_json}

כללים:
- 4 תשובות, רק אחת נכונה
- אם 3 תשובות נכונות — הוסף "הכל נכון" כרביעית והיא הנכונה
- הסבר קצר (1-2 משפטים) למה התשובה נכונה ומאיפה ניתן ללמוד

החזר JSON בלבד של אובייקט יחיד:
{{
  "q": "טקסט השאלה",
  "answers": ["תשובה1", "תשובה2", "תשובה3", "תשובה4"],
  "correct": 0,
  "explanation": "הסבר קצר ומקור"
}}"""
        response = model.generate_content(prompt)
        raw = response.text.strip()
        raw = re.sub(r"^```json|^```|```$", "", raw, flags=re.MULTILINE).strip()
        return json.loads(raw)
    except Exception:
        return None


def _background_generate(topic, sub, lesson_txt, total=10):
    """מייצר שאלות אחת אחת ומוסיף ל-session_state"""
    for i in range(total):
        # בדוק אם עוד צריך
        if not st.session_state.get("show_quiz"):
            break
        existing = st.session_state.get("quiz_questions", [])
        if len(existing) >= total:
            break
        q = _generate_one_question(topic, sub, lesson_txt, i + 1, total, existing)
        if q:
            current = st.session_state.get("quiz_questions", [])
            if len(current) < total:
                st.session_state.quiz_questions = current + [q]
                # אתחל תשובות אם צריך
                answers = st.session_state.get("quiz_answers", [])
                checked = st.session_state.get("quiz_checked", [])
                while len(answers) < len(st.session_state.quiz_questions):
                    answers.append(None)
                    checked.append(False)
                st.session_state.quiz_answers = answers
                st.session_state.quiz_checked = checked


def render_study(logo_tag):
    st.markdown('<div class="wrap">', unsafe_allow_html=True)
    render_top_bar(logo_tag)
    st.markdown("### 📚 שיעורי לימוד")

    current_topic = st.session_state.get("selected_topic", "בחר...")
    topic_options = ["בחר..."] + list(SYLLABUS.keys())
    idx = topic_options.index(current_topic) if current_topic in topic_options else 0
    selected_topic = st.selectbox("נושא:", topic_options, index=idx, label_visibility="collapsed")

    if selected_topic != current_topic:
        for k in ["selected_sub", "lesson_txt", "is_loading"] + QUIZ_KEYS:
            st.session_state.pop(k, None)
        st.session_state.selected_topic = selected_topic
        st.rerun()

    if selected_topic and selected_topic != "בחר...":
        st.markdown(f"**{selected_topic}** — בחר תת נושא:")
        subs = SYLLABUS[selected_topic]
        cols = st.columns(len(subs))
        is_loading = st.session_state.get("is_loading", False)
        for i, sub in enumerate(subs):
            with cols[i]:
                is_active_sub = sub == st.session_state.get("selected_sub")
                is_disabled = bool(is_loading or is_active_sub)
                if st.button(sub, key=f"sub_{sub}", disabled=is_disabled):
                    for k in ["lesson_txt", "is_loading"] + QUIZ_KEYS:
                        st.session_state.pop(k, None)
                    st.session_state.selected_sub = sub
                    st.session_state.is_loading = True
                    st.session_state.page = "lesson"
                    st.rerun()

    selected_sub = st.session_state.get("selected_sub")
    selected_topic = st.session_state.get("selected_topic", "")

    if selected_sub:
        if not st.session_state.get("lesson_txt"):
            try:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel("gemini-2.0-flash")
                prompt = f"""אתה פרופסור בכיר למשפט עסקי וחשבונאות, המתמחה בהכנה למבחני מועצת רואי החשבון בישראל.

כתוב שיעור מקיף ומעמיק ברמה אקדמית גבוהה בנושא: **{selected_sub}** (חלק מנושא: {selected_topic}).

דרישות מחייבות:
- החומר חייב לכסות את כל מה שנדרש לבחינת הלשכה ברמה המלאה
- כלול הגדרות משפטיות/חשבונאיות מדויקות
- כלול עקרונות, כללים וחריגים
- כל נוסחה, חישוב, תרגיל מספרי, או ביטוי מתמטי — חייב להופיע בתוך תיבת קוד (``` ```) בלבד
- ציין מקורות: חוק, תקן, סעיף, או עקרון IFRS הרלוונטי לכל נושא
- רמה: סטודנט שעומד לגשת למבחן הלשכה ברמה המקצועית הגבוהה ביותר
- כתוב בעברית, מובנה עם כותרות וסעיפים ברורים
- אסור להוסיף כותרת או משפט פתיחה — התחל ישירות מהתוכן
- השתמש רק ב-## ומטה, לעולם לא #"""

                placeholder = st.empty()
                full_text = ""
                response = model.generate_content(prompt, stream=True)
                for chunk in response:
                    if chunk.text:
                        full_text += chunk.text
                        placeholder.markdown(full_text + "▌")
                full_text = clean_lesson(full_text)
                placeholder.markdown(full_text)
                st.session_state.lesson_txt = full_text
                st.session_state.is_loading = False
                st.rerun()

            except Exception as e:
                st.session_state.is_loading = False
                st.error(f"שגיאה בטעינת השיעור: {e}")

        else:
            st.markdown(clean_lesson(st.session_state.get("lesson_txt", "")))

            if st.session_state.get("show_quiz"):
                _render_inline_quiz()

            st.divider()
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                quiz_open = st.session_state.get("show_quiz", False)
                if st.button("📝 שאלון תת נושא", key="lesson_quiz_sub", disabled=quiz_open):
                    _clear_quiz()
                    st.session_state.show_quiz = True
                    # יצירת שאלה ראשונה מיידית
                    lesson_txt = st.session_state.get("lesson_txt", "")
                    q1 = _generate_one_question(selected_topic, selected_sub, lesson_txt, 1, 10, [])
                    if q1:
                        st.session_state.quiz_questions = [q1]
                        st.session_state.quiz_idx = 0
                        st.session_state.quiz_answers = [None]
                        st.session_state.quiz_checked = [False]
                        # יצירת שאר השאלות ברקע
                        t = threading.Thread(
                            target=_background_generate,
                            args=(selected_topic, selected_sub, lesson_txt),
                            daemon=True
                        )
                        t.start()
                    st.rerun()
            with c2:
                st.button("📋 שאלון נושא כללי", disabled=True, key="lesson_quiz_topic")
            with c3:
                st.markdown('<a href="#top" style="display:block;text-align:center;padding:10px 0;font-weight:800;text-decoration:none;color:#31333f;">⬆️ לראש העמוד</a>', unsafe_allow_html=True)
            with c4:
                if st.button("🏠 תפריט ראשי", key="lesson_home"):
                    for k in ["selected_topic", "selected_sub", "lesson_txt", "is_loading"] + QUIZ_KEYS:
                        st.session_state.pop(k, None)
                    st.session_state.page = "welcome"
                    st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def _render_inline_quiz():
    sub = st.session_state.get("selected_sub", "")
    questions = st.session_state.get("quiz_questions", [])

    st.divider()
    st.markdown(f"### 📝 שאלון: {sub}")

    if not questions:
        st.info("מכין שאלה ראשונה...")
        return

    if st.session_state.get("quiz_show_summary"):
        _render_summary(questions, sub)
        return

    idx = st.session_state.get("quiz_idx", 0)
    # אם הגענו לשאלה שעוד לא מוכנה
    if idx >= len(questions):
        st.info("מכין את השאלה הבאה...")
        return

    total_expected = 10
    q = questions[idx]
    checked = st.session_state.quiz_checked[idx]
    selected = st.session_state.quiz_answers[idx]

    st.markdown(f"**שאלה {idx + 1} מתוך {total_expected}**")
    st.markdown(f"**{q['q']}**")
    st.markdown("")

    if not checked:
        choice = st.radio(
            "בחר תשובה:",
            options=list(range(len(q["answers"]))),
            format_func=lambda i: q["answers"][i],
            key=f"quiz_radio_{idx}",
            index=None,
            label_visibility="collapsed"
        )
        if choice is not None:
            st.session_state.quiz_answers[idx] = choice
    else:
        correct_idx = q["correct"]
        if selected == correct_idx:
            st.markdown('<div style="background:#d4edda; padding:10px; border-radius:8px; font-weight:bold;">✅ נכון</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="background:#f8d7da; padding:10px; border-radius:8px;">❌ טעות: {q["answers"][selected]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="background:#f8d7da; padding:10px; border-radius:8px; margin-top:4px;">תשובה נכונה: {q["answers"][correct_idx]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="background:#cce5ff; padding:10px; border-radius:8px; margin-top:8px;">📖 {q["explanation"]}</div>', unsafe_allow_html=True)

    st.markdown('<div style="background:#f0f4f8; padding:10px; border-radius:10px; margin-top:16px;">', unsafe_allow_html=True)
    is_last = idx == total_expected - 1
    has_answer = st.session_state.quiz_answers[idx] is not None
    next_ready = (idx + 1) < len(questions)

    qc1, qc2, qc3 = st.columns(3)
    with qc1:
        if st.button("בדוק תשובה", disabled=(not has_answer or checked), key=f"check_{idx}"):
            st.session_state.quiz_checked[idx] = True
            st.rerun()
    with qc2:
        if is_last:
            st.button("לשאלה הבאה", disabled=True, key=f"next_{idx}")
        else:
            next_disabled = not checked or not next_ready
            if st.button("לשאלה הבאה", disabled=next_disabled, key=f"next_{idx}"):
                st.session_state.quiz_idx += 1
                st.rerun()
    with qc3:
        if st.button("סיכום", disabled=not (is_last and checked), key=f"summary_{idx}"):
            st.session_state.quiz_show_summary = True
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


def _render_summary(questions, sub):
    answers = st.session_state.get("quiz_answers", [])
    total = len(questions)
    correct = sum(1 for i, q in enumerate(questions) if i < len(answers) and answers[i] == q["correct"])
    st.divider()
    st.markdown(f"### סיכום שאלון: {sub}")
    st.markdown(f"**ענית נכון על {correct} מתוך {total} שאלות**")
    if st.button("📝 שאלון חדש", key="new_quiz"):
        topic = st.session_state.get("selected_topic", "")
        lesson_txt = st.session_state.get("lesson_txt", "")
        _clear_quiz()
        st.session_state.show_quiz = True
        q1 = _generate_one_question(topic, sub, lesson_txt, 1, 10, [])
        if q1:
            st.session_state.quiz_questions = [q1]
            st.session_state.quiz_idx = 0
            st.session_state.quiz_answers = [None]
            st.session_state.quiz_checked = [False]
            t = threading.Thread(
                target=_background_generate,
                args=(topic, sub, lesson_txt),
                daemon=True
            )
            t.start()
        st.rerun()

# סוף קובץ
