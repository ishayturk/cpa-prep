# File: app.py | Version: CPA71

import streamlit as st
from PIL import Image
from utils import inject_css, get_logo_tag, send_otp_email, clear_login_inputs_only, reset_login_flow, render_top_bar
from study_page import render_study
from exam_page import render_exam_topic, render_exam_instructions, render_exam_feedback
from exam_progress import render_exam_progress
from quiz_page import render_quiz, render_quiz_summary
import random
import time

# -------------------------
# Page config
# -------------------------
try:
    icon = Image.open("favicon.png")
except Exception:
    icon = "✅"

st.set_page_config(
    page_title="רואה חשבון בקליק",
    page_icon=icon,
    layout="centered",
    initial_sidebar_state="collapsed",
)

inject_css()
logo_tag = get_logo_tag()

# -------------------------
# State init
# -------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "login"
if not st.session_state.logged_in:
    st.session_state.page = "login"

# -------------------------
# LOGIN PAGE
# -------------------------
if st.session_state.page == "login":
    if not st.session_state.get("otp_sent", False):
        for k in ["otp_code", "otp_time", "otp_attempts", "pending_name", "pending_email"]:
            if k in st.session_state:
                del st.session_state[k]

    st.markdown('<div class="wrap">', unsafe_allow_html=True)
    st.markdown(f'<div class="logo-wrap">{logo_tag}</div>', unsafe_allow_html=True)
    st.markdown("### כניסה למערכת")

    otp_sent = st.session_state.get("otp_sent", False)

    if not otp_sent:
        st.text_input("שם", placeholder="שם מלא — שם ושם משפחה",
                      key="login_name", label_visibility="collapsed", autocomplete="off")
        st.text_input("מייל", placeholder="כתובת מייל",
                      key="login_email", label_visibility="collapsed", autocomplete="off")
        st.markdown('<div class="hint">להשלמת הכניסה לחץ על הכפתור כדי לקבל קוד חד־פעמי למייל. הקוד תקף ל-2 דקות.</div>', unsafe_allow_html=True)

        if st.button("שלח קוד"):
            name = st.session_state.get("login_name", "").strip()
            email = st.session_state.get("login_email", "").strip().replace(" ", "")
            parts = name.split()
            valid_name = len(parts) >= 2 and all(len(p) >= 2 for p in parts)
            valid_email = ("@" in email) and ("." in email)
            if not (valid_name and valid_email):
                st.warning("יש למלא שם מלא וכתובת מייל תקינה.")
            else:
                code = str(random.randint(100000, 999999))
                if send_otp_email(email, code):
                    st.session_state.otp_sent = True
                    st.session_state.otp_code = code
                    st.session_state.otp_time = time.time()
                    st.session_state.otp_attempts = 0
                    st.session_state.pending_name = name
                    st.session_state.pending_email = email
                    st.rerun()
                else:
                    st.error("שגיאה בשליחת המייל. בדוק/י Secrets ונסה שוב.")
    else:
        pending_email = st.session_state.get("pending_email", "")
        st.info(f"קוד נשלח ל-{pending_email}. תקף ל-2 דקות.")
        code_in = st.text_input("קוד", placeholder="הזן/י קוד בן 6 ספרות",
                                key="otp_input", label_visibility="collapsed",
                                autocomplete="off").strip()
        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("אישור"):
                elapsed = time.time() - st.session_state.get("otp_time", 0)
                if elapsed > 120:
                    st.error("הקוד פג תוקף. יש להתחיל מחדש ולקבל קוד חדש.")
                    for k in ["otp_sent", "otp_code", "otp_time", "otp_attempts", "pending_name", "pending_email"]:
                        if k in st.session_state:
                            del st.session_state[k]
                    clear_login_inputs_only()
                    st.rerun()
                correct_code = st.session_state.get("otp_code", "")
                if code_in == correct_code and code_in:
                    st.session_state.logged_in = True
                    st.session_state.user_name = st.session_state.get("pending_name", "משתמש")
                    for k in ["otp_sent", "otp_code", "otp_time", "otp_attempts", "pending_name", "pending_email", "otp_input"]:
                        if k in st.session_state:
                            del st.session_state[k]
                    st.session_state.page = "welcome"
                    st.rerun()
                else:
                    st.session_state.otp_attempts = st.session_state.get("otp_attempts", 0) + 1
                    remaining = 3 - st.session_state.otp_attempts
                    if remaining <= 0:
                        st.error("3 ניסיונות כושלים — יש להתחיל מחדש ולקבל קוד חדש.")
                        for k in ["otp_sent", "otp_code", "otp_time", "otp_attempts", "pending_name", "pending_email"]:
                            if k in st.session_state:
                                del st.session_state[k]
                        clear_login_inputs_only()
                        st.rerun()
                    else:
                        st.error(f"קוד שגוי. נותרו {remaining} ניסיונות.")
        with c2:
            if st.button("התחל מחדש"):
                for k in ["otp_sent", "otp_code", "otp_time", "otp_attempts", "pending_name", "pending_email"]:
                    if k in st.session_state:
                        del st.session_state[k]
                clear_login_inputs_only()
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == "welcome":
    st.markdown('<div class="wrap">', unsafe_allow_html=True)
    from utils import render_top_bar
    render_top_bar(logo_tag)
    st.markdown("""
        <div style="text-align:right; font-size:1rem; color:#222;
                    margin-bottom:32px; line-height:1.7;">
            ברוכים הבאים למערכת הכנה למבחני מועצת רואי החשבון,
            הסמכה לראיית חשבון
        </div>
    """, unsafe_allow_html=True)
    _space, col1, col2, _end = st.columns([0.15, 1, 1, 2])
    with col1:
        st.markdown('<div class="menu-btn">', unsafe_allow_html=True)
        if st.button("📚 שיעורי לימוד"):
            st.session_state.page = "study"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="menu-btn">', unsafe_allow_html=True)
        if st.button("📝 גש/י לבחינה"):
            st.session_state.page = "exam_topic"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page in ("study", "lesson"):
    render_study(logo_tag)

elif st.session_state.page == "quiz_sub":
    render_quiz(logo_tag)

elif st.session_state.page == "quiz_summary":
    render_quiz_summary(logo_tag)

elif st.session_state.page == "exam_topic":
    render_exam_topic(logo_tag)

elif st.session_state.page == "exam_instructions":
    render_exam_instructions(logo_tag)
    st.stop()

elif st.session_state.page == "exam_progress":
    render_exam_progress(logo_tag)

elif st.session_state.page == "exam_feedback":
    render_exam_feedback(logo_tag)

# סוף קובץ
