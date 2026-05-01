import os
import streamlit as st
import snowflake.connector
import plotly.express as px
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

st.set_page_config(
    page_title="LA CRE Analytics",
    layout="wide",
    page_icon="🏢",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    .section-header {
        border-left: 4px solid #E30613;
        padding-left: 12px;
        margin: 32px 0 16px 0;
        font-size: 1.1rem;
        font-weight: 600;
        color: #2C2C2C;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .kpi-label {
        font-size: 0.78rem;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 1.9rem;
        font-weight: 700;
        color: #2C2C2C;
        line-height: 1.1;
    }
    .kpi-card {
        background: #F8F8F8;
        border-radius: 6px;
        padding: 20px 24px;
    }
</style>
""", unsafe_allow_html=True)

# ── Connection ────────────────────────────────────────────────────────────────

@st.cache_resource
def get_conn():
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        schema="ANALYTICS",
    )

@st.cache_data(ttl=3600)
def run_query(sql: str):
    cur = get_conn().cursor()
    cur.execute(sql)
    return cur.fetch_pandas_all()

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### LA CRE Analytics")
    st.caption("JLL Business Intelligence · Commercial Real Estate")
    st.divider()
    start_year = st.slider("Start Year", 2019, 2024, 2020)
    st.divider()
    st.caption("Data: yfinance · FRED · BLS")

# ── Header ────────────────────────────────────────────────────────────────────

st.markdown("## LA Commercial Real Estate Analytics")
st.caption("Portfolio project — Quinn Medak · JLL Business Intelligence Analyst")

# ── KPI Row ───────────────────────────────────────────────────────────────────

st.markdown('<div class="section-header">Current State</div>', unsafe_allow_html=True)

try:
    latest_date = run_query("""
        SELECT MAX(date_day) AS latest FROM ANALYTICS.FACT_DAILY_PRICES
    """)["LATEST"].iloc[0]

    office_price = run_query(f"""
        SELECT ROUND(AVG(f.close), 2) AS val
        FROM ANALYTICS.FACT_DAILY_PRICES f
        JOIN ANALYTICS.DIM_REIT r ON f.ticker = r.ticker
        WHERE r.property_type = 'Office'
          AND f.date_day = '{latest_date}'
    """)["VAL"].iloc[0]

    industrial_price = run_query(f"""
        SELECT ROUND(AVG(f.close), 2) AS val
        FROM ANALYTICS.FACT_DAILY_PRICES f
        JOIN ANALYTICS.DIM_REIT r ON f.ticker = r.ticker
        WHERE r.property_type = 'Industrial'
          AND f.date_day = '{latest_date}'
    """)["VAL"].iloc[0]

    fedfunds = run_query("""
        SELECT fedfunds
        FROM ANALYTICS.FACT_MACRO_QUARTERLY
        WHERE fedfunds IS NOT NULL
        ORDER BY year DESC, quarter DESC
        LIMIT 1
    """)["FEDFUNDS"].iloc[0]

    delinquency = run_query("""
        SELECT drcrelexfacbs
        FROM ANALYTICS.FACT_MACRO_QUARTERLY
        WHERE drcrelexfacbs IS NOT NULL
        ORDER BY year DESC, quarter DESC
        LIMIT 1
    """)["DRCRELEXFACBS"].iloc[0]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Office REIT Avg Price</div>
            <div class="kpi-value">${office_price:.2f}</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Industrial REIT Avg Price</div>
            <div class="kpi-value">${industrial_price:.2f}</div>
        </div>""", unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Fed Funds Rate</div>
            <div class="kpi-value">{fedfunds:.2f}%</div>
        </div>""", unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">CRE Loan Delinquency</div>
            <div class="kpi-value">{delinquency:.2f}%</div>
        </div>""", unsafe_allow_html=True)

    st.caption(f"REIT prices as of {latest_date} · Macro data quarterly avg (FRED)")

except Exception as e:
    st.error(f"Could not load KPI data: {e}")

# ── Chart 1 — REIT Price Trend by Sector ─────────────────────────────────────

st.markdown('<div class="section-header">Descriptive — What Is Happening</div>', unsafe_allow_html=True)
st.markdown("#### How has investor confidence in office vs. industrial shifted over five years?")

SECTOR_COLORS = {
    "Office":       "#2C2C2C",
    "Industrial":   "#E30613",
    "Retail":       "#6366F1",
    "Multifamily":  "#F59E0B",
    "Life Science": "#10B981",
}

try:
    prices = run_query("""
        WITH daily_avg AS (
            SELECT
                f.date_day,
                r.property_type,
                AVG(f.close) AS avg_close
            FROM ANALYTICS.FACT_DAILY_PRICES f
            JOIN ANALYTICS.DIM_REIT r ON f.ticker = r.ticker
            WHERE YEAR(f.date_day) >= 2019
              AND r.property_type IN ('Office', 'Industrial')
            GROUP BY f.date_day, r.property_type
        )
        SELECT
            date_day,
            property_type,
            ROUND(
                avg_close / FIRST_VALUE(avg_close) OVER (
                    PARTITION BY property_type
                    ORDER BY date_day
                ) * 100, 2
            ) AS indexed_price
        FROM daily_avg
        ORDER BY date_day
    """)

    fig = px.line(
        prices,
        x="DATE_DAY",
        y="INDEXED_PRICE",
        color="PROPERTY_TYPE",
        color_discrete_map=SECTOR_COLORS,
        labels={
            "DATE_DAY": "",
            "INDEXED_PRICE": "Indexed Price (Start = 100)",
            "PROPERTY_TYPE": "Sector",
        },
    )
    fig.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font_color="#2C2C2C",
        legend_title_text="Sector",
        height=380,
        margin=dict(t=20, b=20, l=0, r=0),
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor="#F0F0F0"),
    )
    fig.update_traces(line_width=1.8)

    st.plotly_chart(fig, use_container_width=True)
    st.caption("Source: yfinance via Snowflake · FACT_DAILY_PRICES")

except Exception as e:
    st.error(f"Could not load price trend: {e}")

# ── Chart 6 — CRE Loan Delinquency Rate ──────────────────────────────────────

st.markdown("#### How stressed is the CRE lending market?")

try:
    delinquency = run_query("""
        SELECT
            TO_DATE(year::VARCHAR || '-' || LPAD((quarter * 3 - 2)::VARCHAR, 2, '0') || '-01') AS period_date,
            drcrelexfacbs AS delinquency_rate
        FROM ANALYTICS.FACT_MACRO_QUARTERLY
        WHERE drcrelexfacbs IS NOT NULL
          AND year >= 2008
        ORDER BY year, quarter
    """)

    fig6 = px.line(
        delinquency,
        x="PERIOD_DATE",
        y="DELINQUENCY_RATE",
        labels={"PERIOD_DATE": "", "DELINQUENCY_RATE": "Delinquency Rate (%)"},
    )
    fig6.update_traces(line_color="#E30613", line_width=1.8)
    fig6.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font_color="#2C2C2C",
        height=360,
        margin=dict(t=20, b=20, l=0, r=0),
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor="#F0F0F0"),
    )

    st.plotly_chart(fig6, use_container_width=True)
    st.caption("Source: FRED (DRCRELEXFACBS) via Snowflake · FACT_MACRO_QUARTERLY · 2008–present")

except Exception as e:
    st.error(f"Could not load delinquency data: {e}")
