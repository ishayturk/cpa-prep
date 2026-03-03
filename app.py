# File: app.py | Date & Time: 2026-03-03 21:40 (Asia/Jerusalem) | Version: CPA02

import streamlit as st
import smtplib
import time
import random
from email.mime.text import MIMEText

# -------------------------
# Page config (no sidebar, RTL-friendly, clean white UI)
# -------------------------
st.set_page_config(
    page_title="רואה חשבון בקליק",
    page_icon="favicon.ico",  # expects favicon.ico in repo root
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

  /* Center logo */
  .logo-wrap {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 14px;
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
        msg["Subject"] = "קוד כניסה - רואה חשבון בקליק"
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
    # OTP/session artifacts
    for k in [
        "otp_sent", "otp_code", "otp_time", "otp_attempts",
        "pending_name", "pending_email",
        # input keys (no memory when coming back to login)
        "login_name", "login_email", "otp_input"
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
    # Ensure: every arrival to login starts clean (no remembered inputs/codes)
    if not st.session_state.get("otp_sent", False):
        # clear any old values from previous run/session
        for k in ["login_name", "login_email", "otp_input"]:
            if k in st.session_state:
                del st.session_state[k]

    st.markdown('<div class="card">', unsafe_allow_html=True)

    # Centered logo (logo.png expected in repo root)
    try:
        st.markdown('<div class="logo-wrap">', unsafe_allow_html=True)
        st.image("logo.png", width=240)
        st.markdown('</div>', unsafe_allow_html=True)
    except Exception:
        # If logo is missing, do nothing (no extra UI/headers)
        pass

    st.markdown('<div class="title">כניסה למערכת</div>', unsafe_allow_html=True)

    otp_sent = st.session_state.get("otp_sent", False)

    if not otp_sent:
        # Use a form to avoid "Press Enter to apply" overlays and make TAB flow natural.
        with st.form("login_form", clear_on_submit=False, border=False):
            name = st.text_input(
                "שם מלא",
                placeholder="שם ושם משפחה",
                label_visibility="collapsed",
                key="login_name",
                autocomplete="off"
            ).strip()

            email = st.text_input(
                "מייל",
                placeholder="כתובת מייל",
                label_visibility="collapsed",
                key="login_email",
                autocomplete="off"
            ).strip()

            # Basic validation
            valid_name = len(name.split()) >= 2 and all(len(p) >= 2 for p in name.split())
            valid_email = ("@" in email) and ("." in email)

            if name and not valid_name:
                st.caption("יש להזין שם ושם משפחה.")
            if email and not valid_email:
                st.caption("יש להזין כתובת מייל תקינה.")

            # The explanation MUST be right above the button (not above fields)
            st.markdown('<div class="subtitle">לחץ על הכפתור כדי לקבל קוד חד־פעמי למייל. הקוד תקף ל-2 דקות.</div>', unsafe_allow_html=True)

            submitted = st.form_submit_button("שלח קוד")

        if submitted:
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

                    # Clear input fields (no memory)
                    for k in ["login_name", "login_email"]:
                        if k in st.session_state:
                            del st.session_state[k]

                    st.rerun()
                else:
                    st.error("שליחת המייל נכשלה. בדוק/י Secrets ונסה שוב.")

    else:
        pending_email = st.session_state.get("pending_email", "")
        st.info(f"קוד נשלח ל-{pending_email}. תקף ל-2 דקות.")

        # Also use form here (prevents enter overlays)
        with st.form("otp_form", clear_on_submit=False, border=False):
            code_in = st.text_input(
                "קוד",
                placeholder="הזן/י קוד בן 6 ספרות",
                label_visibility="collapsed",
                key="otp_input",
                autocomplete="off"
            ).strip()

            c1, c2 = st.columns(2)
            with c1:
                confirm = st.form_submit_button("אישור")
            with c2:
                restart = st.form_submit_button("התחל מחדש")

        if restart:
            reset_login_flow()
            st.rerun()

        if confirm:
            elapsed = time.time() - st.session_state.get("otp_time", 0)
            if elapsed > 120:
                st.error("הקוד פג תוקף. יש להתחיל מחדש ולקבל קוד חדש.")
                reset_login_flow()
                st.rerun()

            correct_code = st.session_state.get("otp_code", "")
            if code_in == correct_code and code_in:
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
        reset_login_flow()
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# סוף קובץ
