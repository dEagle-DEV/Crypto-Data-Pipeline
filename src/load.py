"""Load stage of the pipeline: persists fetched coin data into PostgreSQL."""

import psycopg2
from datetime import date
import os
from dotenv import load_dotenv

# Read database credentials from the .env file into the environment.
load_dotenv()


def load_data(coins_data):
	"""Upsert a batch of coins and their daily price snapshots into the database.

	Args:
		coins_data: An iterable of coin records (dicts) as returned by the extract step.
	"""

	# Build the connection parameters from environment variables.
	connection_param = {
		'dbname': os.getenv('DB_NAME'),
		'user': os.getenv('DB_USER'),
		'password': os.getenv('DB_PASSWORD'),
		'host' : os.getenv('DB_HOST'),
		'port' : os.getenv('DB_PORT')
	}

	connection = None
	cursor = None

	try:

		connection = psycopg2.connect(**connection_param)
		cursor = connection.cursor()

		for coin in coins_data:
			# Insert the coin's static metadata; skip if the coin already exists.
			cursor.execute("INSERT INTO coins (id, symbol, name, image) VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO NOTHING;",
						(coin['id'], coin['symbol'], coin['name'], coin['image']))
			# Insert today's price snapshot; skip if a snapshot for this coin/date already exists.
			cursor.execute("INSERT INTO prices (coin_id, snapshot_date, current_price, market_cap, market_cap_rank, fully_diluted_valuation, total_volume, high_24h, low_24h, price_change_24h, price_change_percentage_24h, market_cap_change_24h, market_cap_change_percentage_24h, circulating_supply, total_supply, max_supply, ath, ath_change_percentage, ath_date, atl, atl_change_percentage, atl_date, last_updated) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (coin_id, snapshot_date) DO NOTHING;",
						(coin['id'], date.today(), coin['current_price'], coin['market_cap'], coin['market_cap_rank'], coin['fully_diluted_valuation'], coin['total_volume'], coin['high_24h'], coin['low_24h'], coin['price_change_24h'], coin['price_change_percentage_24h'], coin['market_cap_change_24h'], coin['market_cap_change_percentage_24h'], coin['circulating_supply'], coin['total_supply'], coin['max_supply'], coin['ath'], coin['ath_change_percentage'], coin['ath_date'], coin['atl'], coin['atl_change_percentage'], coin['atl_date'], coin['last_updated']))

		# Commit only after all rows have been inserted successfully.
		connection.commit()
		print(f"Successfully loaded {len(coins_data)} coins into PostgreSQL DB.")

	except psycopg2.Error as e:
		# Roll back the whole batch so a partial load is never persisted.
		print(f"Database error: {e}")
		if connection:
			connection.rollback()


	finally:
		# Always release the cursor and connection, even on error.
		if cursor:
			cursor.close()
		if connection:
			connection.close()

if __name__ == "__main__":
	# Allow running this module directly: fetch fresh data, then load it.
	from extract import get_coin_data
	coins_data = get_coin_data()
	load_data(coins_data)