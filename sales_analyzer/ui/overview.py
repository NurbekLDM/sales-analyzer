import streamlit as st

from sales_analyzer.domain.analyzer import (
    compute_metrics,
    map_columns,
    monthly_sales,
    regional_sales,
    top_products,
)


def render_overview(df):
    cols = map_columns(df)
    metrics = compute_metrics(df)

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Total Sales", f"{metrics['total_sales']:,.2f}" if metrics["total_sales"] is not None else "N/A")
    with m2:
        st.metric("Total Orders", f"{metrics['total_orders']:,}")
    with m3:
        st.metric("Avg Order Value", f"{metrics['avg_order_value']:,.2f}" if metrics["avg_order_value"] is not None else "N/A")

    st.subheader("Data Preview")
    st.dataframe(df, use_container_width=True)

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("Top Products")
        top_df = top_products(df, top_n=10)
        if top_df.empty:
            st.info("Product/Sales ustunlari topilmadi.")
        else:
            st.bar_chart(top_df.set_index("product")["sales"])
            st.dataframe(top_df, use_container_width=True)

    with chart_col2:
        st.subheader("Regional Sales")
        region_df = regional_sales(df, top_n=10)
        if region_df.empty:
            st.info("Region/Sales ustunlari topilmadi.")
        else:
            st.bar_chart(region_df.set_index("region")["sales"])
            st.dataframe(region_df, use_container_width=True)

    st.subheader("Monthly Trend")
    monthly_df = monthly_sales(df)
    if monthly_df.empty:
        st.info("Date/Sales ustunlari topilmadi yoki date format mos emas.")
    else:
        st.line_chart(monthly_df.set_index("month")["sales"])
        st.dataframe(monthly_df, use_container_width=True)

    st.caption(
        "Aniqlangan ustunlar: "
        + ", ".join([f"{key}={value}" for key, value in cols.items() if value is not None])
    )
