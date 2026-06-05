CREATE TABLE coins (
    id      text, -- Unique cryptocurrency identifier
    symbol  text, -- Ticker symbol of the cryptocurrency
    name    text, -- Full name of the cryptocurrency
    image   text, -- URL to cryptocurrency logo/image

    PRIMARY KEY (id)
);


CREATE TABLE prices(
    coin_id                         text NOT NULL,   -- Foreign key reference to coins table
    snapshot_date                   date NOT NULL,   -- Date when the price snapshot was recorded
    current_price                   numeric NOT NULL, -- Current price of the asset in USD
    market_cap                      numeric,         -- Market capitalization of the asset in USD
    market_cap_rank                 int,             -- Rank by market capitalization
    fully_diluted_valuation         numeric,         -- Market cap if all tokens were in circulation
    total_volume                    numeric,         -- 24-hour trading volume in USD
    high_24h                        numeric,         -- Highest price in the last 24 hours (USD)
    low_24h                         numeric,         -- Lowest price in the last 24 hours (USD)
    price_change_24h                numeric,         -- Absolute price change over the last 24 hours
    price_change_percentage_24h     numeric,         -- Percentage price change over the last 24 hours
    market_cap_change_24h           numeric,         -- Absolute market cap change over the last 24 hours
    market_cap_change_percentage_24h numeric,        -- Percentage change in market cap over the last 24 hours
    circulating_supply              numeric,         -- Number of tokens currently in circulation
    total_supply                    numeric,         -- Total number of tokens that exist
    max_supply                      numeric,         -- Maximum number of tokens that can ever exist
    ath                             numeric,         -- All-time high price of the asset
    ath_change_percentage           numeric,         -- Percentage difference from all-time high
    ath_date                        timestamp,       -- Date when the all-time high was recorded
    atl                             numeric,         -- All-time low price of the asset
    atl_change_percentage           numeric,         -- Percentage difference from all-time low
    atl_date                        timestamp,       -- Date when the all-time low was recorded
    last_updated                    timestamp,       -- Timestamp when the data was last updated

    PRIMARY KEY (coin_id, snapshot_date),
    FOREIGN KEY (coin_id) REFERENCES coins(id)
);