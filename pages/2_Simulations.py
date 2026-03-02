import streamlit as st
from core.exam_loader import load_exam
import time

st.title("סימולציות בחינה")

# טעינת רשימת קבצי בחינות
import os
exam_files = os.listdir("data/exams")

selected_exam = st.selectbox("בחר בחינה:", exam_files)

if st.button("התחל בחינה"):
    exam = load_exam(selected_exam)
    st.session_state.exam = exam
    st.session_state.current_q = 0
    st.session_state.answers = {}
    st.session_state.start_time = time.time()
    st.session_state.in_exam = True
    st.rerun()

if st.session_state.get("in_exam"):

    exam = st.session_state.exam
    q_index = st.session_state.current_q
    question = exam["questions"][q_index]

    # טיימר
    elapsed = time.time() - st.session_state.start_time
    remaining = exam["duration_minutes"] * 60 - elapsed
    st.markdown(f"⏱ זמן שנותר: {int(remaining//60)}:{int(remaining%60):02d}")

    st.subheader(f"שאלה {q_index + 1}")
    st.write(question["text"])

    options = question["options"]
    choice = st.radio(
        "",
        list(options.keys()),
        format_func=lambda x: f"{x}. {options[x]}"
    )

    if st.button("שמור תשובה"):
        st.session_state.answers[q_index] = choice

    col1, col2 = st.columns(2)

    with col1:
        if st.button("הקודם") and q_index > 0:
            st.session_state.current_q -= 1
            st.rerun()

    with col2:
        if st.button("הבא") and q_index < len(exam["questions"]) - 1:
            st.session_state.current_q += 1
            st.rerun()

    if st.button("סיים בחינה"):
        correct = 0
        for i, q in enumerate(exam["questions"]):
            if st.session_state.answers.get(i) == q["correct_label"]:
                correct += 1

        st.success(f"ציון: {correct} מתוך {len(exam['questions'])}")
        st.session_state.in_exam = False
