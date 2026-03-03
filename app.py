# File: app.py | Date & Time: 2026-03-03 23:18 (Asia/Jerusalem) | Version: CPA07

import streamlit as st
import smtplib
import time
import random
from email.mime.text import MIMEText
from PIL import Image

# -------------------------
# Page config (uses favicon.ico from repo root)
# -------------------------
icon = Image.open("favicon.ico")

st.set_page_config(
    page_title="רואה חשבון בקליק",
    page_icon=icon,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -------------------------
# Global CSS – clean, RTL, hide Streamlit chrome
# -------------------------
st.markdown(
    """
<style>
    * { direction: rtl; text-align: right; }

    /* Hide Streamlit top chrome */
    header { visibility: hidden; height: 0; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .stDeployButton { display:none !important; }

    html, body, .stApp, .block-container {
        background: #ffffff !important;
    }

    /* Inputs – no gray background */
    div[data-testid="stTextInput"] input {
        background: #ffffff !important;
        border: 1px solid #000 !important;
        border-radius: 8px !important;
        padding: 10px !important;
        font-size: 1rem !important;
        max-width: 420px !important;
        box-shadow: none !important;
    }

    div[data-testid="stTextInput"],
    div[data-testid="stTextInput"] > div,
    div[data-testid="stTextInput"] > div > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    div[data-testid="stTextInput"] label {
        display: none !important;
    }

    /* Buttons */
    .stButton>button,
    div[data-testid="stFormSubmitButton"]>button {
        width: 100% !important;
        border-radius: 8px !important;
        font-weight: 800 !important;
        height: 3em !important;
        max-width: 420px !important;
    }

    /* Centered logo block (isolated from RTL) */
    .logo-center {
        display:flex;
        justify-content:center;
        align-items:center;
        direction:ltr;
        margin-top:-70px;
        margin-bottom:30px;
    }

    .hint {
        color:#666;
        font-size:0.95rem;
        margin: 6px 0 10px 0;
        max-width:420px;
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
            f"קוד הכניסה שלך למערכת רואה חשבון בקליק: {code}\n\n"
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
# State
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
        reset_login_flow()

    # Logo centered and high
    st.markdown('<div class="logo-center">', unsafe_allow_html=True)
    st.image("logo.png", width=320)
    st.markdown("</div>", unsafe_allow_html=True)

    # Right-side form column
    spacer, form_col = st.columns([3, 1.3])

    with form_col:
        otp_sent = st.session_state.get("otp_sent", False)

        if not otp_sent:
            with st.form("login_form", clear_on_submit=False, border=False):
                name = st.text_input(
                    "שם",
                    placeholder="שם מלא — שם ושם משפחה",
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

                parts = name.split()
                valid_name = len(parts) >= 2 and all(len(p) >= 2 for p in parts)
                valid_email = ("@" in email) and ("." in email)

                if name and not valid_name:
                    st.caption("יש להזין שם ושם משפחה")
                if email and not valid_email:
                    st.caption("יש להזין כתובת מייל תקינה")

                st.markdown(
                    '<div class="hint">להשלמת הכניסה קוד יישלח לכתובת המייל שהכנסת</div>',
                    unsafe_allow_html=True,
                )

                submitted = st.form_submit_button("שלח קוד")

            if submitted:
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


# -------------------------
# WELCOME PAGE
# -------------------------
elif st.session_state.page == "welcome":
    spacer, content = st.columns([3, 1.3])
    with content:
        user_name = st.session_state.get("user_name", "משתמש")
        st.markdown(f"### ברוכים הבאים, {user_name} 👋")
        st.write("ברוכים הבאים למערכת הכנה לבחינת לשכת רואי החשבון")

        if st.button("יציאה"):
            st.session_state.logged_in = False
            st.session_state.page = "login"
            if "user_name" in st.session_state:
                del st.session_state["user_name"]
            reset_login_flow()
            st.rerun()

# סוף קובץ
