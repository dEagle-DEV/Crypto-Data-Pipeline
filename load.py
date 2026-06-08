import psycopg2
from datetime import date
import os
from dotenv import load_dotenv

load_dotenv()


def load_data(coins_data):

#Connect to existing database
	connection_param = {
		'dbname': os.getenv('DB_NAME'),
		'user': os.getenv('DB_USER'),
		'password': os.getenv('DB_PASSWORD'),
		'host' : os.getenv('DB_HOST'),
		'port' : os.getenv('DB_PORT')
	}

#Establishing the connection
	connection = psycopg2.connect(**connection_param)
	
#Creating a cursor object

	cursor = connection.cursor()



#Step 2: For each coin in coins_data:
	for coin in coins_data:
		cursor.execute("INSERT INTO coins (id, symbol, name, image) VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO NOTHING;",
					(coin['id'], coin['symbol'], coin['name'], coin['image']))
		cursor.execute("INSERT INTO prices (coin_id, snapshot_date, current_price, market_cap, market_cap_rank, fully_diluted_valuation, total_volume, high_24h, low_24h, price_change_24h, price_change_percentage_24h, market_cap_change_24h, market_cap_change_percentage_24h, circulating_supply, total_supply, max_supply, ath, ath_change_percentage, ath_date, atl, atl_change_percentage, atl_date, last_updated) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (coin_id, snapshot_date) DO NOTHING;",
					(coin['id'], date.today(), coin['current_price'], coin['market_cap'], coin['market_cap_rank'], coin['fully_diluted_valuation'], coin['total_volume'], coin['high_24h'], coin['low_24h'], coin['price_change_24h'], coin['price_change_percentage_24h'], coin['market_cap_change_24h'], coin['market_cap_change_percentage_24h'], coin['circulating_supply'], coin['total_supply'], coin['max_supply'], coin['ath'], coin['ath_change_percentage'], coin['ath_date'], coin['atl'], coin['atl_change_percentage'], coin['atl_date'], coin['last_updated']))



				 



#Step 3 - Commit the changes:
	connection.commit()


#Step 4: Close the connection
	cursor.close()
	connection.close()

if __name__ == "__main__":
	from extract import get_coin_data
	coins_data = get_coin_data()
	load_data(coins_data)