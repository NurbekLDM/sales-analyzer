from __future__ import annotations

from typing import Optional

import pandas as pd
from openai import OpenAI

from sales_analyzer.domain.analyzer import (
    compute_metrics,
    map_columns,
    monthly_sales,
    regional_sales,
    top_products,
)


def _safe_preview(df: pd.DataFrame, rows: int = 12) -> str:
    preview = df.head(rows).copy()
    return preview.to_csv(index=False)


def _product_region_sales(df: pd.DataFrame) -> pd.DataFrame:
    cols = map_columns(df)
    if not cols["product"] or not cols["region"] or not cols["sales"]:
        return pd.DataFrame(columns=["product", "region", "sales"])

    result = (
        df.groupby([cols["product"], cols["region"]], dropna=False)[cols["sales"]]
        .sum()
        .reset_index()
        .sort_values(cols["sales"], ascending=False)
    )
    result.columns = ["product", "region", "sales"]
    return result


def _product_region_summary(df: pd.DataFrame) -> pd.DataFrame:
    cols = map_columns(df)
    if not cols["product"] or not cols["region"] or not cols["sales"]:
        return pd.DataFrame(columns=["product", "region", "sales", "quantity"])

    agg_spec = {cols["sales"]: "sum"}
    if cols["quantity"]:
        agg_spec[cols["quantity"]] = "sum"

    result = (
        df.groupby([cols["product"], cols["region"]], dropna=False)
        .agg(agg_spec)
        .reset_index()
        .sort_values(cols["sales"], ascending=False)
    )

    if cols["quantity"]:
        result.columns = ["product", "region", "sales", "quantity"]
    else:
        result.columns = ["product", "region", "sales"]
        result["quantity"] = pd.NA

    return result


def _build_context(df: pd.DataFrame) -> str:
    cols = map_columns(df)
    metrics = compute_metrics(df)
    top_df = top_products(df, top_n=5)
    region_df = regional_sales(df, top_n=5)
    month_df = monthly_sales(df)
    pr_df = _product_region_sales(df)
    prs_df = _product_region_summary(df)

    product_values = (
        sorted([str(v) for v in df[cols["product"]].dropna().unique().tolist()])
        if cols["product"]
        else []
    )
    region_values = (
        sorted([str(v) for v in df[cols["region"]].dropna().unique().tolist()])
        if cols["region"]
        else []
    )

    return (
        f"Row count: {len(df)}\\n"
        f"Columns: {list(df.columns)}\\n"
        f"Mapped columns: {cols}\\n"
        f"Metrics: {metrics}\\n"
        f"Available products: {product_values}\\n"
        f"Available regions: {region_values}\\n"
        f"Top products (top 5):\\n{top_df.to_csv(index=False) if not top_df.empty else 'N/A'}\\n"
        f"Regional sales (top 5):\\n{region_df.to_csv(index=False) if not region_df.empty else 'N/A'}\\n"
        f"Product-Region sales table (all combinations):\\n{pr_df.to_csv(index=False) if not pr_df.empty else 'N/A'}\\n"
        f"Product-Region summary (sales + quantity):\\n{prs_df.to_csv(index=False) if not prs_df.empty else 'N/A'}\\n"
        f"Monthly sales:\\n{month_df.to_csv(index=False) if not month_df.empty else 'N/A'}\\n"
        f"Raw sample rows (first 12):\\n{_safe_preview(df, 12)}"
    )


def ask_openai_agent(
    df: pd.DataFrame,
    question: str,
    api_key: str,
    model: str = "gpt-4.1-mini",
) -> str:
    client = OpenAI(api_key=api_key)
    context = _build_context(df)

    system_prompt = (
        "You are a sales data analyst assistant. "
        "Answer in Uzbek language, concise and business-friendly. "
        "Use only provided dataset context. If uncertain, state the limitation clearly. "
        "If user asks specific product/region/date filter, calculate using the provided aggregate tables exactly. "
        "Never replace a specific filtered question with a generic top-region/top-product answer. "
        "If quantity column is available and user asks for dona/nechta/quantity, you must return total quantity. "
        "Do not claim quantity is unavailable when quantity exists in the context."
    )

    user_prompt = (
        f"Question: {question}\\n\\n"
        "Dataset context:\\n"
        f"{context}"
    )

    response = client.chat.completions.create(
        model=model,
        temperature=0.2,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    content: Optional[str] = response.choices[0].message.content
    return (content or "Javob olinmadi.").strip()
