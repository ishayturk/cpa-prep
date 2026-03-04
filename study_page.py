# study_page.py | Version: v2.6

import streamlit as st
import google.generativeai as genai
import json, re, threading
from utils import SYLLABUS, clean_lesson, render_top_bar

QUIZ_KEYS = ["quiz_questions", "quiz_idx", "quiz_answers", "quiz_checked",
             "quiz_show_summary", "show_quiz", "quiz_type", "quiz_total",
             "quiz_batch_loading"]


def _clear_quiz():
    for k in QUIZ_KEYS:
        st.session_state.pop(k, None)


def _generate_batch(topic, sub, lesson_txt, from_q, to_q, total, existing_qs, subs=None):
    """מייצר קבוצת שאלות (from_q עד to_q) ומוסיף ל-session_state"""
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-2.0-flash")
        existing_json = json.dumps(existing_qs, ensure_ascii=False) if existing_qs else "[]"

        if subs:
            context = f"נושא: {topic}\nתתי נושאים: {', '.join(subs)}\n\nחומר שיעור:\n{lesson_txt[:5000]}"
        else:
            context = f"נושא: {topic} — {sub}\n\nחומר שיעור:\n{lesson_txt[:5000]}"

        count = to_q - from_q + 1
        prompt = f"""{context}

צור {count} שאלות אמריקאיות (שאלות {from_q} עד {to_q} מתוך {total}).
שאלות שכבר נוצרו (אל תחזור עליהן): {existing_json}

כללים:
- 4 תשובות, רק אחת נכונה
- אם 3 תשובות נכונות — הוסף "הכל נכון" כרביעית והיא הנכונה
- הסבר קצר (1-2 משפטים) למה התשובה נכונה

החזר JSON בלבד — מערך של {count} אובייקטים:
[
  {{
    "q": "טקסט השאלה",
    "answers": ["תשובה1", "תשובה2", "תשובה3", "תשובה4"],
    "correct": 0,
    "explanation": "הסבר קצר ומקור"
  }}
]"""
        response = model.generate_content(prompt)
        raw = response.text.strip()
        raw = re.sub(r"^```json|^```|```$", "", raw, flags=re.MULTILINE).strip()
        batch = json.loads(raw)
        if isinstance(batch, list):
            current = st.session_state.get("quiz_questions", [])
            st.session_state.quiz_questions = current + batch
            answers = st.session_state.get("quiz_answers", [])
            checked = st.session_state.get("quiz_checked", [])
            while len(answers) < len(st.session_state.quiz_questions):
                answers.append(None)
                checked.append(False)
            st.session_state.quiz_answers = answers
            st.session_state.quiz_checked = checked
    except Exception:
        pass
    finally:
        st.session_state.quiz_batch_loading = False


def _start_batch_if_needed(idx, topic, sub, lesson_txt, total, subs=None):
    """מתחיל טעינת קבוצה הבאה אם צריך"""
    if st.session_state.get("quiz_batch_loading"):
        return
    questions = st.session_state.get("quiz_questions", [])
    loaded = len(questions)

    # בשאלה 3 — טען 4-6, בשאלה 6 — טען 7-10 (או עד total)
    if idx == 2 and loaded < 4:  # idx=2 = שאלה 3
        st.session_state.quiz_batch_loading = True
        end = min(6, total)
        t = threading.Thread(target=_generate_batch,
            args=(topic, sub, lesson_txt, 4, end, total, questions, subs), daemon=True)
        t.start()
    elif idx == 5 and loaded < 7:  # idx=5 = שאלה 6
        st.session_state.quiz_batch_loading = True
        end = total
        t = threading.Thread(target=_generate_batch,
            args=(topic, sub, lesson_txt, 7, end, total, questions, subs), daemon=True)
        t.start()


