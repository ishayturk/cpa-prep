# utils.py | Version: v2.7

import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64

# -------------------------
# Syllabus
# -------------------------
SYLLABUS = {
    "מבוא לחשבונאות": [
        "מושגי יסוד ומשוואת החשבונאות",
        "רישום עסקאות ויומן",
        "ספר חשבונות ומאזן בוחן",
        "דוחות כספיים בסיסיים",
    ],
    "חשבונאות פיננסית א'": [
        "דוח רווח והפסד",
        "מאזן והון עצמי",
        "תזרים מזומנים",
        "מלאי והכרה בהכנסות",
        "רכוש קבוע ופחת",
    ],
    "חשבונאות פיננסית מתקדמת": [
        "איחוד דוחות כספיים",
        "מכשירים פיננסיים IFRS 9",
        "חכירות IFRS 16",
        "מיסים נדחים IAS 12",
        "עסקאות מורכבות ורכישות עסקים",
    ],
    "תמחור וחשבונאות ניהולית מתקדמת": [
        "תמחור עלויות ותמחור ABC",
        "ניתוח CVP ונקודת איזון",
        "תקצוב ובקרה תקציבית",
        "תמחור לקבלת החלטות",
        "מדדי ביצוע ו-Balanced Scorecard",
    ],
    "יסודות ביקורת החשבונות": [
        "עקרונות ותקני ביקורת",
        "תכנון הביקורת והערכת סיכונים",
        "ראיות ביקורת ונהלי ביקורת",
        "דוח המבקר וסוגיו",
    ],
    "ביקורת חשבונות ובעיות ביקורת מורכבות": [
        "ביקורת מערכות מידע",
        "ביקורת פנימית ובקרה פנימית",
        "בעיות ביקורת מורכבות",
        "עצמאות המבקר ואתיקה מקצועית",
    ],
    "דיני מיסים א'": [
        "מס הכנסה — יסודות ומקורות הכנסה",
        "הכנסות עבודה ועסק",
        "פטורים ניכויים וזיכויים",
        "מיסוי רווחי הון",
    ],
    "דיני מיסים ב'": [
        "מס חברות ודיבידנדים",
        "מע\"מ — עקרונות ועסקאות",
        "מיסוי מקרקעין",
        "מיסוי בינלאומי ואמנות מס",
    ],
    "משפט עסקי": [
        "דיני חוזים — כריתה ותוקף",
        "דיני נזיקין",
        "דיני קניין ובטחונות",
        "הליכים משפטיים ופסיקה",
    ],
    "דיני תאגידים ומסחר": [
        "דיני חברות — הקמה וניהול",
        "זכויות בעלי מניות ואסיפות",
        "ניירות ערך וחובות גילוי",
        "פשיטת רגל ופירוק",
        "שותפויות ועמותות",
    ],
    "כלכלה": [
        "מיקרוכלכלה — היצע וביקוש",
        "מבנה שוק ותחרות",
        "מקרוכלכלה — צמיחה ומחזורים",
        "מדיניות מוניטרית ופיסקלית",
    ],
    "סטטיסטיקה": [
        "סטטיסטיקה תיאורית ומדדים",
        "הסתברות והתפלגויות",
        "מבחני השערות",
        "רגרסיה וניתוח מתאם",
    ],
    "מימון": [
        "ערך זמן הכסף",
        "הערכת שווי אג\"ח ומניות",
        "ניהול תיקי השקעות וסיכון",
        "מימון חברות ומבנה הון",
        "ניתוח פרויקטים — NPV ו-IRR",
    ],
    "טכנולוגיות מידע": [
        "מערכות מידע בארגון",
        "אבטחת מידע וסייבר",
        "ביקורת מערכות מידע",
        "מערכות ERP ו-BI",
    ],
}

EXAM_FILES = {
    "טכנולוגיות מידע": ["IT_01.json"],
    "משפט עסקי": ["BLaw_01.json", "BLaw_02.json"],
    "דיני תאגידים ומסחר": ["corporation_01.json"],
    "תמחור וחשבונאות ניהולית מתקדמת": ["advanced_pricing_01.json"],
    "דיני מסים א'": ["taxes_a_01.json"],
    "סטטיסטיקה": ["statistics_01.json"],
}

import os as _os
EXAMS_DIR = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "data", "exams")

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
# Top bar
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
    max-width: 80% !important;
    margin-left: auto !important;
    margin-right: auto !important;
  }
  section[data-testid="stMain"] > div,
  section[data-testid="stMain"] > div > div {
    overflow: visible !important;
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

  .desktop-only { display: block; }
  .mobile-only  { display: none; }

  @media (max-width: 768px) {
    .desktop-only { display: none; }
    .mobile-only  { display: block; }
  }
</style>
""", unsafe_allow_html=True)

# -------------------------
# Helpers
# -------------------------
def clean_lesson(txt):
    lines = txt.split("\n")
    while lines and (lines[0].strip() == "" or lines[0].strip().startswith("#")):
        lines.pop(0)
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
        raw_user = st.secrets["GMAIL_USER"]
        raw_pass = st.secrets["GMAIL_PASS"]
        gmail_user = raw_user.strip().encode("ascii", "ignore").decode("ascii")
        gmail_pass = raw_pass.strip().encode("ascii", "ignore").decode("ascii")

        msg = MIMEMultipart("alternative")
        msg["Subject"] = "קוד כניסה - רואה חשבון בקליק"
        msg["From"] = gmail_user
        msg["To"] = to_email

        html = (
            "<div dir='rtl' style='font-family:Arial,sans-serif;font-size:16px;'>"
            "<p>קוד הכניסה שלך לרואה חשבון בקליק:</p>"
            "<h2 style='letter-spacing:4px;'>" + code + "</h2>"
            "<p style='color:#666;'>הקוד תקף ל-2 דקות.</p>"
            "</div>"
        )
        msg.attach(MIMEText(html, "html", "utf-8"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_pass)
            server.sendmail(gmail_user, to_email, msg.as_string())

        return True
    except Exception as e:
        st.error(f"שגיאת מייל: {e}")
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
