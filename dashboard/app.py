import os
import pandas as pd
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
        margin: 36px 0 12px 0;
        font-size: 1.0rem;
        font-weight: 700;
        color: #111827;
        text-transform: uppercase;
        letter-spacing: 0.09em;
    }
    .sub-header {
        font-size: 0.70rem;
        font-weight: 700;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        margin: 20px 0 8px 0;
        padding-left: 4px;
        border-left: 2px solid #D1D5DB;
    }
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-top: 3px solid #E30613;
        border-radius: 3px;
        padding: 14px 12px;
        min-height: 128px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        gap: 2px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .kpi-label {
        font-size: 0.70rem;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.07em;
    }
    .kpi-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #111827;
        line-height: 1.05;
    }
    .kpi-value-red {
        font-size: 1.85rem;
        font-weight: 700;
        color: #B91C1C;
        line-height: 1.05;
    }
    .kpi-value-green {
        font-size: 1.85rem;
        font-weight: 700;
        color: #166534;
        line-height: 1.05;
    }
    .kpi-unit {
        font-size: 0.63rem;
        color: #9CA3AF;
        letter-spacing: 0.04em;
        min-height: 13px;
    }
    .kpi-delta {
        font-size: 0.68rem;
        color: #6B7280;
    }
    .kpi-delta-bad {
        font-size: 0.68rem;
        color: #B91C1C;
    }
    .kpi-delta-good {
        font-size: 0.68rem;
        color: #166534;
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
    start_year = st.slider("Start Year", 2008, 2024, 2020)
    st.divider()
    st.caption("Data: yfinance · FRED · BLS")

# ── Header ────────────────────────────────────────────────────────────────────

st.markdown("## LA Commercial Real Estate Analytics")
st.caption("Portfolio project — Quinn Medak · JLL Business Intelligence Analyst")

# ── KPI Row ───────────────────────────────────────────────────────────────────

st.markdown('<div class="section-header">Current State</div>', unsafe_allow_html=True)

# ── Financial Signals KPI Row ─────────────────────────────────────────────────

st.markdown('<div class="sub-header">Financial Signals</div>', unsafe_allow_html=True)

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

    delinquency_kpi = run_query("""
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
            <div class="kpi-value">{delinquency_kpi:.2f}%</div>
        </div>""", unsafe_allow_html=True)

    st.caption(f"REIT prices as of {latest_date} · Macro data quarterly avg (FRED)")

except Exception as e:
    st.error(f"Could not load KPI data: {e}")

# ── Space Market KPI Row + Submarket Breakdown ────────────────────────────────

st.markdown('<div class="sub-header">Space Market · Cushman & Wakefield MarketBeat</div>', unsafe_allow_html=True)

try:
    snapshot = run_query("""
        SELECT
            property_type,
            vacancy_rate,
            vacancy_rate_bps_yoy,
            ytd_net_absorption_sf,
            absorption_context
        FROM ANALYTICS.FACT_LA_MARKET_SNAPSHOT
        WHERE submarket = 'LA Total'
        ORDER BY property_type
    """)

    off = snapshot[snapshot["PROPERTY_TYPE"] == "Office"].iloc[0]
    ind = snapshot[snapshot["PROPERTY_TYPE"] == "Industrial"].iloc[0]

    def fmt_absorption(sf):
        sf = int(sf)
        sign = "+" if sf > 0 else ""
        if abs(sf) >= 1_000_000:
            return f"{sign}{sf / 1_000_000:.1f}M"
        return f"{sign}{sf / 1_000:.0f}K"

    def fmt_bps(bps):
        bps = int(bps)
        arrow = "▲" if bps > 0 else "▼"
        return f"{arrow} {abs(bps)} bps YoY"

    def absorption_css(sf):
        return "kpi-value-green" if int(sf) > 0 else "kpi-value-red"

    def bps_delta_css(bps):
        return "kpi-delta-bad" if int(bps) > 0 else "kpi-delta-good"

    def context_delta_css(sf):
        return "kpi-delta-bad" if int(sf) < 0 else "kpi-delta-good"

    sm1, sm2, sm3, sm4 = st.columns(4)

    with sm1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Office Vacancy</div>
            <div class="kpi-value">{off['VACANCY_RATE']:.1f}%</div>
            <div class="kpi-unit">&nbsp;</div>
            <div class="{bps_delta_css(off['VACANCY_RATE_BPS_YOY'])}">{fmt_bps(off['VACANCY_RATE_BPS_YOY'])}</div>
        </div>""", unsafe_allow_html=True)

    with sm2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Industrial Vacancy</div>
            <div class="kpi-value">{ind['VACANCY_RATE']:.1f}%</div>
            <div class="kpi-unit">&nbsp;</div>
            <div class="{bps_delta_css(ind['VACANCY_RATE_BPS_YOY'])}">{fmt_bps(ind['VACANCY_RATE_BPS_YOY'])}</div>
        </div>""", unsafe_allow_html=True)

    with sm3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Office YTD Absorption</div>
            <div class="{absorption_css(off['YTD_NET_ABSORPTION_SF'])}">{fmt_absorption(off['YTD_NET_ABSORPTION_SF'])}</div>
            <div class="kpi-unit">SF YTD</div>
            <div class="{context_delta_css(off['YTD_NET_ABSORPTION_SF'])}">{off['ABSORPTION_CONTEXT']}</div>
        </div>""", unsafe_allow_html=True)

    with sm4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Industrial YTD Absorption</div>
            <div class="{absorption_css(ind['YTD_NET_ABSORPTION_SF'])}">{fmt_absorption(ind['YTD_NET_ABSORPTION_SF'])}</div>
            <div class="kpi-unit">SF YTD</div>
            <div class="{context_delta_css(ind['YTD_NET_ABSORPTION_SF'])}">{ind['ABSORPTION_CONTEXT']}</div>
        </div>""", unsafe_allow_html=True)

