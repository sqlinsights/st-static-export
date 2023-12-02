import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
import st_static_export as sse

st.set_page_config(layout="wide")
regions = ["LATAM", "EMEA", "NA", "APAC"]
colors = [
    "#aa423a",
    "#f6b404",
    "#327a88",
    "#303e55",
    "#c7ab84",
    "#b1dbaa",
    "#feeea5",
    "#3e9a14",
    "#6e4e92",
    "#c98149",
    "#d1b844",
    "#8db6d8",
]
months = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]
st.title("2022 Sales Dashboard")


@st.cache_data
def get_data():
    dates = pd.date_range(start="1/1/2022", end="12/31/2022")
    data = pd.DataFrame()
    sellers = {
        "LATAM": ["S01", "S02", "S03"],
        "EMEA": ["S10", "S11", "S12", "S13"],
        "NA": ["S21", "S22", "S23", "S24", "S25", "S26"],
        "APAC": ["S31", "S32", "S33", "S34", "S35", "S36"],
    }
    rows = 5000
    data["transaction_date"] = np.random.choice([str(i) for i in dates], size=rows)
    data["region"] = np.random.choice(regions, size=rows, p=[0.1, 0.3, 0.4, 0.2])
    data["transaction_amount"] = np.random.uniform(100, 250000, size=rows).round(2)
    data["seller"] = data.apply(
        lambda x: np.random.choice(sellers.get(x["region"])), axis=1
    )
    return data.sort_values(by="transaction_date").reset_index(drop=True)


sales_data = get_data()

region_select = alt.selection_single(fields=["region"], empty="all")
region_pie = (
    (
        alt.Chart(sales_data)
        .mark_arc(innerRadius=50)
        .encode(
            theta=alt.Theta(
                "transaction_amount",
                type="quantitative",
                aggregate="sum",
                title="Sum of Transactions",
            ),
            color=alt.Color(
                field="region",
                type="nominal",
                scale=alt.Scale(domain=regions, range=colors),
                title="Region",
            ),
            opacity=alt.condition(region_select, alt.value(1), alt.value(0.25)),
        )
    )
    .add_selection(region_select)
    .properties(title="Region Sales")
)

region_summary = (
    (
        alt.Chart(sales_data)
        .mark_bar()
        .encode(
            x=alt.X(
                "month(transaction_date)",
                type="temporal",
            ),
            y=alt.Y(
                field="transaction_amount",
                type="quantitative",
                aggregate="sum",
                title="Total Sales",
            ),
            color=alt.Color(
                "region",
                type="nominal",
                title="Regions",
                scale=alt.Scale(domain=regions, range=colors),
                legend=alt.Legend(
                    direction="vertical",
                    symbolType="triangle-left",
                    tickCount=4,
                ),
            ),
        )
    )
    .transform_filter(region_select)
    .properties(width=700, title="Monthly Sales")
)

sellers_monthly_pie = (
    (
        alt.Chart(sales_data)
        .mark_arc(innerRadius=10)
        .encode(
            theta=alt.Theta(
                field="transaction_amount",
                type="quantitative",
                aggregate="sum",
                title="Total Transactions",
            ),
            color=alt.Color(
                "month(transaction_date)",
                type="temporal",
                title="Month",
                scale=alt.Scale(domain=months, range=colors),
                legend=alt.Legend(
                    direction="vertical",
                    symbolType="triangle-left",
                    tickCount=12,
                ),
            ),
            facet=alt.Facet(
                field="seller",
                type="nominal",
                columns=8,
                title="Sellers",
            ),
            tooltip=alt.Tooltip(["sum(transaction_amount)", "month(transaction_date)"]),
        )
    )
    .transform_filter(region_select)
    .properties(width=150, height=150, title="Sellers transactions per month")
)

top_row = region_pie | region_summary
full_chart = top_row & sellers_monthly_pie


st.altair_chart(full_chart)

html_report = sse.StreamlitStaticExport()
html_report.export_altair_graph(id="test", graph=full_chart)