import os
import pandas as pd
import yfinance as yf
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

TICKERS = {
    "BXP":  {"company": "Boston Properties",       "property_type": "Office",       "primary_market": "Boston/NYC/DC"},
    "SLG":  {"company": "SL Green Realty",          "property_type": "Office",       "primary_market": "New York City"},
    "VNO":  {"company": "Vornado Realty Trust",     "property_type": "Office",       "primary_market": "New York City"},
    "PLD":  {"company": "Prologis",                 "property_type": "Industrial",   "primary_market": "National"},
    "STAG": {"company": "STAG Industrial",          "property_type": "Industrial",   "primary_market": "National"},
    "SPG":  {"company": "Simon Property Group",     "property_type": "Retail",       "primary_market": "National"},
    "EQR":  {"company": "Equity Residential",       "property_type": "Multifamily",  "primary_market": "National"},
    "AVB":  {"company": "AvalonBay Communities",    "property_type": "Multifamily",  "primary_market": "National"},
    "ARE":  {"company": "Alexandria Real Estate",   "property_type": "Life Science", "primary_market": "National"},
}


def get_conn():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        schema="RAW",
    )


def safe_col(df, name):
    return df[name] if name in df.columns else pd.Series([None] * len(df), dtype=float)


def load_to_snowflake(df, table_name, create_sql):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("CREATE SCHEMA IF NOT EXISTS RAW")
    cur.execute(create_sql)
    cur.execute(f"TRUNCATE TABLE IF EXISTS RAW.{table_name}")
    df.columns = [c.upper() for c in df.columns]
    cols = list(df.columns)
    rows = [tuple(r) for r in df.itertuples(index=False)]
    ph = "(" + ",".join(["%s"] * len(cols)) + ")"
    col_list = ", ".join(cols)
    for i in range(0, len(rows), 5000):
        chunk = rows[i:i + 5000]
        vals = ", ".join([ph] * len(chunk))
        cur.execute(f"INSERT INTO RAW.{table_name} ({col_list}) VALUES {vals}", [v for row in chunk for v in row])
    conn.close()
    print(f"Loaded {len(df)} rows to RAW.{table_name}")


def extract_daily_prices():
    rows = []
    for ticker in TICKERS:
        print(f"  {ticker}: fetching price history")
        hist = yf.Ticker(ticker).history(period="max").reset_index()
        hist["ticker"] = ticker
        hist["date"] = pd.to_datetime(hist["Date"]).dt.tz_localize(None).dt.date
        for _, r in hist.iterrows():
            rows.append({
                "ticker":    r["ticker"],
                "date":      r["date"],
                "open":      r["Open"],
                "high":      r["High"],
                "low":       r["Low"],
                "close":     r["Close"],
                "volume":    r["Volume"],
                "dividends": r["Dividends"],
            })
    return pd.DataFrame(rows)


def extract_quarterly_financials():
    rows = []
    for ticker in TICKERS:
        print(f"  {ticker}: fetching quarterly financials")
        stock = yf.Ticker(ticker)
        try:
            fin = stock.quarterly_financials.T.reset_index().rename(columns={"index": "period_date"})
            bs  = stock.quarterly_balance_sheet.T.reset_index().rename(columns={"index": "period_date"})
            df  = fin.merge(bs, on="period_date", how="outer", suffixes=("_fin", "_bs"))
            df["ticker"]       = ticker
            df["period_date"]  = pd.to_datetime(df["period_date"]).dt.tz_localize(None).dt.date

            result = pd.DataFrame({
                "ticker":        df["ticker"],
                "period_date":   df["period_date"],
                "total_revenue": safe_col(df, "Total Revenue"),
                "net_income":    safe_col(df, "Net Income"),
                "ebitda":        safe_col(df, "EBITDA"),
                "operating_income": safe_col(df, "Operating Income"),
                "total_assets":  safe_col(df, "Total Assets"),
                "total_debt":    safe_col(df, "Total Debt"),
                "net_debt":      safe_col(df, "Net Debt"),
                "long_term_debt": safe_col(df, "Long Term Debt"),
            })
            rows.append(result)
        except Exception as e:
            print(f"  WARNING: {ticker} financials failed — {e}")

    return pd.concat(rows, ignore_index=True)


PRICES_DDL = """
    CREATE TABLE IF NOT EXISTS RAW.REIT_DAILY_PRICES (
        TICKER    VARCHAR,
        DATE      DATE,
        OPEN      FLOAT,
        HIGH      FLOAT,
        LOW       FLOAT,
        CLOSE     FLOAT,
        VOLUME    BIGINT,
        DIVIDENDS FLOAT,
        LOADED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
"""

FINANCIALS_DDL = """
    CREATE TABLE IF NOT EXISTS RAW.REIT_QUARTERLY_FINANCIALS (
        TICKER           VARCHAR,
        PERIOD_DATE      DATE,
        TOTAL_REVENUE    FLOAT,
        NET_INCOME       FLOAT,
        EBITDA           FLOAT,
        OPERATING_INCOME FLOAT,
        TOTAL_ASSETS     FLOAT,
        TOTAL_DEBT       FLOAT,
        NET_DEBT         FLOAT,
        LONG_TERM_DEBT   FLOAT,
        LOADED_AT        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
"""

if __name__ == "__main__":
    print("=== REIT Daily Prices ===")
    prices_df = extract_daily_prices()
    print(f"Total rows: {len(prices_df)}")
    load_to_snowflake(prices_df, "REIT_DAILY_PRICES", PRICES_DDL)

    print("\n=== REIT Quarterly Financials ===")
    fin_df = extract_quarterly_financials()
    print(f"Total rows: {len(fin_df)}")
    load_to_snowflake(fin_df, "REIT_QUARTERLY_FINANCIALS", FINANCIALS_DDL)