except Exception as e:
    st.error(f"Could not load market snapshot: {e}")

try:
    submarkets_raw = run_query("""
        SELECT
            property_type,
            submarket,
            vacancy_rate,
            qtr_net_absorption_sf,
            ytd_net_absorption_sf,
            asking_rent_psf
        FROM ANALYTICS.FACT_LA_MARKET_SNAPSHOT
        WHERE submarket != 'LA Total'
        ORDER BY
            property_type,
            CASE WHEN submarket LIKE '%TOTAL%' THEN 1 ELSE 0 END,
            vacancy_rate DESC
    """)

    def fmt_sf(v):
        if pd.isna(v):
            return "—"
        v = int(v)
        sign = "+" if v > 0 else ""
        return f"{sign}{v:,}"

    with st.expander("Submarket breakdown — Office Q2 2025 / Industrial Q3 2025"):
        for prop_type, period_label in [("Office", "Q2 2025"), ("Industrial", "Q3 2025")]:
            df_sub = submarkets_raw[submarkets_raw["PROPERTY_TYPE"] == prop_type].copy()
            df_display = pd.DataFrame({
                "Submarket":              df_sub["SUBMARKET"].values,
                "Vacancy":                df_sub["VACANCY_RATE"].apply(lambda x: f"{x:.1f}%").values,
                "QTR Absorption (SF)":    df_sub["QTR_NET_ABSORPTION_SF"].apply(fmt_sf).values,
                "YTD Absorption (SF)":    df_sub["YTD_NET_ABSORPTION_SF"].apply(fmt_sf).values,
                "Asking Rent ($/SF/mo)":  df_sub["ASKING_RENT_PSF"].apply(lambda x: f"${x:.2f}").values,
            })
            st.markdown(f"**{prop_type} — {period_label}**")
            st.dataframe(df_display, hide_index=True, use_container_width=True)
        st.caption("Source: Cushman & Wakefield MarketBeat · ANALYTICS.FACT_LA_MARKET_SNAPSHOT")

except Exception as e:
    st.error(f"Could not load submarket data: {e}")

# ── Investor Signals ──────────────────────────────────────────────────────────

st.divider()

st.markdown('<div class="section-header">Market Performance</div>', unsafe_allow_html=True)

