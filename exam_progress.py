# exam_progress.py | Version: v5.0

import streamlit as st
import time
import json
import os
import streamlit.components.v1 as components
from utils import render_top_bar, EXAM_FILES, EXAMS_DIR

EXAM_QUESTIONS = 40
EXAM_SECONDS = 120 * 60  # 120 דקות


def load_exam(subject):
    """טוען בחינה לפי נושא מקובץ JSON"""
    files = EXAM_FILES.get(subject, [])
    if not files:
        return None
    path = os.path.join(EXAMS_DIR, files[0])
    if not os.path.exists(path):
        st.warning(f"קובץ לא נמצא: {path}")
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"שגיאה בטעינת בחינה: {e}")
        return None


def render_exam_progress(logo_tag):
    subject = st.session_state.get("exam_subject", "")
    user_name = st.session_state.get("user_name", "")

    # טעינת בחינה מ-JSON
    exam_data = load_exam(subject)
    if exam_data:
        questions = exam_data.get("questions", {})
        q_count = len(questions)
    else:
        questions = {}
        q_count = EXAM_QUESTIONS

    # אתחול state
    if "exam_start_time" not in st.session_state:
        st.session_state.exam_start_time = time.time()
        st.session_state.exam_answers = [None] * q_count
        st.session_state.exam_visited = [False] * q_count
        st.session_state.exam_visited[0] = True
        st.session_state.exam_current = 0
        st.session_state.exam_frozen = False
        st.session_state.exam_finished = False

    elapsed = time.time() - st.session_state.exam_start_time
    remaining = max(0, EXAM_SECONDS - int(elapsed))

    # הקפאה בלחיצה הבאה כשנגמר הזמן
    if remaining == 0 and not st.session_state.exam_frozen:
        st.session_state.exam_frozen = True

    frozen = st.session_state.exam_frozen
    finished = st.session_state.exam_finished
    current = st.session_state.exam_current

    # לוגו + שם משתמש
    render_top_bar(logo_tag)

    # CSS בסיסי לעמוד
    st.markdown("""
    <style>
    .exam-wrap { max-width:80vw; margin:0 auto; padding:0 16px; }
    @media (max-width:768px) { .exam-wrap { max-width:100%; } }
    div[data-testid="stHorizontalBlock"] button {
        min-width:44px !important; white-space:nowrap !important;
    }
    </style>
    <div class="exam-wrap">
    """, unsafe_allow_html=True)

    # כותרת + שעון קבועים — נבנים ב-window.parent דרך components.html
    header_and_timer = f"""
    <style>body{{margin:0;padding:0;overflow:hidden;}}</style>
    <script>
    (function() {{
        var subject = {repr(subject)};
        var remaining = {remaining};
        var isMobile = window.parent.innerWidth <= 768;

        // בנה כותרת קבועה ב-parent אם עוד לא קיימת
        if (!window.parent.document.getElementById('exam-header-bar')) {{
            var bar = window.parent.document.createElement('div');
            bar.id = 'exam-header-bar';

            if (isMobile) {{
                // נייד: כותרת + שעון בנפרד, רק שעון fixed
                var subjectDiv = window.parent.document.createElement('div');
                subjectDiv.style.cssText = 'text-align:center;font-size:1rem;font-weight:700;padding:6px 0;border-bottom:1px solid #eee;direction:rtl;';
                subjectDiv.innerText = 'בחינה: ' + subject;

                var clockDiv = window.parent.document.createElement('div');
                clockDiv.id = 'exam-header-bar';
                clockDiv.style.cssText = 'position:fixed;top:0;left:0;right:0;z-index:9999;background:#fff;border-bottom:2px solid #eee;text-align:center;padding:5px 0;';
                clockDiv.innerHTML = '<span id="exam-clock-display" style="font-size:1.3rem;font-weight:800;letter-spacing:3px;color:#222;">--:--</span>';

                window.parent.document.body.prepend(clockDiv);
                // הכנס כותרת לפני התוכן הראשי
                var mainBlock = window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
                if (mainBlock) mainBlock.style.paddingTop = '42px';
            }} else {{
                // מחשב: כותרת + שעון fixed יחד
                bar.style.cssText = 'position:fixed;top:0;left:0;right:0;z-index:9999;background:#fff;border-bottom:2px solid #eee;padding:8px 16px;direction:rtl;display:flex;align-items:center;justify-content:center;gap:24px;';
                bar.innerHTML = '<div style="font-size:1.3rem;font-weight:700;color:#222;">בחינה: ' + subject + '</div><span id="exam-clock-display" style="font-size:1.3rem;font-weight:800;letter-spacing:3px;color:#222;">--:--</span>';
                window.parent.document.body.prepend(bar);
                var mainBlock = window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
                if (mainBlock) mainBlock.style.paddingTop = '50px';
            }}
        }}

        // טיימר
        var deadline = Date.now() + remaining * 1000;
        function updateClock() {{
            var s = Math.round((deadline - Date.now()) / 1000);
            if (s < 0) s = 0;
            var m = Math.floor(s / 60); var sec = s % 60;
            var str = (m < 10 ? '0' : '') + m + ':' + (sec < 10 ? '0' : '') + sec;
            var color = (s <= 60) ? '#dc3545' : '#222';
            try {{
                var el = window.parent.document.getElementById('exam-clock-display');
                if (el) {{ el.innerHTML = str; el.style.color = color; }}
            }} catch(e) {{}}
            if (s > 0) setTimeout(updateClock, 1000);
        }}
        updateClock();
    }})();
    </script>
    """
    components.html(header_and_timer, height=0)

    # הודעת תום זמן
    if frozen and not finished:
        st.error("⏰ זמן הבחינה הסתיים — לחץ/י על **סיים בחינה** להגשה")

    col_q, col_map = st.columns([2, 1])

    with col_q:
        q_num = current + 1
        st.markdown(f"**שאלה {q_num}**")

        # טעינת שאלה מ-JSON
        q_data = questions.get(str(q_num), {}) if questions else {}
        if q_data:
            st.markdown(q_data.get("text", ""))
            opts_dict = q_data.get("options", {})
            options_list = [f"{k}. {v}" for k, v in opts_dict.items()]
        else:
            st.markdown(f"_[כאן תופיע השאלה עבור נושא: {subject}]_")
            options_list = ["א. תשובה ראשונה", "ב. תשובה שנייה", "ג. תשובה שלישית", "ד. תשובה רביעית"]

        answer = st.radio(
            "בחר תשובה:",
            options=options_list,
            key=f"exam_radio_{current}",
            index=st.session_state.exam_answers[current],
            label_visibility="collapsed",
            disabled=frozen,
        )
        if answer is not None and not frozen:
            idx = options_list.index(answer)
            st.session_state.exam_answers[current] = idx

        has_answer = st.session_state.exam_answers[current] is not None

        nav1, nav2, nav3, nav4 = st.columns(4)
        with nav1:
            if st.button("הבאה ▶", disabled=(current == q_count - 1 or not has_answer or frozen)):
                st.session_state.exam_current += 1
                st.session_state.exam_visited[st.session_state.exam_current] = True
                st.rerun()
        with nav2:
            if st.button("◀ הקודמת", disabled=(current == 0 or frozen)):
                st.session_state.exam_current -= 1
                st.rerun()
        with nav3:
            can_finish = frozen or st.session_state.exam_answers[q_count - 1] is not None
            if st.button("סיים/י", disabled=not can_finish):
                if frozen and not st.session_state.get("exam_timeout_ack"):
                    st.session_state.exam_timeout_ack = True
                    st.rerun()
                else:
                    st.session_state.exam_finished = True
                    st.session_state.page = "exam_feedback"
                    st.rerun()
        with nav4:
            if st.button("תפריט ראשי", key="exam_home"):
                for k in ["exam_start_time", "exam_answers", "exam_visited",
                          "exam_current", "exam_frozen", "exam_finished", "exam_subject"]:
                    st.session_state.pop(k, None)
                st.query_params.clear()
                st.session_state.page = "welcome"
                st.rerun()

    with col_map:
        st.markdown("**מפת שאלות**")
        visited = st.session_state.exam_visited
        for row in range(0, q_count, 5):
            cols = st.columns(5)
            for i, col in enumerate(cols):
                q_idx = row + i
                if q_idx < q_count:
                    with col:
                        is_active = visited[q_idx]
                        if st.button(str(q_idx + 1), key=f"map_{q_idx}", disabled=not is_active):
                            st.session_state.exam_current = q_idx
                            st.rerun()

    st.markdown("</div></div>", unsafe_allow_html=True)

# סוף קובץ
