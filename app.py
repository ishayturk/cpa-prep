# File: app.py | Date & Time: 2026-03-03 23:33 (Asia/Jerusalem) | Version: CPA15

import streamlit as st
import smtplib
import time
import random
import base64
from email.mime.text import MIMEText
from PIL import Image

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

# -------------------------
# Logo loader (base64)
# -------------------------
def get_logo_base64():
    try:
        with open("logo.png", "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return None

logo_b64 = get_logo_base64()
logo_tag = (
    f'<img src="data:image/png;base64,{logo_b64}" alt="logo">'
    if logo_b64
    else '<span style="font-size:2rem;">✅</span>'
)

# -------------------------
# CSS
# -------------------------
st.markdown(
    """
<style>
  * { direction: rtl; text-align: right; }

  html, body, .stApp, .block-container { background: #ffffff !important; }

  header, #MainMenu, footer { visibility: hidden; height: 0; }
  section[data-testid="stSidebar"] { display: none !important; }
  button[kind="header"] { display: none !important; }

  .block-container {
    padding-top: 0rem !important;
    margin-top: -10px !important;
  }

  .wrap {
    max-width: 520px;
    margin: 0 auto;
    padding-top: 0px;
  }

  .logo-wrap {
    display: flex;
    justify-content: flex-start;
    align-items: center;
    direction: ltr;
    margin-top: 0px;
    margin-bottom: 4px;
  }
  .logo-wrap img {
    width: 160px;
    max-width: 45vw;
    height: auto;
    display: block;
  }

  /* Inputs: 50% width, anchored right */
  div[data-testid="stTextInput"] {
    width: 50% !important;
    margin-right: 0 !important;
    margin-left: auto !important;
  }
  div[data-testid="stTextInput"] input {
    background: #ffffff !important;
    border: 1px solid #000 !important;
    border-radius: 10px !important;
    padding: 12px 12px !important;
    font-size: 1rem !important;
    box-shadow: none !important;
  }
  div[data-testid="stTextInput"] label { display: none !important; }

  .stButton>button {
    width: 100% !important;
    border-radius: 10px !important;
    height: 3em !important;
    font-weight: 800 !important;
  }

  .hint {
    color: #666;
    font-size: 0.95rem;
    margin: 10px 0 10px 0;
  }
</style>
""",
    unsafe_allow_html=True,
)

# -------------------------
# Helpers
# -------------------------
def send_otp_email(to_email: str, code: str) -> bool:
    try:
        gmail_user = st.secrets["GMAIL_USER"]
        gmail_pass = st.secrets["GMAIL_PASS"]

        msg = MIMEText(
            f"קוד הכניסה שלך לרואה חשבון בקליק: {code}\n\n"
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


def clear_login_inputs_only():
    for k in ["login_name", "login_email", "otp_input"]:
        if k in st.session_state:
            del st.session_state[k]


def reset_login_flow(full: bool = True):
    keys = ["otp_sent", "otp_code", "otp_time", "otp_attempts", "pending_name", "pending_email"]
    if full:
        keys += ["logged_in", "user_name"]
    for k in keys:
        if k in st.session_state:
            del st.session_state[k]


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
        clear_login_inputs_only()

    st.markdown('<div class="wrap">', unsafe_allow_html=True)
    st.markdown(f'<div class="logo-wrap">{logo_tag}</div>', unsafe_allow_html=True)
    st.markdown("### כניסה למערכת")

    otp_sent = st.session_state.get("otp_sent", False)

    if not otp_sent:
        name = st.text_input(
            "שם",
            placeholder="שם מלא — שם ושם משפחה",
            key="login_name",
            label_visibility="collapsed",
            autocomplete="off",
        ).strip()

        email = st.text_input(
            "מייל",
            placeholder="כתובת מייל",
            key="login_email",
            label_visibility="collapsed",
            autocomplete="off",
        ).strip()

        parts = name.split()
        valid_name = len(parts) >= 2 and all(len(p) >= 2 for p in parts)
        valid_email = ("@" in email) and ("." in email)

        if name and not valid_name:
            st.caption("יש להזין שם ושם משפחה")
        if email and not valid_email:
            st.caption("יש להזין כתובת מייל תקינה")

        st.markdown('<div class="hint">להשלמת הכניסה לחץ על הכפתור כדי לקבל קוד חד־פעמי למייל. הקוד תקף ל-2 דקות.</div>', unsafe_allow_html=True)

        if st.button("שלח קוד"):
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

        code_in = st.text_input(
            "קוד",
            placeholder="הזן/י קוד בן 6 ספרות",
            key="otp_input",
            label_visibility="collapsed",
            autocomplete="off",
        ).strip()

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


# -------------------------
# WELCOME PAGE
# -------------------------
elif st.session_state.page == "welcome":
    st.markdown('<div class="wrap">', unsafe_allow_html=True)
    st.markdown(f'<div class="logo-wrap">{logo_tag}</div>', unsafe_allow_html=True)

    user_name = st.session_state.get("user_name", "משתמש")
    st.markdown(f"### ברוכים הבאים, {user_name} 👋")
    st.write("ברוכים הבאים למערכת הכנה לבחינת לשכת רואי החשבון")

    if st.button("יציאה"):
        st.session_state.logged_in = False
        st.session_state.page = "login"
        reset_login_flow(full=False)
        clear_login_inputs_only()
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# סוף קובץ
