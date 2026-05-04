import os
import re
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import requests
import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

load_dotenv()

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
OUT_DIR = Path("knowledge/raw")

QUERIES = [
    "JLL US industrial market dynamics 2025 2026 warehouse logistics",
    "CBRE multifamily apartment market outlook 2026 rent vacancy",
    "JLL life science real estate market outlook 2025",
    "CBRE US retail market outlook 2026",
]


def current_quarter():
    now = datetime.now()
    return now.year, (now.month - 1) // 3 + 1


def get_direct_urls():
    year, q = current_quarter()
    q_str = f"q{q}"
    return [
        # C&W landing page — always lists the latest quarterly reports
        "https://www.cushmanwakefield.com/en/united-states/insights/us-marketbeats/greater-los-angeles-marketbeats",
        # Current-quarter C&W LA Office and Industrial PDFs
        f"https://assets.cushmanwakefield.com/-/media/cw/marketbeat-pdfs/{year}/{q_str}/us-reports/office/los-angeles_office_marketbeat-{q_str}-{year}.pdf",
        f"https://assets.cushmanwakefield.com/-/media/cw/marketbeat-pdfs/{year}/{q_str}/us-reports/industrial/la_americas_marketbeat_industrial_{q_str}{year}.pdf",
    ]


def scrape_url(url: str):
    resp = requests.post(
        "https://api.firecrawl.dev/v1/scrape",
        headers={"Authorization": f"Bearer {FIRECRAWL_API_KEY}"},
        json={"url": url, "formats": ["markdown"]},
    )
    if resp.status_code != 200:
        print(f"  ERROR {resp.status_code} scraping {url}: {resp.text[:200]}")
        return None
    data = resp.json().get("data", {})
    return {
        "title": data.get("metadata", {}).get("title", url),
        "url": url,
        "markdown": data.get("markdown", ""),
        "source_query": "direct",
    }


def slugify_url(url: str) -> str:
    slug = re.sub(r"^https?://", "", url)
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", slug)
    return slug.strip("-")


def save_results(results):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    run_ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    for r in results:
        markdown = r.get("markdown") or ""
        if not markdown:
            print(f"  WARNING: no markdown for {r['url']}, skipping")
            continue
        slug = slugify_url(r["url"])
        filepath = OUT_DIR / f"{run_ts}_{slug}.md"
        content = (
            f"---\n"
            f"title: {r['title']}\n"
            f"url: {r['url']}\n"
            f"scraped_at: {datetime.now().isoformat(timespec='seconds')}\n"
            f"---\n\n"
            f"{markdown}\n"
        )
        filepath.write_text(content, encoding="utf-8")
        print(f"  Saved: {filepath}")


def load_to_snowflake(df):
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
        CREATE TABLE IF NOT EXISTS RAW.SCRAPE_ARTICLES (
            TITLE VARCHAR,
            URL VARCHAR,
            SCRAPED_AT TIMESTAMP,
            BODY TEXT,
            SOURCE_QUERY VARCHAR,
            LOADED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    df.columns = [c.upper() for c in df.columns]
    write_pandas(conn, df, "SCRAPE_ARTICLES", auto_create_table=False)
    conn.close()
    print(f"Loaded {len(df)} rows to Snowflake")


if __name__ == "__main__":
    api_url = "https://api.firecrawl.dev/v2/search"
    headers = {"Authorization": f"Bearer {FIRECRAWL_API_KEY}"}

    all_results = []

    # Direct URL scrapes: C&W landing page + current-quarter MarketBeat PDFs
    print("\nScraping direct URLs...")
    for url in get_direct_urls():
        print(f"\n  Scraping: {url}")
        result = scrape_url(url)
        if result:
            print(f"  - {result['title']}")
            print(f"    markdown length: {len(result.get('markdown') or '')} chars")
            all_results.append(result)
        time.sleep(1)

    # Search queries: broader knowledge base content
    for query in QUERIES:
        print(f"\nSearching: {query}")
        payload = {
            "query": query,
            "limit": 2,
            "scrapeOptions": {"formats": ["markdown"]},
        }
        response = requests.post(api_url, headers=headers, json=payload)
        print(f"  status {response.status_code}")

        if response.status_code != 200:
            print(f"  ERROR - HTTP {response.status_code}: {response.text[:200]}")
            continue

        data = response.json()
        results = data["data"]["web"]
        print(f"  Firecrawl returned {len(results)} results")

        for r in results:
            print(f"  - {r['title']}")
            print(f"    {r['url']}")
            print(f"    markdown length: {len(r.get('markdown') or '')} chars")
            r["source_query"] = query

        all_results.extend(results)
        time.sleep(1)

    save_results(all_results)

    rows = [
        {
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "scraped_at": datetime.now().isoformat(),
            "body": r.get("markdown") or "",
            "source_query": r.get("source_query", ""),
        }
        for r in all_results
        if r.get("markdown")
    ]

    if rows:
        df = pd.DataFrame(rows)
        print(f"\nLoading {len(df)} articles to Snowflake...")
        print(df[["title", "url"]].to_string())
        load_to_snowflake(df)
