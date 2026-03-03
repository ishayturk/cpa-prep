# File: app.py | Date & Time: 2026-03-03 21:55 (Asia/Jerusalem) | Version: CPA03

import streamlit as st
import smtplib
import time
import random
from email.mime.text import MIMEText

# -------------------------
# Page config
# -------------------------
st.set_page_config(
    page_title="רואה חשבון בקליק",
    page_icon="favicon.png",  # expects favicon.png in repo root
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
  /* Remove Streamlit chrome (top bar / menu / footer) */
  header[data-testid="stHeader"] { display: none !important; }
  #MainMenu { visibility: hidden !important; }
  footer { visibility: hidden !important; }
  .stDeployButton { display: none !important; }

  /* RTL + clean white */
  html, body, .stApp, .block-container {
    direction: rtl !important;
    text-align: right !important;
    background: #ffffff !important;
  }

  /* Tighten top spacing */
  .block-container {
    padding-top: 1.2rem !important;
    padding-bottom: 2rem !important;
  }

  /* Hide sidebar */
  section[data-testid="stSidebar"] { display: none !important; }

  /* Card */
  .card {
    max-width: 520px;
    margin: 0 auto;
    padding: 22px 20px;
    border: 1px solid #e9e9e9;
    border-radius: 14px;
    box-shadow: 0 10px 26px rgba(0,0,0,0.08);
    background: #fff;
  }

  /* Title/subtitle */
  .title {
    font-size: 1.25rem;
    font-weight: 850;
    margin: 6px 0 2px 0;
    line-height: 1.2;
  }
  .subtitle {
    color: #666;
    margin: 0 0 14px 0;
    font-size: 0.95rem;
    line-height: 1.4;
  }

  /* Inputs */
  div[data-testid="stTextInput"] input {
    border-radius: 12px !important;
    padding: 12px !important;
  }

  /* Buttons */
  .stButton > button, div[data-testid="stFormSubmitButton"] > button {
    width: 100% !important;
    border-radius: 12px !important;
    height: 3.15em !important;
    font-weight: 850 !important;
  }

  /* Logo centering */
  .logo-wrap {
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 4px 0 10px 0;
  }

  /* Mobile */
  @media (max-width: 768px) {
    .card { padding: 18px 14px; }
    .title { font-size: 1.15rem; }
  }
</style>
""",
    unsafe_allow_html=True,
)

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
    # OTP/session artifacts + input keys (no memory when returning to login)
    for k in [
        "otp_sent",
        "otp_code",
        "otp_time",
        "otp_attempts",
        "pending_name",
        "pending_email",
        "login_name",
        "login_email",
        "otp_input",
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
    # Every arrival to login starts clean (no remembered inputs/codes)
    if not st.session_state.get("otp_sent", False):
        for k in ["login_name", "login_email", "otp_input"]:
            if k in st.session_state:
                del st.session_state[k]

    st.markdown('<div class="card">', unsafe_allow_html=True)

    # Centered logo (logo.png expected in repo root)
    try:
        st.markdown('<div class="logo-wrap">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.image("logo.png", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    except Exception:
        pass

    st.markdown('<div class="title">כניסה למערכת</div>', unsafe_allow_html=True)

    otp_sent = st.session_state.get("otp_sent", False)

    if not otp_sent:
        # Use a form: no "Press Enter to apply", TAB flows naturally
        with st.form("login_form", clear_on_submit=False, border=False):
            name = st.text_input(
                "שם מלא",
                placeholder="שם ושם משפחה",
                label_visibility="collapsed",
                key="login_name",
                autocomplete="off",
            ).strip()

            email = st.text_input(
                "מייל",
                placeholder="כתובת מייל",
                label_visibility="collapsed",
                key="login_email",
                autocomplete="off",
            ).strip()

            valid_name = len(name.split()) >= 2 and all(len(p) >= 2 for p in name.split())
            valid_email = ("@" in email) and ("." in email)

            if name and not valid_name:
                st.caption("יש להזין שם ושם משפחה.")
            if email and not valid_email:
                st.caption("יש להזין כתובת מייל תקינה.")

            # Explanation placed directly above the button (as requested)
            st.markdown(
                '<div class="subtitle">לחץ על הכפתור כדי לקבל קוד חד־פעמי למייל. הקוד תקף ל-2 דקות.</div>',
                unsafe_allow_html=True,
            )

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

                    # Clear inputs (no memory)
                    for k in ["login_name", "login_email"]:
                        if k in st.session_state:
                            del st.session_state[k]

                    st.rerun()
                else:
                    st.error("שליחת המייל נכשלה. בדוק/י Secrets ונסה שוב.")

    else:
        pending_email = st.session_state.get("pending_email", "")
        st.info(f"קוד נשלח ל-{pending_email}. תקף ל-2 דקות.")

        with st.form("otp_form", clear_on_submit=False, border=False):
            code_in = st.text_input(
                "קוד",
                placeholder="הזן/י קוד בן 6 ספרות",
                label_visibility="collapsed",
                key="otp_input",
                autocomplete="off",
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
        unsafe_allow_html=True,
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
