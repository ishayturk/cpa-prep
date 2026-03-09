# exam_progress.py | Version: v5.13

import streamlit as st
import time
import json
import os
import streamlit.components.v1 as components
from utils import render_top_bar, EXAM_FILES, EXAMS_DIR, EXAM_OVERRIDES

EXAM_QUESTIONS_DEFAULT = 40
EXAM_MINUTES_DEFAULT = 120


def load_exam(subject):
    """טוען בחינה לפי נושא — מסובב בין הקבצים, לא חוזר על האחרון"""
    import random as _random
    files = EXAM_FILES.get(subject, [])
    if not files:
        return None
    if "exam_file" not in st.session_state or st.session_state.get("exam_file") not in files:
        last = st.session_state.get("exam_file_last_used", {}).get(subject)
        candidates = [f for f in files if f != last] or files
        st.session_state.exam_file = _random.choice(candidates)
    path = os.path.join(EXAMS_DIR, st.session_state.exam_file)
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

    # קריאת זמן — דיפולט 120 אם הנושא לא מופיע ב-EXAM_OVERRIDES
    exam_minutes = EXAM_OVERRIDES.get(subject, {}).get("duration_minutes", EXAM_MINUTES_DEFAULT)
    exam_seconds = exam_minutes * 60

    # טעינת בחינה מ-JSON
    exam_data = load_exam(subject)
    if exam_data:
        raw_questions = exam_data.get("questions", [])
        if isinstance(raw_questions, list):
            questions = {str(i + 1): q for i, q in enumerate(raw_questions)}
        else:
            questions = raw_questions
        q_count = len(questions)
    else:
        questions = {}
        q_count = EXAM_QUESTIONS_DEFAULT

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
    remaining = max(0, exam_seconds - int(elapsed))

    if remaining == 0 and not st.session_state.exam_frozen:
        st.session_state.exam_frozen = True

    frozen = st.session_state.exam_frozen
    finished = st.session_state.exam_finished
    current = st.session_state.exam_current

    user_name = st.session_state.get("user_name", "")
    st.markdown(f"""
    <style>
    .exam-top-frame {{
        position:sticky; top:0; z-index:999;
        background:#fff; border-bottom:1px solid #eee;
        padding:4px 16px 6px 16px; direction:rtl;
        width:100%;
    }}
    .exam-top-row1 {{
        display:flex; align-items:center; justify-content:space-between;
        margin-bottom:0;
    }}
    .exam-top-row2 {{
        display:flex; align-items:center; justify-content:center; gap:24px;
        padding-top:2px;
    }}
    .exam-subject-line {{ font-size:1.3rem; font-weight:700; color:#222; }}
    .exam-clock-val {{ font-size:1.495rem; font-weight:800; letter-spacing:3px; color:#222; }}
    .exam-clock-wrap {{ display:flex; flex-direction:row; align-items:baseline; gap:4px; }}
    .exam-clock-label {{ font-size:0.65rem; font-weight:400; color:#999; }}
    @media (max-width:768px) {{
        .exam-clock-val {{ font-size:1.1rem; }}
        .exam-clock-label {{ font-size:0.55rem; }}
    }}
    .exam-logo-wrap img {{ width:100px; height:auto; display:block; }}
    @media (max-width:768px) {{
        .exam-top-frame {{ position:static; border:none; padding:4px 8px; }}
        .exam-top-row2 {{ display:none; }}
        .exam-clock-mobile {{
            position:sticky; top:0; z-index:999;
            background:#fff; border-bottom:1px solid #eee;
            text-align:center; padding:5px 0;
        }}
    }}
    @media (min-width:769px) {{ .exam-clock-mobile {{ display:none; }} }}
    .exam-wrap {{ max-width:80%; margin:0 auto; padding:0 16px; }}
    @media (max-width:768px) {{ .exam-wrap {{ max-width:100%; }} }}
    div[data-testid="stHorizontalBlock"] button {{
        min-width:44px !important; white-space:nowrap !important;
    }}
    </style>
    <div class="exam-top-frame">
        <div class="exam-top-row1">
            <div style="display:flex;align-items:center;gap:6px;margin-right:8px;">
                <span style="font-size:0.9rem;font-weight:600;">{user_name}</span>
                <span style="font-size:1.2rem;">👤</span>
            </div>
            <div class="exam-logo-wrap">{logo_tag}</div>
        </div>
        <div class="exam-top-row2">
            <div class="exam-subject-line">בחינה: {subject}</div>
            <div class="exam-clock-wrap">
                <span id="exam-clock-display" class="exam-clock-val">--:--</span>
                <span class="exam-clock-label">דק'</span>
            </div>
        </div>
    </div>
    <div class="exam-clock-mobile">
        <div class="exam-clock-wrap">
            <span id="exam-clock-display-mobile" class="exam-clock-val">--:--</span>
            <span class="exam-clock-label">דק'</span>
        </div>
    </div>
    <div class="exam-wrap">
    """, unsafe_allow_html=True)

    # טיימר JavaScript
    timer_js = f"""
    <style>body{{margin:0;padding:0;overflow:hidden;}}</style>
    <script>
    var deadline = Date.now() + {remaining} * 1000;
    function updateClock() {{
        var s = Math.round((deadline - Date.now()) / 1000);
        if (s < 0) s = 0;
        var m = Math.floor(s / 60); var sec = s % 60;
        var str = (m < 10 ? '0' : '') + m + ':' + (sec < 10 ? '0' : '') + sec;
        var color = (s <= 60) ? '#dc3545' : '#222';
        try {{
            var el = window.parent.document.getElementById('exam-clock-display');
            if (el) {{ el.innerHTML = str; el.style.color = color; }}
            var el2 = window.parent.document.getElementById('exam-clock-display-mobile');
            if (el2) {{ el2.innerHTML = str; el2.style.color = color; }}
        }} catch(e) {{}}
        if (s > 0) setTimeout(updateClock, 1000);
    }}
    updateClock();
    </script>
    """
    components.html(timer_js, height=0)

    if frozen and not finished:
        st.error("⏰ זמן הבחינה הסתיים — לחץ/י על **סיים בחינה** להגשה")

    col_q, col_map = st.columns([2, 1])

    with col_q:
        q_num = current + 1
        st.markdown(f"**שאלה {q_num}**")

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

    st.markdown("""
    <style>
    .scroll-top-btn {
        position: fixed; bottom: 32px; left: 150px; z-index: 9999;
        width: 46px; height: 46px; border-radius: 50%;
        background: rgba(170,170,170,0.85); color: #fff;
        border: none; cursor: pointer; display: flex;
        align-items: center; justify-content: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.25); text-decoration: none;
    }
    .scroll-top-btn:hover { background: rgba(130,130,130,0.95); }
    </style>
    <a class="scroll-top-btn" href="#top">
      <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="18 15 12 9 6 15"></polyline>
      </svg>
    </a>
    """, unsafe_allow_html=True)

# סוף קובץ
