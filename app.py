# File: app.py | Date & Time: 2026-03-02 09:19 (Asia/Jerusalem) | Version: CPA01

import streamlit as st
import smtplib
import time
import random
from email.mime.text import MIMEText

# -------------------------
# Page config (no sidebar, RTL-friendly, clean white UI)
# -------------------------
st.set_page_config(
    page_title="CPA Prep",
    page_icon="✅",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
  /* RTL + clean white background */
  html, body, .stApp, [class*="st-"], .block-container {
    direction: rtl !important;
    text-align: right !important;
    background: #ffffff !important;
  }

  /* Hide Streamlit sidebar + its toggle */
  section[data-testid="stSidebar"] { display: none !important; }
  button[kind="header"] { display: none !important; }

  /* Centered card look */
  .card {
    max-width: 520px;
    margin: 0 auto;
    padding: 22px 20px;
    border: 1px solid #e9e9e9;
    border-radius: 14px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
    background: #fff;
  }

  .title {
    font-size: 1.6rem;
    font-weight: 800;
    margin-bottom: 6px;
  }

  .subtitle {
    color: #666;
    margin-bottom: 14px;
    font-size: 0.95rem;
  }

  /* Buttons look a bit more "product" */
  .stButton > button {
    width: 100% !important;
    border-radius: 10px !important;
    height: 3em !important;
    font-weight: 800 !important;
  }

  /* Inputs */
  div[data-testid="stTextInput"] input {
    border-radius: 10px !important;
    padding: 10px !important;
  }

  /* Mobile tweaks */
  @media (max-width: 768px) {
    .card { padding: 18px 14px; }
    .title { font-size: 1.25rem; }
  }
</style>
""", unsafe_allow_html=True)


# -------------------------
# Helpers
# -------------------------
def send_otp_email(to_email: str, code: str) -> bool:
    """
    Sends OTP code via Gmail SMTP using Streamlit secrets:
    st.secrets["GMAIL_USER"], st.secrets["GMAIL_PASS"]
    """
    try:
        gmail_user = st.secrets["GMAIL_USER"]
        gmail_pass = st.secrets["GMAIL_PASS"]

        msg = MIMEText(
            f"קוד הכניסה שלך למערכת ההכנה לבחינת לשכת רואי החשבון: {code}\n\n"
            f"הקוד תקף ל-2 דקות."
        )
        msg["Subject"] = "קוד כניסה - CPA Prep"
        msg["From"] = gmail_user
        msg["To"] = to_email

        with smtplib.SMTP("smtp.gmail.com", 587) as s:
            s.starttls()
            s.login(gmail_user, gmail_pass)
            s.send_message(msg)

        return True
    except Exception:
        return False


def reset_login_flow():
    for k in [
        "otp_sent", "otp_code", "otp_time", "otp_attempts",
        "pending_name", "pending_email"
    ]:
        if k in st.session_state:
            del st.session_state[k]


# -------------------------
# State init
# -------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "login"


# -------------------------
# Router
# -------------------------
if not st.session_state.logged_in:
    st.session_state.page = "login"

# -------------------------
# LOGIN PAGE
# -------------------------
if st.session_state.page == "login":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="title">כניסה למערכת</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">קוד חד־פעמי יישלח למייל. הקוד תקף ל-2 דקות.</div>', unsafe_allow_html=True)

    otp_sent = st.session_state.get("otp_sent", False)

    if not otp_sent:
        name = st.text_input("שם מלא", placeholder="שם ושם משפחה", label_visibility="collapsed").strip()
        email = st.text_input("מייל", placeholder="כתובת מייל", label_visibility="collapsed").strip()

        # Basic validation
        valid_name = len(name.split()) >= 2 and all(len(p) >= 2 for p in name.split())
        valid_email = ("@" in email) and ("." in email)

        if name and not valid_name:
            st.caption("יש להזין שם ושם משפחה.")
        if email and not valid_email:
            st.caption("יש להזין כתובת מייל תקינה.")

        if st.button("שלח קוד"):
            if not (valid_name and valid_email):
                st.warning("יש למלא שם מלא וכתובת מייל תקינה.")
            else:
                code = str(random.randint(100000, 999999))
                ok = send_otp_email(email, code)
                if ok:
                    st.session_state.otp_sent = True
                    st.session_state.otp_code = code
                    st.session_state.otp_time = time.time()
                    st.session_state.otp_attempts = 0
                    st.session_state.pending_name = name
                    st.session_state.pending_email = email
                    st.success("הקוד נשלח. בדוק/י את המייל.")
                    st.rerun()
                else:
                    st.error("שליחת המייל נכשלה. בדוק/י Secrets ונסה שוב.")

    else:
        pending_email = st.session_state.get("pending_email", "")
        st.info(f"קוד נשלח ל-{pending_email}. תקף ל-2 דקות.")

        code_in = st.text_input("קוד", placeholder="הזן/י קוד בן 6 ספרות", label_visibility="collapsed").strip()

        col1, col2 = st.columns(2)
        with col1:
            if st.button("אישור"):
                elapsed = time.time() - st.session_state.get("otp_time", 0)
                if elapsed > 120:
                    st.error("הקוד פג תוקף. יש להתחיל מחדש ולקבל קוד חדש.")
                    reset_login_flow()
                    st.rerun()

                correct_code = st.session_state.get("otp_code", "")
                if code_in == correct_code:
                    st.session_state.logged_in = True
                    st.session_state.user_name = st.session_state.get("pending_name", "משתמש")
                    reset_login_flow()
                    st.session_state.page = "welcome"
                    st.rerun()
                else:
                    st.session_state.otp_attempts = st.session_state.get("otp_attempts", 0) + 1
                    remaining = 3 - st.session_state.otp_attempts
                    if remaining <= 0:
                        st.error("3 ניסיונות כושלים — יש להתחיל מחדש ולקבל קוד חדש.")
                        reset_login_flow()
                        st.rerun()
                    else:
                        st.error(f"קוד שגוי. נותרו {remaining} ניסיונות.")

        with col2:
            if st.button("התחל מחדש"):
                reset_login_flow()
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# -------------------------
# WELCOME PAGE
# -------------------------
elif st.session_state.page == "welcome":
    user_name = st.session_state.get("user_name", "משתמש")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="title">ברוכים הבאים, {user_name} 👋</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">ברוכים הבאים למערכת הכנה לבחינת לשכת רואי החשבון</div>',
        unsafe_allow_html=True
    )

    st.write("")
    st.write("מכאן נמשיך לתפריט הראשי (לימוד / סימולציות / התקדמות).")

    if st.button("יציאה"):
        st.session_state.logged_in = False
        st.session_state.page = "login"
        for k in ["user_name"]:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
