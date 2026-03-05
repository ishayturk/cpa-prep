# exam_progress.py | Version: v3.4

import streamlit as st
import time
import streamlit.components.v1 as components
from utils import render_top_bar

EXAM_QUESTIONS = 5
EXAM_SECONDS = 1 * 60  # דקה לניסיון


def render_exam_progress(logo_tag):
    subject = st.session_state.get("exam_subject", "")
    user_name = st.session_state.get("user_name", "")

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

    # CSS לכותרת קבועה ורוחב דף
    st.markdown(f"""
    <style>
    /* כותרת קבועה */
    .exam-sticky {{
        position:fixed; top:0; left:0; right:0; z-index:9999;
        background:#fff; border-bottom:2px solid #eee;
        padding:6px 24px; direction:rtl;
    }}
    .exam-topbar {{
        display:flex; align-items:center; justify-content:space-between;
    }}
    .exam-username {{ font-size:0.9rem; font-weight:600; color:#444; }}
    .exam-subject {{ font-size:1.3rem; font-weight:700; color:#222; text-align:center; flex:1; }}
    .exam-clock-row {{ text-align:center; margin-top:2px; }}
    .exam-clock-val {{ font-size:1.5rem; font-weight:800; letter-spacing:3px; color:#222; }}

    /* בנייד — הכל מוצג אבל רק שעון קבוע */
    @media (max-width:768px) {{
        .exam-topbar {{ position:static; }}
        .exam-sticky {{ padding:4px 12px; }}
        .exam-clock-row {{ position:fixed; top:0; left:0; right:0; background:#fff;
            border-bottom:2px solid #eee; text-align:center; z-index:9999; padding:4px; }}
        .exam-topbar {{ position:relative; margin-top:40px; }}
    }}

    /* רוחב דף בחינה */
    .exam-wrap {{ max-width:75vw; margin:0 auto; padding:110px 16px 0 16px; }}
    @media (max-width:768px) {{ .exam-wrap {{ max-width:100%; padding-top:60px; }} }}
    </style>
    <div class="exam-sticky">
        <div class="exam-topbar">
            <div class="exam-username">👤 {user_name}</div>
            <div class="exam-subject">בחינה: {subject}</div>
            <div>{logo_tag}</div>
        </div>
        <div class="exam-clock-row">
            <span id="exam-clock-display" class="exam-clock-val">--:--</span>
        </div>
    </div>
    <div class="exam-wrap">
    """, unsafe_allow_html=True)

    # טיימר JavaScript — מעדכן רק את הספרות
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
        // עדכון בדף הראשי
        try {{
            var el = window.parent.document.getElementById('exam-clock-display');
            if (el) {{ el.innerHTML = str; el.style.color = color; }}
        }} catch(e) {{}}
        if (s > 0) setTimeout(updateClock, 1000);
    }}
    updateClock();
    </script>
    """
    components.html(timer_js, height=0)

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
        for row in range(0, EXAM_QUESTIONS, 5):
            cols = st.columns(5)
            for i, col in enumerate(cols):
                q_idx = row + i
                if q_idx < EXAM_QUESTIONS:
                    with col:
                        is_active = visited[q_idx]
                        if st.button(str(q_idx + 1), key=f"map_{q_idx}", disabled=not is_active):
                            st.session_state.exam_current = q_idx
                            st.rerun()

    st.markdown("</div></div>", unsafe_allow_html=True)

# סוף קובץ
