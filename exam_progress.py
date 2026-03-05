# exam_progress.py | Version: v3.0

import streamlit as st
import time
from utils import render_top_bar

EXAM_QUESTIONS = 5
EXAM_SECONDS = 1 * 60  # דקה לניסיון


@st.fragment(run_every=1)
def _render_timer(subject, remaining_at_start, start_time):
    elapsed = time.time() - start_time
    remaining = max(0, EXAM_SECONDS - int(elapsed))
    mins = remaining // 60
    secs = remaining % 60
    color = "#dc3545" if remaining <= 60 else "#222"
    st.markdown(f"""
    <div style="text-align:center; margin-bottom:12px;">
        <span style="font-size:1.4rem; font-weight:700; color:#222;">בחינה: {subject}</span>
        &nbsp;&nbsp;&nbsp;&nbsp;
        <span style="font-size:2.6rem; font-weight:800; letter-spacing:3px; color:{color};">{mins:02d}:{secs:02d}</span>
    </div>
    """, unsafe_allow_html=True)

    if remaining == 0 and not st.session_state.get("exam_frozen"):
        st.session_state.exam_frozen = True
        st.rerun()


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

    frozen = st.session_state.exam_frozen
    finished = st.session_state.exam_finished
    current = st.session_state.exam_current

    # טיימר — מתרענן כל שנייה בלי לרענן את שאר הדף
    _render_timer(subject, remaining, st.session_state.exam_start_time)

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
                st.session_state.exam_finished = True
                st.session_state.page = "exam_feedback"
                st.rerun()
        with nav4:
            if st.button("תפריט ראשי", key="exam_home"):
                for k in ["exam_start_time", "exam_answers", "exam_visited",
                          "exam_current", "exam_frozen", "exam_finished", "exam_subject"]:
                    st.session_state.pop(k, None)
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