# ── Chart 1 — REIT Price Trend by Sector ─────────────────────────────────────

st.markdown("#### Office vs. Industrial REIT Price Performance")
st.caption("Industrial REITs up ~160% since 2018; office down ~36% — and the gap is still widening.")

SECTOR_COLORS = {
    "Office":       "#2C2C2C",
    "Industrial":   "#E30613",
    "Retail":       "#6366F1",
    "Multifamily":  "#F59E0B",
    "Life Science": "#10B981",
}

try:
    prices = run_query(f"""
        WITH daily_avg AS (
            SELECT
                f.date_day,
                r.property_type,
                AVG(f.close) AS avg_close
            FROM ANALYTICS.FACT_DAILY_PRICES f
            JOIN ANALYTICS.DIM_REIT r ON f.ticker = r.ticker
            WHERE YEAR(f.date_day) >= {start_year}
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

    fig.add_vrect(
        x0="2020-02-01", x1="2020-05-01",
        fillcolor="#F3F4F6", opacity=0.6, line_width=0,
        annotation_text="COVID", annotation_position="top left",
        annotation_font=dict(size=11, color="#6B7280"),
    )

    fig.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font_color="#2C2C2C",
        legend_title_text="Sector",
        height=380,
        margin=dict(t=20, b=20, l=0, r=0),
        xaxis=dict(showgrid=False, range=[prices["DATE_DAY"].min(), prices["DATE_DAY"].max()]),
        yaxis=dict(gridcolor="#F0F0F0"),
    )
    fig.update_traces(line_width=1.8)

    st.plotly_chart(fig, use_container_width=True)
    st.caption("Source: yfinance via Snowflake · FACT_DAILY_PRICES")

except Exception as e:
    st.error(f"Could not load price trend: {e}")

# ── Table A — Annual REIT Return % by Ticker ──────────────────────────────────

try:
    annual_returns = run_query("""
        WITH yearly AS (
            SELECT
                r.ticker,
                r.property_type,
                YEAR(f.date_day) AS yr,
                FIRST_VALUE(f.close) OVER (
                    PARTITION BY r.ticker, YEAR(f.date_day)
                    ORDER BY f.date_day
                ) AS yr_open,
                LAST_VALUE(f.close) OVER (
                    PARTITION BY r.ticker, YEAR(f.date_day)
                    ORDER BY f.date_day
                    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
                ) AS yr_close
            FROM ANALYTICS.FACT_DAILY_PRICES f
            JOIN ANALYTICS.DIM_REIT r ON f.ticker = r.ticker
            WHERE r.property_type IN ('Office', 'Industrial')
              AND YEAR(f.date_day) >= 2020
            QUALIFY ROW_NUMBER() OVER (
                PARTITION BY r.ticker, YEAR(f.date_day) ORDER BY f.date_day
            ) = 1
        )
        SELECT
            ticker,
            property_type,
            yr,
            ROUND((yr_close / yr_open - 1) * 100, 1) AS annual_return_pct
        FROM yearly
        ORDER BY property_type, ticker, yr
    """)

    pivot = annual_returns.pivot(index=["PROPERTY_TYPE", "TICKER"], columns="YR", values="ANNUAL_RETURN_PCT")
    pivot.index.names = ["Sector", "REIT"]
    pivot.columns = [str(c) for c in pivot.columns]

    def color_returns(val):
        if val is None or (isinstance(val, float) and val != val):
            return ""
        color = "#16a34a" if val > 0 else "#dc2626"
        return f"color: {color}; font-weight: 600"

    styled = pivot.style.applymap(color_returns).format("{:+.1f}%", na_rep="—")
    st.markdown("**Annual Return % by REIT — Office vs. Industrial**")
    st.dataframe(styled, use_container_width=True)
    st.caption("Source: yfinance via Snowflake · FACT_DAILY_PRICES · Year-open to year-close price return")

except Exception as e:
    st.error(f"Could not load annual return table: {e}")

# ── Chart 2 — Why Did Office Crash? ──────────────────────────────────────────

st.markdown('<div class="section-header">The Drivers</div>', unsafe_allow_html=True)

st.markdown("#### Fed Rate Hike Cycle and Office REIT Valuations")
st.caption("The 2022–2023 hike accelerated office decline. But rates have since eased — and office hasn't recovered. That persistence points to structural demand loss from hybrid work, not a rate cycle that will self-correct.")

try:
    rates = run_query(f"""
        SELECT
            TO_DATE(year::VARCHAR || '-' || LPAD((quarter * 3 - 2)::VARCHAR, 2, '0') || '-01') AS period_date,
            fedfunds
        FROM ANALYTICS.FACT_MACRO_QUARTERLY
        WHERE fedfunds IS NOT NULL
          AND year >= {start_year}
        ORDER BY year, quarter
    """)

    office_q = run_query(f"""
        WITH quarterly AS (
            SELECT
                DATE_TRUNC('quarter', f.date_day) AS period_date,
                AVG(f.close) AS avg_price
            FROM ANALYTICS.FACT_DAILY_PRICES f
            JOIN ANALYTICS.DIM_REIT r ON f.ticker = r.ticker
            WHERE r.property_type = 'Office'
              AND YEAR(f.date_day) >= {start_year}
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

    fig2.add_vline(x="2022-03-01", line_dash="dot", line_color="#6B7280", line_width=1.2)
    fig2.add_vline(x="2023-07-01", line_dash="dot", line_color="#6B7280", line_width=1.2)

    fig2.add_annotation(
        xref="x", yref="paper",
        x="2022-03-01", y=0.98,
        text="Fed begins hiking",
        showarrow=False, xanchor="right",
        font=dict(size=11, color="#6B7280"),
    )
    fig2.add_annotation(
        xref="x", yref="paper",
        x="2023-07-01", y=0.98,
        text="Rate peak: 5.33%",
        showarrow=False, xanchor="left",
        font=dict(size=11, color="#6B7280"),
    )
    fig2.add_annotation(
        xref="x", yref="paper",
        x="2024-09-01", y=0.12,
        text="Rates ease — office stays down",
        showarrow=True, arrowhead=2, arrowcolor="#6B7280",
        ax=0, ay=40,
        font=dict(size=11, color="#6B7280"),
        xanchor="center",
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

# ── Table B — Revenue YoY Change by Property Type ────────────────────────────

try:
    rev_yoy = run_query("""
        WITH annual AS (
            SELECT
                r.property_type,
                f.fiscal_year,
                SUM(f.revenue) AS total_revenue
            FROM ANALYTICS.FACT_QUARTERLY_FINANCIALS f
            JOIN ANALYTICS.DIM_REIT r ON f.ticker = r.ticker
            WHERE r.property_type IN ('Office', 'Industrial')
              AND f.fiscal_year >= 2019
            GROUP BY r.property_type, f.fiscal_year
        )
        SELECT
            property_type,
            fiscal_year,
            total_revenue,
            ROUND(
                (total_revenue / LAG(total_revenue) OVER (
                    PARTITION BY property_type ORDER BY fiscal_year
                ) - 1) * 100, 1
            ) AS revenue_yoy_pct
        FROM annual
        ORDER BY property_type, fiscal_year
    """)

    pivot_rev = rev_yoy.pivot(index="PROPERTY_TYPE", columns="FISCAL_YEAR", values="REVENUE_YOY_PCT")
    pivot_rev.index.name = "Sector"
    pivot_rev.columns = [str(c) for c in pivot_rev.columns]

    styled_rev = pivot_rev.style.applymap(color_returns).format("{:+.1f}%", na_rep="—")
    st.markdown("**Aggregate Revenue Growth YoY % — Office vs. Industrial**")
    st.dataframe(styled_rev, use_container_width=True)
    st.caption("Source: yfinance quarterly financials via Snowflake · FACT_QUARTERLY_FINANCIALS · Confirms whether price divergence reflects real fundamentals")

except Exception as e:
    st.error(f"Could not load revenue table: {e}")

# ── Chart 5 — Why Industrial Held Up ─────────────────────────────────────────

st.markdown("#### E-Commerce Share of Retail Sales vs. Industrial REIT Performance")
st.caption("E-commerce share of retail jumped from ~11% to ~16% post-COVID and held there — a permanent structural shift in how goods move. Industrial demand followed and absorbed a temporary spec oversupply correction.")

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
            marker_color="#9CA3AF",
            opacity=0.6,
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

    fig5.add_vrect(
        x0="2020-01-01", x1="2022-01-01",
        fillcolor="rgba(134, 239, 172, 0.15)", line_width=0,
    )

    fig5.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font_color="#2C2C2C",
        height=380,
        margin=dict(t=20, b=20, l=0, r=0),
        xaxis=dict(showgrid=False),
        legend=dict(orientation="h", yanchor="top", y=0.99, xanchor="left", x=0.01),
    )
    fig5.update_yaxes(title_text="Industrial REIT Price (Start = 100)", secondary_y=False, gridcolor="#F0F0F0")
    fig5.update_yaxes(title_text="E-Commerce % of Retail Sales", secondary_y=True, showgrid=False)

    st.plotly_chart(fig5, use_container_width=True)
    st.caption("Source: yfinance · FRED (ECOMPCTNSA) via Snowflake · FACT_DAILY_PRICES, FACT_MACRO_QUARTERLY")

except Exception as e:
    st.error(f"Could not load e-commerce chart: {e}")

# ── Chart 6 — CRE Loan Delinquency Rate (moved last — context/reassurance) ───

st.markdown("#### CRE Loan Delinquency Rate (2008–Present)")
st.caption("Delinquency is rising but remains less than one-quarter of the 2010 peak. The lending market is under pressure, not in crisis.")

try:
    delinquency_df = run_query(f"""
        SELECT
            TO_DATE(year::VARCHAR || '-' || LPAD((quarter * 3 - 2)::VARCHAR, 2, '0') || '-01') AS period_date,
            drcrelexfacbs AS delinquency_rate
        FROM ANALYTICS.FACT_MACRO_QUARTERLY
        WHERE drcrelexfacbs IS NOT NULL
          AND year >= {start_year}
        ORDER BY year, quarter
    """)

    fig6 = px.line(
        delinquency_df,
        x="PERIOD_DATE",
        y="DELINQUENCY_RATE",
        labels={"PERIOD_DATE": "", "DELINQUENCY_RATE": "Delinquency Rate (%)"},
    )
    fig6.update_traces(line_color="#E30613", line_width=1.8)

    gfc_peak_idx = delinquency_df["DELINQUENCY_RATE"].idxmax()
    gfc_peak_date = delinquency_df.loc[gfc_peak_idx, "PERIOD_DATE"]
    gfc_peak_val  = delinquency_df.loc[gfc_peak_idx, "DELINQUENCY_RATE"]

    fig6.add_annotation(
        x=gfc_peak_date, y=gfc_peak_val,
        text=f"GFC peak: {gfc_peak_val:.1f}%",
        showarrow=True, arrowhead=2, arrowcolor="#6B7280",
        font=dict(size=11, color="#6B7280"),
        ax=50, ay=-30,
    )

    current_val  = delinquency_df["DELINQUENCY_RATE"].iloc[-1]
    current_date = delinquency_df["PERIOD_DATE"].iloc[-1]

    fig6.add_annotation(
        x=current_date, y=current_val,
        text=f"Today: {current_val:.1f}%<br>Stressed, not systemic",
        showarrow=True, arrowhead=2, arrowcolor="#6B7280",
        font=dict(size=11, color="#6B7280"),
        ax=-80, ay=-40,
    )

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

# ── Outlook ───────────────────────────────────────────────────────────────────

st.divider()

st.markdown('<div class="section-header">Outlook</div>', unsafe_allow_html=True)
st.markdown("#### Office-Using Sector Employment: LA vs. Peer Cities")
st.caption("LA's office-using employment hasn't grown since 2020 — Dallas is up 20%. Markets that added workers recovered faster. When LA's line turns upward, leasing demand follows in 6–18 months.")

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
                  AND supersector IN ('Financial Activities', 'Professional & Business Services')
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
