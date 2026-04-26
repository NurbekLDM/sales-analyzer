from dataclasses import dataclass
import time
from typing import Any, Optional

import pandas as pd
from sqlalchemy.engine import Engine

from sales_analyzer.config import AppConfig
from sales_analyzer.domain.analyzer import answer_question
from sales_analyzer.infrastructure.db import log_query
from sales_analyzer.infrastructure.openai_agent import ask_openai_agent


@dataclass
class QuestionResult:
    answer: str
    ai_chart: Optional[dict[str, Any]]
    detail_df: Optional[pd.DataFrame]
    stage_times_ms: dict[str, float]
    db_error: Optional[str]

    @property
    def total_ms(self) -> float:
        return sum(self.stage_times_ms.values())

    @property
    def slowest_stage(self) -> str:
        if not self.stage_times_ms:
            return "Noma'lum"
        return max(self.stage_times_ms.items(), key=lambda item: item[1])[0]


class QuestionService:
    @staticmethod
    def process_question(
        df: pd.DataFrame,
        question: str,
        config: AppConfig,
        engine: Engine,
    ) -> QuestionResult:
        if not config.has_openai_key:
            raise ValueError("OPENAI_API_KEY topilmadi. .env faylga API key qo'shing.")

        stage_times_ms: dict[str, float] = {}

        ai_start = time.perf_counter()
        try:
            ai_result = ask_openai_agent(
                df=df,
                question=question,
                api_key=config.openai_api_key.strip(),
                model=config.openai_model.strip() or "gpt-4.1-mini",
            )
            answer = ai_result.answer
            ai_chart = ai_result.chart
            stage_times_ms["AI agent javobi"] = (time.perf_counter() - ai_start) * 1000
        except Exception as exc:
            stage_times_ms["AI agent urinishi"] = (time.perf_counter() - ai_start) * 1000
            answer = f"AI agent javob bera olmadi: {exc}"
            ai_chart = None

        parser_start = time.perf_counter()
        _, detail_df = answer_question(df, question)
        stage_times_ms["Jadval uchun parser"] = (time.perf_counter() - parser_start) * 1000

        db_error = None
        db_start = time.perf_counter()
        try:
            log_query(engine, question, answer)
            stage_times_ms["DB ga yozish"] = (time.perf_counter() - db_start) * 1000
        except Exception as exc:
            stage_times_ms["DB ga yozish urinishi"] = (time.perf_counter() - db_start) * 1000
            db_error = str(exc)

        return QuestionResult(
            answer=answer,
            ai_chart=ai_chart,
            detail_df=detail_df,
            stage_times_ms=stage_times_ms,
            db_error=db_error,
        )
