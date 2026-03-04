# utils.py | Version: v1.3

import streamlit as st
import smtplib
import base64
from email.mime.text import MIMEText

# -------------------------
# Syllabus
# -------------------------
SYLLABUS = {
    "חשבונאות פיננסית": ["הכנת דוחות כספיים", "תקני דיווח בינלאומיים (IFRS)", "מאזנים ומכשירי הון"],
    "ביקורת": ["עקרונות הביקורת", "ביקורת פנימית וחיצונית", "דוחות המבקר"],
    "מיסוי": ["מס הכנסה", "מיסוי מקרקעין", 'מע"מ ומיסוי בינלאומי'],
    "משפט": ["דיני תאגידים", "דיני חוזים", "דיני ניירות ערך"],
    "כלכלה וניהול פיננסי": ["ניתוח דוחות", "הערכות שווי", "ניהול סיכונים"],
}

# -------------------------
# Logo
# -------------------------
def get_logo_base64():
    try:
        with open("logo.png", "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return None

def get_logo_tag():
    logo_b64 = get_logo_base64()
    if logo_b64:
        return f'<img src="data:image/png;base64,{logo_b64}" alt="logo">'
    return '<span style="font-size:2rem;">✅</span>'

# -------------------------
# Top bar — לוגו שמאל, שם משתמש ימין
# -------------------------
def render_top_bar(logo_tag):
    user_name = st.session_state.get("user_name", "משתמש")
    st.markdown(f"""
        <div id="top" style="display:flex; align-items:center; justify-content:space-between; margin-bottom:8px;">
            <div style="display:flex; align-items:center; gap:6px; margin-right:16px;">
                <span style="font-size:0.9rem; font-weight:600;">{user_name}</span>
                <span style="font-size:1.2rem;">👤</span>
            </div>
            <div class="logo-wrap" style="margin:0;">{logo_tag}</div>
        </div>
    """, unsafe_allow_html=True)

# -------------------------
# CSS
# -------------------------
def inject_css():
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
    width: 128px;
    max-width: 36vw;
    height: auto;
    display: block;
  }
  div[data-testid="stTextInput"] {
    width: 50% !important;
    margin-right: 0 !important;
    margin-left: auto !important;
  }
  @media (max-width: 768px) {
    div[data-testid="stTextInput"] {
      width: 65% !important;
    }
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
def clean_lesson(txt):
    lines = txt.split("\n")
    # הסר שורות ריקות וכותרות markdown בהתחלה
    while lines and (lines[0].strip() == "" or lines[0].strip().startswith("#")):
        lines.pop(0)
    # הסר שורה ראשונה אם היא נראית ככותרת (bold קצרה ללא סימני פיסוק בסוף)
    if lines:
        first = lines[0].strip()
        is_bold_title = first.startswith("**") and first.endswith("**") and len(first) < 120
        is_short_title = len(first) < 80 and not first.endswith((".", ",", ":", ";", "?", "!")) and first.count(" ") < 10
        if is_bold_title or (is_short_title and not first.startswith("-") and not first.startswith("*")):
            lines.pop(0)
            while lines and lines[0].strip() == "":
                lines.pop(0)
    return "\n".join(lines)

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

# סוף קובץ
