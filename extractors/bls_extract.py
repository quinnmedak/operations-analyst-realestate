import os
import time
from datetime import datetime
import requests
import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from dotenv import load_dotenv

load_dotenv()

# BLS CES series — monthly employment (thousands) for office-using industries
# Format: SMU + state_fips(2) + cbsa(5) + supersector(8) + data_type(2)
# 55000000 = Financial Activities | 60000000 = Professional & Business Services
METROS = {
    "New York":    ("36", "35620"),
    "Los Angeles": ("06", "31080"),
    "Boston":      ("25", "14460"),
    "Washington":  ("11", "47900"),
    "San Francisco": ("06", "41860"),
    "Chicago":     ("17", "16980"),
    "Dallas":      ("48", "19100"),
    "Seattle":     ("53", "42660"),
}

SUPERSECTORS = {
    "55000000": "Financial Activities",
    "60000000": "Professional & Business Services",
}

SERIES_MAP = []
for metro, (state, cbsa) in METROS.items():
    for super_code, label in SUPERSECTORS.items():
        sid = f"SMU{state}{cbsa}{super_code}01"
        SERIES_MAP.append({"series_id": sid, "metro": metro, "supersector": label})

BLS_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
START_YEAR = "2020"
END_YEAR = str(datetime.now().year)


def fetch_series(series_ids: list[str]) -> dict:
    payload = {
        "seriesid": series_ids,
        "startyear": START_YEAR,
        "endyear": END_YEAR,
    }
    r = requests.post(BLS_URL, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()


def parse_results(api_response: dict, series_metadata: list[dict]) -> list[dict]:
    meta_by_id = {m["series_id"]: m for m in series_metadata}
    rows = []
    for series in api_response["Results"]["series"]:
        meta = meta_by_id.get(series["seriesID"], {})
        for pt in series["data"]:
            rows.append({
                "series_id": series["seriesID"],
                "metro": meta.get("metro", ""),
                "supersector": meta.get("supersector", ""),
                "year": int(pt["year"]),
                "period": pt["period"],   # e.g. "M01"
                "period_name": pt["periodName"],
                "employment_thousands": float(pt["value"]) if pt["value"] != "-" else None,
            })
    return rows


def load_to_snowflake(df: pd.DataFrame):
    conn = snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        schema="RAW",
    )
    conn.cursor().execute("CREATE SCHEMA IF NOT EXISTS RAW")
    conn.cursor().execute("""
        CREATE TABLE IF NOT EXISTS RAW.BLS_METRO_EMPLOYMENT (
            SERIES_ID VARCHAR,
            METRO VARCHAR,
            SUPERSECTOR VARCHAR,
            YEAR INTEGER,
            PERIOD VARCHAR,
            PERIOD_NAME VARCHAR,
            EMPLOYMENT_THOUSANDS FLOAT,
            LOADED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.cursor().execute("TRUNCATE TABLE IF EXISTS RAW.BLS_METRO_EMPLOYMENT")
    df.columns = [c.upper() for c in df.columns]
    write_pandas(conn, df, "BLS_METRO_EMPLOYMENT", auto_create_table=False)
    conn.close()
    print(f"Loaded {len(df)} rows to Snowflake RAW.BLS_METRO_EMPLOYMENT")


if __name__ == "__main__":
    all_ids = [m["series_id"] for m in SERIES_MAP]
    print(f"Fetching {len(all_ids)} BLS CES series ({START_YEAR}–{END_YEAR})")

    # BLS unregistered API: max 10 series per request
    all_rows = []
    for i in range(0, len(all_ids), 10):
        batch_ids = all_ids[i : i + 10]
        batch_meta = SERIES_MAP[i : i + 10]
        print(f"  Batch {i // 10 + 1}: {[m['metro'] + '/' + m['supersector'][:3] for m in batch_meta]}")
        response = fetch_series(batch_ids)
        if response["status"] != "REQUEST_SUCCEEDED":
            print(f"  WARNING: {response.get('message', 'unknown error')}")
            continue
        rows = parse_results(response, batch_meta)
        all_rows.extend(rows)
        print(f"  Got {len(rows)} data points")
        time.sleep(1)

    df = pd.DataFrame(all_rows)
    print(f"\nTotal rows: {len(df)}")
    print(df.groupby(["metro", "supersector"])["employment_thousands"].count().to_string())

    print("\nLoading to Snowflake...")
    load_to_snowflake(df)
