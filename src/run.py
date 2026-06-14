from extract import get_coin_data
from load import load_data
import psycopg2
import os
from dotenv import load_dotenv

# Read database credentials from the .env file into the environment.
load_dotenv()

def run_transform():
	# Build the connection parameters from environment variables.
	connection_param = {
		'dbname': os.getenv('DB_NAME'),
		'user': os.getenv('DB_USER'),
		'password': os.getenv('DB_PASSWORD'),
		'host' : os.getenv('DB_HOST'),
		'port' : os.getenv('DB_PORT')
	}
	with open("sql/transform.sql") as f:
			data = f.read()
	connection = None
	cursor = None


	try:
		connection = psycopg2.connect(**connection_param)
		cursor = connection.cursor()
		cursor.execute(data)
		connection.commit()
		print(f"Successfully loaded {cursor.rowcount} metrics into PostgreSQL DB.")
			
	except psycopg2.Error as e:
		print(f"Database error: {e}")
		if connection:
			connection.rollback()

	finally:
		if cursor:
			cursor.close()
		if connection:
			connection.close()


if __name__ == "__main__":
	coins_data = get_coin_data()
	load_data(coins_data)
	run_transform()
	






