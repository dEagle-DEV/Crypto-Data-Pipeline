SELECT COUNT(*) AS row_count
FROM prices
WHERE snapshot_date = CURRENT_DATE
HAVING COUNT(*) != 10;


SELECT current_price, coin_id, snapshot_date
FROM prices
WHERE current_price IS NULL;


WITH price_changes AS (
    SELECT
        coin_id,
        snapshot_date,
        current_price,
        LAG(current_price) OVER (PARTITION BY coin_id ORDER BY snapshot_date) AS prev_price
    FROM prices
)
SELECT coin_id, snapshot_date, current_price, prev_price
FROM price_changes
WHERE prev_price IS NOT NULL
  AND prev_price > 0
  AND (current_price > prev_price * 100 OR current_price < prev_price / 100);