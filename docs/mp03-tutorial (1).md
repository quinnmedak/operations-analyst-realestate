# Mini-Project 03: API Data Collection Tutorial

This tutorial covers the in-class session for Mini-Project 03. Part 01 uses the slides. Parts 02-04 are hands-on. If you fall behind during class, use this tutorial to catch up. Every command and prompt is written out so you can follow along on your own.

## Table of Contents

| Step | Topic | What You Will Do |
|------|-------|-----------------|yes
| 00 | [Create repo and start Claude Code](#step-00-create-github-repo-and-start-claude-code) | Set up the project repo, start Claude Code |
| 01 | [Get your API key](#step-01-get-your-api-key) | Create a free weatherapi.com account and copy your key |
| 02 | [Set up your Python file](#step-02-set-up-your-python-file) | Create the script, add imports and API key |
| 03 | [Make your first API call](#step-03-make-your-first-api-call) | Build a request with URL, params, and requests.get() |
| 04 | [Parse the JSON response](#step-04-parse-the-json-response) | Extract nested data from the response |
| 05 | [Loop over multiple cities](#step-05-loop-over-multiple-cities) | Collect weather for a list of zip codes |
| 06 | [Extend the forecast](#step-06-extend-the-forecast) | Get multi-day forecasts with Claude Code |
| 07 | [Save to CSV](#step-07-save-to-csv) | Build a DataFrame and export |wait 
| 08 | [Find APIs for your project](#step-08-find-apis-for-your-project) | Use Claude Code to discover APIs for your domain |
| 09 | [Commit and push](#step-09-commit-and-push) | Push your work to GitHub |

---

## Part 01: Setup

### Step 00: Create GitHub Repo and Start Claude Code

Same workflow as MP02: create the repo on GitHub first, clone it into Cursor, then start building.

**What to do:**

1. Go to [github.com/new](https://github.com/new) and create a new repository:
   - Name it `weather-api-pipeline`
   - Set visibility to **Public**
   - Under **Add .gitignore**, select **Python** from the dropdown
   - Leave everything else as default
   - Click **Create repository**

2. On your new repository's GitHub page, click the green **Code** button, make sure **HTTPS** is selected, and copy the URL.

3. Clone the repo into Cursor. Open a new Cursor window and click **Clone repo** on the welcome screen. Paste the URL you copied.

   When Cursor asks where to save it, navigate to your `isba-4715` folder. Open the cloned folder when prompted.

   Your folder structure should now look like:
   ```
   ~/isba-4715/
   ├── campus-bites-pipeline/     <-- MP01
   ├── basket-craft-pipeline/     <-- MP02
   └── weather-api-pipeline/      <-- MP03 (this project)
   ```

4. Open a terminal in Cursor (`` Ctrl+` `` or **Terminal > New Terminal**).

5. Start Claude Code:
   ```bash
   claude
   ```

6. Ask Claude Code to set up a virtual environment and install dependencies:

   ```
   Set up a Python virtual environment for this project and install
   requests and pandas. Activate the virtual environment.
   ```

   Claude Code will create a `venv/` folder, install the packages, and activate the environment in its shell session. It will tell you something like: "The virtual environment is set up at ./venv with requests and pandas installed."

   Claude Code runs commands in its own shell, so it can use the venv for running your scripts. If you ever need to run Python directly in your own terminal (outside Claude Code), activate the venv first:
   - **Mac:** `source venv/bin/activate`
   - **Windows:** `venv\Scripts\activate`

   The Python `.gitignore` you selected when creating the repo already ignores the `venv/` folder, so it will not be committed to GitHub.

**Checkpoint:** Your repo is cloned, Claude Code is running, and Claude Code has confirmed the virtual environment is set up with `requests` and `pandas` installed.

---

## Before You Start: Writing Python in Cursor

This is our first time writing Python from scratch (instead of running a Colab notebook). Here is the workflow you will use for the rest of the course:

1. **Create a `.py` file** in Cursor (like `weather.py`)
2. **Write or paste code** into the file
3. **Save the file** (`Cmd+S` on Mac, `Ctrl+S` on Windows)
4. **Run it in the terminal** by typing `python weather.py` and pressing Enter
5. **Read the output** in the terminal, then go back to the file and add more code

You will repeat this loop many times today: edit the file, save, run, check the output. If you forget to save before running, you will see old output, so save every time.

---

## Part 02: Weather API by Hand

### Step 01: Get Your API Key

Every API needs to know who is calling it. An API key works like a library card: you sign up once, get a key, and include it with every request.

**What to do:**

1. Go to [weatherapi.com](https://www.weatherapi.com/) and click **Sign Up** (free tier).
2. After signing up, go to your dashboard. Your API key is displayed on the main page.
3. Copy the key. You will paste it into your Python script in Step 02.
4. Open the API documentation in a new tab: [WeatherAPI Swagger Docs](https://app.swaggerhub.com/apis-docs/WeatherAPI.com/WeatherAPI/1.0.2)

   Browse the docs before writing any code. Look for:
   - **Realtime Weather API** (`/current.json`) — this is the endpoint we will use first
   - **Forecast API** (`/forecast.json`) — we will switch to this in Step 06
   - The **parameters** each endpoint accepts (`key`, `q`, `days`)
   - The **response structure** — what JSON comes back

   Reading API docs is a skill you will use for every API in your career. The docs tell you what endpoints exist, what parameters they accept, and what the response looks like. When code from the internet or from Claude Code does not work, the docs are the first place to check.

**Checkpoint:** You have an API key copied to your clipboard and the API docs open in a browser tab.

---

### Step 02: Set Up Your Python File

You need `requests` to make HTTP calls and `json` to work with the response data. These two libraries are standard for API work in Python.

**What to do:**

1. In Cursor, create a new file: **File > New File** (or `Cmd+N` / `Ctrl+N`). Save it immediately as `weather.py` (`Cmd+S` / `Ctrl+S`). Make sure it ends in `.py` — that tells Cursor to treat it as Python and give you syntax highlighting.

2. **Copy** these imports into the file (no need to type these by hand):

   ```python
   import requests
   import json
   ```

3. **Type this line by hand** — replace `YOUR_API_KEY_HERE` with the key you copied in Step 01:

   ```python
   api_key = "YOUR_API_KEY_HERE"
   ```

4. **Save the file** (`Cmd+S` / `Ctrl+S`). Get in the habit of saving after every change.

**Why type it:** Storing a key in a variable and referencing the variable (instead of pasting the raw key everywhere) is a habit that prevents bugs and security mistakes. You will do this for every API you work with.

**A note on security:** Hardcoding an API key directly in a `.py` file is fine for learning today, but it is not safe for real projects. If you push this file to GitHub, anyone can see your key. In your portfolio project, you will store keys in a `.env` file and load them with `python-dotenv` so they never end up in your code. The Spotify tutorial covers this pattern.

**Checkpoint:** You have a `weather.py` file with imports and your API key variable. The file is saved and you can see it in Cursor's file explorer on the left.

---

### Step 03: Make Your First API Call

A REST API call has three parts: the URL (where to send it), the parameters (what you are asking for), and your API key (so the server knows who you are). You pass all three to `requests.get()` and get back a response.

**What to do:**

1. **Type these lines by hand** below your API key:

   ```python
   api_url = "https://api.weatherapi.com/v1/current.json"

   params = {
       "key": api_key,
       "q": "90045"
   }

   response = requests.get(api_url, params=params)
   ```

   Each line has a specific job:
   - `api_url` — the endpoint. This URL returns current weather conditions.
   - `params` — a dictionary of query parameters. `"key"` is your API key, `"q"` is the location (a zip code).
   - `requests.get()` — sends an HTTP GET request and stores the response.

2. **Type this line** to check if the call worked:

   ```python
   print(response.status_code)
   ```

3. **Save the file** (`Cmd+S` / `Ctrl+S`), then run the script. Open a second terminal so Claude Code keeps running in the first one: click the **+** icon in the terminal panel, or go to **Terminal > New Terminal**. In the new terminal, type:

   ```bash
   python weather.py
   ```

   and press **Enter**. The terminal runs your script and prints the output directly below the command.

   You should see `200`. That means success. Any other number means something went wrong: `401` is unauthorized (check your key), `403` is forbidden (wrong permissions), `404` is not found (check the URL).

   From now on, "run the script" means: save the file, go to the terminal, type `python weather.py`, press Enter.

**Why status codes matter:** These codes are the same across every API you will ever use. Learning them now means you will know exactly what broke and where to look.

**Checkpoint:** Your script prints `200`.

---

### Step 04: Parse the JSON Response

The API responded with JSON: a nested structure of dictionaries and lists. You need to convert it to a Python dictionary, then navigate the nesting to pull out the values you want.

**What to do:**

1. **Comment out** the `print(response.status_code)` line by adding a `#` in front of it. Then **type these lines below it by hand:**

   ```python
   data = response.json()

   print(json.dumps(data, indent=2))
   ```

   `json.dumps()` converts the Python dictionary back into a JSON-formatted string. The `indent=2` parameter adds line breaks and spacing so the output is readable instead of a wall of text.

2. Run the script again. You should see formatted JSON with clear nesting in your terminal. Look at the structure: which keys are inside which objects, where the temperature lives, where the condition text is.

3. Now navigate the nesting. **Type these lines** to drill into the structure:

   ```python
   print(data["location"]["name"])
   print(data["location"]["region"])
   print(data["current"]["temp_f"])
   print(data["current"]["condition"]["text"])
   ```

4. Run the script. You should see something like:

   ```
   Los Angeles
   California
   72.0
   Sunny
   ```

**Why this matters:** JSON nesting is the same problem regardless of the API. The weather response has `data["current"]["temp_f"]`. A Spotify track has `data["album"]["artists"][0]["name"]`. Different keys, same idea. Once you can read one, you can read any of them.

**Checkpoint:** Your script prints the city name, region, temperature, and weather condition.

---

## Part 03: Loops and Bulk Collection

You now know how to call an API and parse the response. The next skill is getting **enough** data. Everything in Part 03 builds toward the volume your project will need.

### Step 05: Loop Over Multiple Cities

You just got weather for one zip code. That is one row. Your project needs hundreds. A loop handles the repetition so you are not writing a separate request for every location.

**What to do:**

1. **Type this by hand** — start a new section in your file (you can comment out or delete the previous print statements):

   ```python
   zip_codes = ["90045", "10001", "60601", "98101", "33101"]

   for zip_code in zip_codes:
       params = {
           "key": api_key,
           "q": zip_code
       }
       response = requests.get(api_url, params=params)
       data = response.json()

       city = data["location"]["name"]
       temp = data["current"]["temp_f"]
       condition = data["current"]["condition"]["text"]

       print(f"{city}: {temp}°F, {condition}")
   ```

2. Run the script. You should see weather for all five cities.

3. That loop works, but five cities is not enough data for a real project. Now let Claude Code scale it up. Open Claude Code and type:

   ```
   Look at my weather.py script. I'm looping over 5 zip codes to get
   weather data. I want to:
   1. Add 15 more zip codes for major US cities
   2. Store all results in a list of dictionaries
   3. Add a 1-second delay between calls to avoid rate limiting
   ```

4. Review what Claude Code generates. You should see:
   - A longer list of zip codes
   - A `results = []` list that collects dictionaries
   - `import time` and `time.sleep(1)` between calls

**Why this matters:** The loop you just wrote is the collection pattern for your project. You will swap in different parameters (dates, IDs, page numbers), but the structure is the same. The API changes; the loop does not.

**Checkpoint:** Your script collects weather data for 20 cities and stores it in a list of dictionaries.

---

### Step 06: Extend the Forecast

So far you have one data point per city: current conditions. The forecast endpoint returns multiple days in a single call, which means you can get time-series data without sending more requests.

**What to do:**

1. Before asking Claude Code, check the docs yourself. Go back to the [WeatherAPI Swagger Docs](https://app.swaggerhub.com/apis-docs/WeatherAPI.com/WeatherAPI/1.0.2) and find the **Forecast API** section. Look at what parameters it accepts and what the response JSON looks like. Specifically, find the `days` parameter and the `forecastday` array in the response. This is the habit: check the docs first, then write (or ask for) the code.

2. Ask Claude Code to extend your script:

   ```
   Update my weather script to use the forecast endpoint instead of
   current weather. I want a 7-day forecast for each city. The forecast
   endpoint is:
   https://api.weatherapi.com/v1/forecast.json
   with an additional parameter 'days': 7

   Each day in the forecast is in data['forecast']['forecastday'] as a list.
   Extract the date, max temp, min temp, and condition for each day.
   Store everything in the results list.
   ```

3. Review what Claude Code produces. The key change is a nested loop: the outer loop iterates over cities, the inner loop iterates over forecast days. Compare what Claude Code wrote to what you saw in the docs — do the parameter names and response keys match?

4. Run the script and verify you get roughly 140 results.

**Why this matters:** Most project datasets are thin at first. This step shows two ways to bulk them up: loop over more parameters (zip codes) and request more data per call (forecast days). Your project will probably need one or both of these moves.

**Checkpoint:** Your script collects 7-day forecasts for 20 cities — roughly 140 rows of data.

---

### Step 07: View as a Table and Save to CSV

Right now your data is a list of dictionaries in memory. Before saving it, you should see it in a tabular format so you can confirm it looks right.

**What to do:**

1. Ask Claude Code to convert the data to a table and display it:

   ```
   Convert my weather results to a table using pandas and print it out.
   Show me how many rows and columns it has.
   ```

2. Run the script. You should see your data printed as a table with rows and columns, like a spreadsheet. This is a pandas DataFrame — the standard way to work with tabular data in Python. Check that the columns make sense and the row count is what you expect (~140 rows).

3. Now save it. Ask Claude Code:

   ```
   Save the table to a CSV file called weather_data.csv.
   ```

4. Run the script. Confirm `weather_data.csv` appears in your file explorer. Open it in Cursor to see the raw data.

**Why this matters:** Once the data is in a CSV, you can load it into a database, open it in a BI tool, or pass it to a transformation step. The CSV is the handoff point between collection and analysis.

**Checkpoint:** You have a `weather_data.csv` file with roughly 140 rows of forecast data. That is the full pattern: request, parse, loop, table, save.

---

## Part 04: Project Connection

### Step 08: Find APIs for Your Project

For your portfolio project (Milestone 01), you need an API source relevant to the job posting you selected. The pattern you just built works for any REST API. Claude Code can help you find a good candidate for your domain.

**What to do:**

1. Open a **new Cursor window** (**File > New Window**). Clone your portfolio project repo into it the same way you did in Step 00 — click **Clone repo**, paste your project's GitHub URL, and open the folder. Start Claude Code in the terminal.

   You are now working in your project repo, not the weather pipeline. This is where your API exploration will live.

2. In Claude Code, try a prompt like this (replace the bracketed parts with your actual job posting details):

   ```
   I'm building a portfolio project for a [job title] role in [industry].
   The job posting mentions skills like [list a few from your posting].

   What public APIs have data relevant to this role and industry?
   I need an API that:
   - Has a free tier
   - Returns structured JSON data
   - Has enough data to build a star schema with at least one fact table
     and one dimension table
   - Can be automated on a schedule (for GitHub Actions later)

   Suggest 3-5 APIs with a brief description of what data they provide.
   ```

3. Browse the suggestions. For each one, ask Claude Code follow-up questions:
   - "What endpoints does [API name] have?"
   - "Show me a sample response from [endpoint]"
   - "How many rows of data could I realistically collect?"

4. No formal checkpoint here — this is exploration to support your project proposal and Milestone 01 planning.

**What to take away:** The code you write for your project API will look almost identical to `weather.py`. The URL and the JSON keys will change, but the structure will not: request, parse, loop, save. When you sit down to write your Milestone 01 extraction script, start by copying what you built today and swapping in your API's URL and fields.

---

### Step 09: Commit and Push

Your weather pipeline is complete. Time to save your work.

**What to do:**

1. First, save your dependencies so anyone who clones the repo can recreate your environment:

   ```bash
   pip freeze > requirements.txt
   ```

2. In Claude Code, type:

   ```
   Commit all files and push to GitHub.
   ```

3. Verify on GitHub that your `weather-api-pipeline` repo contains your `weather.py` script, `weather_data.csv`, and `requirements.txt`.

**Checkpoint:** Your repo is pushed to GitHub and visible at your repository URL.

---

## Submission

Push your finished `weather-api-pipeline` repository to GitHub and submit the repo URL as your Lesson Exercises 08.

Your repo should contain:
- `weather.py` — your API extraction script with loops and forecast collection
- `weather_data.csv` — the exported data
- `requirements.txt` — your Python dependencies
- `.gitignore` — Python gitignore (from repo setup)
