# exam_progress.py | Version: v3.2

import streamlit as st
import time
import streamlit.components.v1 as components
from utils import render_top_bar

EXAM_QUESTIONS = 5
EXAM_SECONDS = 1 * 60  # דקה לניסיון


def render_exam_progress(logo_tag):
    st.markdown("""
    <style>
    .exam-wrap { max-width: 900px; margin: 0 auto; padding: 0 16px; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="exam-wrap">', unsafe_allow_html=True)
    render_top_bar(logo_tag)

    subject = st.session_state.get("exam_subject", "")

    # אתחול state
    if "exam_start_time" not in st.session_state:
        st.session_state.exam_start_time = time.time()
        st.session_state.exam_answers = [None] * EXAM_QUESTIONS
        st.session_state.exam_visited = [False] * EXAM_QUESTIONS
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

    # טיימר JavaScript — ויזואלי בלבד, ללא שינוי URL
    timer_html = f"""
    <style>
        body {{ margin:0; padding:0; overflow:hidden; }}
        .exam-header {{ text-align:center; font-family:inherit; }}
        .exam-title {{ font-size:1.4rem; font-weight:700; color:#222; }}
        #exam-clock {{ font-size:2.6rem; font-weight:800; letter-spacing:3px; color:#222; margin-right:1.5rem; display:inline; }}
        @media (max-width:768px) {{
            .exam-title {{ font-size:0.95rem; }}
            #exam-clock {{ font-size:2rem; }}
        }}
    </style>
    <div class="exam-header">
        <span class="exam-title">בחינה: {subject}</span>
        <span id="exam-clock">--:--</span>
    </div>
    <script>
    var deadline = Date.now() + {remaining} * 1000;
    function updateClock() {{
        var s = Math.round((deadline - Date.now()) / 1000);
        if (s < 0) s = 0;
        var m = Math.floor(s / 60); var sec = s % 60;
        var el = document.getElementById('exam-clock');
        if (el) {{
            el.innerHTML = (m < 10 ? '0' : '') + m + ':' + (sec < 10 ? '0' : '') + sec;
            el.style.color = (s <= 60) ? '#dc3545' : '#222';
        }}
        if (s > 0) setTimeout(updateClock, 1000);
    }}
    updateClock();
    </script>
    """
    components.html(timer_html, height=70)

    # הודעת תום זמן
    if frozen and not finished:
        st.error("⏰ זמן הבחינה הסתיים — לחץ/י על **סיים בחינה** להגשה")

    col_q, col_map = st.columns([2, 1])

    with col_q:
        q_num = current + 1
        st.markdown(f"**שאלה {q_num}**")
        st.markdown(f"_[כאן תופיע השאלה עבור נושא: {subject}]_")

        answer = st.radio(
            "בחר תשובה:",
            options=["א. תשובה ראשונה", "ב. תשובה שנייה", "ג. תשובה שלישית", "ד. תשובה רביעית"],
            key=f"exam_radio_{current}",
            index=st.session_state.exam_answers[current],
            label_visibility="collapsed",
            disabled=frozen,
        )
        if answer is not None and not frozen:
            idx = ["א. תשובה ראשונה", "ב. תשובה שנייה", "ג. תשובה שלישית", "ד. תשובה רביעית"].index(answer)
            st.session_state.exam_answers[current] = idx

        has_answer = st.session_state.exam_answers[current] is not None

        nav1, nav2, nav3, nav4 = st.columns(4)
        with nav1:
            if st.button("◀ הקודמת", disabled=(current == 0 or frozen)):
                st.session_state.exam_current -= 1
                st.rerun()
        with nav2:
            if st.button("הבאה ▶", disabled=(current == EXAM_QUESTIONS - 1 or not has_answer or frozen)):
                st.session_state.exam_current += 1
                st.session_state.exam_visited[st.session_state.exam_current] = True
                st.rerun()
        with nav3:
            can_finish = frozen or st.session_state.exam_answers[EXAM_QUESTIONS - 1] is not None
            if st.button("סיים בחינה", disabled=not can_finish):
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
        for row in range(0, EXAM_QUESTIONS, 4):
            cols = st.columns(4)
            for i, col in enumerate(cols):
                q_idx = row + i
                if q_idx < EXAM_QUESTIONS:
                    with col:
                        is_active = visited[q_idx]
                        if st.button(str(q_idx + 1), key=f"map_{q_idx}", disabled=not is_active):
                            st.session_state.exam_current = q_idx
                            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# סוף קובץ
