# File: app.py | Date & Time: 2026-03-03 23:33 (Asia/Jerusalem) | Version: CPA22

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
st.markdown("""
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
  div[data-testid="stTextInput"] {
    width: 50% !important;
    margin-right: 0 !important;
    margin-left: auto !important;
  }
  div[data-testid="stTextInput"] input {
    background: #ffffff !important;
    border: 1px solid #000 !important;
    border-radius: 10px !important;
    padding: 12px !important;
    font-size: 1rem !important;
    box-shadow: none !important;
    direction: ltr !important;
    text-align: right !important;
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
    margin: 10px 0;
  }
  .menu-btn>button {
    background-color: #1a2e5a !important;
    color: white !important;
    font-size: 1rem !important;
  }
  .menu-btn>button:hover {
    background-color: #243d75 !important;
  }
</style>
""", unsafe_allow_html=True)

# -------------------------
# Helpers
# -------------------------
def send_otp_email(to_email: str, code: str) -> bool:
    try:
        gmail_user = st.secrets["GMAIL_USER"]
        gmail_pass = st.secrets["GMAIL_PASS"]
        msg = MIMEText(f"קוד הכניסה שלך לרואה חשבון בקליק: {code}\n\nהקוד תקף ל-2 דקות.")
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
# Syllabus
# -------------------------
SYLLABUS = {
    "חשבונאות פיננסית": ["הכנת דוחות כספיים", "תקני דיווח בינלאומיים (IFRS)", "מאזנים ומכשירי הון"],
    "ביקורת": ["עקרונות הביקורת", "ביקורת פנימית וחיצונית", "דוחות המבקר"],
    "מיסוי": ["מס הכנסה", "מיסוי מקרקעין", "מע\"מ ומיסוי בינלאומי"],
    "משפט": ["דיני תאגידים", "דיני חוזים", "דיני ניירות ערך"],
    "כלכלה וניהול פיננסי": ["ניתוח דוחות", "הערכות שווי", "ניהול סיכונים"],
}

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


# -------------------------
# WELCOME PAGE (תפריט ראשי)
# -------------------------
elif st.session_state.page == "welcome":
    st.markdown('<div class="wrap">', unsafe_allow_html=True)
    st.markdown(f'<div class="logo-wrap">{logo_tag}</div>', unsafe_allow_html=True)

    user_name = st.session_state.get("user_name", "משתמש")

    st.markdown(f"""
        <div style="display:flex; align-items:center; justify-content:flex-end;
                    gap:8px; margin-bottom:20px;">
            <span style="font-size:1rem; font-weight:600;">{user_name}</span>
            <span style="font-size:1.5rem;">👤</span>
        </div>
    """, unsafe_allow_html=True)

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
            st.session_state.page = "exam"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    _s, col_out = st.columns([3, 1])
    with col_out:
        if st.button("יציאה"):
            st.session_state.logged_in = False
            st.session_state.page = "login"
            reset_login_flow(full=False)
            clear_login_inputs_only()
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# STUDY PAGE (בחירת נושא)
# -------------------------
elif st.session_state.page == "study":
    st.markdown('<div class="wrap">', unsafe_allow_html=True)
    st.markdown(f'<div class="logo-wrap">{logo_tag}</div>', unsafe_allow_html=True)

    user_name = st.session_state.get("user_name", "משתמש")
    st.markdown(f"""
        <div style="display:flex; align-items:center; justify-content:flex-end;
                    gap:8px; margin-bottom:20px;">
            <span style="font-size:1rem; font-weight:600;">{user_name}</span>
            <span style="font-size:1.5rem;">👤</span>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📚 שיעורי לימוד")
    st.markdown("<div style='margin-bottom:16px;'>בחר נושא:</div>", unsafe_allow_html=True)

    for topic in SYLLABUS:
        if st.button(topic, key=f"topic_{topic}"):
            st.session_state.selected_topic = topic
            st.session_state.page = "subtopic"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# -------------------------
# SUBTOPIC PAGE (בחירת תת נושא)
# -------------------------
elif st.session_state.page == "subtopic":
    st.markdown('<div class="wrap">', unsafe_allow_html=True)
    st.markdown(f'<div class="logo-wrap">{logo_tag}</div>', unsafe_allow_html=True)

    user_name = st.session_state.get("user_name", "משתמש")
    st.markdown(f"""
        <div style="display:flex; align-items:center; justify-content:flex-end;
                    gap:8px; margin-bottom:20px;">
            <span style="font-size:1rem; font-weight:600;">{user_name}</span>
            <span style="font-size:1.5rem;">👤</span>
        </div>
    """, unsafe_allow_html=True)

    topic = st.session_state.get("selected_topic", "")
    st.markdown(f"### 📖 {topic}")
    st.markdown("<div style='margin-bottom:16px;'>בחר תת נושא ללימוד:</div>", unsafe_allow_html=True)

    for sub in SYLLABUS.get(topic, []):
        if st.button(sub, key=f"sub_{sub}"):
            st.session_state.selected_sub = sub
            st.session_state.page = "lesson"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# סוף קובץ
