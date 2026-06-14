# Crypto Data Pipeline

A small ETL pipeline that pulls cryptocurrency market data from the CoinGecko API,
stores it in PostgreSQL, and calculates a few metrics on top of it (daily price
change, a 7-day moving average, and a daily volatility measure).

I'm building this as a portfolio project while I move into data engineering. It's
meant to be simple on purpose. I wanted to get the whole ETL flow working end to end
with plain Python and SQL before reaching for the bigger tools like Airflow or dbt.

## What it does

Each time you run it, the pipeline grabs the top 10 coins by market cap from CoinGecko
and saves two things: each coin's basic info (name, symbol, logo), and a price snapshot
per coin for that day. Once the raw data is in, a SQL step reads the price history back
out and works out some metrics per coin: the day-over-day percentage change, a rolling
7-day average price, and the daily high-to-low range. Everything goes into Postgres, so
if you run it once a day the tables slowly build up a history you can query.

## Architecture

```
        CoinGecko API
              |
              v
   extract.py    fetch top 10 coins (JSON)
              |
              v
     load.py     upsert into  coins  +  prices
              |
              v
  transform.sql  calculate metrics -> coin_metrics
              |
              v
        PostgreSQL
```

`run.py` is the orchestrator. It calls the three steps in order: extract, then load,
then transform.

## Tech stack

| Component   | Choice                | Why                                                             |
| ----------- | --------------------- | --------------------------------------------------------------- |
| Language    | Python 3.12           | Standard choice for data work, and what I know best.            |
| API         | CoinGecko (free tier) | Free, no API key needed, and well within the rate limit here.   |
| HTTP client | requests              | Simple and everywhere. Didn't need anything fancier.            |
| Database    | Postgres 16           | Solid relational DB. Easy to run in Docker and reset.           |
| DB driver   | psycopg2-binary       | The usual way to talk to Postgres from Python.                  |
| Config      | python-dotenv         | Keeps DB credentials out of source code.                        |
| Schema mgmt | Plain .sql files      | Writing the SQL myself instead of an ORM, to actually learn it. |

## Schema

There are three tables (see [sql/schema.sql](sql/schema.sql)):

- **coins** – the static info that doesn't change between runs (id, symbol, name, image
  URL). Primary key is the coin `id`.
- **prices** – one row per coin per day. The primary key is `(coin_id, snapshot_date)`,
  so there can only be one snapshot per coin per day. `coin_id` is a foreign key back to
  `coins`.
- **coin_metrics** – the calculated values (`daily_pct_change`, `moving_avg_7d`,
  `daily_volatility`), also keyed on `(coin_id, snapshot_date)`, with a foreign key back
  to `prices`.

I split the static data (coins) from the time-series data (prices) on purpose. A coin's
name and logo don't change from one day to the next, so there's no reason to store them
again with every snapshot. Keeping them in their own table means I'm not repeating the
same text on every row, and the prices table stays focused on the stuff that actually
changes day to day.

## How to run it

You'll need Python 3.12 and a running PostgreSQL database. I run Postgres in Docker
because it's easy to throw away and start fresh.

1. Clone the repo and go into it:

   ```bash
   git clone https://github.com/dEAGLE-DEV/Crypto-Data-Pipeline.git
   cd Crypto-Data-Pipeline
   ```

2. Set up a virtual environment and install the dependencies:

   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Start Postgres. If you have Docker, this works:

   ```bash
   docker run --name crypto-pg \
     -e POSTGRES_PASSWORD=your_password \
     -e POSTGRES_DB=your_database_name \
     -p 5432:5432 -d postgres:16
   ```

4. Create the tables by running the schema file against the database:

   ```bash
   psql -h localhost -U your_username -d your_database_name -f sql/schema.sql
   ```

5. Copy the example env file and fill in your own database details:

   ```bash
   cp .env.example .env
   # then edit .env
   ```

6. Run the whole pipeline from the project root:
   ```bash
   python src/run.py
   ```

You can also run the steps on their own while testing: `python src/extract.py` just
prints the data it fetched, and `python src/load.py` fetches and loads without doing the
transform.

One thing to watch: run it from the project root, not from inside `src/`. The transform
step opens `sql/transform.sql` using a path relative to where you start it.

## Project structure

```
Crypto-Data-Pipeline/
├── src/
│   ├── extract.py     # gets the coin data from the CoinGecko API
│   ├── load.py        # writes coins + price snapshots into Postgres
│   └── run.py         # runs extract, load and transform in order
├── sql/
│   ├── schema.sql     # CREATE TABLE statements for the three tables
│   └── transform.sql  # calculates the metrics, inserts into coin_metrics
├── .env.example       # template for the database connection settings
├── requirements.txt   # Python dependencies
└── README.md
```

## Design decisions

**NUMERIC instead of FLOAT for the money columns.** All the price and market-cap fields
use `numeric`, not `float`. Floats can't store decimal values exactly, and those tiny
rounding errors pile up and look wrong on financial data. `numeric` keeps the values
exact, which felt worth the small performance cost.

**Composite primary key on prices.** Instead of adding a separate `id` column, the
primary key is `(coin_id, snapshot_date)`. That matches what a row actually is: one coin
on one day. It also means the database itself stops me from loading the same coin twice
for the same date.

**Idempotent loads with ON CONFLICT.** Both inserts use `ON CONFLICT ... DO NOTHING`, so
if I run the pipeline twice in the same day the second run doesn't error or create
duplicates. It just skips the rows that are already there. That makes the whole thing
safe to re-run, which matters since the idea is to run it on a schedule.

**Config in environment variables.** The database credentials live in a `.env` file
that's gitignored, and the code reads them with python-dotenv. `.env.example` shows
what's needed without committing any real passwords, and the same code runs anywhere as
long as the env vars are set.

**Metrics in SQL, not Python.** The metric calculations live in `transform.sql` and use
window functions (`LAG` for the daily change, `AVG` over a rolling window for the moving
average) instead of pulling everything into Python. The database is already good at this
kind of thing, so it keeps the Python side to just moving data around.

## Limitations and next steps

This is an early version, so there's a fair bit I still want to do.

- **No real scheduling yet.** I run it by hand right now. The obvious next step is a cron
  job, or eventually something like Airflow, to run it once a day on its own.
- **Logging instead of print.** Errors are caught and the database connection is cleaned
  up properly, but I'm using `print` statements where the `logging` module would be more
  appropriate for a real pipeline.
- **"Volatility" is rough.** For now `daily_volatility` is just the 24h high minus the
  low. A standard deviation over a window would be a more honest measure.
- **The metrics need history to mean anything.** With only one snapshot per day, the
  7-day average and the daily change aren't really useful until a week or so of data has
  built up.
- **Only the top 10 coins.** The page size is hard-coded in `extract.py`. I'd make that
  configurable.
- **No tests.** I'd add some unit tests around the transform logic and the loader.
- **Schema setup is manual.** You have to run `schema.sql` yourself. A small setup script
  or an actual migration tool would smooth that out.
