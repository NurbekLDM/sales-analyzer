import re
from typing import Dict, Optional, Tuple

import pandas as pd


ALIASES = {
    "date": ["date", "order_date", "sale_date", "created_at", "timestamp"],
    "product": ["product", "item", "sku", "product_name", "name"],
    "region": ["region", "city", "state", "country", "area", "location"],
    "quantity": ["qty", "quantity", "units", "count", "volume"],
    "sales": ["sales", "revenue", "amount", "total", "total_sales", "price"],
    "order_id": ["order_id", "invoice", "transaction_id", "id", "order"],
}


def _normalize(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(name).strip().lower()).strip("_")


def map_columns(df: pd.DataFrame) -> Dict[str, Optional[str]]:
    normalized = {_normalize(col): col for col in df.columns}
    result: Dict[str, Optional[str]] = {key: None for key in ALIASES}

    for logical, candidates in ALIASES.items():
        for cand in candidates:
            c = _normalize(cand)
            if c in normalized:
                result[logical] = normalized[c]
                break

    for logical, original in result.items():
        if original is not None:
            continue
        for norm_col, raw_col in normalized.items():
            if any(keyword in norm_col for keyword in ALIASES[logical]):
                result[logical] = raw_col
                break

    return result


def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    cols = map_columns(out)

    if cols["date"]:
        out[cols["date"]] = pd.to_datetime(out[cols["date"]], errors="coerce")

    if cols["sales"]:
        out[cols["sales"]] = (
            out[cols["sales"]]
            .astype(str)
            .str.replace(r"[^0-9.\-]", "", regex=True)
            .replace("", pd.NA)
        )
        out[cols["sales"]] = pd.to_numeric(out[cols["sales"]], errors="coerce")

    if cols["quantity"]:
        out[cols["quantity"]] = pd.to_numeric(out[cols["quantity"]], errors="coerce")

    return out


def compute_metrics(df: pd.DataFrame) -> Dict[str, Optional[float]]:
    cols = map_columns(df)

    total_sales = float(df[cols["sales"]].sum()) if cols["sales"] else None
    total_orders = int(df[cols["order_id"]].nunique()) if cols["order_id"] else int(len(df))
    avg_order_value = (
        float(total_sales / total_orders) if total_sales is not None and total_orders else None
    )

    return {
        "total_sales": total_sales,
        "total_orders": total_orders,
        "avg_order_value": avg_order_value,
    }


