CREATE TABLE coin_metrics(
    coin_id                 text NOT NULL,     -- Foreign key reference to coins and prices table
    snapshot_date           date NOT NULL,     -- Date when the metrics were calculated
    daily_pct_change        numeric,           -- Daily percentage change in price
    moving_avg_7d           numeric,           -- 7-day moving average price
    daily_volatility        numeric,           -- Daily price volatility measure

    PRIMARY KEY (coin_id, snapshot_date),
    FOREIGN KEY (coin_id, snapshot_date) REFERENCES prices(coin_id, snapshot_date)
);

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