def _start_quiz(selected_topic, selected_sub, lesson_txt, total, subs=None):
    """מתחיל שאלון — מייצר שאלות 1-3 מיד"""
    _clear_quiz()
    st.session_state.show_quiz = True
    st.session_state.quiz_total = total
    st.session_state.quiz_batch_loading = True

    # שאלות 1-3 synchronously
    existing = []
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-2.0-flash")

        if subs:
            context = f"נושא: {selected_topic}\nתתי נושאים: {', '.join(subs)}\n\nחומר שיעור:\n{lesson_txt[:5000]}"
        else:
            context = f"נושא: {selected_topic} — {selected_sub}\n\nחומר שיעור:\n{lesson_txt[:5000]}"

        prompt = f"""{context}

צור 3 שאלות אמריקאיות (שאלות 1 עד 3 מתוך {total}).

כללים:
- 4 תשובות, רק אחת נכונה
- אם 3 תשובות נכונות — הוסף "הכל נכון" כרביעית והיא הנכונה
- הסבר קצר (1-2 משפטים) למה התשובה נכונה

החזר JSON בלבד — מערך של 3 אובייקטים:
[
  {{
    "q": "טקסט השאלה",
    "answers": ["תשובה1", "תשובה2", "תשובה3", "תשובה4"],
    "correct": 0,
    "explanation": "הסבר קצר ומקור"
  }}
]"""
        response = model.generate_content(prompt)
        raw = response.text.strip()
        raw = re.sub(r"^```json|^```|```$", "", raw, flags=re.MULTILINE).strip()
        existing = json.loads(raw)
    except Exception:
        existing = []

    if existing:
        st.session_state.quiz_questions = existing
        st.session_state.quiz_idx = 0
        st.session_state.quiz_answers = [None] * len(existing)
        st.session_state.quiz_checked = [False] * len(existing)

    st.session_state.quiz_batch_loading = False


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
            _clear_quiz()
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

            # תפריט תחתון
            quiz_open = st.session_state.get("show_quiz", False)
            st.divider()
            st.markdown("""
            <style>
            .quiz-btn button { background-color: #e0f2fe !important; }
            </style>
            """, unsafe_allow_html=True)

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown('<div class="quiz-btn">', unsafe_allow_html=True)
                if st.button("📝 שאלון שיעור", key="lesson_quiz_sub", disabled=quiz_open, use_container_width=True):
                    _start_quiz(selected_topic, selected_sub, st.session_state.get("lesson_txt",""), total=10)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="quiz-btn">', unsafe_allow_html=True)
                if st.button("📋 שאלון מורחב", key="lesson_quiz_topic", disabled=quiz_open, use_container_width=True):
                    _start_quiz(selected_topic, selected_sub, st.session_state.get("lesson_txt",""), total=15, subs=SYLLABUS.get(selected_topic,[]))
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with c3:
                st.markdown('<a href="#top" style="display:block;text-align:center;padding:10px 0;font-weight:800;text-decoration:none;color:#31333f;border:1px solid #ddd;border-radius:8px;">⬆️ למעלה</a>', unsafe_allow_html=True)
            with c4:
                if st.button("🏠 תפריט ראשי", key="lesson_home", use_container_width=True):
                    for k in ["selected_topic", "selected_sub", "lesson_txt", "is_loading"] + QUIZ_KEYS:
                        st.session_state.pop(k, None)
                    st.session_state.page = "welcome"
                    st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def _render_inline_quiz():
    sub = st.session_state.get("selected_sub", "")
    topic = st.session_state.get("selected_topic", "")
    lesson_txt = st.session_state.get("lesson_txt", "")
    questions = st.session_state.get("quiz_questions", [])
    total_expected = st.session_state.get("quiz_total", 10)
    subs = SYLLABUS.get(topic, []) if total_expected == 15 else None

    st.divider()
    title = f"שאלון נושא: {topic}" if total_expected == 15 else f"שאלון: {sub}"
    st.markdown(f"### 📝 {title}")

    if not questions:
        st.info("מכין שאלות...")
        return

    if st.session_state.get("quiz_show_summary"):
        _render_summary(questions, sub, topic, total_expected)
        return

    idx = st.session_state.get("quiz_idx", 0)

    # הפעל טעינת קבוצה הבאה אם צריך
    _start_batch_if_needed(idx, topic, sub, lesson_txt, total_expected, subs)

    if idx >= len(questions):
        st.info("מכין את השאלה הבאה...")
        return

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
            st.markdown('<div style="background:#d4edda;padding:10px;border-radius:8px;font-weight:bold;">✅ נכון</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="background:#f8d7da;padding:10px;border-radius:8px;">❌ טעות: {q["answers"][selected]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="background:#f8d7da;padding:10px;border-radius:8px;margin-top:4px;">תשובה נכונה: {q["answers"][correct_idx]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="background:#cce5ff;padding:10px;border-radius:8px;margin-top:8px;">📖 {q["explanation"]}</div>', unsafe_allow_html=True)

    st.markdown('<div style="background:#f0f4f8;padding:10px;border-radius:10px;margin-top:16px;">', unsafe_allow_html=True)
    is_last = idx == total_expected - 1
    has_answer = st.session_state.quiz_answers[idx] is not None
    next_ready = (idx + 1) < len(questions)

    qc1, qc2, qc3 = st.columns(3)
    with qc1:
        if st.button("בדוק תשובה", disabled=(not has_answer or checked), key=f"check_{idx}", use_container_width=True):
            st.session_state.quiz_checked[idx] = True
            st.rerun()
    with qc2:
        if is_last:
            st.button("לשאלה הבאה", disabled=True, key=f"next_{idx}", use_container_width=True)
        else:
            if st.button("לשאלה הבאה", disabled=(not checked or not next_ready), key=f"next_{idx}", use_container_width=True):
                st.session_state.quiz_idx += 1
                st.rerun()
    with qc3:
        if st.button("סיכום", disabled=not (is_last and checked), key=f"summary_{idx}", use_container_width=True):
            st.session_state.quiz_show_summary = True
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


def _render_summary(questions, sub, topic, total_expected):
    answers = st.session_state.get("quiz_answers", [])
    total = len(questions)
    correct = sum(1 for i, q in enumerate(questions) if i < len(answers) and answers[i] == q["correct"])
    title = f"סיכום שאלון נושא: {topic}" if total_expected == 15 else f"סיכום שאלון: {sub}"
    st.divider()
    st.markdown(f"### {title}")
    st.markdown(f"**ענית נכון על {correct} מתוך {total} שאלות**")
    if st.button("📝 שאלון חדש", key="new_quiz"):
        lesson_txt = st.session_state.get("lesson_txt", "")
        all_subs = SYLLABUS.get(topic, []) if total_expected == 15 else None
        _start_quiz(topic, sub, lesson_txt, total=total_expected, subs=all_subs)
        st.rerun()

# סוף קובץ