def top_products(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    cols = map_columns(df)
    if not cols["product"] or not cols["sales"]:
        return pd.DataFrame(columns=["product", "sales"])

    result = (
        df.groupby(cols["product"], dropna=False)[cols["sales"]]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )
    result.columns = ["product", "sales"]
    return result


def regional_sales(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    cols = map_columns(df)
    if not cols["region"] or not cols["sales"]:
        return pd.DataFrame(columns=["region", "sales"])

    result = (
        df.groupby(cols["region"], dropna=False)[cols["sales"]]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )
    result.columns = ["region", "sales"]
    return result


def monthly_sales(df: pd.DataFrame) -> pd.DataFrame:
    cols = map_columns(df)
    if not cols["date"] or not cols["sales"]:
        return pd.DataFrame(columns=["month", "sales"])

    tmp = df.dropna(subset=[cols["date"]]).copy()
    if tmp.empty:
        return pd.DataFrame(columns=["month", "sales"])

    tmp["month"] = tmp[cols["date"]].dt.to_period("M").astype(str)
    result = tmp.groupby("month")[cols["sales"]].sum().sort_index().reset_index()
    result.columns = ["month", "sales"]
    return result


def _find_value_in_question(question: str, values: pd.Series) -> Optional[str]:
    q = question.lower()
    unique_values = [str(v).strip() for v in values.dropna().unique()]
    unique_values = [v for v in unique_values if v]
    unique_values.sort(key=len, reverse=True)

    for value in unique_values:
        candidate = value.lower()
        if len(candidate) < 3:
            continue
        if candidate in q:
            return value
    return None


def answer_question(df: pd.DataFrame, question: str) -> Tuple[str, Optional[pd.DataFrame]]:
    q = question.strip().lower()
    cols = map_columns(df)
    metrics = compute_metrics(df)

    if not q:
        return "Savol kiriting.", None

    if cols["sales"] and (cols["product"] or cols["region"]):
        product_value = _find_value_in_question(q, df[cols["product"]]) if cols["product"] else None
        region_value = _find_value_in_question(q, df[cols["region"]]) if cols["region"] else None

        asks_for_amount = any(
            k in q for k in ["qancha", "necha", "sotilgan", "sales", "revenue", "jami", "sum"]
        )

        if asks_for_amount and (product_value or region_value):
            filtered = df.copy()
            labels = []

            if product_value and cols["product"]:
                filtered = filtered[
                    filtered[cols["product"]].astype(str).str.lower() == str(product_value).lower()
                ]
                labels.append(f"mahsulot={product_value}")

            if region_value and cols["region"]:
                filtered = filtered[
                    filtered[cols["region"]].astype(str).str.lower() == str(region_value).lower()
                ]
                labels.append(f"hudud={region_value}")

            if filtered.empty:
                return "So'ralgan filter bo'yicha ma'lumot topilmadi.", None

            total_sales = float(filtered[cols["sales"]].sum())
            response = f"{', '.join(labels)} bo'yicha jami savdo: {total_sales:,.2f}"

            if cols["quantity"] and any(k in q for k in ["dona", "quantity", "units"]):
                total_qty = float(filtered[cols["quantity"]].fillna(0).sum())
                response += f" | Jami miqdor: {total_qty:,.0f} dona"

            detail = filtered.head(20).copy()
            return response, detail

    if any(k in q for k in ["total sales", "jami savdo", "umumiy savdo", "revenue"]):
        if metrics["total_sales"] is None:
            return "Savdo summasi ustuni topilmadi.", None
        return f"Umumiy savdo: {metrics['total_sales']:,.2f}", None

    if any(k in q for k in ["average", "avg", "o'rtacha", "ortacha"]):
        if metrics["avg_order_value"] is None:
            return "O'rtacha qiymatni hisoblash uchun yetarli ustunlar topilmadi.", None
        return f"O'rtacha buyurtma qiymati: {metrics['avg_order_value']:,.2f}", None

    if any(k in q for k in ["top product", "best product", "eng yaxshi mahsulot", "top mahsulot"]):
        top_df = top_products(df, top_n=10)
        if top_df.empty:
            return "Product va sales ustunlari topilmadi.", None
        winner = top_df.iloc[0]
        return f"Top mahsulot: {winner['product']} ({winner['sales']:,.2f})", top_df

    if any(k in q for k in ["region", "hudud", "viloyat", "country", "city"]):
        reg_df = regional_sales(df, top_n=10)
        if reg_df.empty:
            return "Region va sales ustunlari topilmadi.", None
        winner = reg_df.iloc[0]
        return f"Eng yuqori savdo hududi: {winner['region']} ({winner['sales']:,.2f})", reg_df

    if any(k in q for k in ["monthly", "oylik", "month", "trend"]):
        mon_df = monthly_sales(df)
        if mon_df.empty:
            return "Date va sales ustunlari topilmadi yoki ma'lumotlar yaroqsiz.", None
        return "Oylik savdo trendi hisoblandi.", mon_df

    if "rows" in q or "qator" in q:
        return f"Jadvalda {len(df):,} ta qator bor.", None

    if "columns" in q or "ustun" in q:
        return f"Jadvalda {len(df.columns):,} ta ustun bor.", None

    available = ", ".join([c for c in [cols["date"], cols["product"], cols["region"], cols["sales"]] if c])
    return (
        "Savolni tushunmadim. Masalan: 'Top product qaysi?', 'Jami savdo qancha?', "
        "'Regional analiz ber', 'Monthly trend ko'rsat'. "
        f"Aniqlangan ustunlar: {available if available else 'topilmadi'}.",
        None,
    )
