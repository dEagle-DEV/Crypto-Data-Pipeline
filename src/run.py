from extract import get_coin_data
from load import load_data
from checks import run_checks
import psycopg2
import os
from dotenv import load_dotenv
import datetime
from datetime import date
today_date = date.today().strftime('%Y%m%d')
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename= f'logs/pipeline_{today_date}.log', encoding='utf-8', level=logging.INFO, format='%(asctime)s %(name)s %(funcName)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

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
		logger.info(f'Successfully loaded {cursor.rowcount} metrics into PostgreSQL DB.')

			
	except psycopg2.Error as e:
		logger.error(f'Database error: {e}')
		if connection:
			connection.rollback()

	finally:
		if cursor:
			cursor.close()
		if connection:
			connection.close()


if __name__ == "__main__":
	try:
		coins_data = get_coin_data()

	except Exception as e:
		logger.error(f'Extract failed, aborting pipeline: {e}')
		exit(1)

load_data(coins_data)
run_transform()
run_checks()
	






