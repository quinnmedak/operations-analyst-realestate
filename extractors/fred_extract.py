import os
import time
import requests
import json
from dotenv import load_dotenv

import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas   

import pandas as pd                                                                                                                          
                  
                                                                                                                                                                
load_dotenv()   

api_key = os.getenv("FRED_API_KEY")                                                                                                                           
api_url = "https://api.stlouisfed.org/fred/series/observations"
series_ids = [
    "MORTGAGE30US",    # 30-year fixed mortgage rate — weekly
    "DGS10",           # 10-Year Treasury yield — daily (cap rate benchmark)
    "FEDFUNDS",        # Federal Funds Rate — monthly (policy rate)
    "T10Y2Y",          # 10yr minus 2yr Treasury spread — daily (yield curve)
    "UNRATE",          # Unemployment rate — monthly (office demand driver)
    "PAYEMS",          # Total nonfarm payrolls — monthly (job growth)
    "ECOMPCTNSA",      # E-commerce as % of retail sales — quarterly (industrial driver)
    "DRCRELEXFACBS",   # CRE loan delinquency rate — quarterly (sector financial stress)
    "CREACBW027SBOG",  # CRE loans at commercial banks — weekly (credit availability)
]
                                                                                                                                               
results = []

def load_to_snowflake(df):                                                                                                                   
    conn = snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),                                                                                                    
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        database=os.getenv("SNOWFLAKE_DATABASE"),                                                                                            
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        schema="RAW"                                                                                                                         
    )
    conn.cursor().execute("CREATE SCHEMA IF NOT EXISTS RAW")
    conn.cursor().execute("""
        CREATE TABLE IF NOT EXISTS RAW.FRED_OBSERVATIONS (
            SERIES_ID VARCHAR,
            DATE VARCHAR,
            VALUE VARCHAR,
            LOADED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.cursor().execute("TRUNCATE TABLE IF EXISTS RAW.FRED_OBSERVATIONS")
    df.columns = [c.upper() for c in df.columns]
    write_pandas(conn, df, "FRED_OBSERVATIONS", auto_create_table=False)                                                                     
    conn.close()
    print(f"Loaded {len(df)} rows to Snowflake")
                                                                                                                                               
for series_id in series_ids:
      params = {                                                                                                                               
          "api_key": api_key,
          "series_id": series_id,                                                                                                              
          "file_type": "json"
      }                                                                                                                                        
      response = requests.get(api_url, params=params)
      print(f"{series_id}: status {response.status_code}")

      if response.status_code != 200:
          print(f"{series_id}: ERROR - HTTP {response.status_code}")
          continue

      data = response.json()

      if "observations" not in data:
          print(f"{series_id}: ERROR - {data}")
          continue                                                                                                                             
   
      for obs in data["observations"]:                                                                                                         
          results.append({
              "series_id": series_id,
              "date": obs["date"],                                                                                                             
              "value": obs["value"]
          })                                                                                                                                   
                  
      print(f"{series_id}: {len(data['observations'])} rows")
      time.sleep(0.5)

df = pd.DataFrame(results)                                                                                                                   
print(df)
print(df.shape)     

load_to_snowflake(df)