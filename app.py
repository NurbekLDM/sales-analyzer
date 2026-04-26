import streamlit as st
from sales_analyzer.config import AppConfig
from sales_analyzer.domain.analyzer import prepare_dataframe
from sales_analyzer.infrastructure.db import get_engine, init_db
from sales_analyzer.services.file_service import FileService
from sales_analyzer.ui.overview import render_overview
from sales_analyzer.ui.question_panel import render_question_panel
from sales_analyzer.ui.sidebar import render_sidebar


@st.cache_resource
def get_db_engine(database_url: str):
    engine = get_engine(database_url)
    init_db(engine)
    return engine


def run_app() -> None:
    st.set_page_config(page_title="Sales Data Analyzer", page_icon="📊", layout="wide")
    st.title("📊 Sales Data Analyzer Agent")
    st.caption("CSV/Excel fayllarni yuklang, statistikani ko'ring va natural language savollar bering.")

    config = AppConfig.from_env()
    uploaded = render_sidebar()

    if not uploaded:
        st.info("Boshlash uchun fayl yuklang.")
        st.stop()

    try:
        raw_df = FileService.read_uploaded_file(uploaded)
        df = prepare_dataframe(raw_df)
    except Exception as exc:
        st.error(f"Faylni o'qishda xatolik: {exc}")
        st.stop()

    if df.empty:
        st.warning("Yuklangan fayl bo'sh.")
        st.stop()

    render_overview(df)
    engine = get_db_engine(config.database_url)
    render_question_panel(df=df, config=config, engine=engine)


run_app()
