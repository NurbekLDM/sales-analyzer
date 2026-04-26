import streamlit as st


def render_sidebar():
    with st.sidebar:
        st.header("Data Upload")
        uploaded = st.file_uploader("CSV yoki Excel faylni tanlang", type=["csv", "xlsx", "xls"])
        st.divider()
        st.header("AI Agent")
        st.caption("Javoblar faqat AI model orqali beriladi. API key va model .env dan olinadi.")
        st.markdown("Savol namunalari:")
        st.write("- Jami savdo qancha?")
        st.write("- Top product qaysi?")
        st.write("- Regionlar bo'yicha analiz ber")
        st.write("- Monthly trend ko'rsat")

    return uploaded
