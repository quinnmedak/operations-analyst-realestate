import os
import streamlit as st
import snowflake.connector
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
        client_session_keep_alive=True,
    )

@st.cache_data(ttl=3600)
def run_query(sql: str):
    try:
        cur = get_conn().cursor()
        cur.execute(sql)
        return cur.fetch_pandas_all()
    except Exception as e:
        if "expired" in str(e).lower() or "08001" in str(e):
            get_conn.clear()
            cur = get_conn().cursor()
            cur.execute(sql)
            return cur.fetch_pandas_all()
        raise

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

# ── Chart 2 — Why Did Office Crash? ──────────────────────────────────────────


st.markdown("#### Rising rates crushed office valuations — as borrowing got expensive, investors priced buildings lower")

try:
    rates = run_query("""
        SELECT
            TO_DATE(year::VARCHAR || '-' || LPAD((quarter * 3 - 2)::VARCHAR, 2, '0') || '-01') AS period_date,
            fedfunds
        FROM ANALYTICS.FACT_MACRO_QUARTERLY
        WHERE fedfunds IS NOT NULL
          AND year >= 2019
        ORDER BY year, quarter
    """)

    office_q = run_query("""
        WITH quarterly AS (
            SELECT
                DATE_TRUNC('quarter', f.date_day) AS period_date,
                AVG(f.close) AS avg_price
            FROM ANALYTICS.FACT_DAILY_PRICES f
            JOIN ANALYTICS.DIM_REIT r ON f.ticker = r.ticker
            WHERE r.property_type = 'Office'
              AND YEAR(f.date_day) >= 2019
            GROUP BY 1
        )
        SELECT
            period_date,
            ROUND(
                avg_price / FIRST_VALUE(avg_price) OVER (ORDER BY period_date) * 100, 2
            ) AS indexed_price
        FROM quarterly
        ORDER BY period_date
    """)

    fig2 = make_subplots(specs=[[{"secondary_y": True}]])

    fig2.add_trace(
        go.Scatter(
            x=office_q["PERIOD_DATE"],
            y=office_q["INDEXED_PRICE"],
            name="Office REIT Price (Indexed)",
            line=dict(color="#2C2C2C", width=2),
        ),
        secondary_y=False,
    )
    fig2.add_trace(
        go.Scatter(
            x=rates["PERIOD_DATE"],
            y=rates["FEDFUNDS"],
            name="Fed Funds Rate (%)",
            line=dict(color="#E30613", width=2, dash="dash"),
        ),
        secondary_y=True,
    )

    fig2.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font_color="#2C2C2C",
        height=380,
        margin=dict(t=20, b=20, l=0, r=0),
        xaxis=dict(showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig2.update_yaxes(title_text="Office REIT Price (Start = 100)", secondary_y=False, gridcolor="#F0F0F0")
    fig2.update_yaxes(title_text="Fed Funds Rate (%)", secondary_y=True, showgrid=False)

    st.plotly_chart(fig2, use_container_width=True)
    st.caption("Source: yfinance · FRED (FEDFUNDS) via Snowflake · FACT_DAILY_PRICES, FACT_MACRO_QUARTERLY")

except Exception as e:
    st.error(f"Could not load rate hike chart: {e}")

# ── Chart 5 — Why Industrial Held Up ─────────────────────────────────────────

st.markdown("#### E-commerce permanently raised demand for warehouses — industrial never needed a recovery")

try:
    ecom = run_query("""
        SELECT
            TO_DATE(year::VARCHAR || '-' || LPAD((quarter * 3 - 2)::VARCHAR, 2, '0') || '-01') AS period_date,
            AVG(ecompctnsa) OVER (
                ORDER BY year, quarter
                ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
            ) AS ecom_4q_avg
        FROM ANALYTICS.FACT_MACRO_QUARTERLY
        WHERE ecompctnsa IS NOT NULL
          AND year >= 2015
        ORDER BY year, quarter
    """)

    industrial_q = run_query("""
        WITH quarterly AS (
            SELECT
                DATE_TRUNC('quarter', f.date_day) AS period_date,
                AVG(f.close) AS avg_price
            FROM ANALYTICS.FACT_DAILY_PRICES f
            JOIN ANALYTICS.DIM_REIT r ON f.ticker = r.ticker
            WHERE r.property_type = 'Industrial'
              AND YEAR(f.date_day) >= 2015
            GROUP BY 1
        )
        SELECT
            period_date,
            ROUND(
                avg_price / FIRST_VALUE(avg_price) OVER (ORDER BY period_date) * 100, 2
            ) AS indexed_price
        FROM quarterly
        ORDER BY period_date
    """)

    fig5 = make_subplots(specs=[[{"secondary_y": True}]])

    fig5.add_trace(
        go.Bar(
            x=ecom["PERIOD_DATE"],
            y=ecom["ECOM_4Q_AVG"],
            name="E-Commerce % of Retail (4Q avg)",
            marker_color="#D1D5DB",
            opacity=0.5,
        ),
        secondary_y=True,
    )
    fig5.add_trace(
        go.Scatter(
            x=industrial_q["PERIOD_DATE"],
            y=industrial_q["INDEXED_PRICE"],
            name="Industrial REIT Price (Indexed)",
            line=dict(color="#E30613", width=3),
            mode="lines",
        ),
        secondary_y=False,
    )

    fig5.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font_color="#2C2C2C",
        height=380,
        margin=dict(t=20, b=20, l=0, r=0),
        xaxis=dict(showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig5.update_yaxes(title_text="Industrial REIT Price (Start = 100)", secondary_y=False, gridcolor="#F0F0F0")
    fig5.update_yaxes(title_text="E-Commerce % of Retail Sales", secondary_y=True, showgrid=False)

    st.plotly_chart(fig5, use_container_width=True)
    st.caption("Source: yfinance · FRED (ECOMPCTNSA) via Snowflake · FACT_DAILY_PRICES, FACT_MACRO_QUARTERLY")

except Exception as e:
    st.error(f"Could not load e-commerce chart: {e}")

# ── Chart 4 — LA Employment vs. Peer Cities ───────────────────────────────────

st.markdown('<div class="section-header">Actionable — What Comes Next</div>', unsafe_allow_html=True)
st.markdown("#### Is LA's office demand recovering? Employment in office-using sectors is the earliest signal.")

try:
    metros_df = run_query("""
        SELECT DISTINCT metro
        FROM ANALYTICS.FACT_METRO_EMPLOYMENT
        ORDER BY metro
    """)
    all_metros = metros_df["METRO"].tolist()

    default_metros = [m for m in all_metros if any(
        x in m.upper() for x in ["LOS ANGELES", "NEW YORK", "CHICAGO", "DALLAS", "HOUSTON"]
    )]
    if not default_metros:
        default_metros = all_metros[:4]

    selected_metros = st.multiselect(
        "Select metros to compare",
        options=all_metros,
        default=default_metros,
        key="chart4_metros",
    )

    if selected_metros:
        metros_sql = ", ".join(f"'{m}'" for m in selected_metros)
        employment = run_query(f"""
            WITH monthly AS (
                SELECT
                    date_day,
                    metro,
                    SUM(employment_thousands) AS employment_thousands
                FROM ANALYTICS.FACT_METRO_EMPLOYMENT
                WHERE metro IN ({metros_sql})
                GROUP BY date_day, metro
            )
            SELECT
                date_day,
                metro,
                ROUND(
                    employment_thousands / FIRST_VALUE(employment_thousands) OVER (
                        PARTITION BY metro
                        ORDER BY date_day
                    ) * 100, 2
                ) AS indexed_employment
            FROM monthly
            ORDER BY date_day
        """)

        other_colors = ["#2C2C2C", "#6B7280", "#D1D5DB", "#9CA3AF"]
        color_map = {}
        other_idx = 0
        for m in selected_metros:
            if "los angeles" in m.lower():
                color_map[m] = "#E30613"
            else:
                color_map[m] = other_colors[other_idx % len(other_colors)]
                other_idx += 1

        fig4 = px.line(
            employment,
            x="DATE_DAY",
            y="INDEXED_EMPLOYMENT",
            color="METRO",
            color_discrete_map=color_map,
            labels={
                "DATE_DAY": "",
                "INDEXED_EMPLOYMENT": "Employment Index (Start = 100)",
                "METRO": "Metro",
            },
        )
        fig4.update_layout(
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            font_color="#2C2C2C",
            height=400,
            margin=dict(t=20, b=20, l=0, r=0),
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor="#F0F0F0"),
            legend_title_text="Metro",
        )
        fig4.update_traces(line_width=1.8)
        st.plotly_chart(fig4, use_container_width=True)
        st.caption("Source: BLS Metro Employment via Snowflake · FACT_METRO_EMPLOYMENT")

except Exception as e:
    st.error(f"Could not load employment chart: {e}")
