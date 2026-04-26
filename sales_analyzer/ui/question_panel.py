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
    if "last_ai_chart" not in st.session_state:
        st.session_state.last_ai_chart = None


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


def _render_ai_chart() -> None:
    chart = st.session_state.last_ai_chart
    if not isinstance(chart, dict):
        return

    chart_type = str(chart.get("type", "none")).lower()
    data = chart.get("data")
    if chart_type == "none" or not isinstance(data, list) or not data:
        return

    rows = []
    for item in data:
        if not isinstance(item, dict):
            continue
        label = item.get("label")
        value = item.get("value")
        try:
            value = float(value)
        except Exception:
            continue
        rows.append({"label": str(label), "value": value})

    if not rows:
        return

    chart_df = pd.DataFrame(rows)
    title = str(chart.get("title", "AI asosida chart"))
    st.subheader(title)

    if chart_type == "line":
        st.line_chart(chart_df.set_index("label")["value"])
    else:
        st.bar_chart(chart_df.set_index("label")["value"])

    st.dataframe(chart_df, use_container_width=True)


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
            st.session_state.last_ai_chart = result.ai_chart
            st.session_state.last_perf = {
                "total_ms": result.total_ms,
                "slowest_stage": result.slowest_stage,
                "stage_times_ms": result.stage_times_ms,
                "db_error": result.db_error,
            }

            st.success(result.answer)
            _render_ai_chart()
            if result.detail_df is not None and not result.detail_df.empty:
                st.dataframe(result.detail_df, use_container_width=True)

    _render_performance()
    _render_history()
