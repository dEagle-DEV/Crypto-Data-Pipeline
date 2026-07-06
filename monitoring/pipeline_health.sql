-- How many days of data do we have?

SELECT COUNT(DISTINCT snapshot_date) AS days_of_data
FROM prices;

-- When did the pipeline last run successfully?

SELECT MAX(snapshot_date) AS latest_run
FROM prices;

-- Which coin had the most volatile day this week?

SELECT coin_id, snapshot_date, daily_volatility
FROM coin_metrics
WHERE snapshot_date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY daily_volatility DESC
LIMIT 1;

-- What's the row count growth rate? Storage health? 
SELECT snapshot_date, COUNT(*) AS rows_loaded
FROM prices
GROUP BY snapshot_date
ORDER BY snapshot_date;

SELECT COUNT(*)
FROM coins;

SELECT COUNT(*)
FROM prices;

SELECT COUNT(*)
FROM coin_metrics;
