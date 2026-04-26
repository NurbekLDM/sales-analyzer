import pandas as pd
import streamlit as st
from sqlalchemy.engine import Engine

from sales_analyzer.config import AppConfig
from sales_analyzer.services.question_service import QuestionService


def _ensure_state() -> None:
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "last_perf" not in st.session_state:
        st.session_state.last_perf = None


def _render_performance() -> None:
    perf = st.session_state.last_perf
    if perf is None:
        return

    st.subheader("Javob Tezligi Metrikalari")
    p1, p2, p3 = st.columns(3)
    with p1:
        st.metric("Umumiy javob vaqti", f"{perf['total_ms']:.0f} ms")
    with p2:
        st.metric("Eng sekin bosqich", perf["slowest_stage"])
    with p3:
        st.metric("O'lchangan bosqichlar", f"{len(perf['stage_times_ms'])} ta")

    stage_df = pd.DataFrame(
        [{"Bosqich": name, "Vaqt (ms)": round(value, 2)} for name, value in perf["stage_times_ms"].items()]
    )
    if not stage_df.empty:
        st.dataframe(stage_df, use_container_width=True)

    if perf["db_error"]:
        st.info("Eslatma: DB log yozishda xatolik bo'ldi, lekin javob muvaffaqiyatli qaytdi.")


def _render_history() -> None:
    if not st.session_state.chat_history:
        return

    st.subheader("Previous Q&A")
    for item in st.session_state.chat_history[:8]:
        st.markdown(f"**Q:** {item['question']}")
        st.markdown(f"**A:** {item['answer']}")


def render_question_panel(df, config: AppConfig, engine: Engine) -> None:
    _ensure_state()

    st.subheader("Ask About Your Sales Data")
    question = st.text_input("Savolingizni yozing", placeholder="Masalan: top product qaysi?")

    if st.button("Analyze", type="primary"):
        if not question.strip():
            st.warning("Savol kiriting.")
        else:
            try:
                result = QuestionService.process_question(df=df, question=question, config=config, engine=engine)
            except ValueError as exc:
                st.error(str(exc))
                st.stop()

            st.session_state.chat_history.insert(0, {"question": question, "answer": result.answer})
            st.session_state.last_perf = {
                "total_ms": result.total_ms,
                "slowest_stage": result.slowest_stage,
                "stage_times_ms": result.stage_times_ms,
                "db_error": result.db_error,
            }

            st.success(result.answer)
            if result.detail_df is not None and not result.detail_df.empty:
                st.dataframe(result.detail_df, use_container_width=True)

    _render_performance()
    _render_history()
