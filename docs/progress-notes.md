# Project Progress Notes

## What We've Built So Far

### Step 1: Python Extractor (`extractors/fred_extract.py`)
- Calls the FRED API (Federal Reserve Economic Data) — free, no rate limits
- Loops over 6 economic series and collects all historical data points
- Stores results in a pandas DataFrame (5,183 rows x 3 columns)
- Loads data into Snowflake

### Step 2: Snowflake Raw Table

Why Snowflake: 
- Allows for querying better of the large data that is stored on PostGres Database
- Storage and computing are paid for separately (data stored in snowflake is not paid, only computing)

- Database: `OPERATIONS_ANALYST`
- Schema: `RAW`
- Table: `FRED_OBSERVATIONS`
- 5,183 rows, 3 columns: `SERIES_ID`, `DATE`, `VALUE`
- All 6 series land in one table, distinguished by `series_id`

---

## The 6 FRED Series (Your Data)

| Series ID | What it measures | Role in the story |
|---|---|---|
| `CPIAUCSL` | CPI inflation | Root cause — why rates spiked |
| `MORTGAGE30US` | 30-year mortgage rate | Financing cost driver |
| `CRLACBS` | CRE loans at banks | Lending activity |
| `DRCRELEXFACBS` | CRE loan delinquency rate | Market stress signal |
| `RRVRUSQ156N` | Rental vacancy rate | CRE market health outcome |
| `UNRATE` | Unemployment rate | Economic demand context |

**Diagnostic story:** Inflation spiked → Fed raised rates → mortgage rates surged → CRE lending tightened → delinquencies rose → vacancies increased

---

## Star Schema (coming in dbt)

**`fact_observations`** — 5,183 rows, one per series per date
| series_id | date | value |

**`dim_series`** — 6 rows, one per series
| series_id | series_name | units | frequency |

They connect on `series_id`.

---

## What's Next

- [ ] Set up dbt project
- [ ] Write staging model (`stg_fred_observations`) — cleans raw data
- [ ] Write mart models (`dim_series` + `fact_observations`) — star schema
- [ ] Set up GitHub Actions to automate the pipeline
- [ ] Add pipeline diagram to README
- [ ] Commit everything
