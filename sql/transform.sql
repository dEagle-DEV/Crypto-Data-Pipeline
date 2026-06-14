INSERT INTO coin_metrics (coin_id, snapshot_date, daily_pct_change, moving_avg_7d, daily_volatility)
SELECT
    coin_id,
    snapshot_date,
    (current_price - LAG(current_price) OVER (PARTITION BY coin_id ORDER BY snapshot_date))
        / LAG(current_price) OVER (PARTITION BY coin_id ORDER BY snapshot_date) * 100 AS daily_pct_change,
    AVG(current_price) OVER (
        PARTITION BY coin_id
        ORDER BY snapshot_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS moving_avg_7d,
    high_24h - low_24h AS daily_volatility
FROM prices
ON CONFLICT (coin_id, snapshot_date) DO NOTHING;