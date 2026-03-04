# study_page.py | Version: v1.0
# study_page.py — עמוד לימוד

import streamlit as st
import google.generativeai as genai
from utils import SYLLABUS, clean_lesson


def render_study(logo_tag):
    user_name = st.session_state.get("user_name", "משתמש")

    st.markdown('<div class="wrap">', unsafe_allow_html=True)
    st.markdown(f"""
        <div id="top" style="display:flex; align-items:center; justify-content:space-between; margin-bottom:4px;">
            <div style="display:flex; align-items:center; gap:6px; margin-right:16px;">
                <span style="font-size:0.9rem; font-weight:600;">{user_name}</span>
                <span style="font-size:1.2rem;">👤</span>
            </div>
            <div class="logo-wrap" style="margin:0;">{logo_tag}</div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("### 📚 שיעורי לימוד")

    # בחירת נושא — dropdown
    current_topic = st.session_state.get("selected_topic", "בחר...")
    topic_options = ["בחר..."] + list(SYLLABUS.keys())
    idx = topic_options.index(current_topic) if current_topic in topic_options else 0
    selected_topic = st.selectbox("נושא:", topic_options, index=idx, label_visibility="collapsed")

    if selected_topic != current_topic:
        st.session_state.selected_topic = selected_topic
        st.session_state.selected_sub = None
        st.session_state.lesson_txt = ""
        st.session_state.is_loading = False
        st.rerun()

    # תתי נושאים — כפתורים באותה שורה
    if selected_topic and selected_topic != "בחר...":
        st.markdown(f"**{selected_topic}** — בחר תת נושא:")
        subs = SYLLABUS[selected_topic]
        cols = st.columns(len(subs))
        is_loading = st.session_state.get("is_loading", False)
        for i, sub in enumerate(subs):
            with cols[i]:
                is_active_sub = sub == st.session_state.get("selected_sub")
                is_disabled = bool(is_loading or is_active_sub)
                if st.button(sub, key=f"sub_{sub}", disabled=is_disabled):
                    st.session_state.selected_sub = sub
                    st.session_state.lesson_txt = ""
                    st.session_state.is_loading = True
                    st.session_state.quiz_questions = None
                    st.session_state.page = "lesson"
                    st.rerun()

    # שיעור
    selected_sub = st.session_state.get("selected_sub")
    if selected_sub:
        if not st.session_state.get("lesson_txt"):
            try:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel("gemini-2.0-flash")
                prompt = f"""אתה פרופסור בכיר למשפט עסקי וחשבונאות, המתמחה בהכנה למבחני מועצת רואי החשבון בישראל.

כתוב שיעור מקיף ומעמיק ברמה אקדמית גבוהה בנושא: **{selected_sub}** (חלק מנושא: {selected_topic}).

דרישות מחייבות:
- החומר חייב לכסות את כל מה שנדרש לבחינת הלשכה ברמה המלאה
- כלול הגדרות משפטיות/חשבונאיות מדויקות
- כלול עקרונות, כללים וחריגים
- כל נוסחה, חישוב, תרגיל מספרי, או ביטוי מתמטי — חייב להופיע בתוך תיבת קוד (``` ```) בלבד. אסור לרשום נוסחאות בשורת טקסט רגילה
- ציין מקורות: חוק, תקן, סעיף, או עקרון IFRS הרלוונטי לכל נושא
- רמה: סטודנט שעומד לגשת למבחן הלשכה ומצפה לחומר ברמה המקצועית הגבוהה ביותר
- כתוב בעברית, מובנה עם כותרות וסעיפים ברורים
- אסור להוסיף כותרת כלשהי בתחילת התשובה — התחל ישירות מהתוכן הראשון
- אסור להוסיף משפט פתיחה, הקדמה, או "שיעור מקיף ב..." — קפוץ ישר לחומר
- השתמש רק ב-## ומטה לכותרות פנימיות, לעולם לא #"""

                placeholder = st.empty()
                full_text = ""
                response = model.generate_content(prompt, stream=True)
                for chunk in response:
                    if chunk.text:
                        full_text += chunk.text
                        placeholder.markdown(full_text + "▌")
                full_text = clean_lesson(full_text)
                placeholder.markdown(full_text)
                st.session_state.lesson_txt = full_text
                st.session_state.is_loading = False
                st.rerun()

            except Exception as e:
                st.session_state.is_loading = False
                st.error(f"שגיאה בטעינת השיעור: {e}")

        else:
            st.markdown(clean_lesson(st.session_state.get("lesson_txt", "")))

        # תפריט תחתון — מוצג רק אחרי שהשיעור נטען
        if st.session_state.get("lesson_txt"):
            st.divider()
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                if st.button("📝 שאלון תת נושא", key="lesson_quiz_sub"):
                    st.session_state.page = "quiz_sub"
                    st.rerun()
            with c2:
                st.button("📋 שאלון נושא כללי", disabled=True, key="lesson_quiz_topic")
            with c3:
                st.markdown('<a href="#top" style="display:block;text-align:center;padding:10px 0;font-weight:800;text-decoration:none;color:#31333f;">⬆️ לראש העמוד</a>', unsafe_allow_html=True)
            with c4:
                if st.button("🏠 תפריט ראשי", key="lesson_home"):
                    st.session_state.page = "welcome"
                    st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
